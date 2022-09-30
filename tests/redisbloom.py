import redis

redis_url = "redis://127.0.0.1:6379"
server = redis.StrictRedis.from_url(redis_url, decode_responses=True)

bf = server.bf()
# redis key
key = "test"
# 错误率
errorRate = 0.001
# 去重数据量
capacity = 10000
if not server.exists(key):
    print(bf.create(key, errorRate, capacity))

for i in range(10):
    print(i, bf.add(key, f"http://www.httpbin.org/get?a={i}"))
for i in range(20):
    print(i, bf.add(key, f"http://www.httpbin.org/get?a={i}"))
for i in range(10):
    print(i, bf.exists(key, f"http://www.httpbin.org/get?a={i}"))
