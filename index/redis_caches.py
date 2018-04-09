from django_redis import get_redis_connection

from written.models import Article
from picture.models import Picture
from users.models import User
from .util import *

rd = get_redis_connection('default')

def update_views(type, obj):

    if rd.hexists(type, obj.id):
        rd.hincrby(type, obj.id)

    else:
        rd.hset(type, obj.id, obj.views + 1)


def get_views(type, obj):

    if rd.hexists(type, obj.id):
        return rd.hget(type, obj.id)

    else:
        rd.hset(type, obj.id, obj.views)
        return obj.views


def sync_views(type):

    obj = what_type(type)

    if obj:
        for k in rd.hkeys(type):
            try:
                o = obj.objects.get(id=k)
                cache = get_views(type, o)
                if cache != o.views:
                    o.views = cache
                    o.save()
            except:
                continue
    else:
        return None

    rd.delete(type)


def like(type, obj, user):
    type = type + 's'
    oid = type[0] + str(obj.id)

    if rd.sismember(type, oid):
        if rd.sismember(oid, user.id):
            return None
        else:
            rd.sadd(oid, user.id)
    else:
        rd.sadd(type, oid)
        for l in obj.likes.all():
            rd.sadd(oid, l.id)


def dislike(type, obj, user):
    type = type + 's'
    oid = type[0] + str(obj.id)

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


def get_like(type, obj):
    type = type + 's'
    oid = type[0] + str(obj.id)

    if rd.sismember(type, oid):
        return rd.smembers(oid)
    else:
        rd.sadd(type, oid)
        for l in obj.likes.all():
            rd.sadd(oid, l.id)
        # set只能用for取值
        return rd.smembers(oid)


def is_likes(type, obj, user):
    type = type + 's'
    oid = type[0] + str(obj.id)
    
    if rd.sismember(type, oid):
        if rd.sismember(oid, user.id):
            return True
        else:
            return False
    else:
        return False


def sync_like(type):
    obj = what_type(type)

    if obj:
        type = type + 's'

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
    else:
        return None

    rd.delete(type)