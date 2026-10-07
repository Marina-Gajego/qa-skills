---
name: test-stack-discovery
description: Maps how the user's own test automation repository is built — language and versions, frameworks (Playwright, Cypress, Selenium, WebdriverIO, RestAssured, Karate, Appium, Detox, k6, JMeter, Jest, pytest, JUnit…), how to run it, folder structure, patterns (Page Object, Screenplay, fixtures, factories, BDD), naming and selector conventions, environment config, test data, auth, CI — with file:line evidence for every claim, and picks 1–2 reference tests to imitate. Saves it as `.qa-skills/test-stack.md` in that repo so automation skills write code that looks like the team wrote it. Use whenever the user wants to understand, map, document, onboard onto or summarize a test/automation project or the test module of a product repo, or before writing new automated tests in a codebase whose conventions aren't known yet — e.g. "analyze my test repo", "what's the stack of this automation project", "learn our test conventions", "entende meu projeto de testes", "mapeia a stack de automação", "como esse repo de testes funciona?", "analiza mi repositorio de pruebas". Read-only: never runs the tests or copies secrets.
---

# Test Stack Discovery

Learn how the user's test repository really works and write it down in a stable file that other skills read before generating test code. The goal is fidelity: a new test written from this file should look like the team wrote it. This skill **reads and documents** — it never runs tests, installs dependencies or edits the user's code; the only file it writes is `.qa-skills/test-stack.md`.

**What to read:** [references/output-template.md](references/output-template.md) always (it is the contract other skills parse); [references/where-to-look.md](references/where-to-look.md) while investigating; [references/labels.md](references/labels.md) only when talking to the user in a language other than English.

## Language
Look for `.qa-skills.yaml` in the analyzed repo's root, then `~/.qa-skills.yaml`. `language` is for what you say to the user; `report_language` (default: `language`) is for the prose inside `test-stack.md`. Section titles, fixed Stack rows and markers in the file are always in English, because other skills look them up by name. An explicit request overrides the file — one that targets only the file changes only the file; any other changes both. Otherwise use the language of the user's message. Don't mention a missing file. Code, identifiers, test titles and messages are quoted as they are, never translated.

## Source fidelity
Another skill will generate code from this file without double-checking it. A guessed framework version, an assumed `npm` when the team uses `yarn`, or a "Page Object" claim based on one file produces code the team has to rewrite — or worse, code that looks right and quietly breaks their conventions. An honest `⚠️ UNCERTAIN` costs far less.

- **Every claim carries evidence** as `path:line` (relative to the repo root), or `path` for whole-file facts (e.g. "lockfile present"). A commit (`a1b2c3d "Move new tests to JUnit 5"`) is valid evidence for *when* a convention changed. Patterns observed across files say how many and of what: "`test.step` in 7/8 sampled specs", "`getByRole` in 31/34 locator calls".
- **Declared beats inferred.** A config value or dependency is a fact. A convention seen in samples is an observation — say so with the count. Something you can't back with a file goes to **Uncertainties**, marked `⚠️ UNCERTAIN`, with what you checked.
- **Never invent:** versions not in a manifest/lockfile/toolchain file, project scripts/profiles/flags that don't exist, environments or env vars not referenced in code, CI that isn't there, how the app under test is started when the repo doesn't say. Two things are allowed because they can't send anyone the wrong way: a command built from something declared (a Maven profile in the pom → `-Psmoke`, with the pom line as evidence), and the tool's own standard CLI syntax for a row the repo doesn't document (e.g. running one file) — labeled `(standard <tool> CLI, not documented in repo)`.
- **Secrets never leave their file.** Record only *names* and *locations*: env var names, "credentials are hardcoded in `support/users.ts:9`", "`playwright/.auth/user.json` is generated storage state". Don't open `.env`, storage-state/cookie files, keystores or credential files beyond what's needed to list variable names; never copy a password, token, key, cookie, connection string with credentials, or a test-account password into the file or the chat (a test username or email alone isn't a secret). Non-secret config values — `localhost` URLs, timeouts, browser lists, base URLs in committed config — can be quoted.

## 1. Find the target
- **The user gave a path** → use it.
- **Otherwise** look at the folders open in the workspace (working directory plus added dirs). Skip folders that are only a skill collection (mostly `skills/*/SKILL.md`, no test code — like the qa-skills repo itself). A test repo that happens to contain `.claude/`, `.agents/`, `_bmad/` or other AI-agent folders is still a test repo.
- One candidate with test code → use it, no question. Several → ask **one** question listing them. None → ask **one** question for the path, mentioning they can add it with `/add-dir <path>` (Claude Code) or "Add folder to workspace".

**AI-agent content inside the target.** Agent skill libraries, knowledge bases and generated agent output are not part of the suite — leave them out of the inventory counts (they can outnumber the real code) and don't mine them for conventions; generic advice there says nothing about how *this* team writes tests. The exception is a context file written for this repo — `AGENTS.md`, `CLAUDE.md`, `project-context.md`, `.github/copilot-instructions.md`, `.cursor/rules` — which is the team's documented conventions: read it like a CONTRIBUTING, cite it, and check the code still follows it (when they disagree, report both; the code shows what's current).

## 2. Tests-only repo or product repo with tests?
Decide from the file listing (see where-to-look.md): a tests-only repo is mostly specs, page objects, support code and test config; a product repo has application source with tests as a part of it.

For a **product repo**, locate the test module(s) first — `e2e/`, `tests/`, `test/`, `src/test/`, `cypress/`, `playwright/`, `integration/`, `*.spec.*`, `*.test.*`, `test_*.py`, `*Test.java`, a workspace package like `packages/e2e` — and analyze **only those**. From the product, read just what the tests depend on: how to start the app locally, seeds/migrations the tests use, env vars the tests read, docker-compose services. If there are several test modules (e.g. dev unit tests next to a QA e2e suite), document each in Stack/Structure, and go deep on the one the user named — or, if they named none, the end-to-end / API / integration suite, which is what QA automation extends. Note in Summary which one is the focus.

## 3. Investigate by sampling
Don't read the whole repo — an agent that reads 200 files runs out of attention before it writes anything useful. Work in this order and stop when each section of the template can be filled or marked uncertain:

1. **Inventory** — list tracked files (`git ls-files` when it's a git repo; otherwise a find that skips `node_modules`, `target`, `build`, `dist`, `.venv`, reports and caches). Count files by folder and extension; that shape answers most of step 2 and tells you where the tests are.
2. **Manifests and configs** — package/build files, lockfiles, toolchain versions, test-runner config, lint/format config, CI workflows, the README/CONTRIBUTING of the test module. These give the declared facts.
3. **Tests** — sample 2–3 tests per kind (UI, API, unit, BDD feature + steps…), preferring recently changed (`git log`) and medium-sized files over the biggest or oldest. Also look at 1–2 old ones if they look different — that's how you spot a convention that changed.
4. **Shared code** — find the most imported helpers (grep import/require/use lines across the specs and count) and read the top few: base pages, fixtures, factories, API clients, auth setup, hooks/conftest.
5. **Confirm conventions with grep** instead of more reading: selector strategy (`getByRole` vs `data-testid` vs CSS/XPath), tags, `test.step`, skips, retries, waits.

15–30 file reads is a ceiling for a typical repo, not a target: a tiny repo can simply be read whole, and a big monorepo may need a bit more — as long as each read answers a question you still have.

## 4. Choose reference tests
Pick 1 or 2 tests a new test should imitate: they use the dominant patterns (the same fixtures, page objects, data factories, assertion style), are recent, readable and not skipped or quarantined. A reference can be a whole file or one test inside a big spec (`path:lines — "test title"`). If the suite has two clearly different kinds (e.g. UI and API), pick one of each. Say *why* each one is the model. Under "Don't imitate", list legacy files and also in-file anti-patterns a generator could copy by accident (a duplicated credential, an unused helper, a hard wait).

## 5. Write `.qa-skills/test-stack.md`
Follow [references/output-template.md](references/output-template.md) exactly: same section order and titles, same fixed rows, the header line, evidence on every row. Keep it dense — it's a reference card for another agent, not an essay; ~100–200 lines for a typical repo.

- **No file yet** → create `.qa-skills/` in the analyzed repo's root and write it.
- **File already exists** → don't overwrite: the team may have corrected it by hand. Write the new version beside it as `.qa-skills/test-stack.new.md`, and in step 6 show what changed (`diff -u` trimmed to the meaningful changes; a bullet list when most of the file changed) together with the replace question, in the same reply as any other questions. Replace only after they say yes; then delete the `.new.md`. Carry forward entries marked `(confirmed by QA)`; if the code now contradicts one (not just partly deviates — note that inline), flag it instead of silently dropping it.
- Don't touch any other file in `.qa-skills/` (e.g. `environment.md`, written by another skill). If `environment.md` exists you may read it for context, but this skill must work the same without it, and environment access details (QA URLs, accounts, tokens) belong there, not here.

## 6. Check, then deliver
Re-read the file as a skeptical automation engineer about to generate code from it: every row traces to a file; nothing secret is in it; uncertainties are listed, not smoothed over.

Then reply with a **short** summary in chat (labels in labels.md): focus module, stack in one line, how to run, the main conventions, the reference test(s), and the file path (the `.new.md` one if it's pending confirmation). Ask a question **only** when the answer can't be found in the code or git history and changes how new tests should be written — typically two conflicting conventions where you can't tell which is current, or a test module choice. At most 3 questions, numbered so the user can answer in one line. Everything else uncertain stays in the file's Uncertainties section without bothering the user. When they answer, update the file and mark the entry `(confirmed by QA)`.

Bugs you happen to notice in the product or tests (a route the specs call that doesn't exist, a missing dependency) aren't this skill's job: one line in Uncertainties if they affect how tests run, no investigation.

End with one line inviting corrections ("Anything wrong or missing? Tell me and I'll update the file.") and, if the repo is shared, that the file contains no secrets and can be committed so the whole team's agents use it.

## Not this skill?
If the user wants a test written, fixed or reviewed, a bug reported, or the QA environment checked, say in one line that this skill maps the test stack, then help with what was asked. If they want new tests written in an unfamiliar repo, offer to run this discovery first — it's what makes the generated code match.
