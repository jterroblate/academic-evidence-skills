---
name: academic-citations
description: 整理与核对学术书目、提取DOI/PMID/arXiv元数据、格式化BibTeX并检查正文引用；用于书目身份与格式质量，不认证引文支持或替代原PDF核验。
---

# 学术书目与引用检查

## 工作方式

1. 接收原始标识符/书目/正文和已分配 source_id，建立版本与来源族关系；未知项为 null，不能猜作者、年份、DOI。
2. 读 [API 契约](references/api_contracts.md) 和 [元数据提取](references/metadata_extraction.md)，按 DOI、PMID、PMCID、arXiv 或可识别 URL 查身份。所有联网脚本要求新的 `--raw-dir`，先留原响应，再生成元数据/BibTeX；不运行非官方 Google Scholar scraper 作为默认取证渠道。
3. 使用 [BibTeX 格式](references/bibtex_formatting.md) 检查花括号、作者分隔、页码范围和 citation key。格式去重以 DOI/书目身份为起点，不能把不同 DOI 判为独立研究。
4. 使用 `validate_citations.py` 查必需字段、重复键、正文 unresolved/unused；默认本地检查，`--check-dois` 才联网。引用数量阈值只有用户/期刊明确要求时才启用，数量本身不是质量。
5. 单独核对 claim 对原文的适用性、方向、大小、对象、时点和不确定性，给反例与定位缺口。DOI 注册、有效 BibTeX、网页可打开仅报告各自检查范围。

## 资源与运行

[使用说明](references/usage.md) 列依赖、示例和输入输出；[脚本参考](references/script_reference.md) 列原参数。保留七个上游 CLI、花括号感知 parser、书目模板与 citation checklist；本版新加 raw response 记录辅助模块。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。

来源及改动见 [UPSTREAM.json](UPSTREAM.json)，许可证见 [LICENSE.md](LICENSE.md)。
