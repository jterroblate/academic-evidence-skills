# WorkBuddy 单技能导入准备包

2026-10-21 · JT 为朋友准备，AI 辅助适配。

这里是三个**独立单技能 ZIP**，用于按本机 WorkBuddy 的实际要求逐项导入；也保留 `skills/` 下的完整展开副本。多技能合集应先解压选择技能，不能作为一个技能直接导入。

| 文件 | 用途 |
| --- | --- |
| `pdf-to-markdown-workbuddy-v0.2.0.zip` | 把 PDF/已有逐页解析结果组织成可追溯 Markdown 包，执行完整性与基本公式诊断 |
| `academic-mineru-workbuddy-v0.2.0.zip` | 使用已有本地 MinerU，并将真实的4.x物化原生产物适配为逐页输入 |
| `academic-docling-workbuddy-v0.2.0.zip` | 使用已有本地 Docling，保留原生 JSON 与出处，了解公式增强的适用边界 |

每个 ZIP 只包含对应的一个完整技能目录。公式任务优先配合前两项；已有 Docling 渠道则按实际环境选第三项。SDK、Python、模型、账号与论文不在这些 ZIP 中；导入技能不会自动安装运行依赖。

## 导入和使用

1. 先查看当前 WorkBuddy 的“添加技能/导入”等本机入口与要求。若提供 ZIP 导入，选择需要的单技能 ZIP；若按目录读取，使用 `skills/` 中对应的完整目录。不要只复制 SKILL.md 而丢掉脚本、references 或许可。
2. 确认界面确实显示了技能及版本，再以一份已授权材料做代表页试跑；仅能读取文件不等于已经成功导入。遇到客户端拒绝，记录实际错误并在新的适配副本中处理，不改唯一原件。
3. 在任务中明确让 WorkBuddy 读取技能入口与相关 usage，检查已有 Python/解析器/模型。PDF公式需求使用 `--require-latex`；转换或验证退出码3代表待复核，不代表公式已通过。
4. 基本词法检查、可渲染和重复稳定都不能证明数学正确。回源核对另存记录，不把未经核验的数学、quote 或定位标成 verified，也不直接写正式 EU/Registry。

本轮只对齐[WorkBuddy 官方公开结构](https://open.workbuddy.cn/docs/skill)，补齐顶层 `description_zh`、`description_en`、`version`、`author`，保留原 `description`、原正文和完整资源。技能版本仍是实际的0.2.0，适配记录在各自 UPSTREAM.json 中；原作者与许可见各技能 LICENSE 文件。

已完成离线 YAML 必填字段、文件哈希、ZIP CRC/逐文件回读与隐私检查。**尚未在朋友的 WorkBuddy 客户端实际导入或验收**；这是导入准备包，不是官方认可或兼容性认证。公开结构核对日期：2026-10-21。

校验见 `校验回执.json`、`manifest.json` 与 `SHA256SUMS.txt`。无需安装或联网即可复核归档内容与 SHA256；无签名哈希只证明一致性，不证明来源真实性。
