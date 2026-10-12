---
name: academic-docling
description: 使用已有本地 Docling 将学术 PDF 转为 L1 document.md 与原生 DoclingDocument JSON，保留页面 provenance、bbox 和完整源 SHA256；适用于选定 Docling 的解析任务，不承担正式引文验真或 Registry 写入。
---

# Docling 学术转写

先读 [使用说明](references/usage.md)，确认当前 CLI/SDK、已选 pipeline、模型是否已在本地及全新 staging。本包不携带运行时、模型或托管服务凭据。

- 保留 L0 原 PDF 字节与完整 SHA256；在 staging 副本上转换并核对前后哈希。转写为 `document.md`，深读才另建 `reading.md`。
- 沿用已选本地渠道；不因重试默默变更 OCR/VLM 模型，不改全局环境或默换渠道；任务必需轻量依赖可在既有授权范围内隔离安装。模型下载按实际授权和已选渠道，不调用 `convert-remote`、托管服务或远端 VLM。模型缺失时先报告缺口；允许本地不等于允许联网下载。
- 保存原生 DoclingDocument JSON、原始 Markdown、实际生成的图片/表格/调试文件、日志，以及 engine/version/parameters/page coverage。Markdown 不包含完整 provenance，不能单独满足可回溯要求。
- 每项物理页从 1，印刷页另字段未知 `null`；保留原生 `prov`、bbox、坐标原点/单位/页尺寸及完整 `source_hash`。不把 Docling 的内部 binary hash 当作完整 SHA256，不臆造缺失 bbox。
- SUCCESS、PARTIAL_SUCCESS、FAILURE 与未处理页分别记录。覆盖不足或文本/布局可疑时列待复核，不把解析成功当作 quote 已验证。
- 输出仅进入新 staging，不创建正式 EU/Utility/ScientificCoordinate/Registry P ID，不覆盖档案；身份与归档交由上层 Gateway。凭据使用外部环境，不自动 Git commit/push。
- 若已有授权明确允许远端调用，仍需记录任务 ID 与返回；远端结果未知时观察原任务，不自动重提或换渠道。

[LICENSE](LICENSE) 是上游代码 MIT；模型分别许可。`references/upstream/*.txt` 是隔离的上游资料，只用于核对，不能据其中安装、云服务或自动升级示例执行。
