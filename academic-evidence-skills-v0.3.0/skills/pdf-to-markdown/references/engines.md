# 解析器选择

核验日期：2026-10-12。以下是工程候选，不是精度排名。先沿用用户已有渠道及原始产物，避免无必要的重解析。本包不包含 MinerU/Docling 云端 API 实现。

| 情形 | 可试用后端 | 应保留的溯源材料 |
| --- | --- | --- |
| 数字文本 PDF，需要轻量试跑 | 内置 PyMuPDF4LLM classic | 源 PDF、逐页 Markdown、本地 PDF 文本块及页映射；本包记录块 bbox，但不建立逐字 Markdown → bbox 对应 |
| 扫描、公式或复杂表格较多 | 用户已有 MinerU，本地或经授权的云端 | 原始 Markdown、图片、content/middle JSON、引擎和模型信息；`page_idx` 的 0 起算需显式转换 |
| 本地结构化解析及丰富页块定位 | Docling | DoclingDocument JSON、Markdown、图片、运行配置；`prov` 中的位置与派生文本分开保存 |

PyMuPDF4LLM 当前 API 的 `page_chunks=True` 返回逐页文本和 1 起算物理页号。classic 与 layout 模式的结构字段不同。本地脚本固定使用 classic、关闭自动 OCR，遇到扫描页不擅自安装语言模型或改走云端。[官方 API](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html)

MinerU 具备 OCR、公式、表格及结构化输出。本地运行仍涉及引擎依赖与模型下载；云端是另一条上传路径。当前云端精准 API 单文件限制为 200 MB、200 页；匿名轻量 API 限制为 10 MB、20 页且只返回 Markdown 链接，未必满足页块溯源要求。不要把无 token 的自动回退当作等价转换。超过限制时可在上游明确按页分片，但必须记录原 PDF 页偏移并检查全篇覆盖。[输出文件](https://opendatalab.github.io/MinerU/reference/output_files/)、[运行层级](https://opendatalab.github.io/MinerU/usage/tiers/)、[云 API](https://mineru.net/apiManage/docs)

Docling 的结构化文档支持页号、bbox、charspan 等 provenance。外部 API 开关与实际 endpoint 共同决定数据是否离开本机；先核实配置。[数据模型](https://docling-project.github.io/docling/concepts/docling_document/)、[字段参考](https://docling-project.github.io/docling/reference/docling_document/)、[安装](https://docling-project.github.io/docling/getting_started/installation/)、[远端选项](https://docling-project.github.io/docling/reference/pipeline_options/)

运行时许可与本 skill 说明文件的 MIT 分开：PyMuPDF4LLM 为 AGPL-3.0，PyMuPDF/MuPDF 有商业许可方案；Docling 代码 MIT、模型分别核查；当前 MinerU 为 Apache-2.0 加附加条件。使用固定版本时以该版本许可原文为准。[PyMuPDF 许可](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)、[Docling 许可](https://github.com/docling-project/docling#license)、[MinerU 许可](https://github.com/opendatalab/MinerU/blob/master/LICENSE.md)

上游 [Uniseem/pdf-skill](https://github.com/Uniseem/pdf-skill) 仍可作为功能与实现参考。它承载入库、检索、翻译及 Git 管理，和本原子转换包的范围不同。不能假定给它添加 `--no-push` 就满足原件保留和证据一致性要求；涉及其配置、密钥和默认行为时须单独核对实际版本。
