---
name: academic-peer-review
description: 独立审视论文或科研候选包的claim与证据对齐、统计复现、报告规范及竞争解释，输出可追踪问题和改进建议；本地结构脚本不认证真实内容或自授审稿权限。
---

# 独立学术审阅与挑战

## 独立审阅

1. 接收用户指定稿件/候选包、冻结的shared evidence及明确审阅范围。正式保密审稿按 `assets/review_intake_template.json`与[伦理实践](references/ethical_review_practice.md)核对已有权限/政策；普通用户已授权本地研究稿的挑战不额外虚设编辑批准。
2. 避开同轮生成者自我认证。读原PDF及[常见问题](references/common_issues.md)，逐条比较claim与一字不改原文定位候选，分清证据方向、大小、对象、时点、因果/机制语言与不确定性。source_id/哈希不符或缺定位就needs_review。
3. 保留反例、rival hypothesis、可区分测试、负对照和判不明处；用 `assets/claim_evidence_matrix_template.csv`写问题、限制与requested_action。`supported`是输入声明；`validate_claim_evidence.py`仅查声明的内部一致性，绝不生成真实supported认证。
4. 按任务读 [统计与复现](references/statistical_reproducibility.md)/[报告标准](references/reporting_standards.md)，查方法、误差、多重性、缺失、代码/数据与可复现边界。报告指南选择器只给候选规范/覆盖，当前版本需当次复核。
5. 生成给用户的审阅稿：主要问题、可行动改进、现有支持、尚未核验处和范围局限。审阅/冲突写进shared evidence派生产物，不能改L0/Registry或直接联系Scientist Dog；不自行向期刊、作者或外部工具传稿。

## 资源与运行

[使用说明](references/usage.md)给依赖、自然语言与CLI示例；[工具契约](references/tool_reference.md)详列输入格式。八个标准库CLI、intake/claim/统计/reporting/citation模板完整保留。本版给matrix report增加显式结构范围和未核验字段。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。

来源及改动见 [UPSTREAM.json](UPSTREAM.json)，许可证见 [LICENSE.md](LICENSE.md)。
