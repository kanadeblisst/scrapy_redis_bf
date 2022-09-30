
class BaseException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self.__doc__, *args, **kwargs)


class RedisNoBloomException(BaseException):
    '''redis没有加载布隆过滤器插件，请加载插件或使用redislabs/rebloom:latest镜像启动redis'''