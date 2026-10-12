---
name: academic-hypotheses
description: 把观察转为可证伪的候选科研假设，设计竞争解释、预测矩阵、测量和负对照，并审计候选引文定位；用于Scientist Dog规划，不选择真假或自动晋升正式证据。
---

# 候选假设与证伪规划

## Scientist Dog 工作方式

1. 从有版本/hash的 shared evidence 读取既有原文候选，按 [概念与工作流](references/concepts_and_workflow.md) 定义观察、问题、机制、假设和适用边界；假设只用 candidate。
2. 填 `assets/hypothesis_record_template.json`，保留因果 estimand、已知/未知、来源链接；区分观察、关联和因果语言，见 [因果推论](references/causal_inference_and_claims.md)。不得因搜索没命中宣称全新。
3. 为每个假设先独立列 rival hypothesis、反例、falsifier、判不明的结果；用预测矩阵与 `assets/falsification_controls_template.json` 定义可区分测试、负对照、测量/分析和扰动有效性。不能用同一 AI 生成的假设又自评 supported 完成认证。
4. 证据账本补 `quote`、物理 `pdf_page`、bbox/segment、L0 SHA-256、来源族与既有 source_id。运行本地 auditor 只查结构和声明；填 true 不会产生实测 verified，完整定位仍是 candidate。
5. 读 [实验设计](references/experimental_design_patterns.md)、[预注册](references/preregistration_and_open_science.md)、[质量标准](references/hypothesis_quality_criteria.md)，写冻结计划、反例检索界限、偏差/未知项和变更记录。将产物写入指定 shared evidence 候选区供独立 Review Dog 挑战，不直接发消息给它。

## 资源与运行

[使用说明](references/usage.md) 是本版字段/命令契约；[工具参考](references/tool_reference.md) 保留上游预测、测量等 schema。八个本地标准库 CLI 与八个模板保留，审计脚本已适配原文定位与声明语义。模板中的 synthetic 行只供结构试跑，不能转为真实证据。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。

来源及改动见 [UPSTREAM.json](UPSTREAM.json)，许可证见 [LICENSE.md](LICENSE.md)。
