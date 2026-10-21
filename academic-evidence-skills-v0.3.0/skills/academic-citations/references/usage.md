# 使用说明 · 学术书目与引用检查

## 自然语言调用

“用 $academic-citations 检查 references.bib 与 paper.md 的引用键和缺失元数据；先离线检查，DOI核验保持元数据范围，按同一研究的不同版本提示去重。”

## 依赖与命令

Python 3.11+。格式化 `_common.py` 和 `format_bibtex.py` 只标准库；其他 CLI 导入 requests。Google Scholar 的 scholarly 是可选第三方 scraper，缺失时 `--help` 仍可运行，不能绕过 CAPTCHA/访问限制，也不保证完整 raw capture；本包不把该渠道默认用于可审计检索。

在隔离环境按需要安装 requests：`python3 -m pip install requests`。不重配全局，不自动安装 scholarly。脚本原依赖分别遵守其许可。

```bash
python3 scripts/format_bibtex.py references.bib --output formatted.bib --deduplicate
python3 scripts/validate_citations.py references.bib --manuscript paper.md --report structure-report.json
python3 scripts/doi_to_bibtex.py --help
python3 scripts/extract_metadata.py --help
python3 scripts/search_openalex.py --help
python3 scripts/search_pubmed.py --help
python3 scripts/search_google_scholar.py --help
```

仅当网络查询在当次任务范围内时：

```bash
python3 scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2 --raw-dir raw-doi --output metadata.bib
python3 scripts/extract_metadata.py --doi 10.1038/s41586-021-03819-2 --raw-dir raw-metadata --format json --output metadata.json
python3 scripts/search_openalex.py 'organoid' --limit 20 --raw-dir raw-openalex --output results.json
python3 scripts/search_pubmed.py 'organoid' --limit 20 --raw-dir raw-pubmed --output results.json
python3 scripts/validate_citations.py references.bib --check-dois --raw-dir raw-registration --report metadata-report.json
```

## 输入与输出

输入标识符、JSON 搜索记录、BibTeX 或 Markdown/LaTeX。格式输出、元数据、BibTeX 与检查报告均为派生；新 raw-dir 保存脱敏请求描述及未经解释的 HTTP entity body/哈希。响应含请求秘密回显时只保存哈希/省略原因，记录审计缺口。脚本会写用户输出位置，有些上游格式命令可覆盖输出；每次选新版本路径，不覆盖 L0。

未知元数据在本任务工作记录中用 JSON null/CSV `null`；BibTeX 不支持 JSON null，缺字段省略，不能写占位作者或年份当事实。上游某些 normalized records 空字符串是“缺失”，adapter须转成 null 并保留 raw。格式 key 是本地 bibliography 键，不能作为 P ID、source_id 或科学坐标。

`validate_citations` 的 DOI checks、citation counts、required fields 是书目/结构检查；引用来源是否支持正文必须另核 PDF 原文。`--venue` 内建数量只是启发式提示，不代替当次期刊规则。保留同研究版本列表、去重决定与手工核验记录，不以两版论文计两份独立支持。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。
