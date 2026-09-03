from django_redis import get_redis_connection
from django_redis.exceptions import ConnectionInterrupted
from redis.exceptions import RedisError

from written.models import Article
from picture.models import Picture
from users.models import User
from .util import *

rd = get_redis_connection('default')


def _redis_down():
    """返回 True 表示 Redis 不可用（连接池惰性，出错时才抛异常）。"""
    return False


def update_views(type, obj):

    try:
        if rd.hexists(type, obj.id):
            rd.hincrby(type, obj.id)

        else:
            rd.hset(type, obj.id, obj.views + 1)
    except (ConnectionInterrupted, RedisError):
        # Redis 不可用：直接回退到数据库
        obj.views += 1
        obj.save(update_fields=['views'])


def get_views(type, obj):

    try:
        if rd.hexists(type, obj.id):
            return rd.hget(type, obj.id)

        else:
            rd.hset(type, obj.id, obj.views)
            return obj.views
    except (ConnectionInterrupted, RedisError):
        return obj.views


def sync_views(type):

    obj = what_type(type)

    if obj:
        try:
            for k in rd.hkeys(type):
                try:
                    o = obj.objects.get(id=k)
                    cache = get_views(type, o)
                    if cache != o.views:
                        o.views = cache
                        o.save()
                except:
                    continue
        except (ConnectionInterrupted, RedisError):
            return None
    else:
        return None

    try:
        rd.delete(type)
    except (ConnectionInterrupted, RedisError):
        pass


def like(type, obj, user):
    type = type + 's'
    oid = type[0] + str(obj.id)

    try:
        if rd.sismember(type, oid):
            if rd.sismember(oid, user.id):
                return None
            else:
                rd.sadd(oid, user.id)
        else:
            rd.sadd(type, oid)
            for l in obj.likes.all():
                rd.sadd(oid, l.id)
    except (ConnectionInterrupted, RedisError):
        obj.likes.add(user)


def dislike(type, obj, user):
    type = type + 's'
    oid = type[0] + str(obj.id)

    try:
        if rd.sismember(type, oid):
            if rd.sismember(oid, user.id):
                rd.srem(oid, user.id)
            else:
                return None
        else:
            rd.sadd(type, oid)
            for l in obj.likes.all():
                rd.sadd(oid, l.id)
            if rd.sismember(type, oid):
                if rd.sismember(oid, user.id):
                    rd.srem(oid, user.id)
                else:
                    return None
            else:
                return None
    except (ConnectionInterrupted, RedisError):
        obj.likes.remove(user)


def get_like(type, obj):
    type = type + 's'
    oid = type[0] + str(obj.id)

    try:
        if rd.sismember(type, oid):
            return rd.smembers(oid)
        else:
            rd.sadd(type, oid)
            for l in obj.likes.all():
                rd.sadd(oid, l.id)
            # set只能用for取值
            return rd.smembers(oid)
    except (ConnectionInterrupted, RedisError):
        return obj.likes.all()


def is_likes(type, obj, user):
    type = type + 's'
    oid = type[0] + str(obj.id)

    try:
        if rd.sismember(type, oid):
            if rd.sismember(oid, user.id):
                return True
            else:
                return False
        else:
            return False
    except (ConnectionInterrupted, RedisError):
        return obj.likes.filter(id=user.id).exists()


def sync_like(type):
    obj = what_type(type)

    if obj:
        type = type + 's'

        try:
            for id in rd.smembers(type):
                l = []
                for i in rd.smembers(id):
                    l.append(i)
                try:
                    o = obj.objects.get(id=int(id[1:]))
                    o.likes.add(*l)
                except:
                    continue
                rd.delete(id)
        except (ConnectionInterrupted, RedisError):
            return None
    else:
        return None

    try:
        rd.delete(type)
    except (ConnectionInterrupted, RedisError):
        pass
