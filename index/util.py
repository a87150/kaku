from written.models import Article
from picture.models import Picture

_TYPE_MAP = {'article': Article, 'picture': Picture}


def what_type(type):
    """把前端传入的类型名解析成模型类；不识别/为空返回 None。

    注意：参数名沿用历史命名 type，实际是类型字符串而非 Python 类型。
    """
    if not type:
        return None
    return _TYPE_MAP.get(type)