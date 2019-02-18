# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import scrapy
import pymongo
from scrapy.exceptions import DropItem
from datetime import datetime
from scrapy.pipelines.images import ImagesPipeline

class ImagedownloaderPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db, collection_name, collection_log_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.collection_log_name = collection_log_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            collection_name=crawler.settings.get('MONGODB_DOCNAME'),
            collection_log_name=crawler.settings.get('MONGODB_LOG_DOCNAME')
        )

    def open_spider(self, spider):
        spider.client = pymongo.MongoClient(self.mongo_uri)
        spider.db = spider.client[self.mongo_db]
        spider.collection = spider.db[self.collection_name]
        spider.collection_log = spider.db[self.collection_log_name]
        # spider.log_doc = []

    def close_spider(self, spider):
        if spider.log_doc:
            spider.collection_log.insert_many(spider.log_doc)
        spider.client.close()
        # print(spider.log_doc)

    def process_item(self, item, spider):
        entry = dict(item)
        if entry:
            spider.collection.insert_one(entry)
            spider.logger.info(item['url'] + '-is ok')
            spider.log_doc.append({'msg': item['url'] + "-is ok", 'time': str(datetime.now())})
        return item


class ImageDown(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item['img_url']:
            yield scrapy.Request(url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item