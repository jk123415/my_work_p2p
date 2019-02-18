# -*- coding: utf-8 -*-
import scrapy
import pymongo
import pprint

class Basicself(scrapy.Spider):
    name = 'gsxy'
    save_time = '20190212_test'

    def __init__(self):
        self.mongodb_url = 'mongodb://localhost:27017/'
        self.mongodb_db = 'SZ_GSXY_CODE'
        self.client = pymongo.MongoClient(self.mongodb_url)
        self.db = self.client[self.mongodb_db]
        self.request_urls_col = self.db['a_20190211']
        self.request_urls = self.request_urls_col.find({})
        save_col_name = 'b_%s' % self.save_time
        self.save_db_col = self.db[save_col_name]

    def start_requests(self):
        for dic_data in self.request_urls:
            href = dic_data.get('url')
            #print(href)
        # yield scrapy.Request(url=href, callback=self.parse)
        test_url = 'https://www.szcredit.org.cn/xy2.outside/gspt/newGSPTDetail3.aspx?ID=78ec60b0dd4b4188af4c8601ee96ddc2'
        yield scrapy.Request(url=test_url, callback=self.parse_item)


    def parse_item(self, response):
        item = {}
        item['url'] = response.url
        # 主体名称
        item['principal_name'] = response.css('.detailsList tr:nth-child(3) td:nth-child(2)::text').get()
        # 注册号
        item['registration_number'] = response.css('.detailsList tr:nth-child(1) td:nth-child(2)::text').get()
        # 统一社会信用代码
        item['credit_code'] = response.css('.detailsList tr:nth-child(2) td:nth-child(2)::text').get()
        # 法定代表人
        item['legal_representative'] = response.css('#tb_0 tr:nth-child(4) td:nth-child(2)::text').get()
        # 住所
        item['residence'] = response.css('.detailsList tr:nth-child(5) td:nth-child(2)::text').get()
        # 成立日期
        item['found_date'] = response.css('.detailsList tr:nth-child(6) td:nth-child(2)::text').get()
        # 营业期限
        item['term_of_operation'] = response.css('.detailsList tr:nth-child(7) td:nth-child(2)::text').get()
        # 核准日期
        item['approval_date'] = response.css('.detailsList tr:nth-child(8) td:nth-child(2)::text').get()
        # 认缴注册资本总额
        item['registered_capital'] = response.css('.detailsList tr:nth-child(9) td:nth-child(2)::text').get()
        # 企业类型
        item['type_of_enterprise'] = response.css('.detailsList tr:nth-child(10) td:nth-child(2)::text').get()
        # 经营范围
        item['business_scope'] = response.css('.detailsList tr:nth-child(11) td:nth-child(2)::text').get()
        # 企业登记状态
        item['Business_registration_status'] = response.css('.detailsList tr:nth-child(12) td:nth-child(2)::text').get()
        # 年报情况
        item['annual_report_status'] = response.css('.detailsList tr:nth-child(13) td:nth-child(2)::text').get()
        # 经营异常
        item['business_anomaly'] = response.css("span#labEetRegNO::text").get()
        # 税务登记信息
        item['tax_registration_information'] = response.css("#TabJBInfo").re('税务登记信息</span>([\S\s]*?)</table>')
        # 载入异常经营名录原因
        item['reasons_for_listing_abnormal_operations'] = response.css("#TabJGInfo").re('载入异常经营名录原因</td>([\S\s]*?)</td>')
        # 载入异常经营名录时间
        item['time_for_listing_abnormal_operations'] = response.css("#TabJGInfo").re('载入经营异常状态时间</td>([\s\S]*?)</td>')
        # 限制原因
        item['limited_reason'] = response.css("#TabJGInfo").re_first('限制原因[\s\S]*?</table>')
        # 案件结案信息
        item['case_information'] = response.css("#TabSSInfo").get()
        # 企业参保信息
        item['enterprise_insurance_information'] = response.css("#TabJBInfo").re_first('企业参保信息</span>([\S\s]*?)</table>')
        # 欠税记录
        item['owing_tax'] = response.css("#TabJGInfo").re_first('纳税人名称[\s\S]*?</table>')
        # 经营者
        item['operator'] = response.css("#TabJBInfo").re_first('经营者</td>([\S\s]*?)<a href=')
        # 注册资金
        item['registered_fund'] = response.css("#TabJBInfo").re_first('注册资金</td>([\S\s]*?)</td>')
        # 投资总额
        item['total_amount_of_investment'] = response.css("#TabJBInfo").re_first('投资总额</td>([\S\s]*?)</td>')
        # 国别或地区
        item['country_or_region'] = response.css("#TabJBInfo").re_first('国别或地区</td>([\S\s]*?)</td>')
        # 执行合伙人
        item['managing_partner'] = response.css("#TabJBInfo").re_first('执行合伙人</td>([\S\s]*?)</td>')
        # 母公司名称
        item['parent_company'] = response.css("#TabJBInfo").re_first('母公司名称</td>([\S\s]*?)</td>')
        # 年检情况
        item['annual_inspection_situation'] = response.css("body").re_first('年检情况</td>([\S\s]*?)</td>')
        # 股东名称
        item['shareholder'] = response.css("body").re_first('股东登记信息</span>([\S\s]*?)</table>')
        # 变更信息
        entId = response.css("body").re_first('id="hfEntId" value="(\d+?)"')
        recdid = response.css("body").re_first('id="hfID" value="(.+?)"')
        temporary_url_template = 'https://www.szcredit.com.cn/XY2.OutSide/GSPT/newGsptHistoryItem.aspx?ID=0&entId={}&itemId=-1&recdid={}'
        temporary_url = temporary_url_template.format(entId, recdid)
        reqests = scrapy.Request(url=temporary_url, callback=self.parse_change_, headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                                                                                          'Accept-Encoding':'gzip, deflate, br',
                                                                                          'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8',
                                                                                          'Cache-Control':'max-age=0',
                                                                                          'Connection':'keep-alive',
                                                                                          'Host':'www.szcredit.com.cn',
                                                                                          'Upgrade-Insecure-Requests':'1',
                                                                                          'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'})
        reqests.meta['item'] = item

        yield reqests

    def parse_change_(self,response):
        print(response.url)
        item = response.meta['item']
        change_details = response.css('body').get()
        item['change_details'] = change_details
        yield item