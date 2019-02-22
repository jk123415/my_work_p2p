# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider


class BasicSpider(Spider):
    name = 'basic'
    start_urls = ['https://wap.xiaogelicai.com/pro_det?borrowId=1508']


    def parse(self, response):
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        item['title'] = response.css('.basic-info .pt .clear span').getall()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item
