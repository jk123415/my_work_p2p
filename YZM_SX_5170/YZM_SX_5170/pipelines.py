# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re, requests
import pymongo
from scrapy.exceptions import DropItem
from datetime import datetime


class YzmSx5170Pipeline(object):
    def process_item(self, item, spider):
        period = re.subn('[\r\n\t\s]', "", item['period'])
        item['period'] = re.search('^(.*?)借款期限', period[0]).group(1)

        rate = re.search('^(.*?)%', item['rate']).group(1)
        item['rate'] = rate

        # title = item['title'].strip('\xa0')
        # item['title'] = title

        pay_type = item['pay_type']
        if re.search('到期还本', pay_type):
            item['pay_type'] = '4'
        else:
            item['pay_type'] = '0'

        end = item['end']
        if not end:
            spider.log_doc.append({'msg': item['url'] + "-时间采集错误", 'time': str(datetime.now())})
            # print('时间采集错误')
            raise DropItem
        if not item['title']:
            spider.log_doc.append({'msg': item['url'] + "-标题采集错误", 'time': str(datetime.now())})
            # print('时间采集错误')
            raise DropItem
        if not item['amount']:
            spider.log_doc.append({'msg': item['url'] + "-amount采集错误", 'time': str(datetime.now())})
            # print('时间采集错误')
            raise DropItem
        if not item['rate']:
            spider.log_doc.append({'msg': item['url'] + "-rate采集错误", 'time': str(datetime.now())})
            # print('时间采集错误')
            raise DropItem
        if not item['period']:
            spider.log_doc.append({'msg': item['url'] + "-period采集错误", 'time': str(datetime.now())})
            # print('时间采集错误')
            raise DropItem
        if not item['start']:
            spider.log_doc.append({'msg': item['url'] + "-start采集错误", 'time': str(datetime.now())})
            # print('时间采集错误')
            raise DropItem
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
        spider.collection_log.insert_many(spider.log_doc)
        spider.client.close()
        # print(spider.log_doc)

    def process_item(self, item, spider):
        spider.collection.insert_one(dict(item))
        # print(item['url'], '-is ok')
        spider.log_doc.append({'msg': item['url'] + "-is ok", 'time': str(datetime.now())})
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
            spider.log_doc.append({'msg': publish_data['title'] + " issued successfull", 'time': datetime.now()})
            # print(publish_data['title'], ' issued successfull')
            item['a'] = 1
        else:
            spider.log_doc.append({'msg': publish_data['title'] + " issued failed", 'time': datetime.now()})
            # print(publish_data['title'], ' issued failed')
            item['a'] = 0
        return item
