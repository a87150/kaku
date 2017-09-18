from django_redis import get_redis_connection

from written.models import Article
from picture.models import Picture

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
            cache_views = get_views(type, o)
            if cache_views != o.views:
                o.views = cache_views
                o.save()
        except:
            pass


def like(type, object, user):
    type = type + 's'

    if REDIS_DB.sismember(type, object.id):
        if REDIS_DB.sismember(object.id, user.id):
            return
        else:
            REDIS_DB.sadd(object.id, user.id)
    else:
        REDIS_DB.sadd(type, object.id)


def dislike(type, object, user):
    pass
