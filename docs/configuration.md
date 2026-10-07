# ⚙️ Configuration

The repository is written in English, but every skill can talk to you — and write its output — in **English, Portuguese (pt-BR) or Spanish**.

## Language preference

Create a `.qa-skills.yaml` file (see [`.qa-skills.example.yaml`](../.qa-skills.example.yaml)):

```yaml
language: pt-BR        # en | pt-BR | es — the language skills talk to you in
report_language: en    # optional — language of bug reports, test cases, etc. Defaults to `language`
```

### Where to put it

| Location | Scope |
|---|---|
| `<project root>/.qa-skills.yaml` | That project. Commit it so the whole team gets the same reports. |
| `~/.qa-skills.yaml` | Your personal default, for every project. |

Skills are installed one folder at a time (e.g. into `~/.claude/skills/`), so the preference lives **outside** the skill folders — that way every installed skill finds it.

### Precedence

1. An explicit request in the conversation. If it clearly targets only the output (*"escreve o bug em inglês"*) it changes just `report_language`; otherwise (*"responde em espanhol"*, *"escreve tudo em inglês"*) it changes both.
2. `.qa-skills.yaml` in the project root
3. `~/.qa-skills.yaml`
4. The language of your message

No file is needed: without one, skills simply reply in the language you write in.

### Why two settings?

A common setup is a team that chats in Portuguese or Spanish but files tickets in English for a distributed dev team. With `language: pt-BR` and `report_language: en`, the skill asks its questions in Portuguese and writes the bug report in English.

## Project context folder (`.qa-skills/`)

Some skills learn things about your project that other skills need later — how your test repo is built, how to reach your QA environment. They save it in a standard folder at the root of **your** project (the test repo, or the product repo that contains the tests), never in this repository:

```
your-test-repo/
├── .qa-skills.yaml        # your preferences (language)
└── .qa-skills/
    ├── test-stack.md      # written by test-stack-discovery · read by automation skills
    └── environment.md     # written by qa-environment-access (planned) · read by exploratory, API… skills
```

- **Created on demand.** The first skill that needs the folder creates it; there's nothing to set up.
- **Commit it.** The files hold no secrets (only variable *names* and file locations), so committing them gives every teammate's agent the same context. Correct them by hand whenever something is wrong — skills keep entries you mark `(confirmed by QA)`.
- **Never overwritten silently.** A skill that finds an existing file writes the new version beside it (`<name>.new.md`), shows what changed and asks before replacing it.
- **Optional for readers.** Each file is a shortcut, not a requirement: a skill that reads one still works without it.

## For skill authors

Every skill should honor this preference. Add this block to your `SKILL.md` (adapt the word "report" to what the skill produces):

```markdown
## Language
Before replying, look for a `.qa-skills.yaml` file — first in the project root, then in the home directory (`~/.qa-skills.yaml`). Use `language` for everything you say to the user and `report_language` (defaults to `language`) for the artifact you produce. An explicit request in the conversation overrides the file: one that clearly targets only the output changes just the output; any other changes both. With neither, use the language of the user's message. A missing file is normal — don't mention it.
```

If the skill produces structured output (templates, labels, status values), add a `references/labels.md` with the fixed translations for `en`, `pt-BR` and `es`, so the same field never gets translated two different ways.

### Writing to `.qa-skills/`

If your skill produces context other skills should reuse, save it in `.qa-skills/` at the root of the user's project — never in the qa-skills repo — following these rules:

1. **One file per skill**, named after what it describes (`test-stack.md`, `environment.md`), with a version marker on the first line (`<!-- qa-skills:<name> v1 -->`) and a fixed structure documented in the skill's `references/`. Section titles stay in English so other skills can find them; prose follows `report_language`.
2. **Create the folder if it's missing.** Don't touch files written by other skills.
3. **Ask before overwriting** — write `<name>.new.md`, show the changes, replace only after the user agrees. Carry forward entries marked `(confirmed by QA)`.
4. **No secrets** — names and locations only, never values.
5. **Never depend on another skill.** You may read another skill's file if it exists, but your skill must work the same without it (skills are installed one by one).

Reports and other deliverables (bug reports, session reports) are not context files — they go wherever the skill says (e.g. `bug-reports/`), not in `.qa-skills/`.
