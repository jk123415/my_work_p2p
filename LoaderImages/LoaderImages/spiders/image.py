# -*- coding: utf-8 -*-
import scrapy
from LoaderImages.items import LoaderimagesItem


class ImageSpider(scrapy.Spider):
    name = 'image'
    allowed_domains = ['www.mm131.com/']
    start_urls = ['http://www.mm131.com/mingxing/2016.html']

    def parse(self, response):
        item = LoaderimagesItem()
        url = response.css('.content-pic img::attr(src)').extract()
        item['image_urls'] = url
        item['title'] = url
        yield item
