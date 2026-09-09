# shared/ — Nature 共享层快照

本目录是 `nature-shared` 技能包（https://github.com/Yuan1z0825/nature-skills 中的
`skills/nature-shared`）的内容快照，于 2026-07-24 复制进本融合技能，使其自包含。

- 包含 `core/`（立场、合规、主文本纪律、术语台账等 11 个共享定义文件）、
  `journal-formats/`（Nature / Nature Communications / Nature Machine Intelligence
  的版式事实）、`scripts/check_consistency.py`（一致性机械检查）与 `tests/`。
- 原始安装中，`nature-writing`、`nature-polishing` 等技能通过 `../nature-shared/...`
  引用本层；本快照中所有引用已改写为相对本技能根目录的 `shared/...`。
- 本层文件是**共享定义**，不是独立工作流：只加载路由/清单指向的具体文件，不要整包预读。
- `journal-formats/nature.md` 仅用于旗舰 Nature；
  `journal-formats/nature-machine-intelligence.md` 仅用于 NMI（勿互相导入限额）；
  `core/research-compliance.md` 仅在其专科适用门控触发时加载。
- 若上游 `nature-shared` 更新，请从原安装
  （`%USERPROFILE%\.agents\skills\nature-shared`）或 GitHub 仓库重新复制
  `core/`、`journal-formats/`、`scripts/`、`tests/`，并重跑 `tests/` 中的测试。
