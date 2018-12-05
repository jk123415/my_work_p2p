# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import sqlite3, re, requests


class Sqlite3Database(object):
    def open_spider(self, spider):
        db_file = spider.name + '.db3'
        post = {'title': "title", 'borrowid': "item_code", 'siteid': 'web_code',
                'lastpostdate': 'end', 'daystr': 'period', 'typeimg': '类型图片',
                'posttype': '回复类型', 'postdata': 'invest_records', 'money': 'amount',
                'rate': 'rate', 'senddate': 'start', 'username': 'loaner_info',
                'jiangli': '投标奖励', 'jianglimoney': '奖励金额', 'ratetype': '利率类型',
                'repayment_type': 'pay_type', 'borrow_url': 'url', 'sex': '性别',
                'age': '年龄', 'industry': '所属行业', 'df': '所在地', 'organization': '发布机构',
                'borrow_use': 'loan_using', 'borrower_type': '借款类别',
                'borrow_info': 'loan_info', 'progress': 'progress', 'web_name': 'web_name'}
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
        spider.conn = conn

    def close_spider(self, spider):
        post = {'title': "title",
                'borrowid': "item_code",
                'siteid': 'web_code',
                'lastpostdate': 'end',
                'daystr': 'period',
                'typeimg': '类型图片',
                'posttype': '回复类型',
                'postdata': 'invest_records',
                'money': 'amount',
                'rate': 'rate',
                'senddate': 'start',
                'username': 'loaner_info',
                'jiangli': '投标奖励',
                'jianglimoney': '奖励金额',
                'ratetype': '利率类型',
                'repayment_type': 'pay_type',
                'borrow_url': 'url',
                'sex': '性别',
                'age': '年龄',
                'industry': '所属行业',
                'df': '所在地',
                'organization': '发布机构',
                'borrow_use': 'loan_using',
                'borrower_type': '借款类别',
                'borrow_info': 'loan_info', }
        reg = re.compile('ok')
        post_uri = 'http://101.201.75.34/curl/insert.php'
        colculmus = ','.join(post.values())
        conn = spider.conn
        db = conn.cursor()
        db.execute('''SELECT {} FROM Content WHERE 已发 is null '''.format(colculmus, ))
        # print(db.fetchall())
        lst = db.fetchall()
        if not lst:
            print('Need post data is 0')
        else:
            for postval in lst:
                publish_data = dict(zip(post.keys(), postval))
                # print(publish_data)
                rr = requests.post(post_uri, data=publish_data)
                if re.search(reg, rr.text):
                    print(publish_data['title'], ' issued successfull')
                    db.execute('''UPDATE Content SET 已发=1 WHERE item_code="{}"'''.format(
                        publish_data['borrowid']))
                else:
                    print(publish_data['title'], ' issued failed')
                    db.execute('''UPDATE Content SET 已发=2 WHERE item_code="{}"'''.format(
                        publish_data['borrowid']))
        conn.commit()
        conn.close()
        print("close database------------------------")


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


class SaveData(object):
    def process_item(self, item, spider):
        conn = spider.conn
        db = conn.cursor()
        dic = item
        columns = ', '.join(dic.keys())
        value = (', ?' * len(dic.keys())).strip(', ')
        s = 'select * from Content where item_code="%s"' % dic['item_code']
        db.execute(s)
        lst = db.fetchall()
        if len(lst) == 0:
            statement = 'insert into Content({}) values ({})'.format(columns, value)
            db.execute(statement, tuple(dic.values()))
            print(dic['title'], ' is done')
        else:
            print(dic['title'], ' 已经采集过')


class Publish34(object):
    def close_spider(self, spider):
        pass
