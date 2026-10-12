# 学术证据工作流 · Skill 合集

14个可携带技能，覆盖PDF转写、文献检索、引用管理、批判性阅读、假设、综述和审查。12个开源技能的定制版本，配合PDF交付适配器与PaperQA2可选适配器；AI参与改编。

## 下载与入门

- [下载 v0.1.0 ZIP](https://github.com/jterroblate/academic-evidence-skills/releases/download/v0.1.0/academic-evidence-skills-v0.1.0.zip)
- [安装与第一篇PDF](academic-evidence-skills-v0.1.0/README_先读.md)
- [每个技能怎么用](academic-evidence-skills-v0.1.0/每个技能怎么用.md)
- [技能目录](academic-evidence-skills-v0.1.0/skills)
- [来源、固定版本和改动](academic-evidence-skills-v0.1.0/来源与修改.md)
- [验证范围](academic-evidence-skills-v0.1.0/验证说明.md)

第一次可只选 `pdf-to-markdown` 和 `academic-docling`；已有解析渠道则直接接入已有结果。支持SKILL.md的agent可安装完整技能文件夹，具体路径与调用方式见安装说明。运行脚本需要对应Python/CLI、模型或API环境；ZIP不捆绑大型依赖与凭据。

在本仓库副本中进入完整包目录，预览选定技能的安装位置：

```sh
cd academic-evidence-skills-v0.1.0
python tools/doctor.py
python tools/install.py --destination /absolute/path/to/project/.agents/skills --skills pdf-to-markdown academic-docling
```

确认目标路径后加 `--apply` 才复制，已有同名目录拒绝覆盖。PDF转写需要Python3.11+，安装工具需要3.10+。

## 工作流边界

原始PDF及完整SHA256保留，转写与原始解析结果可回溯。搜索、摘要、假设和模型回答保持候选；DOI、格式或结构校验不等于内容支持。正式EU、Gateway/Registry和科学坐标接口仍需按目标工程接入。

格式、离线行为、独立审查和解压试跑已验证；真实PDF精度、远端解析/模型/API、Windows与原系统集成未代测。本地文本基线不做OCR，双栏/扫描可能返回needs_review。

## 许可

各技能保留原作者版权与自身许可证；请读各目录LICENSE与UPSTREAM.json。整合工具与说明见包内LICENSE.txt。MinerU采用其自定义条款，模型、运行库、服务和数据另依各自许可；不能将整个合集概括成统一MIT。
