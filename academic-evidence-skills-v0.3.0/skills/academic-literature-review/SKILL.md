---
name: academic-literature-review
description: 基于可追溯查询和材料快照整理学术综述，保留筛选、来源族、反例与claim定位，并区分引用元数据检查与原文支持；用于Review Dog证据整理，不自动生图或入EU。
---

# 学术综述与证据整理

## Review Dog 工作方式

1. 明确问题与综述类型、数据库、纳排和停止规则。读 [核心流程](references/core_workflow.md)/[检索与引用](references/search_and_citation.md)；若流程不是完整系统综述，不自称系统综述或伪造PRISMA数量。
2. 读取冻结的 shared evidence 和 raw search 响应；`search_databases.py`只是处理 normalized JSON，不联网搜库。保存原响应、筛选理由/排除项和转换版本，同研究多版本归组，不能用citation count替代质量。
3. 按设计、对象、效果方向/大小/区间、局限和相反证据综合。每段重要结论指向一字不改quote、原PDF物理页+bbox/segment+hash/source_id候选。摘要级资料明确限定，不当全文支持；图关系也是派生推论。
4. `verify_citations.py`只查DOI注册/Crossref元数据；本版输出registered_dois，禁用“verified”作为内容认证词。网络需新raw-dir，离线可只抽 DOI 候选。再独立核对实际原文适用性与反例。
5. 用 `assets/review_template.md`写综述与缺口；必要时用已有本地Pandoc/XeLaTeX导出，渲染成功只表示产物存在。把挑战/冲突写入 shared evidence 候选/审阅产物，不直接改源事实或向Scientist Dog发消息。

## 资源与运行

[使用说明](references/usage.md) 提供依赖、示例和验证范围。保留本地数据处理、DOI元数据和PDF导出三个CLI、检索策略、引用样式参考与模板；本版删除无关AI生图脚本、付费图像路径和外部技能强制依赖。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。

来源及改动见 [UPSTREAM.json](UPSTREAM.json)，许可证见 [LICENSE.md](LICENSE.md)。
