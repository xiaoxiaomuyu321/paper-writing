# paper-writing

**用于论文撰写的融合技能**：把 **Nature 风格声明驱动写作**（`nature-writing` +
`nature-shared`，来自 [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)）
与**书籍实证知识库**（`scientific-paper-writing-publishing` 技能，内置 Gastel & Day 8th ed.
与 Turabian 7th ed. 经 PDF 校验的全文检索库）合并为一个自包含技能，并新增一层
**书籍工艺凝练层**（`references/craft/`）——两本书的全部写作技巧被蒸馏为按用途组织的
技巧文档，每条技巧带书内章节 locator，可回库验证原文。**写作工艺以书为准。**

> 使用说明：书籍知识库（两本写作指南的完整提取文本）及内置的 nature-skills 内容
> 仅限个人、非商业使用；请勿再分发书籍文本或 `book-knowledge.sqlite`
> （条款见仓库根目录 [LICENSE](LICENSE) 与 [THIRD-PARTY-NOTICE.md](THIRD-PARTY-NOTICE.md)）。

## 与两个来源技能的关系

| 技能 | 关系 | 适用 |
|---|---|---|
| `nature-writing`（+ `nature-shared`） | 本技能 Nature 侧内容的上游 | 仅 Nature 风格起草/初始投稿 |
| `scientific-paper-writing-publishing` | 本技能的书籍侧来源（独立仓库，独立可用） | 仅书籍库 + 通用期刊/学位论文工艺 |
| **`paper-writing`（本技能）** | 两者融合 + 工艺凝练层 | 任意期刊论文 + Nature 系期刊 + 学位论文 |

## 快速开始

### 1. 直接安装（Codex / DeepSeek Harness）

本仓库即标准 Agent 技能包（根目录 `SKILL.md`），支持两种宿主，一行安装、无需 clone：

| 宿主 | 安装位置 | 生效时机 |
|---|---|---|
| OpenAI Codex | `%USERPROFILE%\.codex\skills\paper-writing`（可用 `$env:CODEX_HOME` 改） | 下一轮对话 |
| DeepSeek Harness (DSH) | `%USERPROFILE%\.agents\skills\paper-writing` | 技能目录刷新后（新会话自动可见） |

Windows (PowerShell)：

```powershell
# 安装到两个宿主
irm https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.ps1 | iex

# 只装 Codex
$env:SKILL_INSTALL_TARGET = 'codex'
irm https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.ps1 | iex

# 卸载（两个宿主；设 $env:SKILL_INSTALL_TARGET='dsh' 只卸一个）
$env:SKILL_UNINSTALL = '1'
irm https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.ps1 | iex
```

macOS / Linux：

```bash
curl -fsSL https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.sh | bash              # 两个宿主
curl -fsSL https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.sh | bash -s -- codex  # 只装 Codex
curl -fsSL https://raw.githubusercontent.com/xiaoxiaomuyu321/paper-writing/main/install.sh | bash -s -- all --uninstall
```

- 重复执行 = 更新：git 安装走 `git pull --ff-only`；普通目录安装自动备份（`<目录>.bak-<时间戳>`）后替换。
- 本地 clone 中运行 `.\install.ps1` 若被系统执行策略拦截，改用：
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1`（一行式 `irm | iex` 不受此限制）。
- 也可以手动：`git clone https://github.com/xiaoxiaomuyu321/paper-writing <技能目录>\paper-writing`；
  Codex 里还可以直接对内置 `skill-installer` 说 “install skill from github xiaoxiaomuyu321/paper-writing”。
- 旧方式仍有效：把本目录整体复制到任意 Agent 技能目录（如 `~/.claude/skills/`）。
  入口为 `SKILL.md`；轴路由由 `manifest.yaml` 声明。

### 2. 查询书籍知识库

```powershell
# 仅依赖 Python 3 标准库（无需 pip 安装）
python scripts/paper_kb.py status
python scripts/paper_kb.py query "responding to reviewers" --limit 5
python scripts/paper_kb.py query "dissertation format" --source "A Manual for Writers" --limit 5
```

- 匹配：porter 词干 AND + bm25 排序，AND 无结果自动退化为 OR；`--source` 按书名/URN 限定单本书。
- 每条结果带书名、URN、章节 locator，保留在笔记中以保可溯源。

### 3. 起草论文

直接对 Agent 说例如："用 paper-writing 起草一篇关于 X 的期刊论文，目标期刊 Nature"。
`SKILL.md` 的路由协议会：轴检测（journal / paper_type / language / section / task）→
加载对应 Nature 片段 → 加载书籍工艺凝练层（`craft-core` 常载，其余按条件）→
按需查询书籍知识库验证工艺细节 → 起草 → 质检。

## 目录结构

```
paper-writing/
├── SKILL.md                  ← 统一路由器（轴检测 → 片段加载 → 书籍工艺层 → 起草 → 质检）
├── manifest.yaml             ← 轴声明（nature 五轴 + thesis 任务 + 工艺层/书籍库 on_demand 条件）
├── LICENSE                   ← 私有用途许可（书籍文本 + nature-skills 条款）
├── THIRD-PARTY-NOTICE.md     ← nature-skills 溯源 + 书籍溯源与 SHA-256
├── agents/openai.yaml
├── static/                   ← Nature 侧静态片段（core 3 + fragments 21）
├── references/               ← 统一参考层（Nature 参考 42 + 书籍文档 10 + sqlite）
│   ├── craft/                ← 书籍写作工艺凝练层（craft-core 常载 + section/language/argument/citation-prose 条件加载）
│   └── examples/             ← Nature 侧示例库
├── shared/                   ← nature-shared 本地快照（core 11 + journal-formats 3 + scripts + tests）
├── templates/submission/     ← Nature 初始投稿 LaTeX 模板（4）
├── assets/                   ← 通用模板：manuscript / submission-checklist / response-to-reviewers
└── scripts/                  ← paper_kb.py + build_kb.py + tests/
```

## 来源与快照日期

- **Nature 侧**：`nature-writing` 与 `nature-shared` v1.5.0，快照于 **2026-07-24**
  （来自 [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)）。
  - `static/`、`references/`、`templates/` 为逐字复制；`shared/` 是 `nature-shared` 的快照，
    已随本仓库一起 vendored（自包含，无需另装 nature-shared）；
  - 原始安装中的 `../nature-shared/...` 跨技能相对路径已全部改写为本技能内的 `shared/...`；
  - 未复制上游的 SKILL.md / manifest.yaml——本技能有自己的统一路由；
  - 上游 LICENSE 获取情况见 [THIRD-PARTY-NOTICE.md](THIRD-PARTY-NOTICE.md)。
- **书籍侧**：`scientific-paper-writing-publishing` 技能（独立仓库，2026-09-08 最终版）：
  - `references/book-knowledge.sqlite`（1,502 chunks，`check` 零问题）；
  - 10 个工艺/规范 `.md` + 运行时 CLI + 重建管线 + 测试；
  - 运行时**不依赖**两本书的源 PDF/DOCX。
- **书籍工艺凝练层**：`references/craft/`（2026-07-25 构建）——对书籍库做系统性主题挖掘后
  凝练升华而成：core 工艺核心 + 分节 + 语言 + 论证 + 引用行文共 5 篇，
  **每条技巧带书内章节 locator**。`craft-core.md` 始终加载，其余 4 篇按 `manifest.yaml` 条件加载。

## 优先级规则（冲突时）

1. 目标期刊官网的现行要求（限额、格式、政策）——最高优先；
2. Nature 侧片段——journal 为 Nature 系时主导风格/结构/投稿包；
3. **书籍工艺凝练层与书籍知识库**——写作技巧与通用工艺以书为准；
4. 通用模板与默认工作流。

## 更新

1. **Nature 侧更新**：从更新的 `nature-writing` / `nature-shared` 安装目录（或上游仓库）
   重新复制 `static/`、`references/`、`templates/`（覆盖），再把 `nature-shared` 的
   `core/`、`journal-formats/`、`scripts/`、`tests/` 覆盖到 `shared/`；然后重新执行路径改写
   （`../nature-shared/` → 本地 `shared/`，深度随文件位置而定：`static/core/` 内为
   `../../shared/`，`static/fragments/<x>/` 内为 `../../../shared/`），
   最后跑 `python shared\tests\test_check_consistency.py`。
2. **书籍库更新**：仅当源书更换版本时——用 `scripts/build_kb.py` 配对的 DOCX+PDF 重建
   （命令见 `references/book-dataset-profile.md` 的 Build provenance 节），
   替换 `references/book-knowledge.sqlite`。
3. 两侧原始技能不受影响，继续独立可用。

## 测试

```powershell
python -m unittest discover -s scripts\tests      # 书籍库 19 项
python -m unittest discover -s shared\tests       # 一致性检查 5 项
```
