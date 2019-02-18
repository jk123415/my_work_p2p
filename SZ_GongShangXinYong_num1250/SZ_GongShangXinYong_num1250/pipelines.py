# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.exceptions import DropItem


class SzGongshangxinyongNum1250Pipeline(object):
    def process_item(self, item, spider):
        url = item['url']
        if url:
            return item
        else:
            spider.logger.warning('spider is exception !!!')
            raise DropItem

    def open_spider(self, spider):
        url_file = spider.start_urls_path
        with open(url_file, encoding='utf-8') as f:
            spider.start_urls = f.read().splitlines()


class SAVEDATA(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_ADDR'),
            mongo_db=crawler.settings.get('DB_NAME')
        )

    def open_spider(self, spider):
        self.collection_name = 'a_' + spider.collect_time
        spider.client = pymongo.MongoClient(self.mongo_uri)
        spider.db = spider.client[self.mongo_db]
        spider.collection = spider.db[self.collection_name]

    def process_item(self, item, spider):
        dict_data = dict(item)
        try:
            spider.collection.insert_one(dict_data)
            spider.logger.info(dict_data['name'] + 'is ok')
        except Exception as e:
            spider.logger.worning('mongo_db save except !!!')
            raise DropItem
        else:
            return item

    def close_spider(self, spider):
        spider.client.close()
