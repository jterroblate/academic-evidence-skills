# Claim 中心工作流 · 补充资料包 v0.1

2026-10-12 · JT 为朋友准备 · AI 参与选型与定制。基于 AskChem 视频的完整音轨转写、所有幻灯片代表画面、原论文及官方源码重新筛选。

核心流程：**论文原件 → 可回放的解析文本 → 有引句/定位的 claim 候选 → 独立核验 → 共享证据 → 分类、关系和检索。** 既有14技能包继续负责 PDF、文献入口与阅读研究；本包补充 claim 抽取与检索诊断方法。

## 包里是什么

| 目录/文件 | 用途 |
| --- | --- |
| `skills/academic-langextract/` | 从已有解析文本抽 typed claim 候选与字符跨度的定制技能；附 Google 官方 usage skill、示例、参考和许可证 |
| `skills/academic-claim-search-quality/` | 用小金标集诊断 claim 检索、反例与过滤的定制技能；附 Qdrant 官方检索质量参考子树及许可证 |
| `sources/askchem-*.tar.gz` | AskChem 固定提交的完整公开源码，約2.03MB；包含后台抽取、分类、图关系、检索/服务、SDK/MCP，无大数据库/模型 |
| `工具用途与起步顺序.md` | 七项精选资源、具体用途、安装/阅读入口及起步顺序 |
| `来源与修改.json` / `manifest.json` | 上游固定版本、来源/许可与本包文件 SHA256 |
| `验证说明.md` | 实际检查与未执行的效果验证边界 |

两个技能是 agent 操作指导及上游技术参考，**不是已经实现的正式 claim Compiler、EU/Registry 或完整评测引擎**。它们不自带模型、OCR、数据库、API密钥或朋友的工程契约。本包不含视频、完整转写和朋友的原始系统附件。

## 两个技能怎么用

复制整个技能目录到目标客户端支持的位置：Codex 项目 `.agents/skills/`，Claude Code 项目 `.claude/skills/`；其他客户端按其文档放置。也可不安装，直接让 agent 阅读选定目录的 `SKILL.md`。不要只复制一个入口文件。

普通聊天客户端可以阅读方法，但需要本地文件/命令能力的 agent 才能执行配套后端。两个技能的 `agents/openai.yaml` 是可选 Codex 显示信息。宿主环境不确定时先手动指定完整路径。

**抽取技能提示词：**

> 阅读本包 skills/academic-langextract/SKILL.md。处理我指定的一份已有 L1 解析文本，使用我现有已授权的模型/渠道，保留原件和页映射。输出 claim 候选，分别记录原引句、字符跨度、数值/单位、否定和条件，并列出失败/歧义。把 L1 字面匹配、L0 页/区域定位与语义支持检查分开；不要直接写入正式 EU/Registry。

如果模型渠道尚未配置，先准备输入与抽取方案；不要因为示例里写了某云模型就调用它。读取对应 `references/usage.md` 查看依赖准备和候选输出示例。

**检索诊断技能提示词：**

> 阅读本包 skills/academic-claim-search-quality/SKILL.md。对现有 claim 检索做诊断：固定语料/模型/索引版本，准备可复核查询与支持/反例，按来源族分组比较词法、语义和RRF。报告 Recall@K、排序、反例、条件错配和过滤问题；缺少 semantic 就标 lexical-only。先给出诊断结果，不自动部署服务、切换 embedding 或改正式索引。

这个技能指导如何组织评测，不表示已经有运行的 eval runner。只有工程已经选用 Qdrant，才读取其具体配置指导；小规模起步可复用 AskChem 的 SQLite/FTS5/FAISS 思路。

## AskChem 源码怎么用

在新的工作目录解压 `sources/askchem-*.tar.gz`。先阅读：

1. `src/askchem/models.py`：Claim/Source/Edge 与共享身份。
2. `src/askchem/validation.py`：实际校验范围；quote存在不等于逐字核验。
3. `src/batch_extract_abstracts.py`、`src/batch_extract_arxiv.py`、`src/deep_extract.py`：摘要/全文抽取提示及脚本。
4. `docs/search-pipeline.md`：FTS5、向量、分类召回、RRF与重排。
5. `living_taxonomy/README.md`：探索性的原则树。

先借结构与候选输出，不直接运行批处理、上传数据或作者的云配置。自托管需要另有数据库、依赖、模型及配置；本包仅下载源码，不保证 clone/解压即复现线上生产环境。朋友领域尚未确认，化学类型和分类不能直接当作通用 ontology。

## 先跑哪条路

先用既有 PDF 适配器得到原件哈希、页映射和文本；从少量真实论文产生 candidate，再人工检查原句/定位与条件保留。结构字段复杂时考察 Instructor；已有稳定抽取实现则沿用，不为了新库更换渠道。检索先做可回放的小原型与金标评测，再决定是否需要 Qdrant、Haystack 或图服务。

正式 source_id、EU晋级、坐标、Gate0 与 Gateway/Registry 接口沿用原工程契约。检索分数、模型 confidence、聚类和图关系不能自动成为 Utility、科学坐标或正式事实。
