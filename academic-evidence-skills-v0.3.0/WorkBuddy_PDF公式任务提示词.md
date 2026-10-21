# 可直接发给WorkBuddy的PDF公式任务提示词

2026-10-21 · 先在WorkBuddy打开自己的工程。将下面正文与自己的PDF/参考稿一同提供。支持执行命令与读写文件的宿主才能实际运行后端。

---

请利用我提供的学术证据技能合集，优化PDF转Markdown，重点保证LaTeX公式与原文的可追溯性。公开仓库：https://github.com/jterroblate/academic-evidence-skills 。先读取`academic-evidence-skills-v0.3.0/README_先读.md`、`PDF公式更新与实测范围.md`及本提示词，再按需读取`skills/pdf-to-markdown`、`skills/academic-mineru`、`skills/academic-docling`内的SKILL和usage，不一次加载全部资料。不能访问GitHub时使用我提供的完整ZIP，报告缺失文件。

先检查当前工程、已有技能与解析器、Python/SDK版本、实际模型/资产目录，以及WorkBuddy本机导入规则。沿用已有授权渠道。需要改技能时保留上游版本和许可，在项目适配副本中改，不覆盖唯一原件。合集ZIP先解压，再选择完整技能目录；它不是单技能导入包。包内`WorkBuddy单技能导入包/`另有这三项独立ZIP，已补公开规范的中英简介/版本/作者元数据，可先按本机入口试导入；不能因此声称客户端兼容已验收。

我的参考Markdown只作为版式参考，不是真值。请按下面流程实际工作：

1. 对原PDF计算完整SHA256并保留原件；记录物理页范围/总页数、引擎版本、参数、模型标识、原生JSON/Markdown和本地图像。不要把模型推断的书目补成已核实信息。
2. 先选一个同时含分式、上下标或求和的代表页测试。当前公开测试优先建议MinerU 4.0.12 basic/ONNX作为本地候选；已配置的其他解析器也可试，但要单独记录，不把不同质量档混为一组。PyMuPDF文字抽取未出现LaTeX时不能声称公式完成。
3. 先读`academic-mineru/references/usage.md`。已有4.x物化原生输出与真实producer记录时，可用`academic-mineru/scripts/export_pages.py`导出逐页JSON；不能从Base64 Markdown、标题或平均字数假拆页。原始响应保留，资产外置另存版本，不为导出错误重新推理。
4. 用`pdf-to-markdown/scripts/convert.py`和真实逐页JSON/资产目录组织可追溯包，传`--require-latex`。部分页传真实`--pages`，全文必须核对全部物理页。目标目录必须全新。转换/验证退出码3表示需要复核，不等于程序崩溃或公式已通过。应继续只读核验并保留待审，不因退出码3重跑模型；本地导出/路径问题先修复已有产物。
5. 执行`verify.py`，再执行`math_check.py --require-latex --output <新的独立报告>`。根据`--help`填写实际包路径。检查器不修改转换包；词法pass也保持原文数学未核验。若已有KaTeX或TeX运行环境，可另做渲染/编译兼容性测试，单独记录工具版本、范围、错误和不支持的命令；它仍不证明原文一致。
6. 回到原PDF对应区域，逐项核对分式分母、外层幂、因子数量、求和范围、dagger/星号、正负号、上下标、希腊字母与化学能级。无编号公式、图注与正文内联公式也要抽查。公式不确定时保留原图、页码和疑点，不凭科学常识补写。修订后的阅读稿与原生转写分别保存。若无法直接查看源图或缺少视觉能力，交给人核对并保留待审；不能用另一次文本生成替代独立回源。
7. 对已核对的项目建立源页+bbox/截图、期望结构与人工判断的小金标，再扩大全文。若给出准确率，必须说明分母、抽样和判定规则；缺人工全检时不能宣称全篇100%。另做同配置复跑，分别报告“重复稳定”和“内容正确”。
8. 输出一份忠实转写候选、一份可选的修订阅读稿、图像资产、出处映射、机器报告、回源复核记录和下一步清单。保留作者、DOI、公式编号、图表及参考文献；YAML页码/文章号用字符串，尤其前导零。

标准命令形状（替换占位路径，不照抄示例页码）：

```sh
python skills/academic-mineru/scripts/export_pages.py /path/to/native --source /path/to/source.pdf --run-record /path/to/actual-run.json --output /path/to/new-pages.json
python skills/pdf-to-markdown/scripts/convert.py /path/to/source.pdf --parser-pages /path/to/new-pages.json --assets /path/to/native --require-latex --output /path/to/new-bundle
python skills/pdf-to-markdown/scripts/verify.py /path/to/new-bundle
python skills/pdf-to-markdown/scripts/math_check.py /path/to/new-bundle --require-latex --output /path/to/new-math-report.json
```

未核验数学、引句或原件定位时，不把结果标为verified，也不直接写正式EU/Registry。引用支持、数学正确、资产完整和页面覆盖分别报告。保留错误/未知，不为了展示美观先让模型改写原文。权限范围内的本地可逆工作直接推进；缺服务或模型时报告实际缺口，不伪造运行成功。
