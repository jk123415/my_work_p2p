# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_splash import SplashRequest
from GD_5176.items import Gd5176Item
from scrapy.loader import ItemLoader

lua_splash = '''
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(1))
  local element = splash:select('.section-nav li:nth-child(3)')
  element:mouse_click{}
  assert(splash:wait(1))
  return {
    html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
  }
end
'''


class A5176Spider(scrapy.Spider):
    name = '5176'
    web_name = '小树时贷'
    log_doc = []

    start_urls = [
        'https://www.xiaoshushidai.cn/plans/p-{}'.format(x) for x in range(1, 2)]

    def parse(self, response):
        self.logger.info('Parse function called on %s' % response.url)
        le = LinkExtractor(allow=('plans-detail/id-(.*?)$',))
        url_list = le.extract_links(response)
        for le in url_list:
            url = le.url
            yield SplashRequest(url, self.parse_item, endpoint='execute',
                                args={'lua_source': lua_splash, })

    def parse_item(self, response):
        url = response.url
        item_list = item_code(url, self.web_name, 'plans-detail/id-(.*?)$')
        item = ItemLoader(item=Gd5176Item(), response=response)
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', url)
        item.add_value('item_code', item_list.get('item_code'))
        item.add_css('title', '.plan-header.f18 .vm::text')
        item.add_xpath('amount', '//*[contains(text(),"出借金额")]/../span')
        item.add_xpath('rate', '//*[@id="plan-rate"]/following-sibling::span[1]')
        item.add_xpath('period', '//*[@id="repay-time"]/following-sibling::span[1]')
        #item.add_xpath('loan_using', '//*[contains(text(),"资金用途")]/following-sibling::div[1]/p/text()')
        # item.add_xpath('loaner_info', '//*[@id="userName"]')
        item.add_xpath('pay_type', '//*[contains(text(),"还款方式：")]/../text()')
        item.add_xpath('progress', '//*[contains(text(),"出借进度")]/..')
        # invest records
        i_v = []
        invest_records_temp = '{{username={lst[0]}|rate=-1|postmoney={lst[2]}|money={lst[2]}|postdate={lst[3]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('.schedule-section.jion-records table').css('tr')
        try:
            for i in tr:
                lst = i.css('td::text').extract()
                i_v.append(lst)
            for n in i_v:
                try:
                    invest_records_format += invest_records_temp.format(lst=n)
                except Exception:
                    pass
            item.add_value('invest_records', invest_records_format)
            item.add_value('start', i_v[1][3])
            item.add_value('end', i_v[-1][3])
        except Exception:
            self.logger.info('invest records is error: %s' % url)
        yield item.load_item()


def item_code(str1, str2, exp, url=None):
    result = {}
    try:
        code = re.search(exp, str1).group(1)
        item_c = str2 + '-智投E-' + code
    except Exception:
        pass
        # print("网址提取code错误")
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
