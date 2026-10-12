# 工具用途与起步顺序

2026-10-12 · AI 选型建议。不是朋友已确认方案，亦不是下列后端的实际部署/效果验收。

| 资源 | 类型/许可 | 适用环节 | 起步方式 |
| --- | --- | --- | --- |
| [AskChem](https://github.com/bingyan4science/askchem) | 完整系统源码，MIT；数据另为CC-BY4.0 | claim store、分类、候选关系、混合检索、SDK/MCP | 本包已下载固定源码。按README先读模型、校验、抽取与搜索流程；若只看化学现有claim，可试[官方网页](https://askchem.org/)。API/SDK只读查询返回外部候选，不自动成为本地证据。 |
| [LangExtract](https://github.com/google/langextract) | Python库＋真正的官方usage skill，Apache-2.0 | typed extraction 与输入文本字符跨度 | 使用本包 academic-langextract。SDK安装只是准备，模型另配；沿用已有授权渠道，不默认云。 |
| [Instructor](https://github.com/567-labs/instructor) | Pydantic结构化输出库，MIT；非科学抽取skill | 严格字段、类型、自定义validator与调用结果 | 已有Python工程时考察 `pip install instructor` 的独立环境；先定义候选字段与校验，不复制README默认模型/API调用。可以是替代抽取接口，不要求与LangExtract重复抽取。 |
| [Docling](https://github.com/docling-project/docling) / [MinerU](https://github.com/opendatalab/MinerU) | 解析仓库；具体代码/模型许可各自核对 | 原件→页、块、表与文本 | 复用既有 academic-docling / academic-mineru / pdf-to-markdown。模型/系统依赖按原包usage准备；已选解析器优先沿用。 |
| [SQLite FTS5](https://www.sqlite.org/fts5.html) / [sqlite-vec](https://github.com/asg017/sqlite-vec) | 词法/向量检索部件；SQLite公共领域，sqlite-vec MIT或Apache-2.0 | 可重建检索索引与RRF | 先借AskChem SQLite/FTS5/FAISS。sqlite-vec是另一个可选实现，不是必须新增依赖；库不自动生成embedding。 |
| [SciFact](https://github.com/allenai/scifact) | 评测格式/代码，代码Apache-2.0；数据分项许可 | evidence rationale、支持/反驳/不足与分层评分 | 读 `doc/evaluation.md` 和数据格式；先做本领域人工金标。旧模型不作为现成通用truth engine，本包不含数据或模型。 |
| [Qdrant官方skills](https://github.com/qdrant/skills) | 真正SKILL.md，Apache-2.0 | 混合检索、golden set与检索质量诊断 | 使用本包 academic-claim-search-quality 的通用评测流程；已经采用Qdrant时才读它的服务配置参考。 |

## 最小试跑与升级顺序

1. 保存有权处理的真实原件与完整SHA256，明确来源族/版本；用既有解析器输出可重放文本和物理页映射。
2. 抽取少量 typed claim 候选，保留改述与原 quote 的区别、数字/单位、否定/条件、失败和歧义。核 L1 引句时不改写原 quote；单独回原PDF核 L0 页/区域。
3. 审查给定上下文是否支持该claim。字符串存在、DOI存在、结构合法是不同检查；设计/统计/科学质量还要另外评价。只有原工程授权关卡才能晋级正式EU。
4. 在普通表中保留candidate/review/version，FTS/vector/cache作可重建索引。用人工核过的小查询集比较关键词、语义、融合及可选重排；包含反例、条件错配、同源重复与证据不足。
5. taxonomy先版本化小文件，关系先带两端证据的typed候选表。出现实测容量、并发或延迟瓶颈再考虑Qdrant；组件编排复杂再考虑Haystack；跨关系/时序需求明确后再评估图后端。

建议优先新增的工程能力是：source quote/span verifier、保留限定的claim adapter、来源族去重、版本化taxonomy与金标eval。它们是接入任务，两个SKILL.md并未把这些正式工程组件自动实现。

## 视频指标如何理解

论文v1的240万claims/14.7万论文是历史快照；当前官网/HF已更新，数量存在版本差异。100% DOI可解析仅证明评测引用的书目记录可找到；97.9%是143/146可判定关系边的类型抽样精度。[原论文](https://arxiv.org/html/2607.28618v1)

视频10:12及13:15两页画面带有原论文不支持的卷积核/复杂度40%、效率37%、三个行业等指标，同期口播没有这些结论。本包选型不采用这些数值。

出处必须区分全文与摘要、外部record与本地原件、模型关系解释与逐字证据。探索性原则树提供导航，不直接更新正式科学坐标。
