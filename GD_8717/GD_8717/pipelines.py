# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re, requests
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
        print(item['url'], '-- is ok')
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
            print(publish_data['title'], ' issued successfull')
            item['a'] = 1
        else:
            print(publish_data['title'], ' issued failed')
            item['a'] = 0
        return item
