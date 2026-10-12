---
name: academic-langextract
description: 从已有 L1 论文文本按类型抽取 scientific claim 候选并检查逐字引文与字符跨度；用于接入 LangExtract 的窄抽取层，不用于 PDF 解析、普通综述或生成正式 Evidence Unit。
---

# L1 文本中的候选主张抽取

用 LangExtract 提出保留来源的 typed candidate。只输出 `candidate` / `needs_review`；即使引文检查通过，也不创建 FormalEU、写 Registry、分配 Source/candidate ID、评定科学重要性或改变坐标。ID 与晋级规则由外部 Gateway/Registry/工程提供。

首次使用或准备接入时读 [references/usage.md](references/usage.md)。上游调用细节按需参考 [原版 usage Skill](upstream/langextract-usage/SKILL.md)；该目录是未改上游参考，其中模型示例、默认 provider、过滤方式不授权本次调用。本入口的边界优先适用。来源和改动见 [UPSTREAM.json](UPSTREAM.json)，上游许可见 [LICENSE](LICENSE)。

## 输入与渠道

- 接收只读 L1 文本、外部 Source ID、L1 hash/版本、原件 L0 hash/位置、已有 page/block/bbox 映射、输出位置，以及本次已授权的 model/provider/channel 配置。缺字段注明缺失，不自行补 ID 或伪造 hash/映射。
- 不解析 PDF、不改 L0/L1、页映射或 canonical object。当前抽取不得覆盖原件或源文本；输出使用新的候选/审查工件。
- 仅沿用当前已经授权的渠道与模型。没有明确配置时，返回 `needs_review` 和“待配置”的准备报告，不默认 Gemini、不改到云端、不调用付费 provider，不把 SDK 已安装或环境变量中有 key 当作执行授权。准备 SDK 不代表运行推理。
- 调用前核对固定 SDK 版本、provider 能力与所有 retry 层级。LangExtract 内部 provider、底层 SDK、外层任务可能各自重试；记录实际配置和可关闭项，不承诺已禁用未经核查的重试。SDK 自动生成的 document ID 不能当 Registry ID；透传外部 ID，缺失时停在准备阶段。

## 抽取与来源检查

1. **保存输入边界。** 按原字节/文本保留本次模型实际读取的 L1 输入、hash/版本及输出路径。若为 chunk，记录它在原 L1 中的基准 offset 与上下文；不要把 chunk offset 当全篇 offset。找回指代和跨句条件时可读相邻上下文，仍逐段保留来源，禁止用外部知识补全。
2. **定义窄类型。** 依任务提取 subject、predicate、object、原数量/单位/比较符、否定及作用域、条件/群体/时间、scope、uncertainty/epistemic wording。引用 observation、mechanism、limitation 等时标明候选类型，不混成已验证事实。保留原数值字符串、范围和有效数字；规范化值只能另列，不能覆盖原表述。没有明示的字段留 `null`/未知，不推断。
3. **quote 与改述分开。** `quote` 必须是原 L1 的连续逐字片段；`claim_paraphrase` 是模型改述，永远不是 quote。多个证据片段分别列出。每个关键字段关联其证据或注明无来源；短 quote 不自动支持完整 claim。拆成独立主张时不得丢主客体、数量、否定、限定、不确定性或原实验范围。
4. **独立做 L1 字面检查。** 不以 `char_interval != None` 或 `MATCH_EXACT` 判通过：上游默认容许 fuzzy/lesser，MATCH_EXACT 也是 token 对齐。对本次真实 L1 原文本独立检查 span 边界和 `raw_input[start:end] == quote`；采用左闭右开字符 offset，并声明编码/字符计数口径。保存上游 alignment 状态与独立校验结果。规范化/大小写折叠/去连字符仅用于寻找位置，不能修改原 quote 来凑通过；从原文重新取得片段时保留先前响应及修订记录。
5. **保留歧义与失败。** 记录重复引文的全部可行位置与消歧依据，不能静默选择第一处；不能唯一定位就 `needs_review`。fuzzy、lesser、无 span、schema 失败、漏数字/否定/条件与零候选分别保留原因。不要用仅保留 grounded 的列表过滤丢掉失败；不把 `suppress_parse_errors` 返回空集解释为成功无 claim。
6. **三种检查分开。** `l1_quote_check` 是当前文本的字面匹配；`l0_locator_check` 是已有映射回原 PDF 的可靠性；`entailment_check` 是原文是否支持完整改述。三者分别记录。缺 page/bbox 或未核对 L0 时为 `unknown`；L1 命中、文档 DOI 或映射表存在都不自动成为 L0 验证。quote 出现也不证明 entailment 或科学 truth；未独立审查时 entailment 为 `unknown`/`needs_review`。

## 返回、失败与审计

- 每条仍是 `candidate` 或 `needs_review`。保存所有候选和失败；批次总体状态区分完成、部分完成、失败与待配置，不伪造已完成输出。最小示例是 [usage.md](references/usage.md) 中的非正式示例，不是朋友原工程正式 EU schema。
- 在自己的调用/整合层留存完整原始模型响应、外部 run/attempt ID、模型/provider/channel、SDK 与 prompt/schema 版本、实际输入、usage、解析结果、逐项检查、错误和重试配置。先保存原始返回再作解析；LangExtract 的 annotation JSONL 不等于完整原始模型响应，Skill 本身没有日志执行器。未能获取原始响应时标明审计缺口，不宣称留存完成。认证 key/请求认证头不进入工件。
- 对已知返回，只修本地保存/解析/校验，不重新调用模型以替代原返回。网络超时且远端结果未知时保存 `remote_outcome: unknown`，观察或恢复原任务；不能盲目重发。确认失败后的重试须仍在已授权渠道、预算和次数内，并作为新 attempt 保留前次记录；没有这些条件时返回 `needs_review`。
- 交付候选清单、逐项审查结果和原始响应/输入的文件位置，明确哪些检查实际完成、哪些为未知。把 FormalEU 晋级、Registry 写入、模型切换和 PDF 重编译交回外部流程。
