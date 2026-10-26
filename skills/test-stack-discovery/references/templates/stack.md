# `.qa-skills/test-stack/stack.md` — session 1 template

Rules shared by all session files and the markers are in [../output-index.md](../output-index.md). Keep titles, order, fixed rows and markers exactly as below.

````markdown
<!-- qa-skills:test-stack-stack v2 -->
# Stack and execution
Index: `../test-stack.md`

## Suite: <suite>
Type: <type> · path: <folder(s) or glob>

### Stack
| Item | Value | Evidence |
|---|---|---|
| Language | <language + version, or version ⚠️ UNCERTAIN> | <path:line> |
| Runtime / toolchain | <Node 20 / JDK 17 / Python 3.12 …> | <path:line> |
| Package manager / build tool | <npm / yarn classic / pnpm / Maven / Gradle / pip / poetry / uv …> | <lockfile or build file> |
| Test framework(s) | <name + declared version (+ locked version if different)> | <path:line> |
| Test runner | <playwright test / jest / pytest / surefire / failsafe …> | <path:line> |
| Assertion library | <built-in expect / AssertJ / Hamcrest / chai …> | <path:line> |
| Other test libraries | <faker, DB client, HTTP client, BDD, mocking, schema validation …> | <path:line> |
| Reporting | <html, allure, junit xml …> | <path:line> |
| Lint / format | <eslint/prettier/checkstyle/ruff…, or none found> | <path> |
<extra rows below the fixed ones if useful, e.g. "BDD", "Browsers / devices", "Non-test dependencies">

### How to run
Commands come from the repo (scripts, README, CI, build files); they were **not executed**.

| Goal | Command | Evidence |
|---|---|---|
| Install | | |
| Run all | | |
| Run one file / test | | |
| Run by tag / group | | |
| Debug / headed / UI mode | | |
| Open report | | |

### Structure
```
<suite root>/
├── <folder>/        # <role> (<N files>) — new <kind> files go here
│   └── <subfolder>/ # <role>
└── <config file>    # <role>
```
<Only folders that matter for writing tests, 2–3 levels deep. Counts exclude AI-agent folders; mention ignored noise in one line.>
````
