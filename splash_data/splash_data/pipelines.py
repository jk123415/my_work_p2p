# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import sqlite3


class Sqlite3Database(object):
    def open_spider(self, spider):
        pass


class Rate(object):
    def process_item(self, item, spider):
        if not item['rate']:
            raise DropItem("Missing rate in %s" % item)
        item['rate'] = item['rate'].strip('%')
        return item


class NecessaryData(object):
    def process_item(self, item, spider):
        if not item['title']:
            raise DropItem("Missing title in %s" % item)
        elif not item['amount']:
            raise DropItem("Missing amount in %s" % item)
        elif not item['rate']:
            raise DropItem("Missing rate in %s" % item)
        elif not item['period']:
            raise DropItem("Missing period in %s" % item)
        elif not item['start']:
            raise DropItem("Missing start in %s" % item)
        elif not item['end']:
            raise DropItem("Missing end in %s" % item)
        else:
            return item
