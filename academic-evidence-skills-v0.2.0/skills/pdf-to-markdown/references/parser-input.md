# 接入已有解析结果

这个格式是本次 AI 工程方案，不是朋友原工程已经确认的 schema。它让已有后端和本地后端交付同一类可检查材料；不能替代后端自己的布局 JSON。

`--parser-pages` 接收 UTF-8 JSON：

```json
{
  "engine": {
    "name": "mineru",
    "version": "记录实际版本",
    "parameters": {"deployment": "local"}
  },
  "provenance": "existing-parser-output-for-this-source-pdf",
  "derivation": "parser_raw",
  "source_sha256": "原始PDF完整64位SHA-256",
  "pages": [
    {"page_number": 1, "markdown": "第一物理页的原始解析文本"},
    {"page_number": 2, "markdown": "第二物理页的原始解析文本"}
  ]
}
```

顶层 `provenance` 声明原始解析来源，`derivation` 声明正文加工方式：未进一步清洗的解析结果写 `parser_raw`，OCR/LLM 修正写其实际方式，未知写 `unknown`。使用 `engine.parameters` 记录本地/云端、模型版本、OCR 与提示版本；不要放 token 或认证配置。缺少来源/加工声明会降为 `needs_review`。这些是解析方声明，脚本不独立验真。不把文件修改时间当作引擎版本。

页号指输入原 PDF 的物理页，从 1 起算。MinerU `page_idx=0` 适配为 `page_number=1`；分片结果还要加原文页偏移。Docling 使用原文 `page_no`，先核对它与本次输入 PDF 一致。不要凭标题、字符数或段落序号猜页号。输入页重复、越界或源哈希不匹配应拒绝；遗漏页应报告，不能补造正文。

图片目录通过 `--assets` 指定。将解析后的相对图片引用保持在该目录内；复制时不允许通过 `..` 或软链接引入目录外文件。保留后端完整输出作为旁路档案，但不要把 API key、凭据或调用认证日志放入产物包。缺图、目录外引用或不能解析的引用会明确失败，不会交付为图文完整。

上游只有整篇 Markdown 时，先交付并说明缺少页映射；不能伪造这个 JSON。上游正文已经被模型改写时，保存未清洗版本作为核验材料；没有未清洗版本就降低证据用途并回到 PDF 核对。

可选 `--metadata` 接收对象：

```json
{
  "title": null,
  "authors": null,
  "year": null,
  "journal": null,
  "doi": null,
  "zotero_key": null,
  "source_id": null
}
```

只有从用户或既有入口取得的值才填入；保留来源说明。`authors` 填作者名列表，`year` 为已有整数或字符串，其余非空字段为字符串；不要添加合同外字段。`source_id` 透传已有身份，不由转换脚本分配。此处的 metadata 也不是论文真实性校验。
