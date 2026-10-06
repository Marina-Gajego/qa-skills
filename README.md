# 🧪 QA Skills

> An AI-powered QA framework built from **skills** — reusable instructions that teach AI agents (Claude, Copilot, Codex, Gemini and others) how to do quality work the way an experienced QA engineer would.

Instead of a traditional test framework made of libraries, this repository is a framework made of **know-how**: each skill packages a QA practice (exploratory testing, test design, automation review, performance testing…) so an AI agent can execute it consistently, using MCP servers and real tools along the way.

**Status:** 🚧 Early stage — one skill available today, more being added over time.

---

## 💡 The idea

There is no fixed flow to follow: each skill is independent and can be used on its own or combined with others, whenever it makes sense for your context. Pair skills with MCP servers (browser automation, issue trackers, API clients, repositories) and the agent stops being a chatbot and becomes a QA teammate.

## 🗂️ Skill catalog

Skills available **today**:

| Category | Skill | Description |
|---|---|---|
| Report | [`bug-report-writer`](skills/bug-report-writer/SKILL.md) | Turn any evidence (notes, logs, failed tests) into a clear, reproducible, Jira-style bug report — built strictly from what you provide, with gaps marked instead of invented. Delivers in chat, as a Markdown file, or straight into your tracker via MCP. |

More skills (requirements analysis, test design, exploratory testing, automation, code review, performance…) are planned. Have an idea? Open a **Skill idea** issue.

## 📁 Repository structure

```
qa-skills/
├── skills/                 # One folder per skill, each with a SKILL.md
│   └── <skill-name>/
│       ├── SKILL.md        # Instructions + metadata (required)
│       ├── references/     # Checklists, heuristics, examples (optional)
│       └── scripts/        # Helper scripts (optional)
├── docs/
│   ├── configuration.md    # Language preference (.qa-skills.yaml)
│   └── mcp-and-tools.md    # MCP servers and tools the skills rely on
├── .qa-skills.example.yaml # Preferences template (language)
├── .github/ISSUE_TEMPLATE/ # "Skill idea" issue template
├── CONTRIBUTING.md
└── LICENSE
```

Skills follow the open **Agent Skills** format (a folder with a `SKILL.md` containing `name` and `description` frontmatter), so the same skill can be reused across different AI tools.

## 🚀 Using a skill

1. Copy (or symlink) the skill folder into your agent's skills directory — for example `~/.claude/skills/` for Claude Code.
2. Ask the agent for the task in natural language (e.g. *"run an exploratory session on the checkout flow"*). The agent loads the skill automatically based on its description.
3. Connect the MCP servers listed in the skill for the best results.

### 🌎 Language: English, Português or Español

The repo is in English, but skills talk to you — and write reports — in the language you prefer. Drop a `.qa-skills.yaml` in your project (or in your home folder):

```yaml
language: pt-BR      # en | pt-BR | es
report_language: en  # optional: e.g. chat in Portuguese, file tickets in English
```

No file? Skills reply in the language you write in. Details in [docs/configuration.md](docs/configuration.md).

## 🤝 Contributing

Ideas and new skills are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) or open a **Skill idea** issue.

## 👩‍💻 Author

**Marina Gajego** — QA Engineer exploring how AI agents can raise the bar for software quality.

## 📄 License

[MIT](LICENSE)
