# 使用说明 · 学术批判性精读

## 自然语言调用

“用 $academic-critical-reading 精读 source.pdf 和 document.md。把实验结果、作者机制解释、你的推论分列；逐条保留原PDF物理页定位，重点找选择偏差、反例和可区分的竞争解释。”

## 依赖与可运行命令

无捆绑脚本、无强制网络/模型/PDF转换器依赖。需要宿主能查看用户指定 PDF/文本；扫描页或坏转写需可用 OCR/PDF工具，在没有工具时明确不可核验，不能编页码。以下仅计算原件指纹，可跨操作系统运行：

```bash
python3 -c 'import hashlib,pathlib; p=pathlib.Path("source.pdf"); print(hashlib.sha256(p.read_bytes()).hexdigest())'
```

哈希一致只证明所读文件字节身份，不证明解析忠实或科学结论正确。不要借此将 quote_verified 置 true。

## 输入与输出

输入：既有 source_id、原PDF及 SHA-256、L1转写与转写 manifest、任务问题和独立审阅角色。输出：方法摘要、研究局限、claim/quote候选表、对照/竞争解释和下一步核验清单。原文件不变，摘要可重建。

下列是格式示例而非真实论文证据（null表示尚未取得）：

```json
{
  "source_id": "existing-source-id",
  "source_family": null,
  "l0_sha256": null,
  "quote": null,
  "pdf_page": null,
  "bbox": null,
  "segment_id": null,
  "status": "needs_review",
  "observation": null,
  "author_interpretation": null,
  "ai_inference": null,
  "rival_hypothesis": "观测差异可能由测量漂移产生",
  "discriminating_test": "同批次校准参考与独立批次复测",
  "negative_control": "不能受假设机制影响但共享测量过程的参考量",
  "quote_verified": false,
  "l0_verified": false
}
```

核对原PDF后才能用真正逐字原文填quote；不得用这个合成例子、摘要或AI复述当 Evidence。bbox坐标单位/原点/页尺寸必须由实际PDF工具说明；segment须链接含相同hash和物理页的稳定转写片段。印刷页标签和Markdown行号可另外存，不能替代物理页。

## 限制

保留的英文方法参考是上游固定提交材料；适用的学科标准/医学证据/正式头衔和当前法规需要当次核查。方法讨论不授权外传全文或提供临床决定。未拿到真实PDF时只做文本层讨论并保留needs_review，不能称“完成L0核验”。

## 证据与权限边界

- L0 是不可变原始 PDF；接收既有 `source_id` 与 SHA-256，不修改或搬动原件。L1 转写、摘要、搜索、假设、推论与 graph 都是可重建派生资料，不是 Formal Evidence 或 EU。
- 候选引文保留一字不改的 `quote`、原始 PDF 物理 1-based 页号、`bbox` 或可回溯原始页的 `segment_id`、`l0_sha256` 与 `source_id`。缺任一定位就标 `candidate/needs_review`，不能从 Markdown 行号或印刷页码补造物理页。引文声明和结构通过都不证明真实忠实或 claim 支持。
- 归档 P ID、Registry 写入与晋升 Formal Evidence 由 Gateway 决定；本技能不分配它们、不评分 Utility、不造科学坐标代号。坐标理论尚无正式 schema，本包不宣称完整实现或兼容其接口。
- Scientist Dog 只产生候选假设；Review Dog 整理与挑战。两者通过有版本/哈希的 shared evidence 材料交换，不直接通信；生成者不能在同一轮自我认证。交付保留角色、AI 参与、日期与原材料快照。
- DOI resolve、BibTeX 校验与元数据命中不等于内容支持。同一研究、预印本/期刊版/修订版归为来源族，不能重复计为独立支持；未知元数据保留 `null`。原始查询/API 响应与筛选记录先保留，派生摘要不覆盖它们。
- 只处理用户指定的材料与输出位置。网络任务不额外授权收费 API、图像生成、全局配置、提交/push 或分享；密钥沿用环境变量，不能写入交付。
