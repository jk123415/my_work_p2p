# -*- coding: utf-8 -*-
import scrapy, re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from GD_8717.items import Gd8717Item
from scrapy.loader import ItemLoader


def item_code(str1, str2, exp):
    code = re.search(exp, str1)
    return str2 + '-' + code.group(1)


def invest_records_list(response, s1, s2='tr', s3='td::text'):
    table = response.css(s1).css(s2)
    result = list()
    for i in table:
        text = i.css(s3).extract()
        if text: result.append(text)
    return result


class CrawlSpider(CrawlSpider):
    name = '8717'
    web_name = '明郡融资租赁'
    # allowed_domains = ['http://www.mjcd168.com']
    start_urls = ['http://www.mjcd168.com/invest/index.html?p=1']

    rules = (
        Rule(LinkExtractor(allow=('invest/index\.html\?p=\d+',), restrict_xpaths=('//*[contains(text(),"下一页")]',))),
        Rule(LinkExtractor(allow=('/invest/\d+\.html',)), callback='parse_item')
    )

    def parse_item(self, response):
        invest_records_lst = invest_records_list(response,'body > div.banner > div.loan > div > table')
        print(invest_records_lst)
        item_num = item_code(response.url, self.web_name, 'invest/(.*?)\.html')
        item = ItemLoader(item=Gd8717Item(), response=response)
        item.add_value('web_name', self.web_name)
        item.add_value('web_code', self.name)
        item.add_value('url', response.url)
        item.add_value('item_code', item_num)
        # item.add_value('invest_records', invest_record_str)
        # item.add_value('start', time_value[0])
        # item.add_value('end', time_value[1])
        item.add_value('pay_type', '0')
        return item.load_item()
