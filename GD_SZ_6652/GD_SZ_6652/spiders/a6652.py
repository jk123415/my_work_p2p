# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from GD_SZ_6652.items import GdSz6652Item
from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader

script = '''
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  local element_ir
  element_ir = splash:select('#borrowInfoNav li:nth-child(3) a')
  element_ir.mouse_click{}
  assert(splash:wait(0.5))
  return {
    html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
  }
end
'''


class A6652Spider(scrapy.Spider):
    name = '6652'
    web_name = '8号金融'
    log_doc = []
    start_urls = [
        'https://www.bahaojinrong.com/web/product/list-{}.html?term=0&state=0'
        .format(x) for x in range(1, 3)]

    def parse(self, response):
        le = LinkExtractor(allow=('id=(.*?)$',))
        urls = le.extract_links(response)
        #'''
        for obj in urls:
            href = obj.url
            yield SplashRequest(url=href, callback=self.parse_item, endpoint='execute',
                                args={'lua_source': script})
        #'''
        '''
        yield SplashRequest(url='https://www.bahaojinrong.com/web/product/detail.html?id=7082a47b5e8f4223b961f0b2ea049820', callback=self.parse_item, endpoint='execute',
                            args={'lua_source': script})
        '''

    def parse_item(self, response):
        url = response.url
        item_list = item_code(url, self.web_name, 'id=(.*?)$')
        print(item_list)
        item = ItemLoader(item=GdSz6652Item(), response=response)
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', url)
        item.add_value('item_code', item_list.get('item_code'))
        item.add_css('title', '.title.border-bottom-light::text')
        item.add_xpath(
            'amount', '//*[contains(text(),"借款金额")]/following-sibling::td[1]/text()')
        item.add_xpath(
            'rate', '//*[contains(text(),"历史年化结算利率")]/../span[1]/text()')
        item.add_xpath(
            'period', '//*[contains(text(),"借款期限（天）")]/../span[1]/text()')
        item.add_xpath(
            'loan_using', '//*[contains(text(),"借款用途")]/following-sibling::td[1]/text()')
        # item.add_xpath('loaner_info', '//*[@id="userName"]')
        item.add_xpath('pay_type', '//*[contains(text(),"回款方式")]/text()')
        item.add_xpath(
            'progress', '//*[contains(text(),"剩余可出借金额（元）")]/../span[1]/text()')

        # invest records
        i_v = []
        invest_records_temp = '{{username={lst[0]}|rate=-1|postmoney={lst[1]}|money={lst[1]}|postdate={lst[2]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('#investRecordWrap').css('tr')
        try:
            for i in tr:
                lst = i.css('td::text').extract()
                if lst:
                    i_v.append(lst)
            for n in i_v:
                invest_records_format += invest_records_temp.format(lst=n)
            item.add_value('invest_records', invest_records_format)
            item.add_value('start', i_v[-1][2])
            item.add_value('end', i_v[0][2])
        except Exception:
            print(url, 'invest records is error')
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
