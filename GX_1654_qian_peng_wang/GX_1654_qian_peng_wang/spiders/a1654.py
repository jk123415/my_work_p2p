# -*- coding: utf-8 -*-
import scrapy
import re
from GX_1654_qian_peng_wang.items import Gx1654QianPengWangItem
from scrapy.loader import ItemLoader
# from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest


def item_code(str1, str2, exp, url=None):
    result = {}
    code = re.search(exp, str1).group(1)
    item_c = str2 + '-' + code
    result['item_code'] = item_c
    if url:
        muti_page = url.format(code)
        result['m_p_u'] = muti_page
    return result


lua_splash = '''
function main(splash, args)
  splash.images_enabled=false
  assert(splash:go(args.url))
  assert(splash:wait(5))
  local urls = {}
  local url = splash:select_all('tr td.position-re a')
  for _,v in ipairs(url) do
    local href = v.node.attributes.href
    table.insert (urls, href)
  end
  for i=1,4,1 do
    local next = splash:select('.pagination li:nth-child(7) a'):mouse_click{}
    assert(splash:wait(4))
    local url0 = splash:select_all('tr td.position-re a')
    for _,v in ipairs(url0) do
      local href0 = v.node.attributes.href
      table.insert (urls, href0)
    end
  end
  return {
    cookies = splash:get_cookies(),
    result = urls
  }
end
'''

lua = '''
function main(splash, args)
  splash:init_cookies(args.cookies)
  assert(splash:go(args.url))
  assert(splash:wait(1))
  return {
    html = splash:html(),
    cookies = splash:get_cookies()
  }
end
'''

lua_1 = '''
function main(splash, args)
  splash:init_cookies(args.cookies)
  assert(splash:go(args.url))
  assert(splash:wait(1))
  return {
    html = splash:html(),
    cookies = splash:get_cookies()
  }
end
'''


# yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua_splash})


class A1654Spider(scrapy.Spider):
    name = '1654'
    web_name = '钱盆网'
    log_doc = []

    # allowed_domains = ['1654']
    start_urls = ['https://www.qianpen.com/front/financing/bid/normal/index']

    def start_requests(self):
        for url in self.start_urls:
            # yield scrapy.Requests(url, callback=self.parse)
            yield SplashRequest(url, callback=self.parse, endpoint='execute', args={'lua_source': lua_splash})

    def parse(self, response):
        cookies = response.data['cookies']
        urls_dic = response.data['result']
        for str in urls_dic.values():
            href = 'https://www.qianpen.com%s' % str
            #print(href)
            yield SplashRequest(url=href, callback=self.parse_item, endpoint='execute', args={'lua_source': lua,
                                                                                              'cookies': cookies})
            # yield SplashRequest(url=href, callback=self.parse_item, endpoint='execute', args={'lua_source': lua})
            # yield scrapy.Requests(url, callback=self.parse_item)
            # url_test = 'https://www.qianpen.com/front/financing/bid/normal/detail?id=818585'
            # yield SplashRequest(url=url_test, callback=self.parse_item, endpoint='execute', args={'lua_source': lua,
            #'cookies': cookies})
            # yield scrapy.Request(url=url_test, callback=self.parse_item)

    def parse_item(self, response):
        cookies = response.data['cookies']
        item = ItemLoader(item=Gx1654QianPengWangItem(), response=response)
        url = response.url
        code = re.search('id=(.*?)$', url).group(1)
        # item_list = item_code(url, self.web_name, 'id=(.*?)$')
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', url)
        item.add_value('item_code', code)
        item.add_css('title', '.breadcrumb li:nth-child(3)::text')
        item.add_css('amount', 'center span.bold:nth-child(1)::text')
        item.add_css('rate', 'center span.bold:nth-child(1)::text')
        item.add_css('period', '.padding-top-40 center p:nth-child(2) span::text')
        item.add_css('start', '.progress-border::text')
        progerss = response.css('.progress-border::text').extract_first()
        item.add_value('progress', progerss)
        item.add_css('loan_using', '.project-info span.p-t-cont::text')
        item.add_css('loaner_info', '.borrower-info .p-t-i-right span::text')
        item.add_css('pay_type', 'div.col-xs-4.padding-l-0 span::text')
        data = item.load_item()
        data['invest_records'] = ""
        data['b'] = True
        if progerss == "100%":
            iv_href = 'https://www.qianpen.com/front/financing/bid/normal/bid-join-user?pageNumber=0&id={}'.format(code)
            # req = scrapy.Request(url=iv_href, callback=self.parse_invest_0)
            req = SplashRequest(url=iv_href, callback=self.parse_invest_0, endpoint='execute',
                                args={'lua_source': lua_1,
                                      'cookies': cookies})
            req.meta['data'] = data
            req.meta['code'] = code
            req.meta['num'] = 9
            yield req
        else:
            self.logger.info('this is no done.--%s' % data['title'])
        # req = scrapy.Requests(url, callback=self.parse_invest)

    def parse_invest_0(self, response):
        cookies = response.data['cookies']
        data = response.meta['data']
        code = response.meta['code']
        num = response.meta['num']
        # invest records
        i_v = []
        invest_records_temp = '{{username={lst[1]}|rate=-1|postmoney={lst[2]}|money={lst[2]}|postdate={lst[3]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('tbody').css('tr')
        try:
            for i in tr:
                lst = i.css('td::text').extract()
                if lst:
                    i_v.append(lst)
            for n in i_v:
                invest_records_format += invest_records_temp.format(lst=n)
            if data['b']:
                data['end'] = i_v[0][3]
                data['b'] = False
            data['invest_records'] = data['invest_records'] + invest_records_format
        except Exception:
            self.logger.info('invest records is error %s' % code)
        if num == 0:
            return data
        iv_href = 'https://www.qianpen.com/front/financing/bid/normal/bid-join-user?pageNumber={}&id={}'.format(num,
                                                                                                                code)
        req = SplashRequest(url=iv_href, callback=self.parse_invest_0, endpoint='execute', args={'lua_source': lua_1,
                                                                                                 'cookies': cookies})
        req.meta['data'] = data
        req.meta['code'] = code
        req.meta['num'] = num - 1
        return req
