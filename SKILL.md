---
name: paper-writing
description: 融合 Nature 风格写作与书籍实证知识库的论文撰写技能——写作技巧以两本书为准（Gastel & Day；Turabian），Nature 片段只管刊物约束。Draft, restructure, or plan Nature-style manuscript sections and initial-submission packages from author-provided claims; and write, cite, audit, submit, or revise scientific papers for any journal, plus theses and dissertations with Chicago-style citation. Writing technique follows a distilled book-craft layer (references/craft/) backed by a PDF-verified full-text knowledge base of the two canonical guides. Use for abstracts, introductions, results, discussions, methods, titles, full-manuscript arguments, first-submission packages (cover letters, title pages, highlights, declarations, reviewer suggestions), journal selection, revision and reviewer responses, thesis/dissertation structure and submission, and pre-submission QA. Triggers: Nature, Nature-family journal, manuscript, submission, journal selection, cover letter, reviewer response, journal fit, pre-submission QA, 论文、手稿、投稿、选刊、投稿信、审稿回复、毕业论文、学位论文、芝加哥引用. Prefer this skill over standalone nature-writing or scientific-paper-writing-publishing when the job may span both Nature-style drafting and book-verified general-journal or thesis craft.
---

# Paper Writing — 统一路由器

本技能融合两个已验证的写作系统，共用一条工作流：

- **引擎 A — Nature 风格声明驱动写作**（快照自 `nature-writing` v1.5.0 + `nature-shared`，2026-07-24）：
  声明—证据—边界的起草方法、论文类型 playbook、分节片段、期刊风格约束、初始投稿包。
- **引擎 B — 书籍实证知识库**（快照自 `scientific-paper-writing-publishing`）：
  Gastel & Day（期刊论文写作与出版流程）与 Turabian（研究过程、芝加哥引用、学位论文）
  两本书经 PDF 逐单元校验的全文检索库（`references/book-knowledge.sqlite`）+
  从书中凝练的写作工艺层（`references/craft/`，每条技巧带书内章节出处）+ 配套参考文档。

两个引擎的分工由 `journal` 轴与任务类型决定；**核心工作流是共享的**（引擎 A 的
`static/core/workflow.md` 本身与期刊无关：一句话论点、术语台账、一段一职能、确认门、
声明强度校准——对所有期刊适用）。

## 架构与加载纪律

```
本技能根目录/
├── SKILL.md + manifest.yaml     ← 路由器（本文件 + 轴声明）
├── static/                      ← 引擎 A 静态片段（core + fragments，按轴按需加载）
├── references/                  ← 统一参考层：引擎 A 参考文档 + 引擎 B 书籍参考文档 + book-knowledge.sqlite
│   └── craft/                   ← 书籍写作工艺凝练层（从两本书蒸馏的技巧，带章节出处；写作工艺以此为准）
├── shared/                      ← nature-shared 共享层快照（core/ + journal-formats/ + scripts/）
├── templates/submission/        ← Nature 初始投稿 LaTeX 模板
├── assets/                      ← 通用论文模板（manuscript、submission-checklist、response-to-reviewers）
└── scripts/                     ← paper_kb.py（书籍库 CLI）+ build_kb.py（重建管线）+ tests/
```

**不要预读全部文件。** 按下方协议只加载本次任务选中的片段；参考文档只在清单条件
命中时才读；书籍库永远用命令查询，不要整库阅读。

## 统一路由协议

每次调用执行以下步骤。

### 1. 读取 manifest 与核心层

读 [manifest.yaml](manifest.yaml)，加载其 `always_load` 列表（共享层读者工作流、
论文类型分类、伦理、术语台账 + 本技能 core 三件套 + 书籍工艺核心
`references/craft/craft-core.md`——写作技巧的第一依据，全程在上下文中）。

### 2. 检测轴值

对 manifest 中每个轴按 `detect` 提示取值：`task`（manuscript / submission-package /
thesis）、`paper_type`、`section`（可多选）、`language`（en / zh-to-en）、
`journal`（nature / nature-family / nat-comms / nat-mach-intell / generic，默认 generic）。

动笔前用一行向用户说明检测到的轴值，便于其低成本纠正。

**引擎选择规则**：
- `journal` 为任一 Nature 系值 → 引擎 A 片段主导**刊物约束**（字数/图版限额、叙事形式、
  投稿包模板）；写作工艺仍按书籍为准（见下方工艺优先级）。
- `journal = generic` → 核心工作流仍按 `static/core/workflow.md` 执行；分节工艺、
  语言风格与投稿指导由引擎 B 承担（`references/craft/`、`references/manuscript-sections.md`、
  `references/submission-and-peer-review.md`、书籍库查询）。用户明确要求
  "按 Nature 风格写"时，可借用引擎 A 的 section 片段作结构参考。
- `task = thesis` → 加载 `references/thesis-and-dissertation.md`；引用默认走
  `references/chicago-citation.md`，除非目标机构规定其他体系。

**工艺优先级（以书为准）**：两本书提供完整的写作技巧体系。凡"怎么写"——语言风格、
句段技巧、分节写法、论证组织、引用技巧、修订与润色、审稿回复措辞——一律以书籍工艺层
（`references/craft/` 凝练层 + `book-knowledge.sqlite` 深查询）为准，优先于引擎 A 片段的
一般性工艺表述。引擎 A 片段只管辖 Nature 系刊物的特有约定（限额、结构、形式、投稿包），
属于目标刊物约束而非一般工艺；二者的一般工艺表述冲突时：`journal` 为 Nature 系值 →
从 Nature 片段（目标刊物约束优先）；`journal = generic` → 从书。

### 3. 加载选中片段

按轴值读取 manifest 映射的文件；再按任务读取 `references.on_demand` 中条件命中的
文件（两个引擎的条件并列判断，全部命中者都加载）。`task = submission-package` 时
跳过 `section` 轴。

### 4. 应用书籍工艺层与知识库（引擎 B）

书籍是写作工艺的最高依据（工艺优先级见步骤 2）。两级使用：

1. **凝练层 `references/craft/`**（已从两本书蒸馏，每条技巧带书内章节出处）：
   `craft-core.md`（always_load）之外，按 manifest 条件加载 `section-craft.md`
   （起草/修改任一正文章节时）、`language-craft.md`（语言、句段、风格、润色、
   修订时）、`argument-craft.md`（研究问题、论点、论证规划、论文结构规划时）、
   `citation-prose.md`（引用融入行文、改写、防抄袭、芝加哥引用细则时）。
   起草与修改语言时**先查工艺层**，把书中技巧当作操作规范执行，而不是泛泛参考。
2. **深查询层 `book-knowledge.sqlite`**：工艺层覆盖不到、用户要求"书里怎么说"、
   或需要书中原文佐证时，用 `scripts/paper_kb.py` 查询原文（先读
   [references/knowledge-base.md](references/knowledge-base.md) 的检索纪律）。强项分工：
   Gastel & Day——摘要类型与写法、IMRaD 各节、数据/统计呈现、图表规范、伦理声明措辞、
   审稿回复、期刊选择与投稿信；Turabian——研究问题、假设、文献评估与笔记、论证规划、
   改写与引用融入行文、芝加哥引用细则（学生写作与学位论文尤甚）。

查询方式（技能根目录下运行，`--source` 区分两本书，避免混引）：

```powershell
python scripts/paper_kb.py query "abstract structure" --limit 5
python scripts/paper_kb.py query "cover letter" --source "How to Write and Publish" --limit 5
python scripts/paper_kb.py query "dissertation format" --source "A Manual for Writers" --limit 5
```

**边界**：书籍库是写作工艺与流程建议来源，不是论文科学论断的证据；两本书有年代
（2016 / 2003），时效性要求（期刊政策、报告规范、AI 政策、开放获取）必须按
[references/source-registry.md](references/source-registry.md) 以现行权威来源核实。
检索结果保留书名、source id、章节 locator 以便溯源。

### 5. 起草

按以下优先级应用已加载材料（后条不得推翻前条）：

1. 治理要求阶梯（下节）——期刊现行指令 > 设计报告规范/伦理 > 学科惯例与权威风格 > 本技能建议。
2. 核心立场与受理检查（`static/core/stance.md`）：起草前把缺失的声明/证据/边界摆到桌面。
3. 确认门（`static/core/workflow.md` 步骤 3b）：整节起草前对齐一句话论点、段落图、
   术语、主要读者、关键假设；用户确认后再写全稿。
4. 论文类型 playbook 与分节片段（引擎 A 或引擎 B 的节契约，按引擎选择规则）——
   片段提供**结构契约**（本节必须完成什么）。
5. 书籍工艺层（以书为准）：`references/craft/` 已加载的文件——**写法**（句段技巧、
   分节技巧、论证组织、引用融入行文、修订路径）按书中凝练的技巧执行；分节片段的一般
   工艺表述与书冲突时，generic 期刊语境从书，Nature 系语境从片段（目标刊物约束）。
6. 任务规则（submission-package / thesis）。
7. 期刊风格与限额（`journal` 轴片段 + `shared/journal-formats/`；只管刊物约束——
   限额、形式、投稿包构成；generic 期刊以该刊现行指令为准，先查后写）。
8. 语言规则（`language` 轴片段给语言体系；具体语言技巧按书籍工艺层
   `references/craft/language-craft.md`；zh-to-en 时叠加
   `references/scientific-english.md` 的修复模式）。

全程维护：claim-evidence 表（声明—证据—边界—落位—状态）、术语台账、需求台账
（期刊要求 + 来源 URL + 核实日期）。段落一段一职能；声明动词与证据强度校准；
扫掉无支撑的 `first / unique / unprecedented` 类绝对化表述。

### 6. 质检与交付

- 稿件自检：`references/paper-review.md`（拒稿风险审计、声明—证据对齐）+
  `references/workflow.md` 的七遍修订路径（科学性 → 论证 → 报告完整性 → 跨文档一致性
  → 引用完整性 → 英文 → 格式）。
- 一致性机械检查：`shared/scripts/check_consistency.py`（术语变体、数值精度、单位等价）。
- 投稿包：Nature 系用 `templates/submission/*.tex` + `references/submission-package.md`；
  其他期刊用 `assets/submission-checklist.md` + `references/submission-and-peer-review.md`。
- 交付：文稿 + 显式备注（假设、缺失输入、待核实项）；任何实质性项目未核实时，
  不得声称"可投稿"。

## 治理要求阶梯（不可让渡）

1. 目标期刊现行官方指令、文章类型限额、模板、编辑政策（查过并记录访问日期）。
2. 适用研究设计的报告规范（CONSORT/PRISMA/CARE…）与伦理要求。
3. 学科惯例与权威风格标准。
4. 本技能（两个引擎）的一般建议。

缺失细节不阻塞进度：记录为假设与验证登记项，用显式占位符（如 `[VERIFY SAMPLE SIZE]`）；
绝不编造结果、方法、伦理批准、引用或期刊要求。

## 与姊妹技能的边界

- 修改回复信 / 逐点答辩 / 返修版标注（Nature 风格）→ 专用 `nature-response`；
  非 Nature 期刊的审稿回复 → `references/submission-and-peer-review.md` +
  `assets/response-to-reviewers-template.md`。
- 模拟预审 / 审稿人视角 → `nature-reviewer`；图表制作 → `nature-figure`；
  润色（不新建内容）→ `nature-polishing`；文献检索与引用查找 →
  `nature-academic-search` / `nature-citation`。
- 只做通用期刊/学位论文工作、不需要 Nature 风格时，`scientific-paper-writing-publishing`
  单独可用；本技能是其超集（含同样书籍库与文档）。

## 自包含性

运行时只读本技能目录：书籍库为内置 SQLite（两本书的文本已逐单元对 PDF 校验，
`paper_kb.py check` 零问题），**不需要源 PDF/DOCX、OCR、网络或 API key**。
Nature 侧片段为 2026-07-24 的快照（来源 https://github.com/Yuan1z0825/nature-skills），
上游更新时按 [README.md](README.md) 的更新步骤重同步。
