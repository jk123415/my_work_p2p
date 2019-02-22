# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
from seletest.items import SeletestItem



def item_code(str1, str2, exp, url=None):
    result = {}
    try:
        code = re.search(exp, str1).group(1)
        item_c = str2 + '-' + code
    except Exception:
        pass
        # print("网址提取code错误")
    else:
        result['item_code'] = item_c
        if url:
            muti_page = url.format(code)
            result['m_p_u'] = muti_page
    return result

def invest_records_list(response, s1, s2='tr', s3='td::text'):
    table = response.css(s1).css(s2)
    result = list()
    for i in table:
        text = i.css(s3).extract()
        if text:
            result.append(text)
    return result

class BasicSpider(Spider):
    name = '8235'
    web_name = '小鸽理财'
    start_urls = ['https://wap.xiaogelicai.com/pro_det?borrowId={}'.format(x) for x in range(1520, 1540)]


    def parse(self, response):
        url = response.url
        item = {}
        try:
            item_list = item_code(url, self.web_name, 'borrowId=(.*?)$')
            item['web_name'] = self.web_name
            item['web_code'] = self.name
            item['url'] = url
            item['item_code'] = item_list.get('item_code')
            item['title'] = response.css('body').re_first('项目名称</span><span>([\s\S]+?)</span>')
            item['amount'] = response.css('body').re_first('借款金额</span><span>([\s\S]+?)</span>')
            item['rate'] = response.css('body').re_first('年化利率</span><span>([\s\S]+?)</span>')
            item['period'] = response.css('body').re_first('期限</span><span>([\s\S]+?)</span>')
            item['start'] = response.css('body').re_first('借款日期</span><span>([\s\S]+?)</span>')
            item['loan_using'] = response.css('body').re_first('借款用途</span><span>([\s\S]+?)</span>')
            item['pay_type'] = response.css('body').re_first('还款方式</span><span>([\s\S]+?)</span>')
            item['loaner_info'] = response.css('body').re_first('企业名称</span><span>([\s\S]+?)</span>')
            item['end'] = item['start']
        #item.add_xpath('loan_using', '//*[contains(text(),"资金用途")]/following-sibling::div[1]/p/text()')
        # item.add_xpath('loaner_info', '//*[@id="userName"]')
        #item.add_xpath('pay_type', '//*[contains(text(),"还款方式：")]/../text()')
        #item.add_xpath('progress', '//*[contains(text(),"出借进度")]/..')
        except Exception:
            self.logger.info('invest records is error: %s' % url)
        yield item
