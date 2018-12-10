# -*- coding: utf-8 -*-
import scrapy, re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ZheChenJinFu.items import ZCJFDataItem
from scrapy.loader import ItemLoader


class CrawlSpider(CrawlSpider):
    name = 'ZCJF'
    start_urls = ['https://www.zchfax.com/yxlc.html?page={}&status=11&isAssignment=0'.format(x) for x in range(1, 2)]

    def process_value(value):
        m = re.search("location\.href='(.*?)'", value)
        if m:
            return m.group(1)

    rules = (
        Rule(LinkExtractor(tags=('div',), attrs=('onclick',), process_value=process_value), callback='parse_item'),
    )

    def parse_item(self, response):

        def invest_records(selector_0, selector_1='tr', selector_2='td::text'):
            selector = response.css(selector_0)
            lst_tr = selector.css(selector_1)
            result = list()
            for i in lst_tr:
                text = i.css(selector_2).extract()
                if text: result.append(text)
            return result

        def invest_p2p():
            invest_records = ""
            try:
                for record in invest_records_data:
                    invest_records += "{{username={ls[1]}|rate=-1|postmoney={ls[2]}|money={ls[2]}|postdate={ls[4]}|status=全部通过}}".format(
                        ls=record)
            except Exception:
                invest_records = None
            return invest_records

        invest_records_data = invest_records('.productRecord table')
        invest_records_str = invest_p2p()

        def time_handle():
            if invest_records_data:
                start_time = invest_records_data[start[0]][start[1]]
                end_time = invest_records_data[end[0]][end[1]]
                result_time = (start_time, end_time)
            else:
                result_time = (None, None)
            return result_time

        def item_code_handle():
            try:
                url_str = response.url
                code_str = re.findall('yxlcv/(.*?)\.html', url_str)
                return web_name + "-" + code_str[0]
            except Exception:
                return None

        web_name = '泽诚金服'
        start = (0, 4)
        end = (-1, 4)
        time_value = time_handle()

        item = ItemLoader(item=ZCJFDataItem(), response=response)
        item.add_value('web_name', '泽诚金服')
        item.add_value('web_code', '8038')
        item.add_value('url', response.url)
        item.add_css('title', '.pinfoh_l_tit span:nth-child(1)::text')
        item.add_css('amount', '.tabs2 tr:nth-child(2) td:nth-child(2)::text')
        item.add_css('rate', '.details div:nth-child(1) span:nth-child(1) em::text')
        item.add_css('period', '.details div:nth-child(2) span')
        item.add_css('pay_type', '.pinfoh_l_secTit span:nth-child(2) em::text')
        item.add_css('loan_using', '.tabs2 tr:nth-child(3) td:nth-child(2)::text')
        item.add_css('loaner_info', '.productBorrowContent div:nth-child(1) tr:nth-child(1) td:nth-child(2)::text')
        item.add_value('invest_records', invest_records_str)
        item.add_value('start', time_value[0])
        item.add_value('end', time_value[1])
        item.add_value('item_code', item_code_handle())
        item.add_css('progress','.progressTip::text')
        return item.load_item()
