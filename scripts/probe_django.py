# -*- coding: utf-8 -*-
"""把指定版本的 Django 旁挂到项目目录，用于在不改动 venv 的前提下做兼容性探针。

用法：
    python scripts/probe_django.py 5.2.17              # 解包到 .tmp_dj52/
    python scripts/probe_django.py 5.2.17 -t .probe52  # 指定目标目录

之后用 PYTHONPATH 让它遮蔽 venv 里的 Django：

    PowerShell:
        $env:PYTHONPATH="$PWD\\.tmp_dj52"
        .\\venv\\Scripts\\python.exe manage.py check
        .\\venv\\Scripts\\python.exe manage.py test --verbosity 1

    bash:
        PYTHONPATH="$PWD/.tmp_dj52" python manage.py check

为什么不直接用 pip：pip 安装/下载时需要写临时解包目录（*.whl.metadata），
在受限沙箱下会被拒绝；这里改用 PyPI JSON API 取 wheel 再 zipfile 解包，只依赖标准库。
探针目录形如 .tmp_*/，已在 .gitignore 中忽略，用完可直接删除。

具体结论见 docs/django52-upgrade-assessment.md。
"""

import argparse
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

DEFAULT_VERSION = '5.2.17'
DEFAULT_TARGET = '.tmp_dj52'


def fetch_wheel_url(version):
    """从 PyPI JSON API 取该版本 py3-none-any wheel 的下载地址。"""
    url = 'https://pypi.org/pypi/Django/%s/json' % version
    with urllib.request.urlopen(url, timeout=60) as resp:
        meta = json.load(resp)

    for item in meta.get('urls', []):
        name = item.get('filename', '')
        if item.get('packagetype') == 'bdist_wheel' and name.endswith('py3-none-any.whl'):
            return item['url'], name
    raise SystemExit('no py3-none-any wheel found for Django %s' % version)


def unpack(version, target):
    os.makedirs(target, exist_ok=True)
    wheel_url, filename = fetch_wheel_url(version)
    print('wheel: %s' % filename)

    with urllib.request.urlopen(wheel_url, timeout=180) as resp:
        blob = resp.read()
    print('bytes: %d' % len(blob))

    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        zf.extractall(target)

    init_py = os.path.join(target, 'django', '__init__.py')
    with open(init_py, encoding='utf-8') as fh:
        match = re.search(r'VERSION\s*=\s*\(([^)]*)\)', fh.read())
    print('unpacked version: %s' % (match.group(1).strip() if match else '?'))
    print('target: %s' % os.path.abspath(target))


def main():
    parser = argparse.ArgumentParser(
        description='Side-load a Django version for compatibility probing.')
    parser.add_argument('version', nargs='?', default=DEFAULT_VERSION,
                        help='Django version to fetch (default: %s)' % DEFAULT_VERSION)
    parser.add_argument('-t', '--target', default=DEFAULT_TARGET,
                        help='target directory (default: %s)' % DEFAULT_TARGET)
    args = parser.parse_args()

    unpack(args.version, args.target)
    print('')
    print('next: put it in front of the venv Django via PYTHONPATH, e.g.')
    print('  $env:PYTHONPATH="$PWD\\%s"; .\\venv\\Scripts\\python.exe manage.py check'
          % args.target)
    return 0


if __name__ == '__main__':
    sys.exit(main())
