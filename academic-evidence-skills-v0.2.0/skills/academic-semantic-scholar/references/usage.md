# 安装与使用

## 自然语言调用

- “使用 $academic-semantic-scholar 查这篇论文的准确记录，然后看它引用了哪些论文。”
- “使用 $academic-semantic-scholar 在这个主题下查五篇候选，保留原始 JSON；先不要把推荐当事实。”

## CLI 运行环境

两项社区技能共用一个上游 Python 包，技能文件本身不安装 runtime。Python >=3.10；固定 commit 的依赖为 `httpx>=0.27.0,<1.0.0` 和 `mcp>=1.28.1,<2.0.0`。已有可用 runtime 优先复用；依赖缺失且本次任务需要执行时，在指定隔离环境安装；既有任务授权有效，不重复询问。示例：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install "git+https://github.com/XWang20/semanticscholar-MCP-Server.git@5139c045365244b6940e9fb6e4df62e6a302d0e5"
.venv/bin/semanticscholar-cli --version
.venv/bin/scholarqa-cli --version
```

API key 可选；部分接口匿名可用且限流重，不保证所有端点可用。key 仅沿用环境变量 `SEMANTIC_SCHOLAR_API_KEY`，不填进参数文件、结果或包。本工具集不依赖第二个模型 API；由当前宿主 agent 综合内容。固定来源见 [UPSTREAM.json](../UPSTREAM.json)；未在本包中捆绑 runtime 或依赖。

## 输入与可执行命令

输入：问题、已知真实标题/论文ID或作者ID、所需字段、数量、查询范围。接资料库时另外传 source_id/source_family/SHA256；API 的 S2 paperId 与库 source_id 是不同字段，不互相替换。

离线 tools/schema 不消费学术API额度；以下 call 是远端查询，只有任务已授权才执行。

```bash
.venv/bin/semanticscholar-cli tools > tools.json
.venv/bin/semanticscholar-cli schema search_semantic_scholar_papers > search-schema.json
SEMANTIC_SCHOLAR_MAX_RETRIES=0 .venv/bin/semanticscholar-cli call search_semantic_scholar_papers \
  --params '{"query":"retrieval augmented generation","limit":5}' > search.raw.json
# 复杂参数：--params-file input.json；stdin：--params -。
.venv/bin/semanticscholar-cli schema get_semantic_scholar_paper_references
```

根据真实schema建 params，不照搬没有验证的字段。限额与当前数据库覆盖以真实返回为准；不把示例query当已执行记录。

## 输出与限制

原生 JSON 形状保留，包括 paperId/externalIds、data、offset/token、错误；另存执行时间、runtime版本、请求输入与 claim-support 候选映射。退出码0成功、1顶层API error、2CLI/schema error。CLI缺失就 dependency-blocked；MCP若可用以同名操作替代，不能假造工具。

论文身份、DOI可解析、citation graph与recommendations仅是导航，不证明正文支持，也不构成 exact quote 或正式EU。全文和摘要另分Tier A/B，元数据与图谱为C/D。完整证据边界见 [契约](evidence-contract.md)。数据集链接不自动下载整库；分页显式、有界，检索不称穷尽。本包只实跑离线schema和mock测试，未进行真实远端call。

## 本次调用的重试设置

固定上游SDK会默认对HTTP429/5xx及TransportError/超时自动重试3次；本适配器将每次网络CLI调用的 `SEMANTIC_SCHOLAR_MAX_RETRIES=0` 作为必设进程环境，防止未知结果被自动重试。示例为POSIX；Windows PowerShell用当前会话/子进程对应环境设置并在调用后恢复原值，不写全局配置。已有runtime仍需此次调用使用0。

若使用已有MCP，必须能确认当前server进程已用同一环境值0（或等价禁retry配置）；没有确认时只完成本地计划/结果审查，并报告transport不满足此边界，不执行远端查询。不能为此偷偷更改全局MCP配置。明确返回的限流/错误可以在已有任务范围内另行计划有界后续查询；超时、断链等未知远端结果保存状态，观察原调用，不自动重跑。
