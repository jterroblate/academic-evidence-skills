# 使用 academic-mineru

## 调用与依赖

用户可以说：`使用 $academic-mineru，把已选论文用现有本地 MinerU 转成 document.md，保留原始 JSON 和出处。`

宿主需能读写文件并调用已有 CLI 或 Python。固定上游 commit 对应 MinerU 4.0 契约；支持 Python `>=3.10,<3.15`，已有环境应满足 `mineru>=4.0,<5`。先检查，不执行安装：

```bash
command -v mineru
command -v mineru-kit
mineru version --json
mineru parse --help
mineru-kit parse --help
```

3.x 常见的 `mineru -p ... -o ...` 不是这里的 4.x 命令；不能混用。版本不符或未知时报告实际情况。可给管理员候选安装步骤，但只有已有授权覆盖安装/模型下载时才执行；不全局安装。

必要执行沿用已获授权，不重复询问。任务必需的轻量依赖可在既有授权范围内隔离安装，不改全局环境；模型下载、替换或远端渠道变更按实际授权与已选渠道执行，缺口明确报告。

## 输入与 staging

输入：已授权本地 PDF、既定渠道/质量档、物理页范围和目标 staging。未知参数在日志留空，不从惯例推断。目标目录必须全新，不用 `mkdir -p` 掩盖已存在 run。例子中 `/path/to/...` 是待替换占位路径；先复制原件为 `source.pdf` 并保留原件，使用 SHA256 比对；原件不做重编码、清洗、裁剪或标注。

```bash
TASK_STAGE="/path/to/staging/new-run"
mkdir "$TASK_STAGE"
mkdir "$TASK_STAGE/raw" "$TASK_STAGE/logs"
cp "/path/to/authorized-paper.pdf" "$TASK_STAGE/source.pdf"
```

对源与副本计算完整 SHA256（例如 Python `hashlib.sha256`），保存 `source_hash`、字节数、取得时间和授权来源。只读文件权限是辅助措施，不能代替哈希复核。

## 一次完整原生输出

下面使用已经配置好的本地 standard；若用户已有其他质量档选择，用该已选档并记录，不擅自换模型。不得添加 `--remote`、`--remote-url` 或 `--api-key`。

```bash
mineru-kit parse "$TASK_STAGE/source.pdf" --pages all --tier standard --format zip --output "$TASK_STAGE/raw/source.zip" > "$TASK_STAGE/logs/parser.stdout" 2> "$TASK_STAGE/logs/parser.stderr"
```

也可用明确的 `--pages 1-5`。`mineru-kit parse` 默认 all，普通 `mineru parse` 默认首个 10 页窗口；不要把窗口误报为整篇。ZIP 包经可信路径检查后解入新的 `raw/native/`；拒绝绝对路径、`..`、符号链接，不覆盖源文件。保留 ZIP 与解出的 `markdown.md`、`middle_json.json`、`structured_content.json`、`images/`、存在时的 `model_output.json`。复制原生 Markdown 为 `document.md`；若调整图像相对链接，保留原生版本并记录每项调整。`ParseResult.to_json()` 单文件可能省略图像，不能宣称它是完整包。

SDK 的等价本地保存方式（只在已有对应环境中）：

```python
from mineru.parser import parse
from mineru.parser.writer import FileBasedDataWriter
result = parse("/path/to/staging/new-run/source.pdf", tier="standard", page_range="all")
result.save(FileBasedDataWriter("/path/to/staging/new-run/raw/native"))
```

若仅使用既有文档库阅读，可以保存：

```bash
mineru parse "$TASK_STAGE/source.pdf" --pages 1-5 --json > "$TASK_STAGE/raw/cli-response.json"
mineru read "doc:ab12cd3/tier:standard/page:4/block:7" --json > "$TASK_STAGE/raw/read-response.json"
```

上述 locator 只是形状例子；必须换成真实返回，不照抄。`parse --json` 是状态/内容/continuation，不是 MiddleJson，也不能保证图像和模型原始输出齐全。只有此入口时，明确记录“原生包尚未导出”，不能声称留存要求已满足。首次 `parse` 会更新 MinerU 本地文档库/缓存；本任务的解析产物仍只进入 staging，不能误当 Registry 档案。

## 输出契约与检查

建议 staging 中留：`source.pdf`、`document.md`、`raw/`、`logs/`、`provenance.json`、`review-needed.md`。后者记录漏页、阅读顺序、表格/公式/OCR 疑点；没有疑点也记录检查范围，不能声称自动校验 quote。

`provenance.json` 至少含 engine、实际 producer/version、依赖与模型标识（未知 null）、完整命令/参数（去凭据）、local/remote、requested_pages、processed_pages、total_physical_pages、未处理页/失败状态、完整 `source_hash` 和各输出文件 SHA256。以原生 `metadata.producer.version` 与 `extensions.mineru` 核对实际解析方式，不把代码 commit 当运行时版本。

locator 派生记录示例（所有值必须来自当前实际结果）：

```json
{
  "source_hash": "sha256:<64-hex-actual-source-digest>",
  "physical_page": 4,
  "printed_page": null,
  "page_span": [4, 5],
  "native_page_idx": 3,
  "native_locator": "doc:<actual-id>/tier:<actual-tier>/page:4/block:<actual-block>",
  "bbox": null,
  "bbox_coordinate_system": null,
  "quote_status": "unverified_transcription"
}
```

缺 bbox 保持 null 并注明原生未提供。bbox 存在时原样保存及原点/单位/页尺寸；不同入口 locator 的 short id 不能代替 SHA256。印刷页只能经实际页面标签核对，不能从页码偏移自动猜测。

等待超时不等于失败或取消；保存 parse/task ID，使用 `mineru show parse <实际ID> --json` 或 `mineru show file <实际文件> --json` 查看原状态。不要沿用上游“重新运行相同 parse 继续等”的笼统建议去重提未知远端任务。

## 许可与验证边界

MinerU LICENSE 是 Apache 基础条款加额外商业阈值、服务标识及终止条款，不能标成纯 Apache。模型/第三方依赖另有许可，本包不包含模型。

此包完成固定源码与命令签名核查；未安装/执行 MinerU，未用真实 PDF 解析，未调用云 API，也未验证 OCR/公式精度。使用时以本机 `--help` 和实际输出为准，升级后应重新核对契约。
