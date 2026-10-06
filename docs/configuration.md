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

## For skill authors

Every skill should honor this preference. Add this block to your `SKILL.md` (adapt the word "report" to what the skill produces):

```markdown
## Language
Before replying, look for a `.qa-skills.yaml` file — first in the project root, then in the home directory (`~/.qa-skills.yaml`). Use `language` for everything you say to the user and `report_language` (defaults to `language`) for the artifact you produce. An explicit request in the conversation overrides the file: one that clearly targets only the output changes just the output; any other changes both. With neither, use the language of the user's message. A missing file is normal — don't mention it.
```

If the skill produces structured output (templates, labels, status values), add a `references/labels.md` with the fixed translations for `en`, `pt-BR` and `es`, so the same field never gets translated two different ways.
