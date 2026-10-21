# 使用与非正式候选示例

## 准备 SDK 与渠道

本技能是操作说明和上游参考资源，没有新运行脚本。安装 LangExtract SDK 只完成准备，不启动模型或验证抽取质量。需安装时在目标工程的隔离环境固定经过核查的版本；本包对应上游 commit 见 [UPSTREAM.json](../UPSTREAM.json)，commit 不是 PyPI 版本号，不自动声称二者一致。没有用户授权安装时只报告依赖状态。

可供目标工程准备的 SDK 包名为 `langextract`；既有授权渠道需要 OpenAI provider 时才需要 `langextract[openai]`。实际 `model_id` / `ModelConfig` / endpoint 必须来自已有配置。未配置就返回准备状态 `needs_review`、原因“待配置”，不要从上游例子选择 Gemini、开通 key 或下载本地模型。

按需读未改上游资源：

- [provider 接入](../upstream/langextract-usage/references/providers.md)：核对既有渠道的参数与 schema 能力，不照搬示例 endpoint/key。
- [resolver 参数](../upstream/langextract-usage/references/resolver-params.md)：理解 fuzzy/lesser，执行后仍须独立字符相等检查。
- [prompt/example 对齐](../upstream/langextract-usage/references/prompt-validation.md)：仅验证 few-shot 示例的对齐，不能代替运行结果的来源检查。
- [原入口](../upstream/langextract-usage/SKILL.md) 与 [上游示例目录说明](../upstream/langextract-usage/README.md)：示例可能使用旧模型或直接联网；本技能不会自动执行这些 Python 文件。

SDK 接入层须补可观察的 raw completion 留存、各 attempt 记录和逐项错误。若现有调用封装只交 annotation 而无原始返回，在接入前报告“原始返回接口待补”；不能宣称本技能自动完成审计。完整日志可以写在用户授权的输出目录，不修改原件、Registry 或旧技能包。

## 可复制提示词

```text
使用 $academic-langextract，处理我指定的既有 L1 文本。
Source ID、原件/L1 hash 与版本、页/块映射、输出位置、已授权模型渠道均从本次工程输入透传；缺少时明确列出，不自行注册或切换 provider。
先确认当前调用封装能保留完整原始响应，并核对 LangExtract/provider/SDK/外层任务的重试。
按任务所需类型抽取候选，quote 与改述分开。保留原主客体、数值字符串、单位、比较符、否定作用域、条件、群体/时间、范围和不确定性；没有明示的字段留空。
逐条独立检查真实 L1 的 raw_input[start:end] == quote，并记录重复匹配、fuzzy/lesser、失败和零候选，不筛掉失败项。
分别返回 L1 引文检查、L0 定位检查与 entailment 审查状态；缺映射或未核对就 unknown。所有候选仍是 candidate/needs_review，不创建 FormalEU 或写 Registry。
已知返回只修本地；未知远端不盲目重发。交付完整候选/失败清单、实际检查和原始响应位置，说明尚未验证的部分。
```

## 最小示例 · 非正式格式

下面是人为构造的普通研究句子，供说明字段与状态，并非真实论文证据或模型运行结果。源文本采用 Python Unicode 字符索引；此句为67个字符，span 是 `[0,67)`。hash 必须由工程在实际输入上计算，不能复制示例值。`source_id` / candidate/run/attempt ID 缺失保持 null；真实调用前须由外部提供，不生成身份。

```text
In group A, the intervention may not reduce error by more than 10%.
```

```json
{
  "status": "needs_review",
  "source_id": null,
  "candidate_id": null,
  "input_provenance": {
    "l0_hash": null,
    "l1_hash": null,
    "l1_version": null,
    "offset_unit": "unicode_code_point",
    "chunk_base_offset": 0
  },
  "candidate_type": "claim",
  "claim_paraphrase": "在A组中，该干预可能不会使误差降低超过10%。",
  "subject_text": "the intervention",
  "predicate_text": "reduce",
  "object_text": "error",
  "quantity_raw": "10%",
  "unit_raw": "%",
  "comparison_raw": "more than",
  "negation_raw": "not",
  "negation_scope": "reduce error by more than 10%",
  "conditions_raw": ["In group A"],
  "uncertainty_raw": "may",
  "evidence": [{
    "quote": "In group A, the intervention may not reduce error by more than 10%.",
    "start": 0,
    "end": 67,
    "field_support": ["subject_text", "predicate_text", "object_text", "quantity_raw", "unit_raw", "comparison_raw", "negation_raw", "conditions_raw", "uncertainty_raw"]
  }],
  "checks": {
    "sdk_alignment_status": "not_run",
    "l1_quote_check": "passed_for_this_synthetic_example_only",
    "l0_locator_check": "unknown",
    "entailment_check": "needs_review"
  },
  "l0_locator": {"page": null, "bbox": null},
  "audit": {
    "run_id": null,
    "attempt_id": null,
    "provider": null,
    "model": null,
    "raw_response_path": null,
    "remote_outcome": "not_called"
  },
  "review_reasons": ["演示句：无真实Source ID/hash、L0映射或模型调用；不可晋级FormalEU"]
}
```

这只是说明性 candidate 记录，**不是正式 EU schema，也不是 LangExtract 原生输出格式**。实际工程定义 schema 后再将 LangExtract extraction/attributes 映射到它，并检查字段类型和证据覆盖。`field_support` 只表示待检查的关联，不能当作已证明的 entailment；模型说出的 status 和 span 也必须由调用层重算/校验。未知不等于失败；已知失败单独留 reason、原响应和版本。

重复 quote 的最小处理是列出所有匹配 offset，并记录“当前上下文不足以唯一消歧”，返回 `needs_review`。找不到、局部匹配或 schema 失败时仍保留原 candidate/raw attempt；空结果必须区分成功零主张、解析遗漏、截断、调用失败和未执行。

## 本包已验证与未验证

已做上游固定 commit 的9份资源字节/hash保留、入口结构与相对路径检查。没有运行 provider、下载模型、抽取真实 PDF 或验证 cross-domain accuracy。`quick_validate` 只检查 Skill 基本结构，不证明抽取效果、L0回溯、entailment、预算控制或原始日志保存接口已可用。
