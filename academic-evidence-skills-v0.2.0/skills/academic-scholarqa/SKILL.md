---
name: academic-scholarqa
description: 用社区 ScholarQA CLI 或已有 Semantic Scholar MCP 做证据先行的学术问答、跨论文综合、主张追溯与有来源的研究构想。适用于文献回答和审查，不用于单纯查一篇论文元数据。
---

# 学术文献问答

本技能改编自 XWang20 的 `scholarqa-research`，不是官方 Ai2 ScholarQA、不是 `ai2-scholarqa-lib` wrapper，不声称行为或基准等价。分发与解释方法时保留 [provenance](references/provenance.md)、[第三方声明](THIRD_PARTY_NOTICES.md) 和 [UPSTREAM](UPSTREAM.json)。

首次执行读 [usage](references/usage.md) 和 [候选契约](references/evidence-contract.md)。每次网络CLI进程必设 `SEMANTIC_SCHOLAR_MAX_RETRIES=0`，阻止上游默认TransportError/超时重试；MCP须确认当前实例等价设置，不能确认时报告限制并只做本地工作，不改全局配置。已有 transport 优先：`scholarqa-cli` 负责无模型的 collect/verify，当前 agent 负责主张账本与综合；也可用用户已有 MCP 的同名操作，不重复查两遍。

1. 将问题拆成可回答的子问题，记录日期、范围、关键词、过滤条件与包含/排除规则；聚焦回答用少量互补查询，系统综述还需要明确多数据库与筛选协议。
2. 用 collect 或 MCP 检索全文 snippets 与摘要，再查重要种子引用、被引或推荐以填具体缺口。深入、分页或图谱检索读 [retrieval](references/retrieval.md)。保留 raw JSON、search_queries、query_runs、snippet 原文、candidate_paper_ids 和 operation_errors。
3. 去重先按 S2 ID，再 DOI/arXiv 和标题；同论文多版仍是同源。候选选择按直接相关、证据可用程度、研究方法与冲突覆盖，引用数不是正确性。
4. 写主张账本再写正文，读 [reporting](references/reporting.md)。A 明确全文段落，B 摘要，C 元数据，D 图谱推断；来源不明 snippet 不能自动 A。每项记录支持/反证/不确定、source_id、source_hash、来源组与候选定位。区分发现、解释、建议和假设。
5. 围绕问题综合，保留矛盾与范围限制。缺文本支持就删除或限定该主张。外部回收片段尚未定位 L0，不写为 exact quote 或正式 EU。
6. 对最终引用 verify / batch_get，核对标题、作者、年份、稳定 ID；查 unresolved_ids、resolved 以及各错误渠道。**书目身份验证不证明主张支持**，再次对照账本与原文。
7. 报告检索日期、范围、A/B/C/D、局限、重要冲突与待 L0 回查点。collect exit 1 可为有效 partial，须展示 operation_errors；verify exit 1 也可能 unresolved 或顶层 error。不能把所有 exit 1 当无结果，也不能当全部成功。

Scideator 模式：研究构想读 [workflow](references/scideator-workflow.md)、[prompts](references/scideator-prompts.md) 与 retrieval；新颖性判断再读 [novelty examples](references/scideator-novelty-examples.md)。保留 purpose/mechanism/evaluation 的来源、距离与人类选择；新假设不当事实，只评估检索范围内的新颖性，不认证全球首次。

Snippet 不可用可回退摘要并说明 B 级；元数据冲突保留待查。runtime 缺失报告依赖，不安装或切收费 API。默认禁用SDK自动retry；已知限流/错误返回可在任务范围内规划有界后续查询，未知远端结果继续观察原调用，不重试。L0 不覆盖，source_id 由外部传入，不写 Registry、不造 P ID；两个 Dog 借共享库交接，不直接通信。
