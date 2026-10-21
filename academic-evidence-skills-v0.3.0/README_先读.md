# 学术证据工作流 · 完整Skill包v0.3.0

2026-10-21 · JT为朋友准备 · AI参与选型、适配与测试。

完整包仍有16项正式技能。本轮依据5篇103页材料的测试，更新PDF转写、MinerU和Docling三项；其余13项保持v0.2.0文件。另附既有定向候选ZIP、WorkBuddy提示词、固定AskChem源码、许可与讲解图。候选11个目录含中英版本/primer，不计作11项独立新能力。

- [每个技能怎么用](每个技能怎么用.md)：16项总用法。
- [本轮PDF公式结论](PDF公式更新与实测范围.md)：适合哪条路线、实际测试范围与已知错误。
- [WorkBuddy三项独立导入ZIP](WorkBuddy单技能导入包/README.md)：补齐官方公开元数据，保留全部脚本与许可；尚未代测客户端导入。
- [直接给WorkBuddy的提示词](WorkBuddy_PDF公式任务提示词.md)：先跑代表页，再回源核对与扩展全文。
- [公式核验流程图](讲解图/PDF公式保真流程_2026-10-21.png) · [WorkBuddy三项如何配合](讲解图/WorkBuddy三项技能怎么配合_2026-10-21.png)：本轮2张说明图；文件夹另保留3张历史结构图。
- [候选资料](候选资料/README.md)：Zotero/Obsidian/LangGraph/MCP等按需参考，仍为静态快照。
- [验证说明](验证说明.md)、[来源](来源与修改.md)、[许可](LICENSES.md)。

优先复用现有渠道。本组样本建议继续试MinerU 4.0.12 basic/ONNX；Docling公式增强与PyMuPDF文字基线的边界见报告。需要公式时用`--require-latex`，但它不做OCR，也不保证公式正确。新增数学检查只查基本词法与损坏，零问题仍需回原件，候选不直接当正式EU。

## 安装与运行

解压并保持目录完整。先在本包目录运行：

```sh
python tools/doctor.py
python tools/install.py --destination /absolute/path/to/project/.agents/skills --skills pdf-to-markdown academic-mineru academic-docling
```

安装器需要Python3.10+，PDF适配器需要3.11+。这是预览，加`--apply`才复制；已有同名目录拒绝覆盖。全部16项可用`--skills all`。安装器只复制文件，不安装运行库、下载模型或配置API。后端依赖按各usage在项目隔离环境准备，ZIP未包含SDK/模型/账号。

`.agents/skills`是Codex项目示例；WorkBuddy按其本机版本检查导入位置和元数据，先解压合集，再选择单个完整技能目录。没有自动发现时显式读取SKILL并照其流程工作；不能把读过文件当已成功导入。未在朋友WorkBuddy或原EU/Registry工程上代测。

后续claim候选用`academic-langextract`，检索诊断用`academic-claim-search-quality`，完整综述用`academic-literature-review`与引用技能；原件、quote、claim、假设的状态分开。
