---
name: academic-paperqa
description: 为已有本地PDF资料包生成 PaperQA2 问答计划、核查模型与embedding依赖，在用户明确配置并授权已有后端后运行可追溯问答。是可选Python库适配技能，不替代PDF逐字核验或正式证据单元。
---

# PaperQA2 可选库适配

本技能是 JT/AI 依据 FutureHouse `paper-qa` 固定版本 API 新编的适配器，不是上游现成 skill。库用 Apache-2.0、Python >=3.11；未捆绑全库、依赖或模型，不声称全部后端已实测。读 [usage](references/usage.md)、[候选契约](references/evidence-contract.md) 和 [API说明](references/api.md)。

1. 只接受调用方明确选择的本地已有 PDF bundle；每个 source_id/source_family 从外部传入，完整SHA256比对原件，只读不搬、不覆盖、不写Registry或造P编号。若用户明确要检索新论文，交给已授权的独立 collection workflow，回收并建好映射后再问答；本适配器不会扩展搜索。
2. 先运行 `scripts/paperqa_adapter.py plan`（离线），检查 question、PDF存在性/头部/SHA256与来源映射。它只输出可重建 L1 plan；没有模型库也可运行。
3. `doctor`检查Python、paperqa可导入、显式llm/summary_llm/embedding与后端声明。缺库或后端报告 blocked dependency；doctor不探测网络，所以通过也只表示配置可审阅，不等于后端已实测。当前宿主模型不能自动变成库 API 凭据。
4. 确有已配置的模型和embedding且任务授权调用才执行 query；命令需要 `--allow-model-calls`。优先已有渠道，不自动装库、拉模型、换供应商、云上传或新增付费API。库默认付费配置不可直接用；逐个显式指定模型。模型会接触文档内容，远端内容提交必须已有授权。
5. 通过 `Docs.aadd(... citation=调用方引用, docname=source_id, settings=...)` 添加本地PDF；禁用 use_doc_details 与 multimodal，避免隐式元数据外呼或媒体enrichment。`Docs.aquery`仍会调用embedding、summary_llm和llm，手动添加并不免模型费用。
6. 保存 `answer.derived.json`（AI-derived）、`citations.candidate.json`（source_id/hash、原片段候选、待L0定位）、run manifest分离。PaperQA内部MD5不是本契约SHA256；chunk名不是物理页，页码未知null。gather_evidence / summary / citations 都不等于正式EU；quote先null，回查L0原文与位置后才另出verifiedquote候选供正式schema审核。

引用身份与内容支持分开；推论、假设与事实分开；同源多版共用source_family。两个Dog只借共享库交接，不直接通信。query失败保留开始状态和已产生文件，适配器不重复调用aquery。它不能据此保证PaperQA/fhlmi/LiteLLM/provider内部没有重试或JSON修复；执行前部署者须核查当前后端未知结果不重跑，无法确认就只plan并报告限制，doctor未测试这部分。此技能仅输出候选契约，真正EU/Registry/坐标schema需要对齐原工程再接入。
