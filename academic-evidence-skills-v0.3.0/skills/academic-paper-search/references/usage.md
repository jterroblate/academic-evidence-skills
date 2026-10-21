# 使用 academic-paper-search

## 调用与依赖

用户可以说：`使用 $academic-paper-search，从 arXiv、PubMed、Crossref 找某主题论文，先保存候选。只把明确授权且可访问的 PDF 下载到新 staging。`

需已有 Python `>=3.10` 和 `paper-search-mcp` 包中的 `paper-search` CLI。固定 commit `cab1b5cc276a0cd004a0044003926a6440088049` 的 pyproject 版本 `0.1.4`；该版本号不能代替源码/当前环境核对。先运行帮助，不安装：

```bash
command -v paper-search
paper-search --help
paper-search search --help
paper-search download --help
paper-search read --help
```

包依赖 requests/feedparser/fastmcp/pypdf 等。本包只含 skill 与核对资料，未捆绑 runtime。API key 由外部环境或已有 secret 配置提供；不要复制 `.env`、输出密钥或自动更改 provider。商业与机构 API 只在已有明确授权、凭据及权益覆盖时选择；源站可读不自动授权上传其他材料。

必要执行沿用已获授权，不重复询问。任务必需的轻量依赖可在既有授权范围内隔离安装，不改全局环境；模型下载、替换或远端渠道变更按实际授权与已选渠道执行，缺口明确报告。

## 搜索及原始结果

先建全新 run，示例 `/path/to/...` 需替换：

```bash
TASK_STAGE="/path/to/staging/new-run"
mkdir "$TASK_STAGE"
mkdir "$TASK_STAGE/raw" "$TASK_STAGE/logs" "$TASK_STAGE/downloads"
paper-search search "transformer attention" -n 5 -s arxiv,pubmed,crossref > "$TASK_STAGE/raw/search.json" 2> "$TASK_STAGE/logs/search.stderr"
paper-search sources > "$TASK_STAGE/raw/available-sources.json"
```

`-n` 是每来源上限，`-s` 明确来源不自动扩大。默认源 all 可以发起很多请求，按目标选择来源，别只为凑数量。fastest 为 OpenAlex+Crossref；fast 为公开来源组合且有非空 Semantic Scholar key 时会加入它。`-y` 仅 Semantic Scholar 年份过滤，不是跨源统一过滤；记录每源实际查询规则。结果不全、超时/限流均保留，不从“无命中”推断反证。

CLI search/download 返回 JSON，read 通常纯文本（Scopus 可能结构化摘要）；stdout、stderr 和退出状态分别保存。原始响应不能被整理表格替代。输出候选表可含 title/authors/year/source/DOI/URL、内容类型、版本信息（实际取得才写）和访问状态；先确认元数据，再决定是否取得全文。

原始 query 参数与每源返回原样存档；query、URL、DOI 只是检索出处。DOI 一致不证明 PDF 字节/出版版本一致，多个库同源命中不是多项独立支持。

## 授权 PDF 下载

已有用户授权下载该公开 arXiv 文件时，可执行：

```bash
paper-search download arxiv 2408.09869 -o "$TASK_STAGE/downloads" > "$TASK_STAGE/raw/download-response.json" 2> "$TASK_STAGE/logs/download.stderr"
```

该 ID 为命令形状例子，运行时替换为真实选中且授权的 paper_id。下载响应 `status:ok` 与 path 后，再核对文件存在、PDF magic/可读页、正文题名/DOI/作者、版本、完整 SHA256；未知或不匹配状态保留，不能自动合并身份。下载原件是 L0；保存原下载路径、URL/来源、取得时间、授权访问方式及各文件完整哈希，Gateway 之后决定正式身份/归档。

本入口不执行 `download_scihub` / `--use-scihub`。generic `paper-search tool download_with_fallback ... --no-use-scihub` 虽可关闭该选项，仍可能尝试其他 OA 渠道；未经明确选择不自动换渠道，也不依赖上游默认参数保证所有访问边界。无法取得公开可访问全文时报告候选与缺口。

`paper-search read arxiv <id> -o ...` 会下载并提取，不是只读已有文件，也通常无 bbox/逐页原生解析产物；本入口优先授权下载后交已有本地解析器。Scopus `read` 默认是 abstract metadata，`--full-text` 才尝试全文，成功仍需检查响应 status；摘要不改称完整论文。

## 已下载本地 PDF 的分节候选

仅需要快速筛选且已有 PDF 时可使用上游 `extract_sections`，它复用 pypdf，不 OCR。root 通过进程环境指定；相对 PDF 路径不得包含 `..` 或 symlink。示例文件名换为真实文件：

```bash
PAPER_SEARCH_MCP_SECTION_PDF_ROOT="$TASK_STAGE/downloads" paper-search tool extract_sections paper.pdf --max-pages 20 --max-chars 40000 > "$TASK_STAGE/raw/sections.json" 2> "$TASK_STAGE/logs/sections.stderr"
```

只有符合当前工具可用配置时执行；`paper-search tool --list` 和 `paper-search tool extract_sections --help` 可核对，不能调用任意注册写/清缓存工具。固定源码要求 POSIX resource limits；不支持的平台失败关闭，其他搜索不受影响。默认上限30页/60000字符/50节/30秒，硬上限100页/200000字符/100节/60秒、PDF20MiB。记录 `pages_processed`、`total_pages`、`truncated`、`stop_reasons`。

每节的 page_start/page_end 从1，start_char/end_char 是拼接提取文本 offset，不是 PDF 字节或 bbox。heading/label 只是英语独立标题启发式；多栏、数学、表格和扫描件存在局限。印刷页未知 null，bbox null；保持 `quote_status:unverified_transcription`。不能将分节结果自动生成正式 ScientificCoordinate/EU。若要 L1，保存原始分节响应，在 `document.md` 明确只含处理页/候选提取；完整转写应另交已选解析器。深读另写 reading.md。

## 记录与限制

staging 可含 `raw/search.json`、`raw/download-response.json`、`downloads/`、原始分节/文本输出、日志、`provenance.json`、候选表。记录 engine 实际版本/源码（若可核对）、参数、访问方式、页覆盖、完整 source_hash、物理页/印刷页/bbox/字符定位及待核验项；未取得完整 PDF 时 source_hash 为 null 并解释。

无正式证据/Registry schema 时不能编造接口或 P ID。任务结果只是一组可追溯候选/材料，提交给上层 Gateway；不自动 Git commit/push、索引新凭据、开启搜索缓存或清缓存。

本次只下载固定源码、核对 CLI argparse 与选项；未安装 runtime、未调用学术 API、未下载或解析真实论文、未验证源站可访问性。上游 PDF_SECTIONS 等资料隔离保存为 txt，不能当本轮端到端验证结果。
