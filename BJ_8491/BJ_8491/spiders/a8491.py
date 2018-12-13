# -*- coding: utf-8 -*-
import scrapy

'''function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(2))
  local element = splash:select('.project-tables-top p:nth-child(4)')
  element:mouse_click{}
  assert(splash:wait(2))
  return {
    html = splash:html(),
    png = splash:png(),
    --har = splash:har(),
  }
end
'''


class A8491Spider(scrapy.Spider):
    name = '8491'
    allowed_domains = ['8491']
    start_urls = ['http://8491/']

    def parse(self, response):
        pass
