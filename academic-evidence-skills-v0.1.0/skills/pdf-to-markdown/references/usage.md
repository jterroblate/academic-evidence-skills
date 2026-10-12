# 使用方法

用途：将 PDF 或现有逐页解析产物交付成可回溯的转写包。它是本次编写并验证的交付适配器；不是 Uniseem 外部 `pdfskill` CLI 的重命名安装包。

Python 3.11+，独立环境安装技能根的 `requirements-local.txt`。本地基线固定 PyMuPDF/PyMuPDF4LLM 1.28.2，许可证依运行库各自条款，详见 `THIRD_PARTY_NOTICES.md`。已有解析结果只需 PyMuPDF 读取原件，不调用 PyMuPDF4LLM；安装较小依赖时可用 `python -m pip install pymupdf==1.28.2`。

从技能目录运行（其他 cwd 使用脚本的实际绝对路径）：

```sh
python scripts/convert.py /absolute/path/paper.pdf --output /absolute/path/output/paper-v1
python scripts/verify.py /absolute/path/output/paper-v1 --json
```

已有解析结果：

```sh
python scripts/convert.py /absolute/path/paper.pdf --output /absolute/path/output/paper-v1 \
  --parser-pages /absolute/path/parser-pages.json --assets /absolute/path/parser-assets
```

`parser-pages.json` 包含引擎/参数/版本、完整原件 SHA256、provenance、derivation、物理页号（从1）与原始逐页 markdown。JSON 字段及示例见 [parser-input.md](parser-input.md)。MinerU/Docling 的专有布局字段需依据其真实产物适配，不能把普通 Markdown 等长切分当页映射。输出结构见 [output-contract.md](output-contract.md)。

输入是原始 PDF、新目录、可选页范围/已知 metadata。输出含 `source.pdf`、`document.md`、原始逐页结果、页/行映射、哈希与质量报告。缺失 metadata 为 null；没有读取整个 PDF 时声明 partial。

示例提示词：

> 用 $pdf-to-markdown 转写我指定的 PDF；保留原件和解析输入，输出到新目录，说明覆盖页与待复核项。对首页、末页、双栏、表格和公式回到 PDF 抽查。

返回 0：机器检查完整或明确声明的子集；返回 3：产物存在但 needs_review；返回 1：错误或无效。机器检查不能保证内容忠实。扫描可能无正文；双栏样例有阅读顺序问题。真实后端限制及先前实际测试见 [validation.md](validation.md)。不能根据转换成功把 quote 或 L0 核验字段置真。
