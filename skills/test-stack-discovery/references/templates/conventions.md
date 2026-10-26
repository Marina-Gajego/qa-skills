# `.qa-skills/test-stack/conventions.md` — session 4 template

Rules shared by all session files and the markers are in [../output-index.md](../output-index.md). Keep titles, order, fixed rows and markers exactly as below.

````markdown
<!-- qa-skills:test-stack-conventions v2 -->
# Conventions and rules
Index: `../test-stack.md`

## Shared
### Project rules
| Rule | Source | Followed by the code? |
|---|---|---|
| <rule as written> | <(written: path:line)> | <yes (observed N/M) / partly / no — evidence> |
### Commit and branch conventions
<From commitlint/husky/CI triggers or recent git log, or none found.>

## Suite: <suite>
### Naming
<files, folders, classes, methods, variables, test titles, tags — each with pattern and count.>
### Selectors, requests and assertions
<UI: locator strategy and priority actually used (`getByRole` 15/17…), test-id attribute name, forbidden or legacy styles. API: how requests are built, base path, headers, status/body/schema checks. Assertion style, custom matchers, soft assertions.>
### Waits, timeouts and retries
### Hooks and test structure
<beforeEach/afterEach/Background usage, one or many scenarios per file, describe/grouping, test.step usage.>
### Tags and grouping
### Known defects, skips and flaky tests
<How the team marks them: `test.fail` + comment, `@skip`/`@wip` tags, `test.fixme`, quarantine folders — with evidence.>
### Code style
<indentation, quotes, semicolons, import style and aliases, async style — counts when there's no formatter.>
### Rules for new tests
<8–15 imperative bullets an automation skill can follow directly, each with evidence and `(written: …)` or `(observed N/M …)`: "Import `test`/`expect` from `support/fixtures`, never from `@playwright/test` (observed 3/3 specs, `tests/login.spec.ts:1`)".>
````
