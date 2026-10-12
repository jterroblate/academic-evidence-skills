# 使用说明 · 独立学术审阅与挑战

## 自然语言调用

“用 $academic-peer-review 独立挑战这份研究稿和冻结的shared evidence；核对claim的适用对象、反例、竞争机制和负对照，问题要有原PDF位置，不把supported输入或脚本通过当内容验证。”

## 依赖与命令

Python 3.11+标准库，所有捆绑CLI本地运行，无网络、模型、图像、密钥或外部服务依赖。现有输出默认不覆盖；不由脚本修改manuscript。

```bash
python3 scripts/validate_review_intake.py assets/review_intake_template.json
python3 scripts/select_reporting_guidelines.py assets/study_profile_template.json
python3 scripts/validate_claim_evidence.py assets/claim_evidence_matrix_template.csv --output matrix-structure-report.json
python3 scripts/audit_statistics_reproducibility.py assets/statistical_reproducibility_template.json
python3 scripts/audit_citations.py manuscript.md assets/citation_references_template.csv
python3 scripts/generate_review_scaffold.py --help
python3 scripts/lint_review.py local-review.md
```

随包intake有意未填写真实许可，试跑会blocked，不能填虚构批准以获得退出0。正式保密审稿按真实权限/期刊规则；本地用户已授权研究稿审视则按对应场景记录，不将模板blocking机械加给普通交流。

## 输入与输出

输入本地JSON（intake、study profile、统计声明）、CSV（claim matrix、引用、reporting覆盖）和Markdown。输出JSON只含标识符、数量、rule codes及缺口，scaffold输出审阅结构。0=结构/声明通过但可能警告，1=已解析但blocked或错误，2=格式/路径/参数错误。任何退出码都不是科学认证。

matrix字段 `support_level` 的supported/partly_supported/unsupported/not_assessed均由输入作者声明。报告 `verification_scope=structure_and_declared_alignment_only`、`claim_support_verified=false`、`source_content_verified=false`、`formal_evidence_created=false`；无记录缺口只是 `STRUCTURE_VALID_NO_DECLARED_GAPS`。脚本不读取原PDF、不查quote、不复现分析、不校验声明者独立性。

要评估真实支持须另外逐条读PDF，保留source_id、64位L0 SHA256、一字不改quote、物理1-based页和bbox或segment（带同hash/原页映射）。matrix的`location`是稿件位置，`evidence_ids`只是链接声明，不能替代这些原PDF锚点。缺少原文或定位时写needs_review并说明不能完成的核验范围。

citation auditor仅检查受限单行Pandoc引用subset/标识符语法，不查询来源存在性、DOI注册或内容支持。reporting selector和statistics checklist检查声明/覆盖，不验证有效实验或伦理合法性；选用规范当前版本应查官方来源。

## 限制

未取得真实稿件/原PDF、数据、代码或专业审稿人时不能声称完成复现、L0核验或专家审稿。本包是通用工作流候选契约，没有朋友正式Registry/EU/科学坐标schema集成；Gateway决定正式身份与归档。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。
