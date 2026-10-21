---
name: academic-critical-reading
description: 对已取得论文进行批判性精读，区分原文观察、统计结果、作者解释与AI推论，形成有原PDF定位的候选claim及反例审视；不自动创建EU或认证研究真相。
---

# 学术批判性精读

## 精读产物

1. 读取用户指定 L0 PDF 和对应 L1，核对原件 SHA-256；L1 阅读顺序、表格/公式及 OCR 问题写入 needs_review，不能靠流畅摘要抹去缺口。
2. 按 [核心能力](references/core_capabilities.md) 拆出研究问题、设计、纳排、测量、比较、效应量/区间与结论边界。每个 observation 逐字 quote + 原 PDF 物理页 + bbox/segment + source_id/hash，作者解释与 AI 推论另列。
3. 对照 [研究设计](references/experimental_design.md)、[统计陷阱](references/statistical_pitfalls.md) 查混杂/选择/测量、缺失、多重性、效应大小与精度；“不显著”不当零效应/等效，相关不当因果。
4. 读 [证据层级](references/evidence_hierarchy.md) 与 [常见偏差](references/common_biases.md)，按具体 claim 的对象/测量/时点判断适用性；不只凭研究类型打总分。必要时用 [逻辑谬误](references/logical_fallacies.md)/[科学方法](references/scientific_method.md) 区分可反驳的解释和未测试故事。
5. 对每个重要 claim 列反例或检索未找到的范围、rival hypothesis、可区分预测/测试、负对照及当前无法裁决处。输出候选 reading.md / claim table 和待独立挑战项，不自行改 shared evidence 原事实。

## 资源与运行

本技能是方法指导，没有上游执行脚本；[使用说明](references/usage.md) 给出输入输出、真实调用场景与定位候选示例。已有图/表可按用户授权分析；本版不包含任何生图调用或外部图像技能依赖。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。

来源及改动见 [UPSTREAM.json](UPSTREAM.json)，许可证见 [LICENSE.md](LICENSE.md)。
