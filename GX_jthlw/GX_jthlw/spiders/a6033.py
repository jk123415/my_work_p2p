# -*- coding: utf-8 -*-
import scrapy
import re
import json
from GX_jthlw.items import GxJthlwItem
from scrapy.loader import ItemLoader
# from scrapy.linkextractors import LinkExtractor
# from scrapy_splash import SplashRequest


def item_code(str1, str2, exp, url=None):
    result = {}
    code = re.search(exp, str1).group(1)
    item_c = str2 + '-' + code
    result['item_code'] = item_c
    if url:
        muti_page = url.format(code)
        result['m_p_u'] = muti_page
    return result


# yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua_splash})


class A6033Spider(scrapy.Spider):
    name = '6033'
    web_name = '金投互联网'
    log_doc = []

    #allowed_domains = ['6033']
    #start_urls = ['https://www.jintouwangdai.com/api']

    def start_requests(self):
        with open('F:\\AAA\\aa.txt') as f:
            tuple_post = f.read().splitlines()
        requests_postval = []
        for postval in tuple_post:
            list_result = {}
            list_a = postval.split("&")
            for b in list_a:
                list_b = b.split("=")
                value = re.subn('%3D', '=', list_b[1])
                list_result[list_b[0]] = value[0]
            requests_postval.append(list_result)
        for poat_data in requests_postval:
            yield scrapy.FormRequest(url="https://www.jintouwangdai.com/api", callback=self.parse, formdata=poat_data)
            # yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': lua_splash})

    def parse(self, response):
        response_dic = json.loads(response.text)
        data = response_dic.get('kdjson').get('items')
        for entry in data:
            item = ItemLoader(item=GxJthlwItem())
            item.add_value('web_name', self.web_name)
            item.add_value('web_code', self.name)
            item.add_value('title', entry['product_name_new'])
            item.add_value('url', response.url+ '/' +entry['product_name_new'])
            item.add_value('item_code', self.web_name + '-' + entry['productCodeNew'])
            item.add_value('amount', str(entry['bondAmount']))
            item.add_value('rate', str(entry['annualrate']))
            item.add_value('period', str(entry['deadLine'])+str(entry['deadLineUnitText']))
            item.add_value('pay_type', entry['repayTypeText'])
            item.add_value('progress', str(entry['isfull']))
            item.add_value('start',str(entry['productCodeNew']))
            item.add_value('end',str(entry['onTime']))
            yield item.load_item()

