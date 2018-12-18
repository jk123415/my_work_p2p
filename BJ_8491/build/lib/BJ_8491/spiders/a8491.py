# -*- coding: utf-8 -*-
import scrapy, re
from scrapy_splash import SplashRequest
from BJ_8491.items import Bj8491Item
from scrapy.loader import ItemLoader

script = '''
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  local html, next
  item_list = {}
  html = splash:html()
  table.insert(item_list,html)
  for i=1,3,1 do
    next = splash:select('.btn-next')
  	next:mouse_click{}
  	assert(splash:wait(2))
  	html = splash:html()
  	table.insert(item_list,html)
  end
  return {
    html = table.concat(item_list,",,,")
    --png = splash:png(),
    --har = splash:har(),
  }
end
'''


class A8491Spider(scrapy.Spider):
    name = '8491'
    web_name = '易嘉金服'
    log_doc = []
    start_urls = ['https://www.jiajiabank.com/SportsEvent']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': script})

    def parse(self, response):
        data = response.data['html']
        html_code = data.split(',,,')
        for resp in html_code:
            html_s = scrapy.selector.Selector(text=resp)
            for e in html_s.css('.el-table__body tr'):
                entry = e.css('td').extract()
                item = ItemLoader(item=Bj8491Item())
                item.add_value('web_name', self.web_name)
                item.add_value('title', entry[0])
                item.add_value('rate', entry[1])
                item.add_value('period', entry[2])
                item.add_value('pay_type', entry[3])
                item.add_value('amount', entry[4])
                item.add_value('progress', entry[6])
                yield item.load_item()


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
