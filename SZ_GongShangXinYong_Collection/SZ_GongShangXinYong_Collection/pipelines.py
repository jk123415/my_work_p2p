# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import pprint
import re
from scrapy.exceptions import DropItem
from w3lib.html import remove_tags


class SzGongshangxinyongCollectionPipeline(object):
    # Comment: regex loop extract data and formatted data
    # tar_str is target string 
    # regex_exp_str template : 限制原因([\s\S]*?)限制时间([\s\S]*?)</br>
    # template_str template: 限制原因：{arr[0]}|限制时间：{arr[1]}|
    def regex_loop_match(self, tar_str, regex_exp_str, template_str):
        if tar_str:
            result = ""
            regex_exp = re.compile(regex_exp_str)
            lst = regex_exp.findall(tar_str)
            try:
                for tup in lst:
                    temporary_a = template_str.format(arr=tup)
                    temporary_b = remove_tags(temporary_a)
                    temporary_c = re.subn("[\t\r\n\s]", "", temporary_b)
                    result = result+ temporary_c[0]
            except Exception:
                return "regex_loop_match 方法出错"
            else:
                return result
        else:
            return None

    # 删除标签和特殊字符
    def del_special_char(self,tar_str,tags=True,rnts=True):
        if tar_str:
            if tags:
                result = remove_tags(tar_str)
                if rnts:
                    result_1 = re.subn("[\r\n\t\s]","",result)
                    return result_1[0]
                else:
                    return result
        else:
            return None

    # 处理空值
    def deal_null(self, value):
        if isinstance(value, list) and value:
            temporary_a = '|'.join(value)
            return temporary_a
        elif:
            
        else:
            return ""

    def process_item(self, item, spider):
        # 税务登记信息
        if item['tax_registration_information']:
            tax_registration_information = '|'.join(item['tax_registration_information'])
            item['tax_registration_information'] = self.del_special_char(tax_registration_information)
        else:
            item['tax_registration_information'] = ""
        # 载入异常经营名录原因
        if item['reasons_for_listing_abnormal_operations']:
            reasons_for_listing_abnormal_operations = '|'.join(item['reasons_for_listing_abnormal_operations'])
            item['reasons_for_listing_abnormal_operations'] = self.del_special_char(reasons_for_listing_abnormal_operations)
        # 载入异常经营名录时间
        if item['time_for_listing_abnormal_operations']:
            time_for_listing_abnormal_operations = '|'.join(item['time_for_listing_abnormal_operations'])
            item['time_for_listing_abnormal_operations'] = self.del_special_char(time_for_listing_abnormal_operations)
        # 限制原因
        limited_reason = item['limited_reason']
        if limited_reason: 
            limited_reason_regex_exp_str = "限制原因([\s\S]*?)限制时间([\s\S]*?)限制状态([\s\S]*?)限制说明([\s\S]*?)备注</td>([\s\S]*?)</td>"
            limited_reason_template_str = "限制原因：{arr[0]}|限制时间：{arr[1]}|限制状态:{arr[2]}|限制说明:{arr[3]}|备注:{arr[4]}|"
            item['limited_reason'] = self.regex_loop_match(limited_reason, limited_reason_regex_exp_str, limited_reason_template_str)
        # 案件结案信息
        case_information = item['case_information']
        if case_information: item['case_information'] = self.del_special_char(case_information)
        # 企业参保信息
        enterprise_insurance_information = item['enterprise_insurance_information']
        if enterprise_insurance_information: item['enterprise_insurance_information'] = self.del_special_char(enterprise_insurance_information)
        # 欠税记录
        owing_tax = item['owing_tax']
        if owing_tax:
            owing_tax_regex_exp_str = '纳税人名称([\s\S]*?)纳税人识别号([\s\S]*?)征收项目代码([\s\S]*?)欠税余额([\s\S]*?)当前新发生的欠税额([\s\S]*?)税款所属机关([\s\S]*?)应征发生日期([\s\S]*?)缴款期限([\s\S]*?)</tr>'
            owing_tax_template_str = "纳税人名称:{arr[0]}|纳税人识别号:{arr[1]}|征收项目代码:{arr[2]}|欠税余额:{arr[3]}|当前新发生的欠税额:{arr[4]}|税款所属机关:{arr[5]}|应征发生日期:{arr[6]}|"
            item['owing_tax'] = self.regex_loop_match(owing_tax, owing_tax_regex_exp_str, owing_tax_template_str)
        # 经营者
        operator = item['operator']
        if operator: item['operator'] = self.del_special_char(operator)
        # 注册资金
        registered_fund = item['registered_fund']
        if registered_fund: item['registered_fund'] = self.del_special_char(registered_fund)
        # 投资总额
        total_amount_of_investment = item['total_amount_of_investment']
        if total_amount_of_investment: item['total_amount_of_investment'] = self.del_special_char(total_amount_of_investment)
        # 国别或地区
        country_or_region = item['country_or_region']
        if country_or_region: item['country_or_region'] = self.del_special_char(country_or_region)
        # 国别或地区
        managing_partner = item['managing_partner']
        if managing_partner: item['managing_partner'] = self.del_special_char(managing_partner)
        # 母公司名称
        parent_company = item['parent_company']
        if parent_company: item['parent_company'] = self.del_special_char(parent_company)
        # 年检情况
        annual_inspection_situation = item['annual_inspection_situation']
        if annual_inspection_situation: item['annual_inspection_situation'] = self.del_special_char(annual_inspection_situation)
        # 股东名称
        shareholder = item['shareholder']
        if shareholder:
            shareholder_regex_exp_str = '<tr>[\s\S]*?<td align="left" style="height:22px;">([\s\S]*?)</a></td><td align="left" style="height:22px;">([\s\S]*?)</td><td align="left" style="height:22px;">([\s\S]*?)</td>[\s\S]*?</tr>'
            shareholder_template_str = "{name={arr[0]}|momey={arr[1]}|rate={arr[2]}}"
            item['shareholder'] = self.regex_loop_match(shareholder, shareholder_regex_exp_str, shareholder_template_str)
        pprint.pprint(item)
        return item

    def close_spider(self, spider):
        spider.client.close()


class SaveData(object):
    def process_item(self, item, spider):
        return item
