# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from SX_8672.items import Sx8672Item
from scrapy.loader import ItemLoader
from datetime import datetime


def item_code(str1, str2, exp, url=None):
    result = {}
    try:
        code = re.search(exp, str1).group(1)
        item_c = str2 + '-' + code
    except Exception:
        pass
        spider.logger.info("网址提取code错误")
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
        if text:
            result.append(text)
    return result


class A8672Spider(CrawlSpider):
    name = '8672'
    web_name = '合享众成'
    log_doc = []
    start_urls = ['http://www.hexzc.com/invest/index.html?p=1']

    rules = (
        Rule(LinkExtractor(restrict_xpaths=(
            '//a[text()="下一页"]',)), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=('/invest/(.*?)\.html',)),
             callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        url = response.url
        muti_page_url = "http://www.hexzc.com/invest/investRecord?borrow_id={}&p=1"
        item_list = item_code(url, self.web_name,
                              'invest/(.*?)\.html', muti_page_url)
        progress = response.css(
            '.ui-progressbar-mid.ui-progressbar-mid-100 em::text').extract_first()
        if not progress == "100%":
            self.log_doc.append(
                {'msg': url + " is not done", 'time': str(datetime.now())})
            self.logger.info(url + " is not done")
            yield None
        else:
            item = ItemLoader(item=Sx8672Item(), response=response)
            item.add_value('web_name', self.web_name)
            item.add_value('web_code', self.name)
            item.add_value('url', url)
            item.add_value('item_code', item_list.get('item_code'))
            item.add_xpath('title', '//*[@class="project_left"]/h3/text()')
            item.add_xpath(
                'amount', '//*[contains(text(),"年利率")]/../following-sibling::ul[1]/li[1]/span[1]')
            item.add_xpath(
                'rate', '//*[contains(text(),"年利率")]/../following-sibling::ul[1]/li[1]/span[2]')
            item.add_xpath(
                'period', '//*[contains(text(),"年利率")]/../following-sibling::ul[1]/li[1]/span[3]')
            item.add_xpath('loaner_info', '//*[@id="userName"]')
            item.add_xpath('pay_type', '//*[contains(text(),"还款方式")]/text()')
            item.add_value('progress', progress)
            entry = item.load_item()
            request = scrapy.Request(item_list.get(
                'm_p_u'), callback=self.parse_i_r)
            request.meta['entry'] = entry
            yield request

    def parse_i_r(self, response):
        entry = response.meta['entry']
        i_v = []
        invest_records_temp = '{{username={lst[0]}|rate=-1|postmoney={lst[2]}|money={lst[2]}|postdate={lst[4]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('tr')
        try:
            for i in tr:
                lst = i.css('td::text').extract()
                i_v.append(lst)
            for n in i_v:
                invest_records_format += invest_records_temp.format(lst=n)
            entry['invest_records'] = invest_records_format
            entry['start'] = i_v[0][4]
            entry['end'] = i_v[-1][4]
        except Exception:
            self.logger.info(entry['url'] + ' invest records is error')
        yield entry
