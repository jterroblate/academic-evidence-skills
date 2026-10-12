# 使用 academic-docling

## 调用与依赖

用户可以说：`使用 $academic-docling，沿用已有本地 pipeline，将这篇 PDF 转成 document.md，保留原生 JSON、bbox 和源文件 SHA256。`

需已有 Python `>=3.10` 的 Docling CLI/SDK。固定 commit 的 pyproject 版本是 `2.137.0`，不是对朋友已安装版本的断言。Docling 代码 MIT，具体 OCR/VLM/表结构模型有独立许可；本包不包含模型。检查：

```bash
command -v docling
docling --version
docling --help
```

CLI 来自 `docling`，或 `docling-slim[cli,...]` 中的 CLI extra。不要将 `uvx` 误写成“无需下载”——它仍可下载运行时依赖与模型。依赖缺失时说明需要什么；只在已授权的独立环境安装，不改全局环境。

必要执行沿用已获授权，不重复询问。任务必需的轻量依赖可在既有授权范围内隔离安装，不改全局环境；模型下载、替换或远端渠道变更按实际授权与已选渠道执行，缺口明确报告。

## 输入与命令

输入已授权本地 PDF、现有 pipeline/模型设置、实际页范围和全新 staging。先复制原件为 `source.pdf`，对源与副本计算完整 SHA256。示例路径需替换：

```bash
TASK_STAGE="/path/to/staging/new-run"
mkdir "$TASK_STAGE"
mkdir "$TASK_STAGE/raw" "$TASK_STAGE/logs"
cp "/path/to/authorized-paper.pdf" "$TASK_STAGE/source.pdf"
docling "$TASK_STAGE/source.pdf" --from pdf --to md --to json --output "$TASK_STAGE/raw" > "$TASK_STAGE/logs/parser.stdout" 2> "$TASK_STAGE/logs/parser.stderr"
```

这是已有默认本地 pipeline 示例，可能使用/下载模型；执行前确认模型已存在并沿用配置。不加 `--enable-remote-services`、不运行 `convert-remote`。需指定既有模型目录可加 `--artifacts-path /path/to/existing-models`；该参数本身不是禁止所有网络的保证，还需确认 OCR/VLM 和依赖已就绪。只处理某段可加 `--page-range 1-4`，该范围从 1 开始，必须在元数据标为部分覆盖。

若用户已选的是 native PDF pipeline，可沿用：

```bash
docling "$TASK_STAGE/source.pdf" --from pdf --pipeline native --to md --to json --output "$TASK_STAGE/raw"
```

native 不运行模型，提取 PDF 原有文字/图像；没有标准 pipeline 的阅读顺序、标题和表结构，扫描件可能近空。不能因为示例无需模型就擅自将既定 standard/VLM 替换为 native。

CLI 文件按输入 basename：上述输入产 `raw/source.md` 与 `raw/source.json`。原样保留，然后复制 `source.md` 为 `document.md`。保留生成的图片路径；调整链接需另存派生文件、记录改动，不改原始导出。CLI 是否保留 page images、parsed pages、VLM debug 内容取决于参数；没有生成就标为未生成，不能从 JSON 名称推断“所有原始输出均齐全”。

## SDK 可控保存

需要原始 pipeline options、status/errors 与 provenance 时，使用已有 SDK。下面为已有 standard pipeline 的模式，模型/依赖必须先确认在本地，不执行安装：

```python
import json
from pathlib import Path
from importlib.metadata import version
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

stage = Path("/path/to/staging/new-run")
options = PdfPipelineOptions(enable_remote_services=False)
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=options)
})
result = converter.convert(stage / "source.pdf", raises_on_error=False)
(stage / "raw" / "docling-document.json").write_text(
    json.dumps(result.document.export_to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
(stage / "raw" / "docling-original.md").write_text(
    result.document.export_to_markdown(), encoding="utf-8")
(stage / "raw" / "pipeline-options.json").write_text(
    options.model_dump_json(indent=2), encoding="utf-8")
print(result.status, result.errors, version("docling"), version("docling-core"))
```

这个片段是调用示例，未进行真实 PDF 运行；打印内容还应落入去凭据后的日志。若使用 VLM，`debug_vlm_native_output` 相关 CLI/SDK 调试能力可保存逐页原始模型响应；只在当前 pipeline 已选并支持时启用，不能因此切换模型。图片输出需明确设置 `generate_page_images` / `generate_picture_images` 并使用 referenced 或 embedded 导出；原生 JSON 及 assets 一并留存。

## 输出与页坐标

建议 staging：`source.pdf`、`document.md`、`raw/`、`logs/`、`provenance.json`、`review-needed.md`。记录 source SHA256 与文件大小、引擎/包/模型版本、实际参数、local/remote、转换 status/errors、requested_pages、processed_pages、total_physical_pages、遗漏页和各原生输出 SHA256。不要用 `len(document.pages)` 自动证明完整覆盖；逐页核对请求范围、原生 page 记录与原 PDF 总页数。

Docling item 的 `prov` 中有 page_no、bbox、charspan 等原生定位；逐项保留。bbox 保存原始 l/t/r/b、`coord_origin` 和页面尺寸；坐标若须转换另记映射，不能静默反转原点。由 JSON 有 `prov` 的条目派生页段，跨页 item 保留所有 provenance。印刷页未知用 null。

```json
{
  "source_hash": "sha256:<64-hex-actual-source-digest>",
  "physical_page": 1,
  "printed_page": null,
  "page_span": [1, 1],
  "native_provenance": [],
  "bbox": null,
  "bbox_coordinate_system": null,
  "quote_status": "unverified_transcription"
}
```

这是字段形状，空数组/null 表示尚未提取，不代表原文件没有定位。保留 Docling origin 字段，但独立计算 SHA256，不能假定 `origin.binary_hash` 使用相同算法。表格/公式/多栏顺序、乱码、重复行和低覆盖页列为待回看原 PDF；OCR 修正作为派生保留，不直接覆盖原始文本。

## 局限和恢复

JSON 保留结构不代表内容无误；正文、数学符号、表格和页覆盖需要真实材料复核。自动建议换 VLM/OCR 不能自动执行：先报告当前错误和已授权恢复选项。模型缺失、网络不通、部分成功分别记录；未确认远端结果不重提。

本包仅固定源码、资源哈希及命令签名核查；未安装 Docling/模型、未转换真实 PDF、未调用云服务。上游六份参考保存在 `references/upstream/*.txt`，其中服务/安装示例是隔离资料；执行只按本入口与当前明确授权。
