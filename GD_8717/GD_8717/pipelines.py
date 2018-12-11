# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import pymongo
from scrapy.exceptions import DropItem


class Gd8717Pipeline(object):
    def process_item(self, item, spider):
        period = re.subn(' ', "", item['period'])
        item['period'] = re.search('借款期限：(.*?)$', period[0]).group(1)

        rate = re.search('年化收益：(.*?)%', item['rate']).group(1)
        item['rate'] = rate

        title = item['title'].strip('\xa0')
        item['title'] = title

        pay_type = item['pay_type']
        if re.search('每月还息到期还本', pay_type):
            item['pay_type'] = '4'
        else:
            item['pay_type'] = '0'

        end = item['end']
        if not end:
            print('时间采集错误')
            raise DropItem()
        return item


class SaveMongodb(object):
    def process_item(self, item, spider):
        client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        db = client.p2p
        collection = db.p8717
        collection.insert_one(dict(item))
        print(item['title'], '-- is ok')
        return item
