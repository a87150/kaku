# 依赖安全审计明细（dependabot 残余梳理）

本文件由 `scripts/dep_audit.py` 生成：把当前虚拟环境中**全部已安装包**
（含传递依赖）逐个提交 [OSV 漏洞库](https://osv.dev/) 查询，
列出当前锁定版本命中、且 OSV 标记的所有漏洞。

- 包总数：45
- 命中漏洞条目：7

## 按包汇总

| 包 | 当前版本 | 命中数 | 建议修复版本 |
|----|----------|--------|--------------|
| Django | 4.2.30 | 7 | 5.2.15, 6.0.6 / 5.2.16, 6.0.7 / 5.2.17, 6.0.8 |

## 逐条明细

| 漏洞 ID | 别名(CVE/GHSA) | 包 | 版本 | 严重度 | 修复版本 | 摘要 |
|---------|----------------|----|------|--------|----------|------|
| GHSA-3h9f-r86x-qvjx | BIT-django-2026-48588, CVE-2026-48588, PYSEC-2026-2090 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N | 5.2.16, 6.0.7 | Django: cache middleware may expose private responses when unrelated request cookies are present |
| GHSA-8cjm-8mp7-r2xf | BIT-django-2026-8404, CVE-2026-8404, PYSEC-2026-201 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N | 5.2.15, 6.0.6 | Django: UpdateCacheMiddleware may disclose cached responses due to case-sensitive Cache-Control handling |
| GHSA-8qcx-xf44-272x | BIT-django-2026-53878, CVE-2026-53878, PYSEC-2026-2092 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 5.2.16, 6.0.7 | Django: DomainNameValidator permits newline characters that may enable HTTP header injection |
| GHSA-923m-gv2p-w5qp | BIT-django-2026-48587, CVE-2026-48587, PYSEC-2026-198 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N | 5.2.15, 6.0.6 | Django: has_vary_header may expose cached responses when Vary values contain whitespace |
| GHSA-crhf-3pfg-w68w | BIT-django-2026-53877, CVE-2026-53877, PYSEC-2026-2091 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L | 5.2.16, 6.0.7 |  Django: GDALRaster may over-read heap memory when constructed from bytes |
| GHSA-h7pc-vwp9-298g | BIT-django-2026-6873, CVE-2026-6873, PYSEC-2026-199 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:N | 5.2.15, 6.0.6 | Django: signed cookies are vulnerable to salt namespace collisions |
| PYSEC-2026-3717 | BIT-django-2026-15830, CVE-2026-15830 | Django | 4.2.30 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 5.2.17, 6.0.8 | - |

## 处置建议

按“修复版本是否只在更高大版本线”分三类：

1. **可在补丁线内直接修**：修复版本与当前同主版本（如 6.x → 6.4）。
   直接升级并跑全量测试即可。
2. **需跨大版本修**：修复版本只在更高大版本（如 Django 5.2 / mistune 3.x）。
   升级前需逐个核对 API 变更与生态兼容（编辑器的 Markdown 渲染、
   认证流程、模板包等），并全量回归后再合入。
3. **暂无修复版本**：上游尚未发布修复，只能等待或评估替换组件；
   若相关代码路径不可达（仅构建期/未调用），风险较低，可暂缓。

> 注意：OSV 结果按“当前锁定版本”判定，不含 GitHub dependabot 的
> 严重度评级与部分企业内部评分，因此条目数与 GitHub 页面可能不完全一致。
