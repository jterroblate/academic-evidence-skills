# 使用说明 · 学术综述与证据整理

## 自然语言调用

“用 $academic-literature-review 作为 Review Dog 整理给定 shared evidence 快照和搜索原响应；按研究族综合正反结果，找竞争解释，摘要级来源单列，缺原PDF定位的结论保持needs_review。”

## 依赖与命令

Python 3.11+；`search_databases.py`仅标准库；`verify_citations.py`需要requests（按需在隔离环境 `python3 -m pip install requests`）；PDF导出另需本地pandoc、xelatex及字体/TeX包、用户选定本地CSL。导出是可选步骤，不自动安装或换云后端。无图像服务依赖。

```bash
python3 scripts/search_databases.py normalized-records.json --deduplicate --format markdown --output screened-records.md --summary
python3 scripts/verify_citations.py review.md --offline --output doi-candidates.json
python3 scripts/generate_pdf.py --help
python3 scripts/generate_pdf.py --check-deps
```

当本轮授权联网核对DOI时：

```bash
python3 scripts/verify_citations.py review.md --raw-dir raw-citations --output registration-report.json
```

有本地依赖后可导出：

```bash
python3 scripts/generate_pdf.py review.md --output review.pdf --bibliography references.bib --csl local-style.csl
```

## 输入与输出

输入 normalized JSON array（raw API envelope必须先另存，再显式转换）、既有共享证据快照、筛选/版本组、review.md和bibliography。search输出是派生JSON/Markdown/BibTeX，原始raw不覆盖；deduplicate按规范化DOI或缺DOI标题先留第一条，是记录层启发式，不能确定同研究或独立性。

DOI report 的 `registered_dois` = 注册身份已查到；`claim_support_verified=false`、`l0_quote_verified=false`。offline模式只有 `doi_candidates` 且 `registration_checked=false`；未取到元数据与HTTP失败单独报告，不能将inconclusive当不存在/反证。raw-dir必须新建，保留每个HTTP entity body及SHA256和脱敏请求；若秘密回显则仅哈希/省略理由，记录缺口。已有报告路径拒绝覆盖。

`generate_pdf`在调用依赖/渲染程序前拒绝任何既有或symlink输出路径，每次选新的派生PDF路径。它不会重新取证，只用Pandoc渲染用户指定稿件与本地CSL；引用键缺失/TeX问题照实报告。主张支持、表格准确性、原PDF忠实和统计有效性仍需独立阅读；不要用PDF成功、DOI命中或结构检查退出0给科学结论认证。

## 实际任务示例与限制

先用保存的两条normalized记录跑数据处理，再将preprint与journal source_family关联、记录筛选理由。综述写“在已检索范围内未找到反例”，附数据库/查询/日期/停止条件；不能写“没有反例”或“证据已完全覆盖”。没有原PDF的摘要段不填假的物理页，保持needs_review。

指南与数据库资料为上游固定提交快照，当前专业规则当次核查。没有朋友Gateway/Registry/EU schema，技能不会创建正式条目或科学坐标。Markdown模板本身不是研究证据。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。
