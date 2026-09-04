"""测试辅助：模拟 Redis 掉线。

站点在 Redis 不可用时会自动回退到数据库（见 index/redis_caches.py）。
测试里用本模块把模块级连接对象 rd 替换成“任何调用都抛 RedisError”的桩，
从而稳定走数据库回退路径，不依赖本机是否真的运行 Redis。
"""
from unittest import mock

from redis.exceptions import RedisError


class RedisDown:
    """模拟 Redis 掉线的客户端：任何方法调用都抛 RedisError。"""

    def __getattr__(self, name):
        def boom(*args, **kwargs):
            raise RedisError('simulated redis unavailable')
        return boom


def patch_redis_down():
    return mock.patch('index.redis_caches.rd', new=RedisDown())
