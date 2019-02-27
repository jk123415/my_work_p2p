# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import pymongo
import requests
from datetime import datetime
import re


class SeletestPipeline(object):
    def process_item(self, item, spider):
        amount = item['amount']
        item['amount'] = amount.strip('元')
        if not item['amount']:
            raise DropItem()
        else:
            rate = item['rate']
            item['rate'] = rate.strip('%')
            if not item['rate']:
                raise DropItem()
            else:
                pay_type = item['pay_type']
                if '一次性还本付息' in pay_type:
                    item['pay_type'] = 3
                else:
                    item['pay_type'] = 0
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
            spider.logger.info(publish_data['title'] + " issued successfull============>>>>>>")
            item['a'] = 1
        else:
            spider.logger.info({'msg': publish_data['title'] + " issued failed", 'time': datetime.now()})
            item['a'] = 0
        return item


class Savepymongo(object):
    """docstring for Save"""
    def __init__(self):
        self.url = 'mongodb://localhost:27017/'
        self.db = 'p2p'
        self.collection = 'a_8235'

    def open_spider(self, spider):
        spider.logger.info('---------open pymongo-client-----------')
        spider.client = pymongo.MongoClient(self.url)
        spider.col = spider.client[self.db][self.collection]

    def process_item(self,item,spider):
        spider.col.insert_one(item)
        return item

    def close_spider(self, spider):
        spider.logger.info('---------close pymongo-client-----------')
        spider.client.close()