# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import sqlite3


class Sqlite3Database(object):
    def open_spider(self, spider):
        db_file = spider.name
        post = {'title': "标题", 'item_code': "编号", 'web_code': '网站编号',
                'end': '时间', 'period': '借款期限', 'typeimg': '类型图片',
                'posttype': '回复类型', 'invest_records': '回复内容', 'amount': '借款金额',
                'rate': '年利率', 'start': '发标时间', 'loaner_info': '作者',
                'jiangli': '投标奖励', 'jianglimoney': '奖励金额', 'ratetype': '利率类型',
                'pay_type': '还款方式', 'url': '网址', 'sex': '性别',
                'age': '年龄', 'industry': '所属行业', 'df': '所在地',
                'organization': '发布机构', 'loan_using': '借款用途',
                'borrower_type': '借款类别', 'loan_info': '借款详情', }
        print('''start initialize database: ''', db_file)
        conn = sqlite3.connect(db_file)
        db = conn.cursor()
        db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name = db.fetchall()
        if ('Content',) not in table_name:
            print('create table: Content in ', db_file)
            s = post.values()
            v = ''
            for i in s:
                c = ', ' + i + ' TEXT'
                v += c
            db.execute(
                'CREATE TABLE Content(ID INTEGER PRIMARY KEY AUTOINCREMENT,已采 TINYINT(1),已发 TINYINT(1){})'.format(v))
        else:
            print('already exist table: Content in ', db_file)
        conn.commit()
        conn.close()


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
