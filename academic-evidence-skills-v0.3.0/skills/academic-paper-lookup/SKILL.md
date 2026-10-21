---
name: academic-paper-lookup
description: 使用学术数据库原生接口发现论文、获取合法公开全文并保留查询与响应溯源；用于有边界的文献检索，不把摘要、搜索命中或API数据提升为正式证据。
---

# 学术论文发现与溯源

## 工作方式

1. 把问题写成可重放查询，确定数据库、日期/语言范围、记录上限与停止条件；当前接口/配额须查相应官方文档，固定提交的参考资料只作为起点。
2. 按任务读一个接口参考：生物医学用 [PubMed](references/pubmed.md)/[Europe PMC](references/europepmc.md)，跨学科用 [OpenAlex](references/openalex.md)/[Crossref](references/crossref.md)，预印本用 [arXiv](references/arxiv.md)、[bioRxiv](references/biorxiv.md)、[medRxiv](references/medrxiv.md)，全文可及性用 [PMC](references/pmc.md)/[Unpaywall](references/unpaywall.md)。其余数据库参考保留在 `references/`。
3. API 返回先保存原始响应及脱敏请求记录，再解释结果。`paginate.py` 要求新的 `--raw-dir`，逐页记录 HTTP 实体与 SHA-256；参数密钥不进溯源。每站串行，遇限流遵循该站规则与有界重试，不绕过访问限制。
4. 核对总数/实际数、页数与截断。空结果只表示该查询没命中；元数据不是全文，JATS 无 body 退出 2；arXiv error feed/限流不得当论文。
5. 输出标题/标识符、既有 source_id、来源族候选、端点/参数/访问时间、原始响应路径、检索覆盖与缺口。合法下载的 PDF 留在用户暂存位置，由 Gateway 归档。

## 资源与运行

[使用说明](references/usage.md) 提供依赖、自然语言示例和离线命令。保留 `paginate.py`、`jats_to_text.py`、`arxiv_atom.py` 与 `openalex_abstract.py`；后面三者只解析本地原始响应，其段落/索引不是 PDF bbox。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。

来源及改动见 [UPSTREAM.json](UPSTREAM.json)，许可证见 [LICENSE.md](LICENSE.md)。
