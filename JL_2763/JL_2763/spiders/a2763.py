# -*- coding: utf-8 -*-
import scrapy
import re
from JL_2763.items import Jl2763Item
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
  splash.images_enabled = false
  splash.resource_timeout = 900
  assert(splash:go(args.url))
  assert(splash:wait(0.5))	
  urls = {}
  local next_element
  local element = splash:select_all('.h3_item a')
  for key,value in ipairs(element) do
    local href = value.node.attributes.href
    --local _,_,u = string.find(href,href_pattern)
    table.insert (urls, href)
  end
  for i=1,1,1 do
    next_element = splash:select('.next a')
    next_element:mouse_click{}
    splash:wait(1)
    local element_1 = splash:select_all('.h3_item a')
    for key,value in ipairs(element_1) do
        local href = value.node.attributes.href
        table.insert (urls, href)
    end
  end
  return {
    --html = splash:html(),
    --png = splash:png(),
    href = urls
    --urls = table.concat(urls," ")
  }
end
'''


# yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua_splash})


class A2763Spider(scrapy.Spider):
    name = '2763'
    web_name = '民贷网'
    log_doc = []

    # allowed_domains = ['2763']
    start_urls = ['https://www.mindaiw.com/loanBidFront.do?method=investList']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua_splash})

    def parse(self, response):
        urls_dic = response.data['href']
        for i in urls_dic.values():
            url = 'https://www.mindaiw.com' + i
            yield scrapy.Request(url, callback=self.parse_item)
        '''
        yield scrapy.Request(
            url='https://www.mindaiw.com/investControllerFront.do?method=detail&code=58ba32f7-0b0a-4250-bbc7-7177d2b90bf3',
            callback=self.parse_item)
        '''

    # //*[contains(text(),"")]
    # //*[text()=""]
    # preceding-sibling::div[1]
    # preceding-sibling::div[1]
    # parent::li[1]
    def parse_item(self, response):
        item = ItemLoader(item=Jl2763Item(), response=response)
        url = response.url
        item_list = item_code(url, self.web_name, 'code=(.*?)$')
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', url)
        item.add_value('item_code', item_list.get('item_code'))
        item.add_css('title', '.tit_left_invest::text')
        item.add_css('amount', '.dl_left_invest.width-250 span::text')
        item.add_css('rate', 'dd')
        item.add_css('period', 'dd:nth-child(2)')
        # item.add_xpath('loan_using', '//*[contains(text(),"")]/following-sibling::td[1]/text()')
        # item.add_xpath('loaner_info', '//*[contains(text(),"证件号码")]/parent::li[1]')
        item.add_css('pay_type', '.money_left_invest i::text')
        item.add_css('progress', "[src='/mdw/images/repayment_r.png']")

        # invest records
        i_v = []
        invest_records_temp = '{{username={lst[0]}|rate=-1|postmoney={lst[1]}|money={lst[1]}|postdate={lst[2]}|status=全部通过}}'
        invest_records_format = ""
        tr = response.css('div .table02_repay').css('tr')
        # print(tr)
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
            self.logger.info('invest records is error %s' % url)
        yield item.load_item()
