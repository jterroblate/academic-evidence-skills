# 固定版本API依据

依据 commit `57e89f7223b0960d5ee5ea048c69e3c47e088572`（2026-10-12取得）的 [README](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/README.md)、[Docs API](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/src/paperqa/docs.py)、[Settings](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/src/paperqa/settings.py)、[types](https://github.com/Future-House/paper-qa/blob/57e89f7223b0960d5ee5ea048c69e3c47e088572/src/paperqa/types.py)。

- 包名 `paper-qa`，导入 `paperqa`，CLI `pqa`；Python >=3.11。上游main是活跃源码，不等于已发布稳定版本。
- `Docs.aadd(path, citation=None, docname=None, dockey=None, title=None, doi=None, authors=None, settings=None, ...)`；`Docs.aquery(query, settings=None, ...)` 返回 `PQASession`。同步包装为 add/query，async版更适合脚本。
- `Settings` 支持 llm、llm_config、summary_llm、summary_llm_config、embedding、embedding_config、parsing等；llm_config使用LiteLLM router model_list。
- `parsing.use_doc_details` 默认true、multimodal默认enrichment。本适配器强制false并传citation，避免自动书目推断、metadata providers、媒体enrichment的额外渠道。embedding与summary仍可能模型调用。
- session.answer/formatted_answer是AI派生文字；session.contexts中 context是AI摘要，text是解析片段；内部chunk/引用不能替代L0 exact quote和物理页校验。通过ctx.text.doc.docname对接传入source_id；不把库内部MD5升级成SHA256。
- 本包测试plan/doctor与模拟API控制流，不调用真实backend。不同LiteLLM/provider版本可能有模型名/config差异，应读本地已安装版本schema与供应商文档后更新配置，不凭doctor输出认证可用性。

## 重试保证的边界

`retry_allowed:false` 是本适配器不重复 `aquery` 的策略，不代表所有库、SDK、provider都已禁retry。固定Settings显示llm_config/summary_llm_config可传router_kwargs，但不同后端的retry/timeout/JSON修复可能处在不同层；不能凭此提供通用且已实测的retry=0配置。doctor不探测内部retry。运行前按目标工程实际库版本核对所有启用层，未知远端结果不自动重跑；不能确认就先停在plan，不声称全链路保证。
