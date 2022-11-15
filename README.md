# Scrapy-Redis-BloomFilter

这是个scrapy_redis的布隆过滤器版本，与`https://github.com/Python3WebSpider/ScrapyRedisBloomFilter` 
不同的是，该项目使用redis里的布隆过滤器，而不是使用bit来实现

## 必要条件

需要redis加载了布隆过滤器的插件，默认安装的redis是没有加载的
具体请看：https://redis.io/docs/stack/bloom/quick_start/


## 安装

使用pip: `pip install scrapy-redis-bf`

## 使用

在scrapy项目里的 `settings.py`添加如下设置:

```python
SCHEDULER = "scrapy_redis_bf.scheduler.Scheduler"

DUPEFILTER_CLASS = "scrapy_redis_bf.dupefilter.RFPDupeFilter"
# 默认是通过spider的name来创建redis key
SCHEDULER_DUPEFILTER_ATTR = "name"

# 格式：redis://[:password@]host[:port][/database][?[timeout=timeout[d|h|m|s|ms|us|ns]][&database=database]]
REDIS_URL = 'redis://localhost:6379'
# 错误率
BLOOMFILTER_ERRORRATE = 0.001
# 去重量
BLOOMFILTER_CAPACITY = 10000


```

## 测试

下载该项目，然后运行里面的test spider即可

## Github

https://github.com/kanadeblisst/scrapy_redis_bf

