# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import requests
import pymongo
from scrapy.exceptions import DropItem
from datetime import datetime

'''
class XsxzPipeline(object):
    def process_item(self, item, spider):
        return item
'''


class XsxzPipeline(object):

    def process_item(self, item, spider):
        pattern = '/(\d+?)\.html'
        code_str = re.search(pattern, item['url'])
        code_num = int(code_str.group(1))
        item['code'] = code_num
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
        with open('jplz.txt', 'w',encoding='utf-8') as f:
            list_data = spider.collection.find({})
            new_list = sorted(list_data, key=lambda x: x['code'])
            for item in new_list:
                print(item['title'])
                a = item['content']
                b = re.subn('<dd id="contents">', "", a)
                c = re.subn('</dd>', "", b[0])
                d = re.subn('\r\n', "", c[0])
                e = re.subn('<br>', "", d[0])
                f.writelines(item['title']+'\n\n'+ e[0] + '\n\n')
        spider.client.close()
        # print(spider.log_doc)

    def process_item(self, item, spider):
        entry = dict(item)
        if entry:
            spider.collection.insert_one(entry)
            spider.logger.info(item['url'] + '-is ok')
            spider.log_doc.append(
                {'msg': item['url'] + "-is ok", 'time': str(datetime.now())})
        return item


class Publish34(object):
    def process_item(self, item, spider):
        entry = dict(item)
        post = {'title': "title", 'borrowid': "item_code", 'siteid': 'web_code',
                'lastpostdate': 'end', 'daystr': 'period', 'typeimg': '类型图片',
                'posttype': '回复类型', 'postdata': 'invest_records', 'money': 'amount',
                'rate': 'rate', 'senddate': 'start', 'username': 'loaner_info',
                'jiangli': '投标奖励', 'jianglimoney': '奖励金额', 'ratetype': '利率类型',
                'repayment_type': 'pay_type', 'borrow_url': 'url', 'sex': '性别',
                'age': '年龄', 'industry': '所属行业', 'df': '所在地', 'organization': '发布机构',
                'borrow_use': 'loan_using', 'borrower_type': '借款类别', 'borrow_info': 'loan_info', }
        reg = re.compile('ok')
        post_uri = 'http://101.201.75.34/curl/insert.php'
        publish_data = {}
        for key, value in post.items():
            publish_data[key] = entry.get(value, None)
        rr = requests.post(post_uri, data=publish_data)
        if re.search(reg, rr.text):
            spider.log_doc.append(
                {'msg': publish_data['title'] + " issued successfull", 'time': datetime.now()})
            spider.logger.info(publish_data['title'] + ' issued successfull')
            item['a'] = 1
        else:
            spider.log_doc.append(
                {'msg': publish_data['title'] + " issued failed", 'time': datetime.now()})
            spider.logger.info(publish_data['title'] + ' issued failed')
            item['a'] = 0
        return item
