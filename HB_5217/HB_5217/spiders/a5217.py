# -*- coding: utf-8 -*-
import scrapy
import re
from HB_5217.items import Hb5217Item
from scrapy.loader import ItemLoader
# from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest


def item_code(str1, str2, exp, url=None):
    result = {}
    code = re.search(exp, str1).group(1)
    item_c = str2 + '=' + code
    result['item_code'] = item_c
    if url:
        muti_page = url.format(code)
        result['m_p_u'] = muti_page
    return result


lua = '''
function main(splash, args)
  splash.images_enabled = false
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  local username, password, commit
  username = splash:select("[name='email']")
  username:send_keys('minmin520')
  password = splash:select("[name='user_pwd']")
  password:send_keys('minmin520')
  commit = splash:select("#user-login-submit")
  commit:mouse_click{}
  assert(splash:wait(2))
  
  return {
    html = splash:html(),
    png = splash:png(),
    cookies = splash:get_cookies()
    --har = splash:har(),
  }
end
'''

lua_splash = '''
function main(splash, args)
  splash.images_enabled = false
  --splash:init_cookies(args.cookies)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))  
  urls = {}
  local next_element
  local element = splash:select_all('.item-left a')
  for key,value in ipairs(element) do
    local href = value.node.attributes.href
    --local _,_,u = string.find(href,href_pattern)
    table.insert (urls, href)
  end
  for i=1,2,1 do
    next_element = splash:select('.invest-list .pages .next')
    next_element:mouse_click{}
    splash:wait(2)
    local element_1 = splash:select_all('.item-left a')
    for key,value in ipairs(element_1) do
        local href = value.node.attributes.href
        table.insert (urls, href)
    end
  end
  return {
    --html = splash:html(),
    --png = splash:png(),
    href = urls
    --cookies = splash:get_cookies()
    --urls = table.concat(urls," ")
  }
end
'''

lua_just = '''
function main(splash, args)
  splash.images_enabled = false
  splash:init_cookies(args.cookies)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  return {
    html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
  }
end
'''


# yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua_splash})


class A5217Spider(scrapy.Spider):
    name = '5217'
    web_name = '跃马财富-id'
    log_doc = []
    cookies = None
    # allowed_domains = ['5217']
    start_urls = ['https://www.yuemacf.com/index.php?ctl=user&act=login']

    def start_requests(self):
        for url in self.start_urls:
            # yield scrapy.Requests(url, callback=self.parse)
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua})

    def parse(self, response):
        self.cookies = response.data['cookies']
        href = 'https://www.yuemacf.com/index.php?ctl=deals&select=1'
        # yield scrapy.Requests(url, callback=self.parse_item)
        yield SplashRequest(url=href, callback=self.parse_hrefs, endpoint='execute', args={'lua_source': lua_splash,
                                                                                           'cookies': self.cookies})

    def parse_hrefs(self, response):
        # cookies = response.data['cookies']
        urls_dic = response.data['href']
        for i in urls_dic.values():
            url = 'https://www.yuemacf.com' + i
            yield SplashRequest(url, self.parse_item, endpoint='execute', args={'lua_source': lua_just,
                                                                                'cookies': self.cookies})
        '''
        url = 'https://www.yuemacf.com/index.php?ctl=deal&id=41'
        # yield scrapy.Requests(url, callback=self.parse_item)
        yield SplashRequest(url, self.parse_item, endpoint='execute', args={'lua_source': lua_just,
                                                                           'cookies': self.cookies})
        '''

    def parse_item(self, response):
        # print(response.data['html'])
        item = ItemLoader(item=Hb5217Item(), response=response)
        url = response.url
        item_list = item_code(url, self.web_name, 'id=(.*?)$')
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', url)
        item.add_value('item_code', item_list.get('item_code'))

        item.add_css('title', 'h3 a::text')
        item.add_css('amount', '.listcon em::text')
        item.add_css('rate', '.listcon em::text')
        item.add_css('period', '.listcon em::text')
        # item.add_css('loan_using', '::text')
        item.add_css('loaner_info', 'dl')
        item.add_css('pay_type', 'li em::text')
        item.add_css('progress', '#progressPrecent::text')

        # invest records
        i_v = []
        invest_records_temp = '{{username={lst[3]}|rate=-1|postmoney={lst[6]}|money={lst[6]}|postdate={lst[8]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('.box_view_4 tr').css('tr')
        try:
            for i in tr:
                lst = i.css('td *::text').extract()
                if lst:
                    i_v.append(lst)
            # print(i_v)
            for n in i_v:
                invest_records_format += invest_records_temp.format(lst=n)
            item.add_value('invest_records', invest_records_format)
            item.add_value('start', i_v[0][8])
            item.add_value('end', i_v[-1][8])
        except Exception:
            self.logger.info('invest records is error %s' % url)

        yield item.load_item()
