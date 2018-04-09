from written.models import Article
from picture.models import Picture

def what_type(type):
    if type:
        d = {'article': Article, 'picture': Picture}
        type = d[type]
    else:
        return False

    return type