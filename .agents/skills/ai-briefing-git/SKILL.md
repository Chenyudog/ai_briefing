---
name: ai-briefing-git
description: 在 ai_briefing 项目准备 Git 提交说明、创建提交或完成一版并验收通过时使用。按 Conventional Commits 编写中文提交说明，并按项目要求交付已验收版本。
---

# ai_briefing 提交规范

- 提交首行使用 `<type>: <中文说明>`。需要指出改动范围时，用 `<type>(<scope>): <中文说明>`。类型用小写英文，使用半角冒号，冒号后加一个空格。
- 根据实际改动选类型。新增功能用 `feat`，修复问题用 `fix`，文档用 `docs`，仓库维护用 `chore`。也可以按改动选用 `refactor`、`test`、`perf`、`ci`、`build` 等合适的类型。
- 中文说明写清具体改动。例如 `chore: 初始化仓库`、`feat: 新增机器人 VLA 新闻频道`、`fix(feed): 修复首页新闻排序`。
- 每完成一版并通过该版验收，检查本版的改动范围，提交并推送到已关联的 GitHub 远程仓库。推送完成后告知用户分支和提交说明。
