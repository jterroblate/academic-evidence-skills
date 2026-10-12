# 安装与使用

## 自然语言调用

- “使用 $academic-scholarqa 帮我回答这个研究问题，保留支持、反证和每项主张的出处。”
- “使用 $academic-scholarqa 审查这组引用；请把论文身份是否有效与结论是否被原文支持分开。”
- “使用 $academic-scholarqa 基于这些种子论文提出研究方向，标明原论文发现与新假设。”

## CLI 运行环境

两项社区技能共用一个上游 Python 包，技能文件本身不安装 runtime。Python >=3.10；固定 commit 的依赖为 `httpx>=0.27.0,<1.0.0` 和 `mcp>=1.28.1,<2.0.0`。已有可用 runtime 优先复用；依赖缺失且本次任务需要执行时，在指定隔离环境安装；既有任务授权有效，不重复询问。示例：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install "git+https://github.com/XWang20/semanticscholar-MCP-Server.git@5139c045365244b6940e9fb6e4df62e6a302d0e5"
.venv/bin/semanticscholar-cli --version
.venv/bin/scholarqa-cli --version
```

API key 可选；部分接口匿名可用且限流重，不保证所有端点可用。key 仅沿用环境变量 `SEMANTIC_SCHOLAR_API_KEY`，不填进参数文件、结果或包。本工具集不依赖第二个模型 API；由当前宿主 agent 综合内容。固定来源见 [UPSTREAM.json](../UPSTREAM.json)；未在本包中捆绑 runtime 或依赖。

## 输入与命令

输入是明确的问题/子问题、日期/领域/人群等范围、可选种子论文 ID；若要接现有资料库，再传调用方的 source_id/source_family 与原 PDF SHA256 映射。没有该映射只输出检索候选。

先离线检查帮助；只有本次任务已授权远端学术检索才执行 collect 和 verify。示例 query 仅为演示：

```bash
.venv/bin/scholarqa-cli collect --help
.venv/bin/scholarqa-cli verify --help
SEMANTIC_SCHOLAR_MAX_RETRIES=0 .venv/bin/scholarqa-cli collect "How do agents synthesize literature?" \
  --query "agent literature synthesis" --query "scholarly question answering" \
  --paper-limit 5 --snippet-limit 5 > collect.raw.json
# 在 shell 中马上记录 status=$?；保留 collect.raw.json，即使 status=1。
SEMANTIC_SCHOLAR_MAX_RETRIES=0 .venv/bin/scholarqa-cli verify --ids-file selected-ids.json > identity.raw.json
```

selected-ids.json 是字符串数组或逐行 ID 文件；ID 支持 S2/DOI/arXiv 等，DOI: 前缀示例只是身份查询。禁止虚构 DOI。

离线审查已有输出：

```bash
python3 scripts/inspect_bundle.py collect.raw.json --exit-code 1 > collect-inspection.json
```

该脚本不请求 API、不生成答案；退出码与 JSON 错误分开检查，输出原始文件 SHA256 和候选状态。用于验证 fixture 或已有真实结果。

## 输出与限制

保留上游 bundle 原样，不用摘要覆盖；claim ledger、回答和来源映射是可重建 L1。collect 正常返回 schema_version、search_queries、filters、query_runs、candidate_paper_ids、operation_errors；verify 返回 items/resolved 与 unresolved_ids，只代表书目身份。verify 若 API 错误可能仅顶层 error，没有 operation_errors，必须显示它。

exit 0=本次成功；collect exit 1=partial；verify exit 1=未解决ID或API错误；exit 2=输入/本地错误。A/B/C/D 与 L0 exact quote 规则见 [候选契约](evidence-contract.md)。元数据不能支持研究结论，摘要不能冒充全文；同源多版不能算独立证据。没有完整筛选协议不称穷尽或系统综述。此包已做本地mock/静态测试，未执行真实 Semantic Scholar collection，也未认证所有 MCP 或API端点可用。

## 本次调用的重试设置

固定上游SDK会默认对HTTP429/5xx及TransportError/超时自动重试3次；本适配器将每次网络CLI调用的 `SEMANTIC_SCHOLAR_MAX_RETRIES=0` 作为必设进程环境，防止未知结果被自动重试。示例为POSIX；Windows PowerShell用当前会话/子进程对应环境设置并在调用后恢复原值，不写全局配置。已有runtime仍需此次调用使用0。

若使用已有MCP，必须能确认当前server进程已用同一环境值0（或等价禁retry配置）；没有确认时只完成本地计划/结果审查，并报告transport不满足此边界，不执行远端查询。不能为此偷偷更改全局MCP配置。明确返回的限流/错误可以在已有任务范围内另行计划有界后续查询；超时、断链等未知远端结果保存状态，观察原调用，不自动重跑。
