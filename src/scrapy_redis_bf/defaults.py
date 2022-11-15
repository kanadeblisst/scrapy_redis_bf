from scrapy_redis.defaults import *


SCHEDULER_DUPEFILTER_KEY = '%(spider)s:bloomfilter'
SCHEDULER_DUPEFILTER_ATTR = "name"
DUPEFILTER_DEBUG = False

BLOOMFILTER_ERRORRATE = 0.001  # 误报率
BLOOMFILTER_CAPACITY = 100000  # 去重数量
