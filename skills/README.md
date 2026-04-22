# Skills for momapy

This directory ships [Claude Code](https://docs.claude.com/en/docs/claude-code) **skills** — packaged instructions that teach Claude how to use the `momapy` library correctly without having to read the whole codebase first.

Skills are opt-in. They are *not* loaded automatically when you clone this repo; you install them yourself, once, and Claude will then load each skill on demand whenever its description matches the task you're working on.

## Available skills

| Skill | What it does |
|---|---|
| [`momapy`](momapy/SKILL.md) | Build, read, write, modify, and render SBGN / CellDesigner maps with `momapy`. Covers the frozen-dataclass + builder pattern, `read()` / `write()` / `render_map()`, `LayoutModelMapping`, styling, the CLI, and the common pitfalls. |

## Install

Skills live in `~/.claude/skills/<name>/SKILL.md` (user-level, available in every project) or in `<your-project>/.claude/skills/<name>/SKILL.md` (project-level, only available there).

### One-shot copy

Pick the location, then copy the skill into it:

```bash
# user-level (recommended) — available in every project you work on
mkdir -p ~/.claude/skills/momapy
curl -fsSL https://raw.githubusercontent.com/adrienrougny/momapy/main/skills/momapy/SKILL.md \
  -o ~/.claude/skills/momapy/SKILL.md
```

```bash
# project-level — only when Claude Code is run inside that project
mkdir -p .claude/skills/momapy
curl -fsSL https://raw.githubusercontent.com/adrienrougny/momapy/main/skills/momapy/SKILL.md \
  -o .claude/skills/momapy/SKILL.md
```

### From a local clone

```bash
git clone https://github.com/adrienrougny/momapy.git
cp -r momapy/skills/momapy ~/.claude/skills/
```

### Update / uninstall

```bash
# update
curl -fsSL https://raw.githubusercontent.com/adrienrougny/momapy/main/skills/momapy/SKILL.md \
  -o ~/.claude/skills/momapy/SKILL.md

# uninstall
rm -rf ~/.claude/skills/momapy
```

## How it works

Each `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: momapy
description: Build, read, write, modify, or render SBGN…
---
```

Claude Code reads the `description` and decides on its own when the skill is relevant — for example, when your code imports `momapy`, when you ask about `Map` / `Model` / `Layout`, or when you're rendering a map to SVG/PDF. The body of the file is then loaded into the conversation as guidance.

You don't need to invoke the skill manually; just ask Claude to do something momapy-related and it will pick it up.

## Contributing

These skills live in the main `momapy` repository. If you spot something out-of-date, open an issue or PR against [`skills/`](.).
