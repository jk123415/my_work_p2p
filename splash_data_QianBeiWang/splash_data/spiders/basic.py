# -*- coding: utf-8 -*-
import scrapy, re
from scrapy_splash import SplashRequest
from splash_data.items import SplashDataItem
from scrapy.loader import ItemLoader
from scrapy.exceptions import DropItem

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
  splash:wait(1)
  local element = splash:select(args.selector_all)
  element:mouse_click{}
  splash:wait(2)
  local element_url = splash:select_all(selector)
  for key,value in ipairs(element_url) do
    local href = value.node.attributes.href
    local _,_,u = string.find(href,href_pattern)
    table.insert (urls, u)
  end
  return {
    --html = splash:html(),
    --png = splash:png(),
    --har = splash:har(),
    urls = table.concat(urls," ")
  }
end
'''


class BasicSpider(scrapy.Spider):
    name = 'QBW'
    start_urls = ['http://www.qianbeimoney.com/newInvest/4']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute',
                                args={
                                    'lua_source': lua_splash,
                                    'page_num': 1,
                                    'selector_all': 'div.xmqixian00 div:nth-child(2)',
                                    'selector': ".ljjr1",
                                    'href_pattern': 'invest/(.*)/$',
                                }
                                )

    def parse(self, response):
        string = "http://www.qianbeimoney.com/front/invest/{}/"
        try:
            lst = response.data['urls'].split(" ")
            for i in lst:
                entry_url = string.format(i)
                print("start get: ", entry_url)
                yield scrapy.Request(entry_url, callback=self.public_info_parse)
        except Exception:
            pass
        else:
            pass

    def public_info_parse(self, response):
        title = response.css('.asfw::text').extract_first()
        rate = response.css('.uyasw span::text').extract_first()
        period = response.css('.adbhu *::text').extract_first()
        remainder_amount = response.css('.bdja span::text').extract_first()
        invest_records_url = 'http://www.qianbeimoney.com/front/invest/ajaxInvestHis'
        if remainder_amount != '0':
            print(title, ' is not done')
            raise DropItem()
        else:
            formdata = {"Page": '1', "bid": '8'}
            request_1 = scrapy.FormRequest(invest_records_url, formdata=formdata, callback=self.invest_records_page_num)
            item = {}
            item['title'] = title
            item['rate'] = rate
            item['period'] = period + '个月'
            request_1.meta['item'] = item
            yield request_1

    def invest_records_page_num(self, response):
        item = response.meta['item']

        try:
            page_num = response.css('.pageDivClass::text').extract_first()
            num_str = re.findall('共(.*?)页', page_num)[0]
            num = int(num_str) + 1
        except Exception:
            print(item['title'], '-投资记录页数提取出错')
            raise DropItem()
        else:
            formdata = {"Page": None, "bid": '8'}
            invest_records_url = 'http://www.qianbeimoney.com/front/invest/ajaxInvestHis'
            for i in range(0, num):
                formdata['Page'] = str(i)
                request_2 = scrapy.FormRequest(invest_records_url, formdata=formdata, callback=self.entry_parse)
                request_2.meta['item'] = item
                yield request_2

    def entry_parse(self, response):
        public_data = response.meta['item']

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
                    invest_records += "{{username={ls[0]}|rate=-1|postmoney={ls[1]}|money={ls[1]}|postdate={ls[2]}|status=全部通过}}".format(
                        ls=record)
            except Exception:
                invest_records = None
            return invest_records

        def time_handle():
            if invest_records_data:
                start_time = invest_records_data[start[0]][start[1]]
                end_time = invest_records_data[end[0]][end[1]]
                result_time = (start_time, end_time)
            else:
                result_time = (None, None)
            return result_time

        def item_code_handle():
            try:
                url_str = invest_records_data[0][0]
                return public_data['title'] + "-" + url_str
            except Exception:
                return None

        web_name = '钱贝网智投'
        web_code = '8191'
        start = (0, 2)
        end = (0, 2)
        invest_records_data = invest_records(response.css('table'))
        # invest_record_str = invest_p2p()
        # item_code = item_code_handle()
        # '''
        for n in invest_records_data:
            time_value = n[2]
            item_code = public_data['title'] + '-' + n[0]
            entry = ItemLoader(item=SplashDataItem(), response=response)
            entry.add_value('web_name', web_name)
            entry.add_value('web_code', web_code)
            entry.add_value('url', response.url)
            entry.add_value('item_code', item_code)
            entry.add_value('title', public_data['title'])
            entry.add_value('amount', n[3])
            entry.add_value('rate', public_data['rate'])
            entry.add_value('period', public_data['period'])
            entry.add_value('start', time_value)
            entry.add_value('end', time_value)
            entry.add_value('pay_type', '0')
            yield entry.load_item()
        # '''
