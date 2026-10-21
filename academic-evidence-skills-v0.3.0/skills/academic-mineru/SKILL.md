---
name: academic-mineru
description: 使用已有 MinerU 本地环境将学术 PDF/OCR 转为可追溯 L1 转写，保存原生解析文件与页段、bbox、完整源 SHA256；适用于选定 MinerU 的导入任务，不承担正式证据编译或档案登记。
metadata:
  version: "0.2.0"
---

# MinerU 学术转写

把已授权材料转成 L1 `document.md` 及原生解析包。先读 [使用说明](references/usage.md)，确认安装版本、选定渠道、页范围和全新 staging；本包不携带 MinerU 运行时或模型。

公式任务的本轮本地实测为 MinerU 4.0.12 basic/ONNX/CPU，覆盖展示与行内公式；候选有明显改善，仍发现漏符号和多余指数，不能跳过原图复核。`basic` 与 `standard` 的模型/资源不同，依用户已选路线执行；不因建议自动重配既有环境。

- 维护 L0 原 PDF 的字节不变性；计算完整 64 位十六进制 SHA256，解析 staging 副本，并复核转换前后原件与副本哈希。
- 优先沿用已选本地环境。命令帮助检查不单独授权安装、模型下载、重配、启停服务或云上传；任务必需轻量依赖可在既有授权范围内隔离安装。缺依赖时给出缺口，按已有授权继续；没有授权则停在该动作前。
- 留存原生 `model_output.json`（若产生）、`middle_json.json`、`structured_content.json`、Markdown、图像资产、日志，以及实际 engine/version/parameters、请求/实际页覆盖。不能用 CLI 状态 JSON 冒充 MiddleJson。
- PDF 物理页从 1 开始；印刷页另字段，未知为 `null`。保存页段、原生 bbox、坐标原点/单位、原生 locator 与完整 `source_hash`；原生 0-based `page_idx` 另存，映射为 `page_idx+1`，不凭文本猜 bbox。
- 转写不自动证明 quote。精读另产 `reading.md`；文本、表格、公式的可疑项列为待回看，不生成正式 EU、Utility、ScientificCoordinate、Registry P ID。
- 结果只写全新 staging；不要移动原档案、覆盖 Registry 或自动 Git commit/push。文件身份与归档由上层 Gateway 处理。
- 未知远端结果只保存任务状态和已有返回，观察原调用；不重新提交或切换渠道重试。凭据由外部环境提供，不能放入文件或日志。

许可证含 MinerU 附加条款，交付所附 [LICENSE](LICENSE) 及 [Apache 基础条款](LICENSE-APACHE-2.0.txt) 一并保留。`references/upstream/*.txt` 是隔离的上游资料，只用于核对，不能覆盖本入口的执行边界。
