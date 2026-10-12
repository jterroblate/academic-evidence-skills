# 安装、输入与运行

## 自然语言调用

- “使用 $academic-paperqa 先检查我的本地论文包和已有模型配置，给我可运行计划。”
- “使用 $academic-paperqa 用我已授权的本地后端回答这个问题；把AI摘要与待回查的引文分开。”

## 可选安装

已有可用环境优先。本技能本身不用paperqa即可plan/doctor；真正query需要Python>=3.11和paper-qa库。依赖缺失且本次任务需要执行时，在指定隔离环境安装；既有任务授权有效，不重复询问。示例，绝不安装全部dev extras：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install "git+https://github.com/Future-House/paper-qa.git@57e89f7223b0960d5ee5ea048c69e3c47e088572"
.venv/bin/python -c "import paperqa; print('paperqa import OK')"
```

该main版本为monorepo，pip可能还从包索引解析paper-qa-pypdf/fhlmi等依赖，安装的依赖锁应由目标工程保存，不能把固定主仓库commit误称所有依赖已锁。若Git源码安装不可用，可选择与工程兼容的已发布 `paper-qa` 并记录实际版本差异；本包没实测源码安装/真实模型。

## Bundle 输入

复制 `assets/bundle.example.json`，编辑为真实PDF路径、已有source_id/source_family、完整SHA256和bibliographic_citation（没有真实引用可用来源标签，不能编造作者年份）。source_path相对bundle文件位置；原PDF只读。示例不含真论文与凭据，SHA256全0是明显占位，必须替换。可以独立计算：

```bash
python3 -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('paper.pdf').read_bytes()).hexdigest())"
python3 scripts/paperqa_adapter.py plan --bundle bundle.json --question "这些论文报告了什么共同限制？" --out run-plan
```

plan使用标准库，不导入paperqa/调用模型；它核查PDF头部和hash，不检测全部PDF页，也不证明文本质量。

## 后端配置与执行

`assets/settings.local.example.json` 是上游README本地Ollama示例的可审阅配置：llm与summary_llm=`ollama/llama3.2`、embedding=`ollama/mxbai-embed-large`，api_base回环。它**不会安装或启动Ollama/下载模型**；须已有这两模型和服务且使用者决定适用性。不把本地示例声称已实测或高质量。实际工程可用已有供应商，显式填三种模型与其config，backend_declared_ready由调用方确认，不能让agent猜。

```bash
python3 scripts/paperqa_adapter.py doctor --config settings.json
python3 scripts/paperqa_adapter.py plan --bundle bundle.json --config settings.json --question "问题" --out run-plan
# 只有本次授权模型调用、资料内容提交且doctor无阻塞，才运行下面命令：
.venv/bin/python scripts/paperqa_adapter.py query --bundle bundle.json --config settings.json \
  --question "问题" --out run-query --allow-model-calls
```

config外壳含backend_declared_ready(boolean)、content_submission_authorized(boolean)、backend_scope(local/existing-remote)、settings(真实PaperQA字段)。示例均false，拒绝直接query是预期。不要把真实api_key写进settings文件；用原有供应商环境变量或已有后端认证配置，adapter拒绝嵌入非空api_key/password/token。doctor不会读取或打印凭据值，不联网探测；字段齐全仅为config-ready-unverified。

query采用手动Docs集合，没有agent远端论文搜索。禁用use_doc_details/multimodal；对局部kwargs及结果解释见 [API说明](api.md)。它不接入新的cloud上传或查询凭据。问答、embedding、上下文摘要可产生模型费用；`--allow-model-calls`不是预算保证，实际授权应在任务中先明确已有渠道和允许范围。

## 输出与退出码

- plan.json + source-map.candidate.json：离线计划和对L0的hash映射，可重建L1。
- answer.derived.json：question、answer、formatted_answer、AI context summaries，不当逐字引用。
- citations.candidate.json：source_id/source_hash/source_family和excerpt_candidate；quote/pdf_page_1based/printed_page先null，locator_status=pending-L0-check。
- run-manifest.json：开始/returned/failed-or-unknown、输入hash、禁用项与候选状态。保存返回后再处理本地映射，局部失败不重做模型请求。

exit0成功或可审阅计划；exit2输入/本地错误；doctor/query exit3为blocked dependency/config。没有后端时doctor会清楚blocked，不能声称完整问答已完成。A/B/C/D及正式EU边界见 [契约](evidence-contract.md)。本包实测标准库plan、错误路径、mock query与doctor缺库，无真实LLM/embedding/backend实测。

`run-manifest.retry_allowed=false` 仅限制本adapter重调aquery；PaperQA/fhlmi/LiteLLM/provider内部retry或JSON修复没有在本包实测。配置调用前须确认当前后端未知结果不会自动重跑；无法确认时只执行离线plan并报告缺口。doctor的config-ready-unverified不认证retry/timeout配置，不能当全链路已验证。
