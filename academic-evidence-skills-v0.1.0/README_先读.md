# 学术证据工作流 · 通用 Skill 包 v0.1.0

本包提供 14 个可选择使用的技能：12 个开源技能的定制版本、1 个 PDF 转写交付适配器、1 个 PaperQA2 可选适配器。按学术知识系统的原件、证据回溯、假设与审查边界改编；AI 参与，2026-10-12。入口是中文，必要技术参考保留上游英文。

## 先装哪几个

第一次建议只选 `pdf-to-markdown` 与 `academic-docling`：前者整理可回溯交付，后者提供结构化解析渠道。扫描/公式复杂且准备使用 MinerU 时再选 `academic-mineru`。已有 MinerU 或其他解析渠道，直接接它的结果，不需改换工具。

已有 Zotero 库再选 `academic-zotero-read`；查论文可先用 `academic-scholarqa` 与 `academic-semantic-scholar`，也可沿用 Paper Search 或 paper-lookup。研究阶段再选假设、批判性阅读、综述、引用管理和审查。PaperQA2 需要索引及 embedding/LLM 后端，放在原件回溯跑通之后。

完整用途、输入输出及可复制提示词见 [每个技能怎么用](每个技能怎么用.md)。具体后端依赖与命令位于各技能的 `references/usage.md`；[来源与改动](来源与修改.md) 记录固定版本和许可证。

## 安装与使用

解压后保持目录完整。需要能读本地文件/执行命令的 agent 才能运行配套脚本；纯聊天客户端可以阅读方法和模板，但不能因此自动执行解析器。

| 环境 | 放置位置 | 调用方式 |
| --- | --- | --- |
| Codex 项目技能 | 项目下 `.agents/skills/<技能目录>` | 用 `$技能名` 明确调用，或由 description 匹配 |
| Claude Code 项目技能 | 项目下 `.claude/skills/<技能目录>` | 用 `/技能名`；也可在消息中指明技能 |
| 其他支持 SKILL.md 的 agent | 该客户端文档规定的技能目录 | 按客户端规定加载 SKILL.md 及所需脚本/资源 |
| 手动使用 | 任意本地目录 | 让 agent 阅读选定 SKILL.md，给它技能路径、输入文件和输出目录 |

复制的是整个技能文件夹，不能只复制 `SKILL.md`。`agents/openai.yaml` 是可选的 Codex UI 信息；其他客户端可忽略。自动发现是否刷新取决于客户端，可重新打开会话。

安装工具需要 Python 3.10+。在解压后的包目录执行以下预览，目标路径替换成实际项目路径：

```sh
python tools/doctor.py
python tools/install.py --destination /absolute/path/to/project/.agents/skills \
  --skills pdf-to-markdown academic-docling
```

预览无误，原命令加 `--apply` 才复制。Claude Code 把 destination 改成 `.claude/skills`。`--skills all` 可以复制全部；已有同名目录会拒绝覆盖。也可以直接手工复制 `skills/` 下选定的文件夹。工具不会安装运行库、改客户端设置或调用远端服务。

## 跑第一篇 PDF

PDF 转写器需要 **Python 3.11+**，高于安装工具的 3.10+。确认版本后，在已安装的 `pdf-to-markdown` 目录下创建独立环境并安装：

```sh
python -m venv .venv
# macOS/Linux:
.venv/bin/python -m pip install -r requirements-local.txt
.venv/bin/python scripts/convert.py /absolute/path/paper.pdf \
  --output /absolute/path/output/paper-v1
.venv/bin/python scripts/verify.py /absolute/path/output/paper-v1 --json
```

Windows 将 `.venv/bin/python` 换成 `.venv\Scripts\python.exe`。这条本地基线适合文本 PDF；扫描和复杂双栏可能输出 `needs_review`，退出码 3 表示待复核。已有解析结果应走外部结果适配，不重新解析。其他技能按自己的 usage 安装必需依赖；本 zip 没有捆绑 OCR 模型、LLM、索引库或 API 凭据。

命令示例主要采用 macOS/Linux 的 Bash 写法；Windows 需按 PowerShell、Git Bash 或 WSL 调整路径、重定向及环境变量写法。技能内容和 Python 脚本可携带，后端的系统/GPU支持以目标运行库为准；本次未在 Windows 实测。

可以向 agent 发送：

> 使用 $pdf-to-markdown，读取我指定的 PDF，输出到新的 paper-v1 目录。保留原件、原始解析结果、哈希与物理页映射。给出待复核项，再回到 PDF 抽查；不要创建正式 EU 或修改 Registry。

## 验证和接回系统

[验证说明](验证说明.md) 区分实际测试、离线 mock 与未执行的后端测试。`doctor.py` 检查文件完整性及命令是否存在；它不能判断模型已准备好、API 有效或论文内容正确。

本包是原子工作流工具集。正式 EU、Gateway/Registry、Gate0、Science Coordinate Atlas 的接口仍需按原工程 schema 接入。先试一篇真实 PDF，再逐步加入搜索和研究工作流。共同约定见 [证据边界与接入说明](证据边界与接入说明.md)。
