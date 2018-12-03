# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from w3lib.html import remove_tags
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from scrapy.selector import Selector


# 两个默认参数selector_1:条目选择器；selector_2:具体数据文本选择器
def invest_records(value, selector_1='tr', selector_2='td::text'):
    inv_rec = Selector(text=value)
    lst_tr = inv_rec.css(selector_1)
    result = list()
    for i in lst_tr:
        text = i.css(selector_2).extract()
        if text: result.append(text)
    return result


class SplashDataItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(),
    )
    amount = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    rate = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    period = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    start = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    end = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    invest_records = scrapy.Field(
        output_processor=Join()
    )
    pay_type = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    loaner_info = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    loan_using = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    loan_info = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    progress = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    code = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        output_processor=Join(), )
    pass
