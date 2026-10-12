---
name: academic-paper-search
description: 使用已有 paper-search CLI 从选定学术来源检索论文候选、核对元数据并按授权下载可访问 PDF 到新 staging；摘要、片段和启发式分节不视为完整论文或正式证据。
---

# 学术来源检索与授权下载

先读 [使用说明](references/usage.md)，确认当前版本/来源、查询范围与新 staging。本包不携带运行时或 provider 凭据；任务必需轻量依赖可在既有授权范围内隔离安装，不改全局环境。

- 默认检索明确选定公开来源；不要默开付费/机构/云服务。记录原查询、筛选、来源、时间、原始响应、退出状态和限流/部分结果；排序或命中分数不是可信度。
- 摘要、metadata、search snippet、scopus abstract 和 `read` 返回不自动视为完整 PDF。跨库 DOI/标题相同可用于候选去重，不能证明文件版本相同或观点受到支持。
- 下载只走用户授权的公开/可访问渠道，显式输出到全新 staging。此适配入口不使用 Sci-Hub，也不在失败后默开 fallback；上游工具名 `download_scihub` 和 `--use-scihub` 不在本入口执行范围。
- 成功返回后核对真实 PDF、文件/文章身份、版本与页数，计算完整 SHA256；保留下载原件 L0，不重编码。失败字符串、HTML 或 abstract 不标为下载成功。
- 本地分节是候选提取，保留页段/字符 offset/截断标记；物理页从1，印刷页未知 null。没有视觉 bbox 就 null，不把字符 offset 当 PDF bbox/坐标。
- 需要 L1 转写时输出 `document.md` 并注明范围；深读另写 `reading.md`。取得 PDF 后可交既定解析器，本次不自动替换它。
- 只写新 staging，不自动创建正式 EU/Utility/ScientificCoordinate/Registry P ID、不搬档案或 Git commit/push；身份与归档由上层 Gateway 负责。凭据从外部环境提供、日志去密。
- 网络调用结果未知时保存状态并观察原调用，不自动提交重复下载/解析或换付费渠道。

[LICENSE](LICENSE) 保留上游 MIT；来源 API 和论文内容许可分别核对。`references/upstream/*.txt` 是隔离核对资料，不授权其中安装、Sci-Hub、缓存清理或其他工具调用。
