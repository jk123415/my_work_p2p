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
class Hn8736181225Pipeline(object):
    def process_item(self, item, spider):
        return item
'''


class Hn8736181225Pipeline(object):

    def process_item(self, item, spider):
        # period = re.subn('[\r\n\s]', "", item['period'])
        # item['period'] = period[0] + '天'

        # progress = re.subn('[\r\n\s]', "", item['progress'])
        # item['progress'] = progress[0]
        if item['progress'] == '100%':
            item['progress'] = None

        # rate = re.subn('[\r\n\t\s%]', "", item['rate'])
        # item['rate'] = str(eval(rate[0]))

        # amount = re.search('^(.*?)万元融资金额', item['amount']).group(1)
        # item['amount'] = str(float(amount) * 10000)

        title = re.subn('[\xa0]', "", item['title'])
        item['title'] = title[0]

        invest_r = re.subn('[\t\n]', "", item['invest_records'])
        item['invest_records'] = invest_r[0]

        try:
            loaner_info = re.subn('[\t\n\s]', "", item['loaner_info'])
            item['loaner_info'] = loaner_info[0][:50]
        except Exception:
            spider.logger.info('loaner_info is error --%s' % item['url'])
        '''
        amount = item['amount']
        if re.search('万元', amount):
            num = amount.strip('万元')
            amount_f = float(num) * 10000
            item['amount'] = str(amount_f)
        else:
            item['amount'] = amount.strip('元')
        '''

        pay_type = item['pay_type']
        if re.search('按月付息', pay_type):
            item['pay_type'] = '4'
        else:
            item['pay_type'] = '4'

        if not item['title']:
            spider.log_doc.append(
                {'msg': item['url'] + "-标题采集错误", 'time': str(datetime.now())})
            spider.logger.info('title 采集错误')
            raise DropItem
        if not item['amount']:
            spider.log_doc.append(
                {'msg': item['url'] + "-amount采集错误", 'time': str(datetime.now())})
            spider.logger.info('amount 采集错误')
            raise DropItem
        if not item['rate']:
            spider.log_doc.append(
                {'msg': item['url'] + "-rate采集错误", 'time': str(datetime.now())})
            spider.logger.info('rate 采集错误')
            raise DropItem
        if not item['period']:
            spider.log_doc.append(
                {'msg': item['url'] + "-period采集错误", 'time': str(datetime.now())})
            spider.logger.info('period 采集错误')
            raise DropItem
        if item['progress']:
            spider.logger.info(item['url'] + '-is not done')
            spider.log_doc.append(
                {'msg': item['url'] + "-is not done", 'time': str(datetime.now())})
            raise DropItem
        if not item['start']:
            spider.log_doc.append(
                {'msg': item['url'] + "-start采集错误", 'time': str(datetime.now())})
            spider.logger.info('start 采集错误')
            raise DropItem
        if not item['end']:
            spider.log_doc.append(
                {'msg': item['url'] + "-时间采集错误", 'time': str(datetime.now())})
            spider.logger.info('end 采集错误')
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
            spider.logger.info(publish_data['title'] + ' issued successfull')
            item['a'] = 1
        else:
            spider.log_doc.append({'msg': publish_data['title'] + " issued failed", 'time': datetime.now()})
            spider.logger.info(publish_data['title'] + ' issued failed')
            item['a'] = 0
        return item
