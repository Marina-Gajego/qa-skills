# 🧪 QA Skills

> An open collection of QA **skills** — reusable instructions that help AI agents (Claude, Copilot, Codex, Gemini and others) with quality work, with a human always reviewing and approving the result.

Instead of a library of code, this repository is made of **know-how**: each skill packages a QA practice so an AI agent can execute it consistently, using MCP servers and the tools your team already uses along the way.

**Status:** 🚧 Early stage — four skills available today, more being added over time.

---

## 💡 The idea

There is no fixed flow to follow: each skill is independent and can be used on its own or combined with others, whenever it makes sense for your context. Pair skills with MCP servers (browser automation, issue trackers, API clients, repositories) and the agent stops being a chatbot and becomes a QA teammate.

## 🗂️ Skill catalog

Skills available **today**:

| Category | Skill | Description |
|---|---|---|
| Discovery | [`test-stack-discovery`](skills/test-stack-discovery/SKILL.md) | Study how your tests are built — inside the product repo or in a separate test repo — in focused sessions: stack and how to run every suite (e2e, API, unit, performance…), the architecture and how consistently it follows OOP, how test cases are written (Gherkin, titles, Jira/Xray keys), naming/selector conventions and team rules, step-by-step recipes to add tests, page objects, steps and fixtures the team's way, plus data, auth, environments, CI and coverage. `file:line` evidence for every claim. Saves it in `.qa-skills/` in your repo so other skills write tests that look like your team wrote them. Read-only: never runs tests or copies secrets. Takes a while on purpose (≈8–12 min on a mid-size repo). **Model:** use your strongest model (e.g. Opus) for the first discovery of a repo — it catches more (in our tests, a real bug in the test code and the full set of recipes); a lighter model (e.g. Sonnet) used ~30% fewer tokens at a lower price per token and is a good fit for re-runs that update existing files. |
| Automation | [`test-automation`](skills/test-automation/SKILL.md) | Write new automated tests in your repo the way your team already writes them — test case first (a Gherkin scenario in BDD suites, test and step titles in code-only ones), then the step definitions, page objects, services and fixtures behind it. Before writing anything it maps what already exists and reuses it (a bundled script finds near-duplicate steps), so it doesn't add duplicate steps, locators or requests; you get a reuse map showing what was reused, extended and created. Reads the `.qa-skills/` files from `test-stack-discovery` (and does a lighter discovery without them), runs compile/dry-run checks, then the new tests alone and with the suite when the environment is safe to use (isolating tests that would break shared state, like a global logout). Writes code only — never commits. Validated on Playwright + TypeScript (UI) and Cucumber + REST Assured (Java API): generated tests passed against the real apps, and existing suites kept passing; other stacks are covered by the instructions but not validated yet. |
| Testing | [`exploratory-testing`](skills/exploratory-testing/SKILL.md) | Run a real exploratory session (SBTM) on a web app, API, mobile or desktop app — driving the product through MCP tools (Playwright MCP by default) — and get a session report with charter, notes, defects with evidence, questions and next charters. Warns you when the tools to reach the product aren't connected. Validated on web (Playwright MCP) and REST APIs (`curl`); mobile and desktop targets are not validated yet. |
| Report | [`bug-report-writer`](skills/bug-report-writer/SKILL.md) | Turn any evidence (notes, logs, failed tests) into a clear, reproducible, Jira-style bug report — built strictly from what you provide, with gaps marked instead of invented. Delivers in chat, as a Markdown file, or straight into your tracker via MCP. |

More skills (requirements analysis, test design, code review, performance…) are planned. Have an idea? Open a **Skill idea** issue.

## 🔗 How the skills fit together

Every skill works on its own, but some of them hand context to each other:

```
test-stack-discovery ──writes .qa-skills/──▶ test-automation ──failing test──▶ bug-report-writer
                                                                                     ▲
exploratory-testing ─────────────────defects found in the session────────────────────┘
```

- **`test-stack-discovery` → `test-automation`.** Discovery saves what it learns about your test repo (stack, architecture, conventions, recipes) in `.qa-skills/`. Automation reads those files to write tests that look like your team's. If the files aren't there, Automation does a lighter discovery of its own, so you don't have to run Discovery first.
- **`test-automation` / `exploratory-testing` → `bug-report-writer`.** When a new test or an exploratory session finds a real defect, the report writer turns that evidence into a ticket.

Shared context lives in your project's `.qa-skills/` folder — see [docs/configuration.md](docs/configuration.md#project-context-folder-qa-skills).

## 📁 Repository structure

```
qa-skills/
├── skills/                 # One folder per skill, each with a SKILL.md
│   └── <skill-name>/
│       ├── SKILL.md        # Instructions + metadata (required)
│       ├── references/     # Checklists, heuristics, templates, labels (optional)
│       ├── scripts/        # Helper scripts, Python stdlib only (optional)
│       └── evals/          # Eval cases: prompt.md + case.yaml + graders/ (optional)
├── .claude/skills/         # Symlinks to skills/, so Claude Code loads them when opened here
├── .mcp.json               # Playwright MCP, loaded by Claude Code when opened here
├── docs/
│   ├── configuration.md    # Language preference (.qa-skills.yaml) and the .qa-skills/ folder
│   └── mcp-and-tools.md    # MCP servers and tools the skills rely on
├── .qa-skills.example.yaml # Preferences template (language)
├── .github/ISSUE_TEMPLATE/ # "Bug report" and "Skill idea" issue templates
├── CONTRIBUTING.md
└── LICENSE
```

Skills follow the open **Agent Skills** format (a folder with a `SKILL.md` containing `name` and `description` frontmatter), so the same skill can be reused across different AI tools.

## 🚀 Using a skill

1. Copy (or symlink) the skill folder into your agent's skills directory — for example `~/.claude/skills/` for Claude Code. To install all of them at once:
   ```bash
   for s in /path/to/qa-skills/skills/*/; do ln -s "$s" ~/.claude/skills/; done
   ```
   Or just open Claude Code inside this repository: the skills (`.claude/skills/`) and the Playwright MCP (`.mcp.json`) are already wired up.
2. Ask the agent for the task in natural language (e.g. *"run an exploratory session on the checkout flow"*). The agent loads the skill automatically based on its description.
3. Point the agent at what you want to work on: open your project folder together with the skill (in Claude Code, start in your project or run `/add-dir <path>`), or just give it a URL. This repository never contains your stack — each skill discovers your project's setup on its own.
4. Connect the MCP servers listed in the skill for the best results.

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
