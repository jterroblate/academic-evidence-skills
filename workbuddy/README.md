# WorkBuddy 交接入口

2026-10-13 · 本轮提供启动提示词与候选资料的公开入口，**未修改正式16项技能，也未在朋友的 WorkBuddy 上代测**。

先让朋友在 WorkBuddy 打开他自己的项目目录，再把 [启动提示词](START_HERE.md) 发给它。提示词能指导它读取仓库、审查技能、按本机工程改造与验证；读取 GitHub 文件本身不会安装插件或接通 API。

需要一次下载全部资料时，用 [WorkBuddy 完整交接包 v0.1](https://github.com/jterroblate/academic-evidence-skills/releases/download/workbuddy-handoff-v0.1/academic-workbuddy-handoff-v0.1.zip)：包括原16项正式技能、本轮候选、提示词和结构图。它是交接资料合并包，未增加正式技能数量。

## 下载与读取

| 资料 | 用法 | 校验 |
| --- | --- | --- |
| [正式完整包 v0.2.0](https://github.com/jterroblate/academic-evidence-skills/releases/download/v0.2.0/academic-evidence-skills-v0.2.0.zip) | 16项技能、中文用法、脚本/资源和已有讲解图；先选 PDF、claim、综述相关项 | SHA256：`92be20a332b92d435ce56e74f38fc2a04e0d69c67041fd1e84917f5f539a7cf3` |
| [本轮候选资料 v0.1](https://github.com/jterroblate/academic-evidence-skills/releases/download/workbuddy-handoff-v0.1/meeting-tool-candidates-v0.1.zip) | 已审查的 Zotero、Obsidian、LangGraph、MCP Builder 等指引与固定源码；解压后按需读取 | SHA256：`0432e3140603844f6b1cb9a1351595d0e4591b0533d58484f30a95af5334f89f` |
| [机器可读目录](TOOL_CATALOG.json) | 候选路径、用途、采用条件、固定版本及公开来源 | 状态明确区分静态审查与运行验证 |

正式包可在仓库目录 `academic-evidence-skills-v0.2.0/skills/` 直接读取。本轮候选 ZIP 中的11个标准技能目录包括中英版本和框架 primer；不应算成11项独立新能力。候选包没有朋友的私有附件，不包含大型运行依赖或账号凭据。

## WorkBuddy 怎么导入

官方说明支持通过“专家·技能·连接器 → 技能 → 添加技能”导入本地技能包或创建技能；技能入口为带 YAML 元数据的 `SKILL.md`，可附脚本及参考文件。[WorkBuddy 使用说明](https://intl.cloud.tencent.com/document/product/1316/84503)、[开放平台技能规范](https://open.workbuddy.cn/docs/skill)。

这两个下载都是**多技能资料合集**。先解压，再选择一个完整技能目录；不能把合集 ZIP 当成单技能包提交。朋友本机的 WorkBuddy 版本/导入器尚未核验，先由它检查当前技能目录和导入要求：必要时在适配副本补充 `description_zh`、`description_en`、`version`、`author` 等字段，保留上游版权与许可证，再单独打包。不能用其他腾讯产品或 CodeBuddy 的规范代替本机 WorkBuddy 的实际要求。

暂时无法自动发现时，可让 WorkBuddy 显式读取选中的 `SKILL.md` 并按其指引开发；这仍需要实际可用的文件、命令或连接器能力。`agents/openai.yaml` 是原包的 Codex 可选信息；原包安装器的 `.agents/skills` 示例不是 WorkBuddy 的安装承诺。

## 先选择哪些

| 当前任务 | 优先读取 | 接入条件 |
| --- | --- | --- |
| 原文、引句与 claim 候选 | 正式包 `pdf-to-markdown`、`academic-langextract` | 复用已有 PDF 解析/模型渠道，正式 EU 仍按原工程合同 |
| 文献与附件查询/补入 | Zotero Bridge 中文技能 | 实际为本地用户库且需要它的插件/MCP；已有连接则复用 |
| Vault 归档 | Obsidian Markdown/CLI | 仅实际采用 Obsidian 时启用 CLI；Registry 分配文献 ID |
| query/返回字段/EU ID 回取 | MCP Builder | 帮开发结构化接口，不是现成 EU 检索器 |
| 缺 PDF 暂停、补料后恢复 | LangGraph HITL/persistence | 框架选择未确定；现有调度器可借方法，无需强制迁移 |
| 外部科学搜索 | Elicit/OpenAlex 官方接口与源码 | 账户、用量和用途要对齐；Elicit 样例不是标准 `SKILL.md` |
| 完整综述 | 正式包 `academic-literature-review` 与引用技能 | 先验证引用回取链，再做“人给题目→完整综述” |

Pinecone FTS、Zotkit 等候选只在当前平台/渠道匹配时考虑，不作为默认安装列表。详见目录 JSON。

## 朋友本机需要提供

当前相关代码/运行入口，实际系统设计与正式 EU/Registry/paper list schema，一组 PDF/Markdown/EU 样例，Zotero 库类型、Vault 路径、检索后端和已配置服务。凭据使用本机连接器或环境配置，资料仓库无需它们。

## 验证范围

本轮核对公开来源、技能入口、许可、固定文件和 ZIP 校验，另审查启动提示词与项目优先级。尚未验证 WorkBuddy 自动发现/导入、插件安装、服务账户或朋友真实系统的两分支运行；由接收工程完成。

[本轮结构示意图](workbuddy-handoff-diagram.png) 为确定性代码排版；此前未确认结果的 AI 生图调用没有被重试或宣称成功。
