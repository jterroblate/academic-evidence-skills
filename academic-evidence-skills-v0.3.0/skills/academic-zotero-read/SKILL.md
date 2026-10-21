---
name: academic-zotero-read
description: 按明确只读 CLI 白名单检索和读取既有 Zotero 文库的书目、附件、页段、笔记与标注，输出可追溯 staging 材料；不修改 Zotero、同步文库、建立索引或授权写入。
---

# Zotero 只读学术材料

先读 [使用说明与白名单](references/usage.md)。沿用用户已有可读环境，优先既有本地模式；本包不配置 Zotero、不携带库/凭据/运行时。

- 只运行 usage 中明确列出的读命令及其列明选项。`toolsets=none` 只是只保留 core，仍有写工具；`ZOTERO_LOCAL_WRITE=false` 只是写路由设置，也不是只读保证。
- 不执行 add/edit/attach/delete/batch、notes/annotations 的写子命令、collections manage/create/update、db update/batch-import、library switch/reset；不运行 `authorize-local` 或自动同步，不把已有写凭据当作授权。
- 搜索/提取使用原始 JSON 响应，确认 `ok` 后保存库身份、item/attachment key、DOI/URL、查询时间与取得范围。搜索命中、笔记或摘要都不是全文 PDF，也不是正式证据。
- 本地附件需确认可读、版本及授权，再复制到全新 staging，保持 L0 原件不变、计算完整 SHA256。读不到完整附件时注明“不具备 L0 PDF/hash”，不能用 Zotero key 或缓存短哈希代替。
- 页段物理页从 1、印刷页未知 null，原生 bbox/标注坐标与来源区分保留。文本返回未给 bbox 时保持 null；已有笔记/标注属于作者记录，不自动确认为原文 quote。
- 转写叫 `document.md`，深读才 `reading.md`。不得自动创建正式 EU/Utility/坐标/Registry P ID；身份与归档交由上层 Gateway。只输出新 staging，不覆盖档案或自动 Git commit/push。
- 凭据由外部环境供给且不落文件；不用 `config --show-secrets`，去除配置输出中无关隐私。关键词使用 advanced 字段检索；默认 items 会级联语义搜索，semantic 可能后台更新，CLI db status 会初始化 client，均不在只读白名单。不自动建索引、同步或新增 embedding 服务。

[LICENSE](LICENSE) 保留核心 MIT；上游聊天插件不包含在本包。`references/upstream/*.txt` 含全命令与写示例，仅作为隔离资料，不授予执行权。
