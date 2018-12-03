# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from splash_data.items import SplashDataItem
from scrapy.loader import ItemLoader

lua_splash = '''
function main(splash, args)
  splash.images_enabled = false
  local selector, href_pattern, urls, page_num, next_selector
  urls = {}
  selector = args.selector
  href_pattern = args.href_pattern
  next_selector = args.next_selector
  page_num = args.page_num
  --body
  splash:go(args.url)
  splash:wait(2)
  for i=1,page_num,1 do
  local element = splash:select_all(selector)
  for key,value in ipairs(element) do
    local href = value.node.attributes.href
    local _,_,u = string.find(href,href_pattern)
    table.insert (urls, u)
  end
  next_element = splash:select(next_selector)
  next_element:mouse_click{}
  splash:wait(1)
  end
  return {
    html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
    urls = table.concat(urls," ")
  }
end
'''


class BasicSpider(scrapy.Spider):
    name = 'basic'
    start_urls = ['https://www.fmshang.com/invest.html']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute',
                                args={
                                    'lua_source': lua_splash,
                                    'page_num': 1,
                                    'next_selector': '.js-page-next.js-page-action.ui-pager',
                                    'selector': ".gray",
                                    'href_pattern': 'id=(.*)$',
                                }
                                )

    def parse(self, response):
        string = "https://www.fmshang.com/project/detail.html?id="
        try:
            lst = response.data['urls'].split(" ")
            for i in lst:
                entry_url = string + i
                print("start get: ", entry_url)
                yield SplashRequest(entry_url, self.entry_parse, args={"wait": 5})
        except Exception:
            pass
        else:
            pass

    def entry_parse(self, response):
        # 从表中提取投资记录列表
        # 两个默认参数selector_1:条目选择器；selector_2:具体数据文本选择器
        def invest_records(selector, selector_1='tr', selector_2='td::text'):
            lst_tr = selector.css(selector_1)
            result = list()
            for i in lst_tr:
                text = i.css(selector_2).extract()
                if text: result.append(text)
            return result

        def invest_p2p():
            invest_records = ""
            try:
                for record in invest_records_data:
                    invest_records += "{{name={ls[0]}|amount={ls[1]}}}".format(ls=record)
            except Exception:
                invest_records = None
            return invest_records

        invest_records_data = invest_records(response.css('#invest_record'))
        invest_record_str = invest_p2p()
        # '''
        entry = ItemLoader(item=SplashDataItem(), response=response)
        entry.add_css('title', '#item_name')
        entry.add_css('amount', '.borrow_money::text')
        entry.add_css('rate', '.fontColor.borrow_interest_rate')
        entry.add_css('period', '.borrow_duration')
        entry.add_css('start', '.add_time')
        entry.add_css('loan_info', '.borrow_info')
        entry.add_css('progress', '.fl.progress')
        entry.add_value('invest_records', invest_record_str)
        # entry.add_value('code', response.body)
        return entry.load_item()
        # '''
