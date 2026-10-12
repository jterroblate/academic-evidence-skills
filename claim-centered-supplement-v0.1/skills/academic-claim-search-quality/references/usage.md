# 使用说明 · 分阶段 claim 检索质量诊断

本文件是方法与输入输出约定，2026-10-12 由 AI 定制；不是朋友正式 schema、可执行 runner 或已验证 backend。按当前任务选择阶段，无需先部署新服务。

## 阶段 A：固定对象与建立金标

接收或从现有材料读取：

| 输入 | 需要记录 |
| --- | --- |
| 任务目标 | 要找某项发现、比较条件、检索反例还是收集综述证据；返回单位是 claim、evidence span 或 source-family |
| 语料 | 语料快照/hash、允许的来源、已分配 source_id/claim_id、版本、source-family、原文和定位；未知来源族留缺口 |
| 分类与解析 | taxonomy version、parser/chunker/分词版本；原件 L0/hash 和 L1 引文定位的可用状态 |
| 执行渠道 | 用户指定的现有命令/API 或保存的检索返回；访问范围与可用过滤；没有渠道就计划-only |
| 向量与排序 | embedding 模型完整 revision、维度、前缀/归一化、索引版本；候选窗口、RRF/rerank 配置；未配置记录 lexical-only |
| 查询/标注 | query_id、原始查询、筛选语境、开发或 held-out 分组、人工标注来源/日期、相关证据及困难负例 |
| 评价条件 | K、相关性规则、来源聚合规则、延迟/成本预算；先约定标准，再运行或比较 |

先用少量真实查询跑通可审查闭环。可以建议 50–100 条起步，但数量取决于任务、困难样本与预期增益；它不保证统计充分，也不要求使用者先填完整表。AI 从提供的资料抽取字段，不知道的留空。

金标应涵盖条件相同但方向相反、条件/对象/时点不同、否定词、数量级/单位变化、同研究多版本、多条同源 claim、相关但不足裁决，以及没有已知相关证据的查询。每条带可回读上下文。LLM 合成或自动标签先是候选，经独立复核才作为金标；不让被评测检索器的排序/分数定义自己的正确答案。

开发与 held-out 按 source-family 隔离，预印本/期刊版、摘要/全文和重复导出不能跨组造成泄漏。没有可靠来源族时说明分组不确定，不凭 DOI 不同认定独立研究。指标按查询聚合时记录查询与来源族的相关依赖，不能把同源版本当独立样本扩大置信度。

相关性可以用 `0=不相关、1=相关但不完整、2=直接覆盖查询语境` 的分级标签，这是可选约定。支持和反驳方向均可是 2；另列 `supports / contradicts / insufficient / context_mismatch / not_checked` 的语义审查字段。前者评检索，后者需要独立判断，不互相替代。

复制提示词：

> 使用 $academic-claim-search-quality。读取我指定的 claim 语料快照、已有 source_id/claim_id/source-family 与查询。先提取版本和过滤范围，建立可审查的金标候选，覆盖反例、条件错配、否定、数值、同源重复和 insufficient。把相关性与支持方向分开；按来源族隔离开发与 held-out。没有已配置 embedding 或运行入口时明确 lexical-only 或计划-only。不要部署服务、切模型、改索引或编造指标。

## 阶段 B：在现有渠道做最小比较

如果只有保存的检索返回，可对它们评测并注明“离线结果评测”；没有运行证据不声称后台已执行。只有词法渠道就报告 lexical baseline；有现成且授权的 semantic/RRF/rerank 才增加对应比较。不在这一步购买模型、启动服务或改线上索引。

检查返回是否保留 claim/source/version/hash 和过滤参数。排序结果的 score 仅作为检索诊断字段；不能依据高分给 claim 支持/可信度标签。RRF 用名次融合，其参数与候选窗口固定并记录；直接混合不同尺度的分数须有明确实现与金标证据，不能用“融合”掩盖。

建议输出这些指标，按实际标注和需求取舍：

| 指标 | 口径与限制 |
| --- | --- |
| Recall@K | 前 K 个结果命中的金标相关项数 / 已标注相关项总数。明确项是 claim、span 或来源族；金标不完备时是“对当前金标的召回”。零相关项查询的 recall 为 N/A，另测错误返回/拒答，不能除零或填 100% |
| nDCG@K | 用预先约定的相关等级与 gain（例如 2^rel−1）、log2(rank+1) 折损计算，再除以同一金标的理想排序。缺分级标签或 IDCG=0 时为 N/A；不拿模型分数作 relevance label |
| 反例命中 | 同可比条件的反向证据在前 K 中的覆盖；语境错配材料单独计难负例，不能混成反例 |
| 来源族重复 | 重复版本是否占据候选/可见窗口，报告来源族级覆盖与唯一 claim/span 覆盖；同来源多条不同必要证据不等于重复 claim |
| 过滤漏出/误排除 | 不满足授权范围、source/version、类型或 taxonomy 过滤的返回；以及被错误排除的已知相关项。没有漏出不代表没有误排除 |
| 工程成本 | 有真实运行记录时报告 P50/P95、候选规模、内存/调用次数/耗时；保存的结果没有可靠时序就留空 |

若一条查询需要同论文的多条不同 claim，保留必要证据集合。source-family 只控制重复版本与独立支持计数；论文上限/来源分组是策略参数，不默认“每论文一条”适用于所有任务。比较策略时同时看唯一 claim/span 与来源族口径，避免多样性提升掩盖证据完整性下降。

lexical/semantic 的过滤范围与来源版本要可比。审查先过滤还是融合后过滤、补取/截断位置与 cache key 是否绑定语料/taxonomy/embedding/filter 版本；只看最终 top-K 不足以诊断漏召回。修改/删除来源后，应停用失效缓存与旧引文，重新索引不改变 source_id/claim_id。

若现有 backend 有 ANN：exact KNN overlap 衡量近似索引能否找回同模型空间的邻居；人工金标衡量这些邻居是否相关。exact 也差时先审查数据、语境、分词、模型匹配和候选流程；exact 好而 ANN 差才检查近似参数。不能把 ANN overlap 当 claim 支持准确率。已有 FAISS IndexFlat 等 exact 索引不需虚构 ANN 调参任务。

复制提示词：

> 使用 $academic-claim-search-quality 比较这两份已有检索返回和固定金标。先声明评价单位、K、gain、来源族去重与过滤规则，分别报告 Recall@K、nDCG、反例、重复和漏出。把 not_checked 与失败保留，缺后台运行或时间记录就不补造。每个失败读原文语境，提出最少必要的工程改进；held-out 不用于挑参数。

## 阶段 C：提出改进与独立复核

围绕实际失败提出小步修改：术语/分词、引用/数字检索、候选深度、过滤与缓存、来源聚合或版本映射。先用开发集检查具体失败是否修复，再在固定 held-out 上报告整体变化；没有显著/可靠增益就称结果不确定。需要区间时以配对查询差值或合适的来源族分组计算，记录方法与样本；无执行工具则提出做法，不声称已经 bootstrap。

优先参考 AskChem 已有检索实现：[固定 search pipeline](https://github.com/bingyan4science/askchem/blob/cbb612ab355cca0b9fbd23a457b42ae82c172a70/docs/search-pipeline.md)。阅读源码和配置后裁剪适配；不因引用量 boost、论文多样性、分类位置或 ranking score 给朋友的 Utility/coordinate 赋值。

只有用户已选 Qdrant，才从 [固定 Qdrant 入口](upstream/qdrant/skills/qdrant-search-quality/SKILL.md) 按症状读子技能。它的默认阈值、候选窗口、模型榜单和托管推理是上游场景参考，须本任务金标与实测决定；加载参考资源不授权新安装、云调用、微调、模型迁移或生产配置更新。

quote 是否逐字匹配、原件物理页/bbox/segment 是否正确，是另一个来源核验。claim 是否被给定原文支持，是另一个 entailment 审查；研究可信度还需设计、偏倚、统计和独立重复。请求这些检查时保留独立字段/角色与证据，不以检索指标替代；本技能不提供对应执行器或 Formal EU 晋升。

复制提示词：

> 使用 $academic-claim-search-quality 阅读检索失败案例，给出可在现有 backend 实行的分阶段改进与 held-out 复核计划。优先借 AskChem SQLite/FAISS/FTS5 实现。未选择 Qdrant 时不用它的排障子树；不得自动更换 embedding、改线上索引或晋升生成 graph。区分工程相关性、原文定位、entailment 与科学可信度，明确哪些已执行、哪些只是方案。

## 输出与状态

优先沿用用户既有输出格式；没有格式时交以下小包即可：

- `evaluation-plan.md`：目标、评价单位、K/gain/过滤/去重、开发/held-out 分组、参数和缺口。
- 版本化的金标或候选标注：query_id、相关 claim/span/source-family ID、等级、判断者、上下文位置、版本和审查状态。
- 每查询结果/失败记录：实际通道、原排序及 ID、固定配置、是否被过滤、重复/反例/insufficient、原始返回路径。
- `quality-report.md`：实际完成、指标及定义、对比/不确定性、失败、成本、最小改进和未执行项；未运行时不生成虚假的 run_id/得分。

这些文件名与字段是通用示例，不是新后端已实现的接口。状态可用 `plan-only`、`lexical-only`、`offline-results-evaluated`、`backend-run-evaluated`、`needs-review`，也可沿用原工程同义状态；实际范围写清楚。

## 来源与适配

本技能将 Qdrant 官方检索质量诊断方法改为已有学术 claim 检索的中文入口，并保留固定的上游 search-quality 子树及其必要 model-migration 相对引用。上游完整 SHA、逐文件 hash 与适配文件见 [UPSTREAM.json](../UPSTREAM.json)；原样资源受 [Apache-2.0 LICENSE](../LICENSE) 约束。中文入口与本说明是 AI 参与定制，不冒充 Qdrant 官方发布或朋友已确认的方法。
