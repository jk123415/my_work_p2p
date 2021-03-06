# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
from YZM_SX_5170.items import YzmSx5170Item
from scrapy.loader import ItemLoader

lua_splash = '''
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  local name, password
  name = splash:select('#username')
  name:send_keys('minmin520')
  local bf_c = splash:select('#tx')
  bf_c:mouse_click{}
  password = splash:select('#password')
  password:send_keys('minmin520')
  --
  assert(splash:wait(0.5))
  local commit = splash:select('#login-btn')
  commit:mouse_click{}
  assert(splash:wait(1))
  assert(splash:go("https://www.guangdiancaifu.com/invest/list"))
  assert(splash:wait(1))

  return {
    html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
    cookies = splash:get_cookies()
  }
end
'''

lua = '''
function main(splash, args)
  splash:init_cookies(splash.args.cookies)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  return {
    html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
  }
end
'''


def item_code(str1, str2, exp, url=None):
    result = {}
    try:
        code = re.search(exp, str1).group(1)
        item_c = str2 + '-' + code
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


class BasicSpider(scrapy.Spider):
    name = '5170'
    web_name = '广电财富'
    log_doc = []
    start_urls = ['https://www.guangdiancaifu.com/login']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua_splash})

    def parse(self, response):
        cookies = response.data['cookies']
        # 采集页数
        '''
        post_val = [{"currentPage": str(i), "priceRangeIndex": "0", "interestRangeIndex": "0", "termCountIndex": "0",
                     "loanStatusIndex": "0", "loanTypeIndex": "0"} for i in range(1, 5)]
        for pv in post_val:
            yield scrapy.FormRequest(url, formdata=pv, cookies=cookies, callback=self.parse_list,
                                     meta={'cookiejar': 1})
        '''
        url_list = response.css('#hot-tabs-content1 a::attr(href)').extract()

        for url in url_list:
            if url != '#':
                href = 'https://www.guangdiancaifu.com' + url
            # yield SplashRequest(href, self.item, endpoint='execute', args={'lua_source': lua
            #'cookies': cookies})
                yield SplashRequest(url=href, callback=self.parse_item, endpoint='execute', args={'lua_source': lua,
                                                                                                  'cookies': cookies})
            else:
                return None

    def parse_list(self, response):
        lk = LinkExtractor(allow=('/loan/'))
        for url in lk.extract_links(response):
            yield scrapy.Request(url.url, callback=self.parse_item, meta={'cookiejar': response.meta['cookiejar']})
        # yield
        # scrapy.Request(url="https://www.guangdiancaifu.com/loan/528683",
        # callback=self.parse_item, meta={'cookiejar':
        # response.meta['cookiejar']})

    def parse_item(self, response):
        url = response.url
        item_list = item_code(url, self.web_name, '/loan/(.*?)$')
        item = ItemLoader(item=YzmSx5170Item(), response=response)
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', url)
        item.add_value('item_code', item_list.get('item_code'))
        item.add_xpath('title', '//title/text()')
        item.add_css('amount', "p[style='text-align: left;']")
        item.add_xpath('rate', "//ul[@class='left-1-ul']//li[2]//p[1]")
        item.add_xpath('period', "//ul[@class='left-1-ul']//li[3]//p[1]")
        item.add_xpath(
            'loan_using', '//*[contains(text(),"资金用途")]/following-sibling::div[1]/p/text()')
        # item.add_xpath('loaner_info', '//*[@id="userName"]')
        item.add_css('pay_type', '.left-1-ol span:nth-child(1)')
        item.add_xpath(
            'progress', "//ol[@class='left-1-ol']//li[2]/span/text()")

        # invest records
        i_v = []
        invest_records_temp = '{{username={lst[0]}|rate=-1|postmoney={lst[2]}|money={lst[2]}|postdate={lst[1]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('.invest-table').css('tr')
        if not tr:
            tr = response.css('.tou.info-tab-main').css('tr')
        try:
            for i in tr:
                lst = i.css('td::text').extract()
                i_v.append(lst)
            for n in i_v:
                invest_records_format += invest_records_temp.format(lst=n)
            item.add_value('invest_records', invest_records_format)
            item.add_value('start', i_v[1][1])
            item.add_value('end', i_v[-1][1])
        except Exception:
            print(url, 'invest records is error')
        yield item.load_item()
