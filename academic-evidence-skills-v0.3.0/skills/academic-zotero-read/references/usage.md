# 使用 academic-zotero-read

## 调用与依赖

用户可以说：`使用 $academic-zotero-read，只读找出 Zotero 中关于某主题的论文，将指定附件与书目来源放入全新 staging。不要修改 Zotero。`

需已有 Python `>=3.10`、`zotero-mcp` 包提供的 `zotero-cli`。本地读取通常依赖运行中的 Zotero 桌面/local API 或既有 SQLite backend；web 读取用外部环境的 `ZOTERO_API_KEY`、`ZOTERO_LIBRARY_ID`、library type。沿用用户已选模式，不能默切云读取或新建配置。验证入口：

```bash
command -v zotero-cli
zotero-cli --help
zotero-cli --json-schema
zotero-cli --json config
```

`config` 默认混淆凭据，仍可能含个人路径/库身份；只用于运行时诊断，导出前去凭据和非必要隐私。禁止 `--show-secrets`。库可达性须实际读命令确认，不能从 config 成功推断。

必要执行沿用已获授权，不重复询问。任务必需的轻量依赖可在既有授权范围内隔离安装，不改全局环境；模型下载、替换或远端渠道变更按实际授权与已选渠道执行，缺口明确报告。

## 明确只读白名单

只许可下表中完全匹配的命令；表外包括“看起来是查询”的同名变体，需另行核验且本 skill 不扩大范围。所有数据读命令前加顶层 `--json`；不要放在第二级子命令后。

| 许可命令 | 许可选项/范围 |
| --- | --- |
| `search <query>` | 必须显式 `--mode advanced/tag/citekey/notes`；advanced 用 `--conditions` 字段条件，`--join-mode`/排序/`--limit`/`--detail`；tag 可指定 `--collection`；`--all-libraries` 仅在该模式支持且用户已授权相关库时 |
| `get metadata/fulltext/bibtex <key>` | metadata 可用 `--no-abstract`/`--output-format`；fulltext 可能触发本地提取或缓存，确认当前 backend 未越过既定渠道 |
| `get collections/tags/recent/libraries` | 已授权库；对应 `--limit`/`--collection` |
| `get collection-items <key>` | `--detail`/`--limit`/`--offset` |
| `get children <key>` | 可用 `--item-keys`，已授权条目 |
| `notes list` | `--item-key`/`--limit`/`--full`/`--raw-html` |
| `annotations list` | `--item-key`/`--limit`/`--format`；不自动用 `--pdf-extraction` |
| `outline <key>` | 原生 PDF 目录 |
| `read <key>` | `--start-page`/`--end-page`/`--find`/`--context`；`--format image --rect --out` 仅指定新 staging 中的图片输出目录 |
| `layout <attachment-key>` | `--pages` 的明确物理页段；输出 bbox 来源需记录 |
| `path <attachment-key>` | 只获得本地附件实际路径 |
| `export` | 已授权 `--item-keys` 或 `--collection`、`--style`/`--format`；重定向到新 staging，不写文库 |
| `config`、`--help`、`--json-schema` | 不加显示密钥选项；仅诊断/帮助 |

本白名单是 agent 行为边界，不是硬隔离 wrapper。如果宿主允许原始全部 CLI/MCP，仍需在 Gateway/工具路由实施相同白名单。现有包本身可以写文库；`toolsets=none` 保留 core 写工具，`ZOTERO_LOCAL_WRITE=false` 可以转向 web 写入，二者都不是只读开关。最小读权限和无写凭据有帮助，但不能用来替代命令约束。不修改用户已有凭据/授权。

## 可执行读取示例

```bash
zotero-cli --json search "attention" --mode advanced --conditions '[{"field":"title","operation":"contains","value":"attention"}]' --limit 10 --detail keys_only
zotero-cli --json get metadata ABCD1234
zotero-cli --json get children ABCD1234
zotero-cli --json outline ABCD1234
zotero-cli --json read ABCD1234 --start-page 3 --end-page 8
zotero-cli --json read ABCD1234 --find "robustness check"
zotero-cli --json path WXYZ5678
zotero-cli --json notes list --item-key ABCD1234 --full
zotero-cli --json annotations list --item-key ABCD1234 --format json
```

keys 是占位例子，必须来自真实返回，不能照抄。search 不包含全文，`--find` 返回匹配页及片段。`get fulltext` 是提取文本，不能代替完整 PDF 与原生解析存档。标准 JSON 输出为 `{"ok":true,"command":"...","schema":1,"data":...}`；错误为 `ok:false`。同时保存 stderr 与退出状态，不能忽略部分结果或截断提示。

固定源码中，默认 `search --mode items` 无命中时可级联语义搜索；`search --mode semantic` 会触发可能的后台索引同步；CLI `db status` 构造 semantic client，也可能初始化/重建集合或加载 embedding。因此这三个入口及省略 mode 的 search 都不在白名单。关键词用 advanced 的 title/creator 等字段条件，不称为模型语义检索。若另需语义功能，须由 Gateway 先提供经过验证、无自动同步/建索引/新embedding渠道的只读适配；本包不通过改配置或授权写入来开启它。上游 MCP `zotero_get_search_database_status` 有独立轻量读取实现，不能与同名用途的 CLI db status 混同，当前本包不假定宿主提供该工具。

## staging 与 L0

```bash
TASK_STAGE="/path/to/staging/new-run"
mkdir "$TASK_STAGE"
mkdir "$TASK_STAGE/raw" "$TASK_STAGE/logs" "$TASK_STAGE/images"
zotero-cli --json get metadata ABCD1234 > "$TASK_STAGE/raw/item-metadata.json" 2> "$TASK_STAGE/logs/metadata.stderr"
zotero-cli --json read ABCD1234 --start-page 3 --end-page 8 > "$TASK_STAGE/raw/page-read.json" 2> "$TASK_STAGE/logs/read.stderr"
zotero-cli --json read ABCD1234 --start-page 4 --format image --out "$TASK_STAGE/images"
```

需 L0 时先调用 `get children` 获得附件 key，再 `path` 获得实际本地 PDF。确认所选附件身份及授权，复制至 staging 的 `source.pdf`，计算原件/副本完整 SHA256 并核对。文件下载或未本地同步时报告缺口；不要自动 Zotero 同步、上传、attach 或启动写授权。

保留库身份、item key、attachment key、Zotero item 版本/修改时间（实际取得才写）、bibliographic DOI/URL、取得方式和原始 JSON。物理页按 read 从1，印刷页未知 null；layout/annotations 坐标有各自原点/单位与 pageIndex 约定，保存原生字段再显式映射，不能把文本输出凭空补 bbox。Zotero notes 和用户 annotations 分开标记作者与内容类型，不默当论文原文。

输出至少 `raw/`、日志、`provenance.json`；若生成 L1，`document.md` 写明“来自哪些读取页/原生提取”，保持部分范围。未取得 L0 不填写假 source_hash，也不把附件 key 当哈希。每个实际引用候选附来源 key、页段、bbox 或 null、完整 source_hash（若取得）；quote 状态保持未核验。

## 局限及测试范围

本文没有安装 CLI、连接真实文库、读附件或调用 API。固定 commit 的 argparse 对示例已离线核对，不代表真实库权限/联网/提取质量验证。无结果不等于没有相关论文；先区分库不可达、库选错、字段/过滤条件与确实无命中。当前默认明确使用字段查询，不运行语义索引。

上游核心 MIT，聊天插件为独立 AGPL-3.0-or-later 部分，本包未包含插件。隔离的上游 reference 含写命令，不作为执行说明；正式 Registry 身份和搬档案由上层 Gateway 完成。
