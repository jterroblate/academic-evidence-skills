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

4.0.12 实际运行过的 SDK 本地保存方式（只在已有且模型就绪的对应环境中；质量档由既定选择决定）：

```python
from mineru.parser import MinerUParser
from mineru.parser.writer import FileBasedDataWriter
parser = MinerUParser(tier="basic", parse_mode="auto")
result = parser.parse("/path/to/staging/new-run/source.pdf", page_range="all")
result.save(FileBasedDataWriter("/path/to/staging/new-run/raw/native"))
```

该版本本次采用 basic/ONNX/CPU、4线程，LLM辅助和远程VLM关闭，在隔离模型/配置目录中运行。模型下载与推理分开；推理阶段按本地模型执行。这个简短片段不代替环境配置检查，也不保证当前宿主已经隔离或离线。`ParseResult.save` 外置图像后，`native/markdown.md` 应有真实相对图像链接；不要把仍有 `data:image` 的 `result.markdown()` 当作可交付的本地链接版。保留原始响应，修正本地导出另存版本，无须重跑模型。

派生逐页输入时从已物化的 `middle_json.json` 导出，保留 `page_idx+1` 与原生块，并检查资产引用。只有单页结果时可以直接用对应 `native/markdown.md`；不能凭标题或平均字数拆分全文。与 `pdf-to-markdown` 接线时启用 `--require-latex` 并另运行基本数学检查；原始PNG截图/公式区域数量均不证明数学正确。

已有真实producer运行记录（含 `source_sha256`、`engine.name/version`、`actual_pages`）时，本包提供一个不启动推理/模型下载的页级适配器：

```bash
python /path/to/academic-mineru/scripts/export_pages.py /path/to/raw/native \
  --source /path/to/source.pdf --run-record /path/to/existing-run.json \
  --output /path/to/new-parser-pages.json
python /path/to/pdf-to-markdown/scripts/convert.py /path/to/source.pdf \
  --parser-pages /path/to/new-parser-pages.json --assets /path/to/raw/native \
  --pages 3 --require-latex --output /path/to/new-page3-bundle
```

`--pages 3` 只是单页示例，必须换成实际处理范围；已有全篇输入则不缩成示例页。适配器使用已有MinerU4 SDK反序列化，不包含SDK/模型；拒绝覆盖、源哈希不一致、页记录不匹配或仍嵌入Base64的结果。它核对的是运行记录与源文件的一致性，不证明无签名运行记录的真实性，也不能凭空给缺少绑定信息的旧产物补证。输出位置在原生目录外，`--assets`仍指向原素材；正式转换包会独立验证并复制图像资产。

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

2026-10-21已在隔离环境真实运行 MinerU 4.0.12、basic/ONNX/CPU 的5篇代表页，另外进行单篇全文与重复运行回归，具体范围以合集本轮报告为准。未调用云解析或上传论文；不把样本表现推广成103页公式全检。实测仍有漏星号、字母大小写误读、化学能级多余指数和阅读顺序问题，候选须回源页核对。旧版本的静态核查记录保留为历史，不代表本轮测试覆盖了全部SDK/CLI或所有质量档。
