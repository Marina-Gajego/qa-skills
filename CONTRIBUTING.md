# Contributing

Thanks for your interest in improving **QA Skills**!

## Reporting a problem
Something didn't work as expected? Open an issue using the **Bug report** template. Tell us which skill and AI tool you used, what you asked, what you expected and what happened.

## Suggesting an idea
Open an issue using the **Skill idea** template. Describe the QA problem, who it helps, and which tools/MCPs it could use.

## Small fixes
Typos, unclear wording and broken links don't need an example or a prior issue — just open a pull request.

## Adding a skill
1. Create a folder under `skills/` using kebab-case: `skills/<skill-name>/`.
2. Create `skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter. Use [`bug-report-writer`](skills/bug-report-writer/SKILL.md) as a reference.
3. Put long checklists, heuristics or examples in `references/` and helper scripts in `scripts/`.
4. Add the standard **Language** block so the skill honors `.qa-skills.yaml` — see [docs/configuration.md](docs/configuration.md#for-skill-authors). If it produces structured output, include a `references/labels.md` with `en`, `pt-BR` and `es` translations.
5. If the skill saves context other skills can reuse, write it to `.qa-skills/` in the user's project, following the rules in [docs/configuration.md](docs/configuration.md#writing-to-qa-skills).
6. Add the skill to the catalog in `README.md`.
7. Open a pull request (fork the repo, create a branch, push, and open the PR against the default branch) with an example of the skill in action (prompt + result).

## Guidelines
- **One skill, one job.** Keep each skill focused on a single QA practice.
- **Write a great `description`.** It decides when the agent uses the skill — say *what* it does and *when* to use it.
- **Be tool-agnostic when possible.** Mention preferred tools/MCPs, but provide fallbacks.
- **Show, don't just tell.** Include examples of good output.
- **Write in English, reply in the user's language.** Skill files are in English; the output follows the user's language preference.
- **No secrets.** Never commit credentials, tokens or real customer data.
