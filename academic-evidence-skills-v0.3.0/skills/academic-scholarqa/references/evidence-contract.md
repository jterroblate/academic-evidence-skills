# 接入候选契约与证据边界

此包没有目标工程的 EU、Registry 或坐标 schema。以下是待对接的候选契约，不代表已经实现正式 Evidence Unit 或完整坐标系统。

- L0 是原始 PDF：只读、不可覆盖、不搬动，保留完整 SHA256。source_id、source_family 由调用方传入，不新造 P 编号，不写 Registry；没有 source_id 就先补真实映射。
- L1 是可重建的摘要、解析文本、查询输出和结构化结果。AI 派生内容明确写 `content_nature: AI-derived`。保留 raw JSON、查询、过滤条件、原文 snippets、claim ledger、工具版本、时间和来源。
- `pdf_page_1based` 指 PDF 第一个物理页面为 1；`printed_page` 是印刷页码，未知为 null。不得把 chunk 名、摘要顺序、搜索排名当物理页码。
- `quote` 必须是原文 exact quote；与 source_id、source_hash、物理页和可回查定位绑定。文本规范化、OCR、翻译和模型改写都不能冒充逐字原文。尚未回查 L0 时 `quote` 留 null，可另存 `excerpt_candidate`。
- Tier A：有明确全文来源的段落；B：摘要直接支持；C：元数据仅确认身份与上下文；D：标题、图谱、推荐关系推断。搜索 snippet 并不自动为 A。
- Search、QA、DOI resolve、paper ID verify 成功都不等于 verified quote、正式 EU 或论文支持该主张。书目身份与 claim support 分开；support / contradiction / uncertain 都保留。
- 假设、建议、研究构想与已报告事实分开。相同 DOI/论文的预印本、发表版、镜像、摘要与全文共用来源组，不当多份独立支持；source_family 未知时不估计独立性。
- 两个 Dog 通过共享资料库交接任务、结果和 provenance；本技能不提供直接互发消息、隐式状态同步或共写原档案。
- 优先已有模型和 API 渠道；不默认新增收费 API、云上传、安装全局工具、修改全局模型配置、commit/push 或打包凭据。资料发给远端模型必须已在任务授权范围。未知远端结果保存状态并观察原调用，不自动重试。

候选 claim ledger 的最小字段：claim、claim_kind(finding/inference/hypothesis)、source_id、source_family、source_hash、paper_id、evidence_tier、support_relation、quote、excerpt_candidate、pdf_page_1based、printed_page、locator_status、retrieval_artifacts、review_status。不能取得的字段为 null；默认 review_status=candidate、locator_status=pending-L0-check。
