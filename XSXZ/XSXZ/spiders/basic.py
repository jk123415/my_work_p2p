# -*- coding: utf-8 -*-
import scrapy


class BasicSpider(scrapy.Spider):
    name = 'basic'
    log_doc = []
    allowed_domains = ['www.23us.so']
    start_urls = ['https://www.23us.so/files/article/html/15/15547/index.html']

    def parse(self, response):
        urls = response.css('td a')
        for url in urls:
            yield response.follow(url, callback=self.parse_item)

    def parse_item(self, response):
        item = {}
        item['title'] = response.css('h1::text').extract_first()
        item['content'] = response.css('dl #contents').extract_first()
        item['url'] = response.url
        yield item
