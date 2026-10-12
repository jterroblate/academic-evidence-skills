# 来源与运行时依赖

本包参考并改编了 Uniseem/pdf-skill 的 skill 工作流说明，保留原 MIT 版权与许可文件；未复制或分发其外部 CLI、retain-pdf、KaTeX vendor 代码。原 LICENSE 中提及的 vendor 路径是上游项目中的路径，不在本包内。

新的转换与校验胶水脚本按本包 MIT 许可交付。下列后端由使用者另行安装，不随 zip 分发，其许可独立于本包：

- PyMuPDF4LLM：AGPL-3.0；依赖的 PyMuPDF/MuPDF 有 AGPL/商业许可方案。https://github.com/pymupdf/pymupdf4llm
- MinerU：固定使用版本的许可单独核对；当前官方为 Apache-2.0 加附加条件。https://github.com/opendatalab/MinerU/blob/master/LICENSE.md
- Docling：代码 MIT，模型按各模型许可。https://github.com/docling-project/docling#license

版本与依赖信息详见 requirements-local.txt 与 references/engines.md；安装并不将这些依赖重新许可为 MIT。
