"""
Python 3.14 兼容补丁。

Django 4.2 官方仅支持 Python 3.8 - 3.12。在 Python 3.13+ 中，
django.template.context.BaseContext.__copy__ 里的 ``copy(super())``
返回的 super 对象不允许再设置属性（'super' object has no __dict__），
导致 crispy_forms 等任何复制模板 Context 的代码崩溃。

这里在不修改 site-packages 的前提下，于项目启动时替换该方法实现。
"""

import sys


def apply_python314_compat():
    if sys.version_info < (3, 13):
        return

    try:
        from django.template import context as context_module
    except ImportError:
        return

    BaseContext = context_module.BaseContext

    if not hasattr(BaseContext, "__copy__"):
        return

    # 仅当现有实现会被 Python 3.13+ 破坏时才替换（避免重复执行）。
    import inspect

    try:
        source = inspect.getsource(BaseContext.__copy__)
    except (OSError, TypeError):
        source = ""

    if "copy(super())" not in source:
        return

    def _safe_copy(self):
        duplicate = object.__new__(type(self))
        # 拷贝所有实例属性（dicts、autoescape、render_context 等）
        for key, value in self.__dict__.items():
            if key == "dicts":
                duplicate.dicts = self.dicts[:]
            else:
                setattr(duplicate, key, value)
        return duplicate

    BaseContext.__copy__ = _safe_copy
    context_module.Context.__copy__ = None  # 让子类回退使用父类实现
    del context_module.Context.__copy__
