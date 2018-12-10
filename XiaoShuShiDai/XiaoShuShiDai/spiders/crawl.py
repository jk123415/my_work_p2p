# -*- coding: utf-8 -*-
import scrapy


class CrawlSpider(scrapy.Spider):
    name = 'XSSD'
    allowed_domains = ['xiaoshushidai']
    start_urls = ['https://www.xiaoshushidai.cn/plans/p-1',
                  'https://www.xiaoshushidai.cn/plans/p-2']

    def parse(self, response):
        pass
