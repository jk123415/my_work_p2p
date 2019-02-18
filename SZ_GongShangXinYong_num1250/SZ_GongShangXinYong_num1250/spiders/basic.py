# -*- coding: utf-8 -*-
import scrapy
import json


class BasicSpider(scrapy.Spider):
    name = 'gsxy'
    start_urls_path = 'C:\\Users\\Administrator\\Desktop\\sz_gsxy_code.txt'
    collect_time = '20190211'
    database_name = 'gsxy_url_database'

    def start_requests(self):
        if self.start_urls:
            for code in self.start_urls:
                href_mode = 'https://www.szcredit.org.cn/SZXYMBWSercives/WeiXinCXService.asmx/GetList?sNameKey={}&DeptName=&EntType=&IndName=&DataTime=&idcode=ABcdef123321&secret=www.szcredit.org.cn'
                href = href_mode.format(code)
                yield scrapy.Request(url=href, callback=self.parse)

    def parse(self, response):
        item = {}
        data = json.loads(response.text)
        try:
            _id_ = data['Data'][0]['Recordid']
            href_prefix = 'https://www.szcredit.org.cn/xy2.outside/gspt/newGSPTDetail3.aspx?ID={}'
            href = href_prefix.format(_id_)
        except Exception as e:
            self.logger.worning('extract_content is exception: ' + e)
        else:
            item['target_href'] = response.url
            item['url'] = href
            item['credit_code'] = data['Data'][0]['EntSCCode']
            item['name'] = data['Data'][0]['EntName']
            item['addr'] = data['Data'][0]['Addr']
        yield item

