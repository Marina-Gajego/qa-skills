# Where to look

Signals that answer each part of the templates, by ecosystem. Use it as a lookup table, not a checklist to read top to bottom — open only what the inventory says exists.

## Contents
- Tests-only vs product repo
- Pairing a separate test repo with its product
- Locating suites and telling them apart
- How test cases are written
- Documented rules
- Signals by ecosystem (JS/TS, JVM, Python, .NET, Ruby, Go, Robot Framework, mobile, performance)
- Cross-cutting (CI, containers, env, reporting)
- Coverage map
- Sampling tips
- Never read or copy

## Tests-only vs product repo

| Points to tests-only | Points to product repo |
|---|---|
| Name/description like `*-tests`, `*-automation`, `qa-*`, `e2e-*` | App entrypoints: `src/main/`, `app/`, `server/`, `cmd/`, `main.py`, `Program.cs`, `pages/` + `next.config.*` |
| Almost all code is specs, page objects, steps, support/helpers | Tests are a minority folder or colocated `*.test.*` files |
| baseURL / host points to an app that lives elsewhere | Dockerfile/compose that builds the app itself; migrations; `webServer` starting a local build |
| Dependencies are only test tooling | Runtime dependencies of a web/API framework (React, Spring, Django, Express, FastAPI…) |

A tests-only repo can still have a `docs/` folder or AI-agent folders (`.claude/`, `.agents/`, `_bmad/`, `.github/copilot-*`, `.cursor/`): those don't make it a product repo. A tests-only repo that touches the product's database directly (DB client, SQL, ORM schema) is still tests-only — it just depends on the product's schema.

## Pairing a separate test repo with its product
Look in the other workspace folders first, then in sibling folders of the test repo on disk (same parent directory). Strong signals, best first:
- The test repo's README/CI names the product repo (git URL, folder, docker image) or checks it out in CI.
- Folder or package names match: `shop` / `shop-tests` / `shop-e2e` / `shop-automation`, `LunarPass` / `LunarPassTests`.
- The baseURL/host port matches the product's dev server port (`next dev -p 3000`, `server.port`, `PORT=` in `.env.example`, docker-compose ports).
- Routes, page paths or API endpoints the tests call exist in the product (`/checkout` → `app/checkout/page.tsx`, `/api/orders` → a controller).
- Tables or columns the tests query exist in the product's schema/migrations.

One strong signal or two medium ones are enough to pair — say which ones you used. A name match alone with nothing else is a guess: pair it but flag it as a question. Never pair with a folder you only assume exists.

## Locating suites and telling them apart
- Folders: `e2e/`, `tests/`, `test/`, `src/test/`, `src/it/`, `integration-tests/`, `cypress/`, `playwright/`, `features/`, `specs/`, `qa/`, `automation/`, `api/`, `contract/`, `pact/`, `perf/`, `load/`, `__tests__/`.
- File names: `*.spec.*`, `*.test.*`, `*.cy.*`, `*.e2e.*`, `test_*.py`, `*_test.py`, `*_test.go`, `*Test.java`, `*IT.java`, `*Tests.cs`, `*_spec.rb`, `*.feature`, `*.robot`, `*.jmx`, k6 scripts importing `k6/http`, `locustfile.py`, Gatling `simulations/`.
- Monorepos: `workspaces` in `package.json`, `pnpm-workspace.yaml`, `nx.json`/`project.json`, `turbo.json`, `lerna.json`, Maven `<modules>`, Gradle `settings.gradle(.kts)` `include(...)`. A package/module named `e2e`, `tests`, `*-tests`, `acceptance`, `qa` is a strong candidate.
- **What makes two suites different:** a different type (UI vs API vs unit vs load), runner or config (`jest.config` vs `playwright.config`, surefire vs failsafe), runner project (`projects: [{ name: 'api' }, { name: 'chromium' }]`), or way of being run (separate script, profile, CI job). Same runner but different folders and fixtures (UI specs with page objects vs API specs with `request`) are two suites.
- **Telling the type from the code:** UI tests drive a browser/app (`page.`, `cy.get`, `driver.find`, Appium capabilities); API tests send requests and assert status/body (`request.`, `given().when()`, `httpx`, `supertest`); unit tests import product modules directly and mock their dependencies; component tests mount a component (`mount(`, `render(`); contract tests use Pact/Spring Cloud Contract or validate against a schema/OpenAPI; performance tests define load (stages, VUs, thread groups, `users`/`spawn_rate`).
- Count files and tests per suite (`grep -c "test(\|it("`, `@Test`, `Scenario:` / `Scenario Outline:`, `def test_`).

## How test cases are written
- **Gherkin/BDD:** `*.feature` files; the spoken language from `# language: pt` (keywords `Funcionalidade`, `Cenário`, `Esquema do Cenário`, `Dado`/`Quando`/`Então`) or `# language: es` (`Característica`, `Escenario`, `Dado`/`Cuando`/`Entonces`), English otherwise; `Background`, `Scenario Outline` + `Examples`, tags; how many scenarios per feature; step definitions folder and whether steps are generic ("I send a POST to {string}") or business-level ("I add a product to the cart"). Frameworks: Cucumber (JS/Java), SpecFlow/Reqnroll, Behave, pytest-bdd, Karate, `playwright-bdd`, `cypress-cucumber-preprocessor`.
- **Code-only:** the test titles *are* the test cases — record the pattern (`should … when …`, `deve … quando …`, `CT01 - …`, `[JIRA-123] …`) and language, counting how many follow it.
- **Test-case documents in the repo:** `test-cases/`, `docs/test-cases/`, `casos-de-teste/`, `*.csv`/`*.xlsx` exports, Markdown with "Pré-condição / Passos / Resultado esperado", Robot Framework `*** Test Cases ***`.
- **Traceability and test management:** Jira keys in titles or tags (`@PROJ-123`, `test.info().annotations`), Xray (`xray` reporter, `@TestCaseKey`, `cucumber` JSON upload in CI), TestRail (`testrail-reporter`, `C1234` IDs), Zephyr, Qase, Allure TestOps (`@AllureId`, `allure.id`), Azure Test Plans. A README pointing to an external tool ("cases live in TestRail project X") counts — name it, don't guess its content.

## Documented rules
README and CONTRIBUTING of the test repo/module, `docs/` (architecture, conventions, ADRs), PR template checklist (`.github/pull_request_template.md`), issue templates, agent context files (`AGENTS.md`, `CLAUDE.md`, `project-context.md`, `.github/copilot-instructions.md`, `.cursor/rules/`), lint rules that enforce test style (`eslint-plugin-playwright` `no-wait-for-timeout`, `no-focused-tests`), commit conventions (`commitlint.config.*`, `.husky/`, recent `git log --oneline -30`), branch naming in CI triggers. Written rules beat inferred ones, but stale docs are common: check the code still follows each rule and report both when they disagree.

## Signals by ecosystem

### JavaScript / TypeScript
- **Versions:** `package.json` (`engines`, `devDependencies`), lockfile for the resolved version (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lockb`), `.nvmrc`, `.node-version`, `.tool-versions`, `volta` field, `packageManager` field.
- **Package manager:** the lockfile present (two lockfiles → note it as uncertain). Yarn classic vs berry: `.yarnrc.yml` / `.yarn/` means berry.
- **Frameworks & config:** `playwright.config.*` (testDir, projects, baseURL, storageState, webServer, reporter, retries), `cypress.config.*` (`e2e.baseUrl`, `specPattern`, `supportFile`, `env`), `wdio.conf.*` (framework mocha/jasmine/cucumber, services, capabilities), `jest.config.*`/`vitest.config.*`, `detox.config.*`/`.detoxrc`, `codecept.conf.*`, `nightwatch.conf.*`, `testcafe` in scripts.
- **TypeScript:** `tsconfig.json` (paths aliases used in imports), or TS files without tsconfig (Playwright transpiles on its own).
- **Patterns:** `test.extend` / `base.extend` (custom fixtures), `class .*Page` (page objects), `Cypress.Commands.add` (custom commands / app actions), `test.step`, `test.describe.configure`, `@cucumber/cucumber` + `features/`, `test.use({ storageState })`.
- **Commands:** `scripts` in `package.json`; `npx playwright test <file>`, `--grep @tag`, `--project`, `--headed`, `--ui`, `show-report`; `npx cypress run --spec`, `cypress open`.
- **Lint/format:** `.eslintrc*`/`eslint.config.*` (plugins: `playwright`, `cypress`, `jest`), `.prettierrc*`, `biome.json`, `.editorconfig`.

### JVM (Java / Kotlin)
- **Versions:** `pom.xml` (`maven.compiler.source/target/release`, `java.version`, dependency versions, often in `<properties>`), `build.gradle(.kts)` (`toolchain`, `sourceCompatibility`), `gradle/libs.versions.toml`, `.java-version`, `.sdkmanrc`, Maven/Gradle wrapper files.
- **Frameworks:** JUnit 4 (`junit:junit`, `@Test` from `org.junit`) vs JUnit 5 (`junit-jupiter`, `org.junit.jupiter.api`) — when both are present, check git history (dates, commit messages) before treating it as an open question; TestNG (`testng.xml`, `@Test` from `org.testng`); RestAssured (`given().when().then()`), Selenium/Selenide, Appium java-client, Cucumber (`cucumber-java`, `@CucumberOptions`, `src/test/resources/features`), Karate (`*.feature` + `karate-config.js`), Serenity (Screenplay: `Actor`, `Task`, `Question`), Testcontainers, WireMock, AssertJ/Hamcrest.
- **Runner & commands:** surefire (`*Test`) vs failsafe (`*IT`, `mvn verify`), Maven profiles (`-P`), `-Dtest=Class#method`, `-Dgroups`/`-Dcucumber.filter.tags`, `./gradlew test --tests`, system properties for env (`-Denv=qa`).
- **Config/env:** `src/test/resources/*.properties|yml`, `application-<profile>.yml`, `karate-config.js` (`karate.env`), `serenity.conf`, Owner/typesafe config classes.

### Python
- **Versions:** `pyproject.toml` (`requires-python`, deps under `[project]`, `[tool.poetry]`, `[dependency-groups]`), `requirements*.txt`, `poetry.lock`, `uv.lock`, `Pipfile(.lock)`, `.python-version`, `tox.ini`, `noxfile.py`.
- **pytest:** `pytest.ini`, `[tool.pytest.ini_options]`, `setup.cfg`, `conftest.py` at each level (fixtures, hooks, `pytest_addoption` for `--env`/`--base-url`), markers (`@pytest.mark.<name>` + registered `markers`), `parametrize`, plugins (`pytest-playwright`, `pytest-xdist`, `pytest-bdd`, `pytest-html`, `allure-pytest`, `pytest-rerunfailures`).
- **Others:** Robot Framework (`*.robot`, `resources/`, keywords), Behave (`features/steps/`), `unittest`, Selenium, `requests`/`httpx` API clients, `factory_boy`/`faker`/`pydantic` models, Locust (`locustfile.py`).
- **Commands:** `pytest -m <marker>`, `-k <expr>`, `path::test_name`, `-n auto`; `tox -e`, `make test`.

### .NET
`*.csproj` (`TargetFramework`, `PackageReference` for NUnit/xUnit/MSTest, SpecFlow/Reqnroll, Playwright for .NET, RestSharp), `*.runsettings`, `appsettings.*.json`, `dotnet test --filter`.

### Ruby
`Gemfile`/`Gemfile.lock`, `.ruby-version`, RSpec (`spec/`, `spec_helper.rb`, `.rspec`), Capybara, Cucumber (`features/`, `support/env.rb`), `bundle exec rspec --tag`.

### Go
`go.mod` (Go version), `*_test.go`, testify, `go test ./... -run`, build tags.

### Robot Framework
`*.robot` files (`*** Settings ***`, `*** Variables ***`, `*** Test Cases ***`, `*** Keywords ***`), `resources/` with keyword files, libraries in `Library` lines (Browser, SeleniumLibrary, RequestsLibrary, AppiumLibrary), `requirements.txt`/`pyproject.toml` for versions, `robot --include <tag> --variable ENV:qa`, `[Tags]`, `[Documentation]`, Gherkin-style keywords (`Given`/`When`/`Then` prefixes) used as test-case writing style.

### Mobile
Appium (capabilities in config/JSON, `wdio.conf` with appium service, java-client), Detox (`.detoxrc`, `e2e/` with jest), Maestro (`.maestro/*.yaml`), Espresso/XCUITest (inside the app's `androidTest`/`UITests` targets).

### Performance
k6 (`import http from 'k6/http'`, `options` with stages/thresholds), JMeter (`*.jmx`, `user.properties`, jmeter-maven-plugin), Gatling (`simulations/`), Locust, Artillery (`*.yml` with `scenarios`).

## Cross-cutting
- **CI:** `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`, `.circleci/config.yml`. Read for the real run command, toolchain version, env vars/secrets *names*, sharding, schedule, artifacts/reports.
- **Containers / app startup:** `docker-compose*.yml`, `Dockerfile`, `Makefile`, `Procfile`, `webServer` in Playwright config, `start-server-and-test` in scripts, README "running locally". In a product repo, also `seeds/`, `migrations/`, `fixtures/` used by tests.
- **Env:** `.env.example`/`.env.sample`/`.env.template` (names only), `process.env.X`, `os.environ`/`os.getenv`, `System.getenv`/`System.getProperty`, `Cypress.env`, `karate.env`. Grep for them to build the variable table.
- **Reporting:** reporter config, `allure-*`, `junit` xml paths, `mochawesome`, `extent`, `pytest-html`; where reports are written (often gitignored).
- **Docs:** see Documented rules above.

## Coverage map
- **Areas from the tests:** feature folders (`tests/cart/`), `describe`/`Feature:` titles, tags (`@cart`), page objects and API clients named after areas, routes/endpoints in `goto`/`request` calls. Group by the names the team uses; count tests per area and per suite.
- **Areas from the product (layouts A/B):** Next/Nuxt/SvelteKit route folders (`app/**/page.tsx`, `pages/`), React Router route tables, Express/Nest/Spring/FastAPI/Django route or controller definitions, OpenAPI paths. Compare with the areas the tests touch; list the uncovered ones as observed, not as a verdict — a product area can be covered by tests you didn't find (another repo, manual testing).

## Sampling tips
- Recently changed files: `git log --name-only --since=<~6 months> -- <test dir>` and pick frequent ones; they reflect the current style.
- Most imported helpers: grep import lines in specs, normalize paths, count, read the top 3–5.
- Convention counts: `grep -c` over the test folder (e.g. `getByRole` vs `getByTestId` vs `locator('css`), `@pytest.mark.` names, `@Tag(`, `test.skip`, `.only`.
- Old vs new style: compare an old file (first commits) with a recent one; if the style changed, the recent one is the model unless the user says otherwise — and that's a fair ❓ question if they're evenly mixed.
- Skip generated or vendor content: `node_modules`, `target`, `build`, `dist`, `.venv`, `__pycache__`, `playwright-report`, `test-results`, `allure-results`, `cypress/videos|screenshots`, lockfile bodies (search them, don't read them).
- Skip AI-agent libraries and output when counting and sampling: `.claude/`, `.agents/`, `.cursor/` (except rules), `.github/copilot-*` (except instructions), `_bmad/`, `_bmad-output/`, `.windsurf/`, similar skill/knowledge folders. Filter them out of `git ls-files` before counting, e.g. `git ls-files | grep -vE '^(\.claude|\.agents|_bmad|_bmad-output)/'`.

## Never read or copy
Values from `.env*` (other than the `.example` templates), storage-state / cookie / session files (`**/.auth/*.json`, `storageState*.json`), keystores and certificates (`*.jks`, `*.p12`, `*.pem`), cloud credential files, `secrets.*`, CI secret values. Hardcoded credentials in test code: record the location and that they're hardcoded, never the value.
