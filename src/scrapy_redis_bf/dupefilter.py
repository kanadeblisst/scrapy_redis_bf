import logging
import time

from redis import StrictRedis
from scrapy.dupefilters import BaseDupeFilter
from scrapy.exceptions import NotConfigured
from scrapy.utils.request import request_fingerprint
from .exception import RedisNoBloomException

from . import defaults


logger = logging.getLogger(__name__)


class RFPDupeFilter(BaseDupeFilter):
    logger = logger

    def __init__(self,
                 server: StrictRedis,
                 key: str,
                 errorRate: float,
                 capacity: int,
                 debug: bool = False
                 ):
        """
        server: redis.Redis
        key: redis key
        errorRate: 去重错误率
        capacity: 去重数量
        """
        self.server = server
        self.key = key
        self.debug = debug
        self.errorRate = errorRate
        self.capacity = capacity
        self.logdupes = True
        self.bf = server.bf()
        self.valid_redis_has_bloom()
        if not server.exists(key):
            self.bf.create(key, errorRate, capacity)
        else:
            if server.type(key) != "MBbloom--":
                server.delete(key)
                self.bf.create(key, errorRate, capacity)

    def valid_redis_has_bloom(self):
        try:
            self.bf.info('a')
        except Exception as e:
            if "unknown command" in str(e):
                raise RedisNoBloomException

    @classmethod
    def from_settings(cls, settings):
        redis_url = settings.get("REDIS_URL")
        if not redis_url:
            logger.error("未配置REDIS_URL！")
            raise NotConfigured
        server = StrictRedis.from_url(redis_url, decode_responses=True)
        key = defaults.DUPEFILTER_KEY % {'timestamp': int(time.time())}
        errorRate = settings.get(
            'BLOOMFILTER_ERRORRATE', defaults.BLOOMFILTER_ERRORRATE)
        capacity = settings.getint(
            'BLOOMFILTER_CAPACITY', defaults.BLOOMFILTER_CAPACITY)
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(server, key=key, errorRate=errorRate, capacity=capacity, debug=debug)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    @classmethod
    def from_spider(cls, spider):
        settings = spider.settings
        redis_url = settings.get("REDIS_URL")
        if not redis_url:
            logger.error("未配置REDIS_URL！")
            raise NotConfigured
        server = StrictRedis.from_url(redis_url, decode_responses=True)
        dupefilter_key = settings.get(
            'SCHEDULER_DUPEFILTER_KEY', defaults.SCHEDULER_DUPEFILTER_KEY)
        dupefilter_attr = settings.get(
            'SCHEDULER_DUPEFILTER_ATTR', defaults.SCHEDULER_DUPEFILTER_ATTR)
        value = getattr(spider, dupefilter_attr, None)
        if not value:
            logger.error("配置的SCHEDULER_DUPEFILTER_ATTR错误，无法获取spider的属性!")
            raise NotConfigured
        key = dupefilter_key % {'spider': value}
        errorRate = settings.get(
            'BLOOMFILTER_ERRORRATE', defaults.BLOOMFILTER_ERRORRATE)
        capacity = settings.getint(
            'BLOOMFILTER_CAPACITY', defaults.BLOOMFILTER_CAPACITY)
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(server, key=key, errorRate=errorRate, capacity=capacity, debug=debug)

    def request_seen(self, request):
        """
        request : scrapy.http.Request
        """
        fp = self.request_fingerprint(request)
        added = self.bf.add(self.key, fp)
        return added == 0

    def request_fingerprint(self, request):
        return request_fingerprint(request)

    def close(self, reason=''):
        self.clear()

    def clear(self):
        """Clears fingerprints data."""
        self.server.delete(self.key)

    def log(self, request, spider):
        """Logs given request.

        Parameters
        ----------
        request : scrapy.http.Request
        spider : scrapy.spiders.Spider

        """
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request},
                              extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request},
                              extra={'spider': spider})
            self.logdupes = False
        spider.crawler.stats.inc_value('bloomfilter/filtered', spider=spider)
