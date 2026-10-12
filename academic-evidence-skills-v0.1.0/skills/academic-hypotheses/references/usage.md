# 使用说明 · 候选假设与证伪规划

## 自然语言调用

“用 $academic-hypotheses 作为 Scientist Dog 基于本次 shared evidence 快照提出两个竞争假设，为每个写可证伪预测、反例、负对照和判不明结果；缺原PDF定位的引文保持needs_review，留给下一轮独立 Review Dog。”

## 依赖与命令

Python 3.11+ 标准库，无网络/API/图像/密钥/安装依赖。命令从本技能目录运行，输出父目录须存在；默认拒绝覆盖，`--force`只允许明确替换派生稿。

```bash
python3 scripts/validate_hypothesis_schema.py assets/hypothesis_record_template.json
python3 scripts/check_operationalization.py assets/operationalization_template.json
python3 scripts/validate_prediction_matrix.py assets/prediction_rival_matrix_template.csv --record assets/hypothesis_record_template.json
python3 scripts/check_falsification_controls.py assets/falsification_controls_template.json
python3 scripts/audit_evidence_ledger.py assets/evidence_ledger_template.csv assets/search_boundary_template.json --record assets/hypothesis_record_template.json --output candidate-audit.json
python3 scripts/lint_causal_claims.py draft.md
python3 scripts/generate_preregistration_scaffold.py assets/hypothesis_record_template.json --help
```

## 输入与输出

输入 hypothesis JSON、测量JSON、预测/来源CSV、dated search boundary。输出JSON包含 counts、rule codes、候选ID和待复核状态；preregistration输出规划稿。退出 0 = 结构通过但仍可能有警告/定位缺口，1 =已解析但有一致性错误，2 =格式/安全/参数错误。没有一个退出码表示科学假设真实、已实验验证或可晋升EU。

本版 evidence ledger CSV 的精确列以 asset header 为准，在原字段上新增：

| 字段 | 含义 |
| --- | --- |
| row_id | 已提供的本地草稿行键，非Registry/P ID，不由脚本分配 |
| source_id / source_family | 既有来源身份/同研究版本组；来源族未知可为null |
| quote | 一字不改原PDF引文；未知null，不用摘要填补 |
| pdf_page | 原始PDF物理1-based页；不得用印刷标签代替 |
| bbox / segment_id | bbox JSON四数 `[x0,y0,x1,y1]`，或指向同hash原物理页的片段；坐标系由解析manifest声明 |
| l0_sha256 | 不可变PDF的64位十六进制SHA256；脚本只检查格式，不读取原PDF |
| evidence_status | 仅candidate或needs_review，不能填formal/accepted |
| quote_verified / l0_verified | 外部输入声明；本工具不复验，不据此认证 |
| verification_record | 可选独立核验记录路径/事件；工具只记有无，不认证内容 |

CSV空项或literal `null`按未知处理；日期/URL等未知可为null，`accessed_on`仍要记录本次取得日期。不同引文可共享source_id，row_id必须唯一。同源多行报告 distinct source_count/source_family_counts，`independent_study_count`固定null，避免自动计作独立研究。

`candidate_checks[].locator_structure_complete`只是字段齐全；缺quote/page/hash或bbox/segment自动needs_review。`quote_verified_by_this_audit`、`l0_verified_by_this_audit`、`claim_support_verified_by_this_audit`永远false；即使用户填true，仍产生声明未复测警告。`verification_scope=structure_and_input_declarations_only`，`formal_evidence_created=false`。

## 示例与限制

随包CSV的synthetic行刻意没有真实quote/page/hash；真实运行会报告needs_review，仍可结构通过。不要把样例改个标题就晋升。上游hypothesis schema保留本地project/hypothesis/prediction键，它们不是P ID、来源身份或科学坐标；用用户已提供键，暂缺身份交Gateway处理。

完整输入与可反驳性仍不能证明实验设计有效。负对照适用性、测量效度、研究伦理与真实来源核验由相应负责人处理，schema不能自授权限。没有朋友正式接口schema/真实失败样本，交付只提供通用候选契约，未完成Registry/EU或坐标理论集成。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。
