from written.models import Article
from picture.models import Picture

def what_type(type):
    if type == 'article':
        type = Article
    elif type == 'picture':
        type = Picture
    else:
        return False

    return type