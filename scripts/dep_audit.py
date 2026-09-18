# -*- coding: utf-8 -*-
"""依赖安全审计：把当前环境所有已安装包提交 OSV 查询，输出明细 markdown。

用法： python scripts/dep_audit.py [输出路径]
依赖： 仅标准库（urllib / importlib.metadata）
"""
import io
import json
import sys
import urllib.request
from importlib import metadata

OSV_BATCH = 'https://api.osv.dev/v1/querybatch'
OSV_VULN = 'https://api.osv.dev/v1/vulns/'
BATCH_SIZE = 60

# 与本项目运行无关或非 PyPI 分发的包，跳过
SKIP = {'pip', 'wheel', 'kaku'}


def installed_packages():
    pkgs = {}
    for dist in metadata.distributions():
        name = (dist.metadata.get('Name') or '').strip()
        version = (dist.version or '').strip()
        if not name or not version or name.lower() in SKIP:
            continue
        pkgs[name] = version
    return dict(sorted(pkgs.items(), key=lambda kv: kv[0].lower()))


def osv_query(packages):
    """返回 {package_name: [vuln_id, ...]}"""
    names = list(packages.keys())
    found = {n: [] for n in names}
    for i in range(0, len(names), BATCH_SIZE):
        chunk = names[i:i + BATCH_SIZE]
        queries = []
        for n in chunk:
            queries.append({
                'package': {'name': n, 'ecosystem': 'PyPI'},
                'version': packages[n],
            })
        body = json.dumps({'queries': queries}).encode('utf-8')
        req = urllib.request.Request(
            OSV_BATCH, data=body,
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        for name, result in zip(chunk, data.get('results', [])):
            for vuln in (result or {}).get('vulns', []):
                found[name].append(vuln.get('id'))
    return found


def fetch_vuln(vuln_id):
    req = urllib.request.Request(OSV_VULN + vuln_id)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fixed_versions(vuln, package):
    """从 affected 中提取该包受影响区间里的 fixed 版本集合。"""
    fixed = set()
    for affected in vuln.get('affected', []):
        pkg = (affected.get('package') or {}).get('name', '')
        if pkg.lower() != package.lower():
            continue
        for rng in affected.get('ranges', []):
            for event in rng.get('events', []):
                if event.get('fixed'):
                    fixed.add(event['fixed'])
    return sorted(fixed, key=ver_key)


def ver_key(v):
    parts = []
    for chunk in str(v).replace('-', '.').split('.'):
        parts.append(int(chunk) if chunk.isdigit() else 0)
    return parts


def severity_of(vuln):
    for sev in vuln.get('severity', []) or []:
        if sev.get('score'):
            return sev['score']
    db = vuln.get('database_specific') or {}
    if db.get('severity'):
        return str(db['severity'])
    return ''


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else 'docs/dependabot-audit.md'
    packages = installed_packages()
    print('installed packages: %d' % len(packages))
    found = osv_query(packages)

    detail = {}
    for name, ids in found.items():
        for vid in ids:
            detail.setdefault(vid, {'vuln': None, 'packages': []})
            detail[vid]['packages'].append((name, packages[name]))
    print('vulnerable advisories: %d' % len(detail))

    vuln_cache = {}
    for vid in detail:
        try:
            vuln_cache[vid] = fetch_vuln(vid)
        except Exception as exc:  # 网络异常时保留 id
            vuln_cache[vid] = {'id': vid, 'summary': 'fetch failed: %s' % exc}

    rows = []
    for vid, info in sorted(detail.items()):
        vuln = vuln_cache[vid]
        for name, version in info['packages']:
            rows.append({
                'id': vid,
                'aliases': ', '.join(vuln.get('aliases', []) or []),
                'package': name,
                'version': version,
                'severity': severity_of(vuln),
                'summary': (vuln.get('summary') or '').replace('|', '/'),
                'fixed': ', '.join(fixed_versions(vuln, name)) or '（无修复版本）',
            })

    lines = []
    lines.append('# 依赖安全审计明细（dependabot 残余梳理）')
    lines.append('')
    lines.append('本文件由 `scripts/dep_audit.py` 生成：把当前虚拟环境中**全部已安装包**')
    lines.append('（含传递依赖）逐个提交 [OSV 漏洞库](https://osv.dev/) 查询，')
    lines.append('列出当前锁定版本命中、且 OSV 标记的所有漏洞。')
    lines.append('')
    lines.append('- 包总数：%d' % len(packages))
    lines.append('- 命中漏洞条目：%d' % len(rows))
    lines.append('')
    by_pkg = {}
    for r in rows:
        by_pkg.setdefault(r['package'], []).append(r)
    lines.append('## 按包汇总')
    lines.append('')
    lines.append('| 包 | 当前版本 | 命中数 | 建议修复版本 |')
    lines.append('|----|----------|--------|--------------|')
    for name in sorted(by_pkg, key=str.lower):
        items = by_pkg[name]
        fixes = sorted({r['fixed'] for r in items}, key=ver_key)
        lines.append('| %s | %s | %d | %s |' % (
            name, items[0]['version'], len(items), ' / '.join(fixes)))
    lines.append('')
    lines.append('## 逐条明细')
    lines.append('')
    lines.append('| 漏洞 ID | 别名(CVE/GHSA) | 包 | 版本 | 严重度 | 修复版本 | 摘要 |')
    lines.append('|---------|----------------|----|------|--------|----------|------|')
    for r in rows:
        lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            r['id'], r['aliases'] or '-', r['package'], r['version'],
            r['severity'] or '-', r['fixed'], r['summary'] or '-'))
    lines.append('')
    lines.append('## 处置建议')
    lines.append('')
    lines.append('按“修复版本是否只在更高大版本线”分三类：')
    lines.append('')
    lines.append('1. **可在补丁线内直接修**：修复版本与当前同主版本（如 6.x → 6.4）。')
    lines.append('   直接升级并跑全量测试即可。')
    lines.append('2. **需跨大版本修**：修复版本只在更高大版本（如 Django 5.2 / mistune 3.x）。')
    lines.append('   升级前需逐个核对 API 变更与生态兼容（编辑器的 Markdown 渲染、')
    lines.append('   认证流程、模板包等），并全量回归后再合入。')
    lines.append('3. **暂无修复版本**：上游尚未发布修复，只能等待或评估替换组件；')
    lines.append('   若相关代码路径不可达（仅构建期/未调用），风险较低，可暂缓。')
    lines.append('')
    lines.append('> 注意：OSV 结果按“当前锁定版本”判定，不含 GitHub dependabot 的')
    lines.append('> 严重度评级与部分企业内部评分，因此条目数与 GitHub 页面可能不完全一致。')
    lines.append('')

    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines))
    print('written: %s' % out_path)

    # 控制台仅输出 ASCII 统计，避免终端编码问题
    print('--- vulnerable packages ---')
    for name in sorted(by_pkg, key=str.lower):
        print('%-28s %-12s %d advisories' % (name, by_pkg[name][0]['version'], len(by_pkg[name])))


if __name__ == '__main__':
    main()
