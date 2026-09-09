# 第三方内容与出处声明（THIRD-PARTY NOTICE）

本仓库包含来自第三方来源的内容。在使用或共享本仓库前，请完整阅读本文件。

## 1. nature-skills（Yuan1z0825）

本仓库中的 Nature 侧内容取自公开 GitHub 仓库：

- 来源：<https://github.com/Yuan1z0825/nature-skills>
- 快照版本：v1.5.0（本地安装快照，制作于 **2026-07-24**）
- 纳入范围：
  - `static/`（core 3 + fragments 21）← `nature-writing`
  - `shared/`（core 11 + journal-formats 3 + scripts + tests）← `nature-shared`
  - `templates/submission/`（4 个 LaTeX 投稿模板）← `nature-writing`
  - `references/` 中 Nature 侧参考与 `references/examples/` 示例库 ← `nature-writing`
- 本地化修改：原安装中指向 `../nature-shared/...` 的跨技能相对路径已改写为本技能内的
  `shared/...`（10 个文件 20 处引用）；未复制上游的 SKILL.md / manifest.yaml，
  本仓库使用自己的统一路由。
- **许可状态提示**：制作本快照时未能获取上游仓库的 LICENSE 文件（网络受限）。
  在将本仓库共享给任何人之前，请先到上游仓库确认其许可证；如上游要求署名、
  保留版权声明或禁止再分发，请以其条款为准并更新本文件。

## 2. 书籍文本（两本受版权保护的商业书籍）

`references/book-knowledge.sqlite` 及派生文档包含以下书籍的完整提取文本
（构建于 2026-09-08，SHA-256 见 `references/book-dataset-profile.md`）：

1. Barbara Gastel & Robert A. Day, *How to Write and Publish a Scientific Paper*,
   8th ed. (2016). Cambridge University Press. ISBN 978-1-316-64043-2.
   DOI 10.1017/9781108105293.
   - PDF SHA-256: `9B8D562AA3F28F0F942990365E555D18F276B8F7E9BF53B742CF202F3B5422A7`
   - DOCX SHA-256: `C003927737427B690360559C0E773C04D31318BB18B0BCC90DFF101AA1241610`
2. Kate L. Turabian, *A Manual for Writers of Research Papers, Theses, and Dissertations:
   Chicago Style for Students and Researchers*, 7th ed. (2003; 2007 paperback printing).
   University of Chicago Press. ISBN 978-0-226-82337-9.
   - PDF SHA-256: `9D1156CA4F8347F53A5F7585EBDAD2FA74FF43AB0F84921DA208B3FE41371283`
   - DOCX SHA-256: `0EE848C55752AB1A4EF7612DFAE712282E1389262AE44CFAC812BA3FEE6B6C5E`

书籍版权归出版商所有。提取文本来自仓库所有人合法获得的副本，**仅限个人、非商业使用**；
请勿再分发 `book-knowledge.sqlite`、书籍文本或其可辨认的摘录。详见 [LICENSE](LICENSE) 第 2 条。
如需使用一个不含书籍文本的变体：删除本地克隆中的 `book-knowledge.sqlite`，
改用 `scripts/build_kb.py` 以你自行合法获得的副本构建（本仓库支持）。

原始源文件（PDF/DOCX）**有意不纳入本仓库**（见 `.gitignore`），仅保留在仓库所有人
的本地目录用于溯源与重建；上表的 SHA-256 即可校验本地副本与构建时所用文件一致。
