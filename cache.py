import redis


from config.config import get_redis_config


class Cache:

    def __init__(self):
        config = get_redis_config()
        self.__connect = redis.Redis(host=config['host'], port=config['port'], db=config['db'])

    def set(self, key, value):
        self.__connect.set(key, value, ex=60*60*24)

    def get(self, key, get_int=True):
        value = self.__connect.get(key).decode("utf-8")
        return int(value) if get_int else value


