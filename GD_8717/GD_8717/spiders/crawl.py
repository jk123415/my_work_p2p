# -*- coding: utf-8 -*-
import scrapy, re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from GD_8717.items import Gd8717Item
from scrapy.loader import ItemLoader
from scrapy.exceptions import DropItem


def item_code(str1, str2, exp, url=None):
    result = {}
    try:
        code = re.search(exp, str1).group(1)
        item_c = str2 + '-' + code
    except Exception:
        print("网址提取code错误")
    else:
        result['item_code'] = item_c
        if url:
            muti_page = url.format(code)
            result['m_p_u'] = muti_page
    return result


def invest_records_list(response, s1, s2='tr', s3='td::text'):
    table = response.css(s1).css(s2)
    result = list()
    for i in table:
        text = i.css(s3).extract()
        if text: result.append(text)
    return result


class CrawlSpider(CrawlSpider):
    name = '8717'
    web_name = '明郡融资租赁'
    # allowed_domains = ['http://www.mjcd168.com']
    start_urls = ['http://www.mjcd168.com/invest/index.html?p=1']

    rules = (
        Rule(LinkExtractor(allow=('invest/index\.html\?p=\d+',), restrict_xpaths=('//*[contains(text(),"下一页")]',))),
        Rule(LinkExtractor(allow=('/invest/\d+\.html',)), callback='parse_item')
    )

    def parse_item(self, response):
        url = response.url
        muti_page_url = "http://www.mjcd168.com/invest/investRecord?borrow_id={}&p=1"
        item_list = item_code(url, self.web_name, 'invest/(.*?)\.html', muti_page_url)
        progress = response.xpath('//*[contains(text(),"剩余可投")]//following-sibling::p/span/text()').extract_first()
        if not progress == "0":
            raise DropItem(url, ' is not done')
        else:
            item = ItemLoader(item=Gd8717Item(), response=response)
            item.add_value('web_name', self.web_name)
            item.add_value('web_code', self.name)
            item.add_value('url', url)
            item.add_value('item_code', item_list.get('item_code'))
            item.add_xpath('title', '//*[@id="fina"]/div/p/text()')
            item.add_xpath('amount', '//*[contains(text(),"项目金额")]//following-sibling::p/span/text()')
            item.add_xpath('rate', '//*[contains(text(),"年化收益")]/text()')
            item.add_xpath('period', '//*[contains(text(),"借款期限")]/text()')
            item.add_xpath('loan_using', '//*[contains(text(),"借款用途")]/text()')
            item.add_xpath('loaner_info', '//*[@id="userName"]')
            item.add_xpath('pay_type', '//*[contains(text(),"还款方式")]/text()')
            item.add_xpath('progress', '//em/text()')
            # item.add_value('invest_records', invest_record_str)
            # item.add_value('start', time_value[0])
            # item.add_value('end', time_value[1])
            entry = item.load_item()
            request = scrapy.Request(item_list.get('m_p_u'), callback=self.parse_i_r)
            request.meta['entry'] = entry
            yield request

    def parse_i_r(self, response):
        entry = response.meta['entry']
        i_v = []
        invest_records_temp = '{{username={lst[0]}|rate=-1|postmoney={lst[3]}|money={lst[3]}|postdate={lst[2]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('tr')
        for i in tr:
            lst = i.css('td::text').extract()
            i_v.append(lst)
        for n in i_v:
            invest_records_format += invest_records_temp.format(lst=n)
        entry['invest_records'] = invest_records_format
        entry['start'] = i_v[-1][2]
        entry['end'] = i_v[0][2]
        yield entry
