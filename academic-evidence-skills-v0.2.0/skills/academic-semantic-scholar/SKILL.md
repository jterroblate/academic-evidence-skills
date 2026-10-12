---
name: academic-semantic-scholar
description: 用已有 Semantic Scholar CLI 或 MCP 精确查论文、作者、全文片段、引用图谱和推荐，检查端点schema并保存原始响应。用于学术入口检索，不把元数据或推荐排名当内容证据。
---

# Semantic Scholar 文献入口

社区 XWang20 `semantic-scholar-cli` 的中文适配。首次读 [usage](references/usage.md) 和 [证据契约](references/evidence-contract.md)；不熟悉的操作、过滤和分页读完整 [operations](references/operations.md)。它和 `academic-scholarqa` 可独立使用，前者负责窄端点调用，后者负责文献综合。

1. 检查已有 `semanticscholar-cli`，或用户已有 Semantic Scholar MCP。每次网络CLI进程必设 `SEMANTIC_SCHOLAR_MAX_RETRIES=0`，因为上游默认也会对TransportError/超时重试；MCP须确认当前实例等价禁retry配置，无法确认时只做本地工作并说明限制，不改全局配置。同一 runtime 的 tools/schema 是有效参数权威；此包不自动装全局工具、不修改宿主配置。
2. 选择最窄的有界操作，首次 call 前先 `semanticscholar-cli schema OPERATION`。不要猜端点名、fields、offset 或 token；复杂输入用 --params-file，保存该输入。
3. 通过一个 JSON object 调用，保留原始返回、查询、时间、过滤、分页和外部 ID；检查退出码和顶层 error，MCP 还检查工具错误与成功外壳内嵌 error。
4. 模糊标题/ID先 resolve，最终引用批量取 metadata。DOI、paper ID resolve 仅确认身份；A全文/B摘要/C元数据/D图谱推断及 L0回查规则见契约。未知出处 snippet 不自动A。
5. 输出检索候选和来源映射，不把搜索/身份verify成功改成 verified quote 或正式EU。source_id 与来源组由调用方传入；不造P编号、不写Registry、不搬或覆盖原PDF，hash用完整SHA256。

路由：完整或近似标题→match；补全→autocomplete(不是证据)；主题→search；大规模与token分页→bulk_search；全文片段→snippets；已知论文/作者→get_*_details；多ID→batch_get；被谁引用→citations；引用了谁→references；相似工作→recommendations；作者论文→author_papers；数据集→四项dataset操作。避免legacy合并分页操作，除非兼容要求明确。

引用数、推荐排序、标题相似和图谱边均不能证明主张；同源多版不当独立支持。假设/推论和事实分开。两个Dog仅从共享库读写交接，不直接通信。

exit 0成功，1上游顶层API错误，2参数/schema错误；空成功不是失败。SDK自动retry默认禁用；明确返回的限流/错误可在任务范围内规划有界后续查询，参数错误先修输入，未知远端结果观察原调用、不重试。缺runtime清楚报告dependency，不静默编REST或新增收费渠道。远端上传、额外模型API或更改既有配置需要任务本来已授权。
