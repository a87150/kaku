# 依赖安全审计明细（dependabot 残余梳理）

本文件由 `scripts/dep_audit.py` 生成：把当前虚拟环境中**全部已安装包**
（含传递依赖）逐个提交 [OSV 漏洞库](https://osv.dev/) 查询，
列出当前锁定版本命中、且 OSV 标记的所有漏洞。

- 包总数：45
- 命中漏洞条目：41

## 按包汇总

| 包 | 当前版本 | 命中数 | 建议修复版本 |
|----|----------|--------|--------------|
| Django | 4.2.30 | 7 | 5.2.15, 6.0.6 / 5.2.16, 6.0.7 / 5.2.17, 6.0.8 |
| django-allauth | 0.63.6 | 6 | 65.13.0 / 65.14.1 |
| mistune | 2.0.4 | 28 | （无修复版本） / 3.2.1 / 3.3.0 |

## 逐条明细

| 漏洞 ID | 别名(CVE/GHSA) | 包 | 版本 | 严重度 | 修复版本 | 摘要 |
|---------|----------------|----|------|--------|----------|------|
| GHSA-2hm2-hc3v-44h9 | CVE-2026-59930, PYSEC-2026-2218 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N | 3.3.0 | Mistune toc / TableOfContents directive: heading IDs use predictable `toc_N` numbering with no slugification, allowing collision with attacker-controlled `id="toc_N"` content |
| GHSA-2jpr-83rg-v67j | CVE-2026-27982, PYSEC-2026-56 | django-allauth | 0.63.6 | CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N | 65.14.1 | django-allauth has an open redirect vulnerability |
| GHSA-3h9f-r86x-qvjx | BIT-django-2026-48588, CVE-2026-48588, PYSEC-2026-2090 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N | 5.2.16, 6.0.7 | Django: cache middleware may expose private responses when unrelated request cookies are present |
| GHSA-4j32-57v6-6g45 | CVE-2026-59925, PYSEC-2026-2213 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 | Mistune inline_parser: quadratic-time parsing on long runs of `**x**` and `***x***` emphasis pairs |
| GHSA-58cw-g322-p94v | CVE-2026-44896, PYSEC-2026-168 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.2.1 | Mistune has XSS via unescaped figclass/figwidth in Figure directive |
| GHSA-8c25-4j27-2rv3 | CVE-2026-59923, PYSEC-2026-2211 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.3.0 | Mistune: XSS via percent-encoded javascript URI bypass in safe_url() |
| GHSA-8cjm-8mp7-r2xf | BIT-django-2026-8404, CVE-2026-8404, PYSEC-2026-201 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N | 5.2.15, 6.0.6 | Django: UpdateCacheMiddleware may disclose cached responses due to case-sensitive Cache-Control handling |
| GHSA-8g87-j6q8-g93x | CVE-2026-44708, PYSEC-2026-2206 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | （无修复版本） | Mistune Math Plugin has an XSS Escape Bypass |
| GHSA-8m3c-c723-h4p4 | CVE-2025-65431, PYSEC-2025-111 | django-allauth | 0.63.6 | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N | 65.13.0 | django-allauth's Okta and NetIQ implementations used a mutable identifier for authorization decisions |
| GHSA-8mpj-m6qm-5qr8 | CVE-2026-59927, PYSEC-2026-2215 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L | 3.3.0 | Mistune directives/include: mutual `.. include::` recursion crashes the renderer with `RecursionError`, denial of service via two attacker-controlled markdown files |
| GHSA-8qcx-xf44-272x | BIT-django-2026-53878, CVE-2026-53878, PYSEC-2026-2092 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 5.2.16, 6.0.7 | Django: DomainNameValidator permits newline characters that may enable HTTP header injection |
| GHSA-923m-gv2p-w5qp | BIT-django-2026-48587, CVE-2026-48587, PYSEC-2026-198 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:N | 5.2.15, 6.0.6 | Django: has_vary_header may expose cached responses when Vary values contain whitespace |
| GHSA-c8j7-8cv4-2xmq | CVE-2026-59922, PYSEC-2026-2210 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 | Mistune plugins/formatting: quadratic-time parsing on long runs of `~~x~~`, `==x==`, and `^^x^^` markers (strikethrough / mark / insert) |
| GHSA-crhf-3pfg-w68w | BIT-django-2026-53877, CVE-2026-53877, PYSEC-2026-2091 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L | 5.2.16, 6.0.7 |  Django: GDALRaster may over-read heap memory when constructed from bytes |
| GHSA-ffq3-xpv3-j92q | CVE-2026-59928, PYSEC-2026-2216 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 | Mistune block_parser: quadratic-time parsing on long lists of repeated reference-link definitions |
| GHSA-g97x-gvcm-x72h | CVE-2026-59926, PYSEC-2026-2214 | mistune | 2.0.4 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N | 3.3.0 | Mistune: XSS via unescaped class option in Admonition directive |
| GHSA-h7pc-vwp9-298g | BIT-django-2026-6873, CVE-2026-6873, PYSEC-2026-199 | Django | 4.2.30 | CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:N | 5.2.15, 6.0.6 | Django: signed cookies are vulnerable to salt namespace collisions |
| GHSA-qcq2-496w-v96p | CVE-2026-49851, PYSEC-2026-2652 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 |  Mistune: Potential DoS via quadratic-time parsing in parse_link_text |
| GHSA-qfrw-5rxm-mhh2 | CVE-2026-59929, PYSEC-2026-2217 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.3.0 | Mistune renderers/html.safe_url: HARMFUL_PROTOCOLS list misses legacy and chained schemes that historically chain to `javascript:` execution |
| GHSA-qhmc-3mvr-f2j4 | CVE-2025-65430, PYSEC-2025-110 | django-allauth | 0.63.6 | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N | 65.13.0 | django-allauth does not reject access tokens for inactive users |
| GHSA-r4rv-85jg-w4mf | CVE-2026-59924, PYSEC-2026-2212 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N | 3.3.0 | Mistune: Arbitrary File Read via Include directive path traversal |
| GHSA-v87v-83h2-53w7 | CVE-2026-44897, PYSEC-2026-2207 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.2.1 | Mistune Heading ID Attribute has Injection XSS |
| PYSEC-2025-110 | CVE-2025-65430, GHSA-qhmc-3mvr-f2j4 | django-allauth | 0.63.6 | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N | 65.13.0 | - |
| PYSEC-2025-111 | CVE-2025-65431, GHSA-8m3c-c723-h4p4 | django-allauth | 0.63.6 | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N | 65.13.0 | - |
| PYSEC-2026-168 | CVE-2026-44896, GHSA-58cw-g322-p94v | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.2.1 | - |
| PYSEC-2026-2206 | CVE-2026-44708, GHSA-8g87-j6q8-g93x | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.2.1 | - |
| PYSEC-2026-2207 | CVE-2026-44897, GHSA-v87v-83h2-53w7 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.2.1 | - |
| PYSEC-2026-2208 | CVE-2026-44898, GHSA-6269-cqxg-mhhv | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.2.1 | - |
| PYSEC-2026-2209 | CVE-2026-44899, GHSA-ccfx-mfmx-2fx9 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.2.1 | - |
| PYSEC-2026-2210 | CVE-2026-59922, GHSA-c8j7-8cv4-2xmq | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 | - |
| PYSEC-2026-2211 | CVE-2026-59923, GHSA-8c25-4j27-2rv3 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.3.0 | - |
| PYSEC-2026-2212 | CVE-2026-59924, GHSA-r4rv-85jg-w4mf | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N | 3.3.0 | - |
| PYSEC-2026-2213 | CVE-2026-59925, GHSA-4j32-57v6-6g45 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 | - |
| PYSEC-2026-2214 | CVE-2026-59926, GHSA-g97x-gvcm-x72h | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.3.0 | - |
| PYSEC-2026-2215 | CVE-2026-59927, GHSA-8mpj-m6qm-5qr8 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L | 3.3.0 | - |
| PYSEC-2026-2216 | CVE-2026-59928, GHSA-ffq3-xpv3-j92q | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 | - |
| PYSEC-2026-2217 | CVE-2026-59929, GHSA-qfrw-5rxm-mhh2 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 3.3.0 | - |
| PYSEC-2026-2218 | CVE-2026-59930, GHSA-2hm2-hc3v-44h9 | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N | 3.3.0 | - |
| PYSEC-2026-2652 | CVE-2026-49851, GHSA-qcq2-496w-v96p | mistune | 2.0.4 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H | 3.3.0 |  Mistune: Potential DoS via quadratic-time parsing in parse_link_text |
| PYSEC-2026-3717 | BIT-django-2026-15830, CVE-2026-15830 | Django | 4.2.30 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X | 5.2.17, 6.0.8 | - |
| PYSEC-2026-56 | CVE-2026-27982, GHSA-2jpr-83rg-v67j | django-allauth | 0.63.6 | CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N | 65.14.1 | - |

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
