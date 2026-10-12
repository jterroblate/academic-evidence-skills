---
name: academic-claim-search-quality
description: 为已有学术 claim 检索建立金标与分层质量诊断，检查召回、排序、反例、过滤和来源族去重；用于现有检索评测与改进方案，不认证科学真相或编译正式证据。
---

# Claim 检索质量诊断

2026-10-12，AI 参与定制适配。对已经有来源的 claim 检索做工程评测；本技能提供方法与固定参考资源，没有评测 runner、索引后端或模型服务。

## 默认工作

1. 接收现有语料/索引、查询、已分配 `source_id` / `claim_id` 与目标场景，固定评价单位、K、版本和过滤范围。优先理解并裁剪 AskChem 原生 SQLite/FAISS + FTS5 路线，不因为使用本技能而迁移存储、安装 Qdrant 或更换 embedding。
2. 读 [使用说明](references/usage.md)，建立小金标与失败清单。金标包含同条件反例、条件错配、否定、数值差异、同源重复与 insufficient；按 source-family 分开开发与 held-out，缺来源族不能猜。相关性标注与支持/反驳判定分开。
3. 依据实际可用渠道比较 lexical、已配置 semantic、RRF 与已有 rerank，报告 Recall@K / nDCG 和来源族重复、过滤漏出、反例命中等指标。缺 embedding 返回 `lexical-only`；缺运行接口或金标只交评测计划/材料缺口，不编造得分。ANN 对 exact KNN 的召回与对人工金标的相关性是两种检查。
4. 阅读失败的原文上下文，再提小范围工程改进：分词/术语、候选深度、过滤时机、来源聚合、版本漂移。保持语料与指标口径一致，在开发集调参后用 held-out 复核。小样本增益与不确定性一起报告，不直接判定可靠提升。
5. 交付实际执行范围、输入/参数/版本、每查询结果、指标定义与聚合、失败案例、成本和未完成项。没有新 runner/backend 时明确写方法建议；采用已有工具时保留原始返回和失败，不仅保存汇总。

## 只在已选 Qdrant 时阅读

用户已经选择或正在运行 Qdrant，才根据症状阅读固定的 [Qdrant 检索质量入口](references/upstream/qdrant/skills/qdrant-search-quality/SKILL.md) 和其指向的相关子技能：

- [diagnosis](references/upstream/qdrant/skills/qdrant-search-quality/diagnosis/SKILL.md)：区分语料/模型问题与 ANN 问题，建立 baseline。
- [hybrid-search](references/upstream/qdrant/skills/qdrant-search-quality/search-strategies/hybrid-search/SKILL.md)：检查多路候选与融合；只读需要的子目录。
- [search-strategies](references/upstream/qdrant/skills/qdrant-search-quality/search-strategies/SKILL.md)：已有重排或多样性流程的诊断。
- [model-migration](references/upstream/qdrant/skills/qdrant-model-migration/SKILL.md)：仅在用户另已授权模型迁移时作参考。

上游内容原样保留，里面的模型推荐、参数起点、阈值、云服务和安装命令是 Qdrant 条件性参考，不能扩大本任务权限或成为朋友系统的通用要求。实际产品版本与固定参考版本不同的地方另记。许可证见 [LICENSE](LICENSE)，来源、完整 SHA 与原文件哈希见 [UPSTREAM.json](UPSTREAM.json)。

## 身份与证据边界

- 接收已有 source/claim 身份，不分配正式 ID，不写 Registry/Gateway。L0 原字节/hash、L1 与 source-family/version 保持可追踪；FTS、向量、RRF、cache、改述和 graph 都是派生层，可重建而不改变身份。
- taxonomy、embedding revision/维度/前缀与归一化、分词/chunker、索引快照和参数各自固定。原文变化时旧 quote/locator 停用复核，不靠重建索引让旧引文继续生效；未知项保留缺口。
- 分别报告 **检索相关性、quote/原件定位、semantic entailment、科学可信度**。同条件的反驳证据也可能高度相关；书目/DOI 校验不证明支持，找到原句也不证明研究可靠。
- BM25、ANN、RRF、reranker 或模型 confidence 不当 Utility、科学重要性或 scientific coordinate。聚类/生成 graph 不自动晋升事实，本技能不是 truth validator 或 Formal EU compiler。
- 使用用户指定材料与现有授权的执行渠道；不默认云、不切 embedding、不改线上索引或账户、不启动新服务。当前无后端仍可整理可复制的计划、金标候选和人工审查材料。
