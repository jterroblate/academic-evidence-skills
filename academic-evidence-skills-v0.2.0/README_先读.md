# 学术证据工作流 · 完整 Skill 包 v0.2.0

2026-10-12 · JT为朋友准备 · AI参与整合与定制。

**这是更新后的完整包：原14个技能＋新增2个claim技能，共16项。** 下载这一个ZIP即可取得全部技能、中文用法、固定上游来源与许可证、AskChem源码参考和3张讲解图。基础版与补充版保留为历史来源，本版不要求另外下载它们。

## 包里有什么

- `skills/`：16个完整技能文件夹，含SKILL.md、必要脚本/资源、usage、来源和许可。
- [每个技能怎么用](每个技能怎么用.md)：16项用途、输入输出和可复制调用方式。
- [讲解图](讲解图/)：前14项的两张结构图，加本轮2项新增技能与AskChem参考的讲解图。
- [新增Claim工具说明](新增Claim工具说明.md)、[起步顺序](Claim工具用途与起步顺序.md)：从PDF解析到claim候选、核验与检索的接入方法。
- `sources/askchem-*.tar.gz`：约2MB固定公开源码参考，不含大型数据库/模型。
- [证据与接入边界](证据边界与接入说明.md)、[来源与修改](来源与修改.md)、[验证说明](验证说明.md)、[许可范围](LICENSES.md)。

## 先用哪几个

沿用已有PDF解析渠道，用 `pdf-to-markdown` 整理原件哈希、转写和物理页映射；需要结构化解析时看 `academic-docling`，复杂扫描/公式可考察 `academic-mineru`。得到L1文本后，用新增 `academic-langextract` 抽保留原句、数值、条件和否定的claim候选。

候选经独立原件/支持核验后再接正式证据流程。已有检索系统时用新增 `academic-claim-search-quality` 诊断召回、排序、反例、过滤和来源族去重；先借AskChem的SQLite/FTS5/FAISS结构，采用Qdrant后再读取其具体指导。其他文献入口与阅读研究技能按实际任务选择，不必一次运行全部。

两个新增技能是操作方法与技术参考，未实现朋友的正式Compiler、EU/Registry或完整eval runner。模型、解析器、数据库和API配置由接收环境另行准备，不捆绑大型依赖或凭据。

## 安装

解压后保持整个包目录完整。安装工具需要Python3.10+；PDF本地转写器需要Python3.11+。先在包根目录运行：

```sh
python tools/doctor.py
python tools/install.py --destination /absolute/path/to/project/.agents/skills \
  --skills pdf-to-markdown academic-langextract academic-claim-search-quality
```

这是预览。确认目标路径后加 `--apply` 才复制；已有同名技能目录会拒绝覆盖。需要16项全部复制时使用 `--skills all`，也可手工复制选定的整个技能文件夹。

Codex项目可使用 `.agents/skills`，Claude Code项目可使用 `.claude/skills`；其他客户端按其技能目录约定放置。环境尚未确定时，直接让agent阅读包中选定 `SKILL.md`。客户端自动发现是否刷新以实际客户端为准。`agents/openai.yaml`为可选CodexUI信息。

安装只复制技能文件，不安装运行库、不调用模型/远端API、不改客户端配置。各技能后端准备方式见对应 `references/usage.md`。调用沿用现有已授权渠道；缺模型/定位/来源等条件如实标待配置或needs_review。

## 第一份材料

> 使用本包pdf-to-markdown整理我指定PDF的可回溯交付；已有解析结果则直接适配。随后阅读academic-langextract，对已有L1文本提出claim候选。原引句与改述分开，保留数值、条件、否定和歧义，分别报告L1字面匹配、L0原件定位和原文是否支持claim。不要直接写正式EU/Registry。

只有能读取文件/执行命令的agent才能运行后端；纯聊天客户端可以阅读方法与模板。本版验证了文件整合和复制机制，未代测朋友真实材料、远端模型效果或原工程接入。完整说明见 [验证说明](验证说明.md)。
