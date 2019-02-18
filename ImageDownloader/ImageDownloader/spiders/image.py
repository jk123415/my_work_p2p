# -*- coding: utf-8 -*-
import scrapy
from ImageDownloader.items import ImagedownloaderItem


class ImageSpider(scrapy.Spider):
    name = 'image'
    start_urls = ['https://www.p2p001.com/']

    def parse(self, response):
        item = ImagedownloaderItem()
        img_url = response.css('li img::attr(src)').extract()
        item['img_url'] = img_url
        yield item
