# -*- coding: utf-8 -*-

# Scrapy settings for BJ_8491 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'BJ_8491'
SPIDER_MODULES = ['BJ_8491.spiders']
NEWSPIDER_MODULE = 'BJ_8491.spiders'
ROBOTSTXT_OBEY = False

SPLASH_URL = 'http://192.168.99.100:8050'

ITEM_PIPELINES = {
    'BJ_8491.pipelines.Bj8491Pipeline': 300,
    'BJ_8491.pipelines.Filter': 350,
    'BJ_8491.pipelines.Publish34': 400,
    'BJ_8491.pipelines.MongoPipeline': 500,
}

DOWNLOADER_MIDDLEWARES = {
    # 'BJ_8491.middlewares.Bj8491DownloaderMiddleware': 543,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# MONGONDB SETTING
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'p2p'
MONGODB_DOCNAME = 'p8491'
MONGODB_LOG_DOCNAME = 'p8491_log'
