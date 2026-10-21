# WorkBuddy交接入口

2026-10-21 · JT为朋友准备，AI参与适配与实测。

当前先做PDF公式任务时，把[公式任务提示词](PDF_FORMULA_TASK.md)和自己的PDF/参考稿给WorkBuddy；推进整个EU系统时用[项目启动提示词](START_HERE.md)。两者都从当前v0.3.0读取相关技能。

## 一次下载

[完整技能包v0.3.0](https://github.com/jterroblate/academic-evidence-skills/releases/download/v0.3.0/academic-evidence-skills-v0.3.0.zip)：16项正式技能（更新其中3项）、既有候选资料ZIP、两段WorkBuddy提示词、中文用法、许可、AskChem固定源码及讲解图。模型、账号与论文不捆绑。

SHA256：`c656a03342709c83c8ebaa0c409c41fbc7e0e2111ddd8be35836d7762102513b`

[本轮实测结论](../academic-evidence-skills-v0.3.0/PDF公式更新与实测范围.md) · [机器目录](TOOL_CATALOG.json) · [公式流程图](../academic-evidence-skills-v0.3.0/讲解图/PDF公式保真流程_2026-10-21.png)

v0.3.0已替代旧v0.1交接ZIP中的正式技能；旧包继续保留为历史。候选仍是原静态快照，不因合包升级为运行验证。11个候选目录含中英版本和primer，不应算成11项独立能力。

## 怎么用

先在WorkBuddy打开自己的工程，让它检查已有技能、解析器、Python/模型、连接器与当前导入规则。合集先解压，再选一个完整技能目录；不是把多技能合集作为一个技能上传。未自动发现时，可以先显式读取选定SKILL并执行指引。

官方结构是YAML元数据的SKILL.md，可附references/scripts/templates，开放平台还列出中英简介、版本和作者等字段要求。实际导入前在适配副本按本机要求补齐，保留版权和许可证；原包的`.agents/skills`示例不是WorkBuddy目录承诺。[WorkBuddy官方技能规范](https://open.workbuddy.cn/docs/skill)（2026-10-21核对）。

当前公式路线优先读pdf-to-markdown、academic-mineru、academic-docling；结构/词法通过不证明公式正确，回源复核单独记录。后续再按实际缺口选Zotero查询、Vault归档、MCP接口或LangGraph等待/恢复方法；已有工程可做的优先复用。

## 已验证到哪里

本机已跑5篇103页文字基线各2次、两个后端各5代表页、MinerU另5篇103页全文及同页复跑。还有包完整性、复制、适配导出和状态拒绝测试；详细范围及发现的错误见报告。

尚未在朋友的WorkBuddy自动发现/导入、Windows、服务账户和原EU/Registry工程上验证。搜索结果、摘要、quote候选与数学词法结果不自动成为正式证据。原会议、设计、论文库、完整测试稿和凭据留在本机。

[三项WorkBuddy独立导入ZIP](../academic-evidence-skills-v0.3.0/WorkBuddy单技能导入包/README.md)已补公开元数据，仍须本机导入验证。
