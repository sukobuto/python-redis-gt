# from typing import *
from redis import StrictRedis


class Throttle:

    def __init__(self, redis: StrictRedis):
        self.redis = redis

    def set_string(self):
        self.redis.set('t-key', 't-value'.encode('utf8'))

    def get_string(self):
        return self.redis.get('t-key').decode('utf8')
