# 使用说明 · 学术论文发现与溯源

## 自然语言调用

“用 $academic-paper-lookup 在 Europe PMC 检索 2023–2026 年 organoid 的方法研究，最多 100 条；保留每页原始响应，列出预印本/期刊版的来源族候选，不作 EU 入库。”

## 依赖与命令

Python 3.11+，全部脚本仅标准库。离线验证不访问接口；联网检索的条款、配额与可用性需当次核查。用户级环境变量可选，具体接口见各数据库参考；不把密钥传到文件。

从本技能目录运行：

```bash
python3 scripts/paginate.py --help
python3 scripts/paginate.py --list-apis
python3 scripts/paginate.py --api europepmc --query 'organoid' --max-records 100 --dry-run
python3 scripts/arxiv_atom.py response.xml --output arxiv-records.json
python3 scripts/jats_to_text.py article.xml --sections METHODS,RESULTS
python3 scripts/openalex_abstract.py openalex-response.json
```

授权联网时才运行（`raw-responses` 的父目录须存在，该目录须为新目录）：

```bash
python3 scripts/paginate.py --api europepmc --query 'organoid' --max-records 100 --max-calls 5 --raw-dir raw-responses --output records.json
```

## 输入与输出

`paginate` 输入数据库/查询/上限，输出 `records`、脱敏 `provenance` 与 `reconciliation`；每页保存 `response-NNNN.bin` 和 JSON（时间、HTTP 状态、原始响应 SHA-256）。JSON 解析失败或 HTTP 错误仍先留响应。若响应回显请求秘密/联系信息，保存哈希和省略理由而不保存该原文，停止解释；报告审计缺口，不能重新尝试掩盖它。

解析脚本输入 UTF-8 XML/JSON，输出 sectioned text 或 normalized records。保留原文件；解析结果不替换 raw response。`--dry-run`、`--list-apis` 可离线；分页退出 4 表示数量对不上，退出 0 仍可能显式截断，检查 reconciliation。JATS 退出 2 只得元数据；arXiv 退出 3 是错误 feed、5 是限流。

API 原始全文通常是 HTML/JATS，只有取得原 PDF 后才能填写物理页与 bbox/segment。摘要重建不能证明原文引用。检索计数按记录/版本而非独立研究；来源族关系须另读原材料确认。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。
