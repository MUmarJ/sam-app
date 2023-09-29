import redis, redis.exceptions

# TODO : Get the redis credentials from aws

def get_redis_client():
    try:
        redisurl = 'rediss://:' + os.getenv('REDIS_PASSWORD', '') + '@' + os.getenv('REDIS_URI',
                                                                                    default='localhost:6379') + '/1'

        redis_client = redis.from_url(redisurl)
        return redis_client

    except redis.ConnectionError as e:
        print('Redis connection failed %s', str(e))
        return None