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


class Ll2028Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(),
    )
    amount = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    rate = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    period = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    start = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    end = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    invest_records = scrapy.Field(
        output_processor=Join()
    )
    pay_type = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    loaner_info = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    loan_using = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    loan_info = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    progress = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    code = scrapy.Field(
        input_processor=MapCompose(remove_tags, lambda x: x.strip()),
        output_processor=Join(), )
    web_name = scrapy.Field(output_processor=Join())
    url = scrapy.Field(output_processor=Join())
    web_code = scrapy.Field(output_processor=Join())
    item_code = scrapy.Field(output_processor=Join())
    a = scrapy.Field()
    b = scrapy.Field()
