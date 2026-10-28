# Without `.qa-skills/` — a lighter discovery

When the repo has no `.qa-skills/test-stack.md` (or an unknown version of it), learn just enough to write *this* test the team's way. It's narrower than test-stack-discovery: only the suite and layers this test touches. Spend the reading where the test will plug in.

1. **Find the suite** — manifests (`package.json`, `pom.xml`, `build.gradle`, `pyproject.toml`, `*.csproj`), runner configs (`playwright.config.*`, `cypress.config.*`, `cucumber.*`, runner classes, `pytest.ini`/`conftest.py`), and the test folders. Note the language, framework and how tests are run (scripts, README, CI).
2. **Read the documented rules** — README, CONTRIBUTING, agent context files (`AGENTS.md`, `CLAUDE.md`, `project-context.md`, `.github/copilot-instructions.md`), lint/format config. Check the code still follows them; the code shows what's current.
3. **Pick 2–3 model tests** — recent (`git log --format='%h %ad' --date=short -- <file>`), not skipped, in the area closest to the new test. Read them in full, and trace one end to end: test → fixtures/steps → page objects/services → framework calls.
4. **Read the structural code the test will touch** in full — the fixture registry, base classes, the page objects/services/steps for that area, the data factories and cleanup.
5. **Note the conventions with counts** where they matter for this test (file naming, title pattern, locator strategy, assertion style, tags/IDs) — e.g. "`getByRole` in 14/16 locators".
6. **Run the reuse index** — it works the same without the discovery files.

Then follow the sessions as usual, treating your notes as the files. In the delivery, say the tests were written without the discovery files and suggest running test-stack-discovery, so the next automation starts from a full map.
