# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from w3lib.html import remove_tags
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from scrapy.selector import Selector


'''
class ImagedownloaderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
'''

class ImagedownloaderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(),
    )
    img_url = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    url = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    path = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    time = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
