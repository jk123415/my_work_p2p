# -*- coding: utf-8 -*-
import scrapy
import re
from LL_2028.items import Ll2028Item
from scrapy.loader import ItemLoader


class BasicSpider(scrapy.Spider):
    name = '2028'
    web_name = '为为贷'
    log_doc = []
    start_urls = ['https://www.wiwidai.com/financing/sbtz/index/{}'.format(x) for x in range(1, 10)]

    def parse(self, response):
        url_list = response.css(
            '.tzlb .w1200:nth-child(1) a::attr(href)').extract()
        try:
            #'''
            for u in url_list:
                href = 'https://www.wiwidai.com%s' % u
                yield scrapy.Request(href, callback=self.parse_item)
            #'''
            #yield scrapy.Request(url='https://www.wiwidai.com/financing/sbtz/bdxq/14638.html', callback=self.parse_item)
        except Exception:
            self.logger.info('列表网址采集错误')

    def parse_item(self, response):
        item = ItemLoader(item=Ll2028Item(), response=response)
        url = response.url
        item_list = item_code(url, self.web_name, '/bdxq/(.*?)\.html')
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', url)
        item.add_value('item_code', item_list.get('item_code'))
        item.add_css('title', '.fl.name::text')
        item.add_xpath(
            'amount', '//*[contains(text(),"借款金额")]/preceding-sibling::div[1]')
        item.add_xpath(
            'rate', '//*[contains(text(),"出借利率")]/preceding-sibling::div[1]')
        item.add_xpath(
            'period', '//*[contains(text(),"项目期限")]/preceding-sibling::div[1]')
        # item.add_xpath('loan_using', '//*[contains(text(),"")]/following-sibling::td[1]/text()')
        item.add_xpath(
            'loaner_info', '//*[contains(text(),"证件号码")]/parent::li[1]')
        item.add_xpath(
            'pay_type', '//*[contains(text(),"还款方式")]/parent::li/text()')
        item.add_css('progress', '.progress_number::text')

        # invest records
        i_v = []
        invest_records_temp = '{{username={lst[1]}|rate=-1|postmoney={lst[2]}|money={lst[2]}|postdate={lst[4]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('[name="third"]').css('tr')
        # print(tr)
        try:
            for i in tr:
                lst = i.css('td *::text').extract()
                if lst:
                    i_v.append(lst)
            for n in i_v:
                invest_records_format += invest_records_temp.format(lst=n)
            item.add_value('invest_records', invest_records_format)
            item.add_value('start', i_v[0][4])
            item.add_value('end', i_v[-1][4])
        except Exception:
            self.logger.info('invest records is error %s' % url)
        yield item.load_item()


def item_code(str1, str2, exp, url=None):
    result = {}
    code = re.search(exp, str1).group(1)
    item_c = str2 + '-' + code
    result['item_code'] = item_c
    if url:
        muti_page = url.format(code)
        result['m_p_u'] = muti_page
    return result
