from django_redis import get_redis_connection

from written.models import Article
from picture.models import Picture
from users.models import User

REDIS_DB = get_redis_connection('default')

def update_views(type, object):

    if REDIS_DB.hexists(type, object.id):
        REDIS_DB.hincrby(type, object.id)

    else:
        REDIS_DB.hset(type, object.id, object.views + 1)


def get_views(type, object):

    if REDIS_DB.hexists(type, object.id):
        return REDIS_DB.hget(type, object.id)

    else:
        REDIS_DB.hset(type, object.id, object.views)
        return object.views


def sync_views(type):

    if type=='article':
        object = Article
    else:
        object = Picture

    for k in REDIS_DB.hkeys(type):
        try:
            o = object.objects.get(id=k)
            cache = get_views(type, o)
            if cache != o.views:
                o.views = cache
                o.save()
        except:
            continue


def like(type, object, user):
    type = type + 's'
    oid = type[0] + str(object.id)

    if REDIS_DB.sismember(type, oid):
        if REDIS_DB.sismember(oid, user.id):
            return
        else:
            REDIS_DB.sadd(oid, user.id)
    else:
        REDIS_DB.sadd(type, oid)
        for l in object.likes.all():
            REDIS_DB.sadd(oid, l.id)


def dislike(type, object, user):
    type = type + 's'
    oid = type[0] + str(object.id)

    if REDIS_DB.sismember(type, oid):
        if REDIS_DB.sismember(oid, user.id):
            REDIS_DB.srem(oid, user.id)
        else:
            return
    else:
        REDIS_DB.sadd(type, oid)
        for l in object.likes.all():
            REDIS_DB.sadd(oid, l.id)
        if REDIS_DB.sismember(type, oid):
            if REDIS_DB.sismember(oid, user.id):
                REDIS_DB.srem(oid, user.id)
            else:
                return
        else:
            return


def get_like(type, object):
    type = type + 's'
    oid = type[0] + str(object.id)

    if REDIS_DB.sismember(type, oid):
        return REDIS_DB.smembers(oid)
    else:
        REDIS_DB.sadd(type, oid)
        for l in object.likes.all():
            REDIS_DB.sadd(oid, l.id)
        # set只能用for取值
        return REDIS_DB.smembers(oid)


def is_likes(type, object, user):
    type = type + 's'
    oid = type[0] + str(object.id)
    
    if REDIS_DB.sismember(type, oid):
        if REDIS_DB.sismember(oid, user.id):
            return True
        else:
            return False
    else:
        return False


def sync_like(type):

    if type=='article':
        object = Article
    else:
        object = Picture

    for id in REDIS_DB.smembers(type + 's'):
        l = []
        for i in REDIS_DB.smembers(id):
            l.append(i)
        try:
            o = object.objects.get(id=int(id[1:]))
            o.likes.add(*l)
        except:
            continue
