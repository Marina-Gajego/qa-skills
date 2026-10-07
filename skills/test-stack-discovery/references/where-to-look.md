# Where to look

Signals that answer each part of the template, by ecosystem. Use it as a lookup table, not a checklist to read top to bottom — open only what the inventory says exists.

## Contents
- Tests-only vs product repo
- Locating test modules
- Signals by ecosystem (JS/TS, JVM, Python, .NET, Ruby, Go, mobile, performance)
- Cross-cutting (CI, containers, env, reporting)
- Sampling tips
- Never read or copy

## Tests-only vs product repo

| Points to tests-only | Points to product repo |
|---|---|
| Name/description like `*-tests`, `*-automation`, `qa-*`, `e2e-*` | App entrypoints: `src/main/`, `app/`, `server/`, `cmd/`, `main.py`, `Program.cs`, `pages/` + `next.config.*` |
| Almost all code is specs, page objects, steps, support/helpers | Tests are a minority folder or colocated `*.test.*` files |
| baseURL / host points to an app that lives elsewhere | Dockerfile/compose that builds the app itself; migrations; `webServer` starting a local build |
| Dependencies are only test tooling | Runtime dependencies of a web/API framework (React, Spring, Django, Express, FastAPI…) |

A tests-only repo can still have a `docs/` folder or AI-agent folders (`.claude/`, `.agents/`, `_bmad/`, `.github/copilot-*`, `.cursor/`): those don't make it a product repo.

## Locating test modules
- Folders: `e2e/`, `tests/`, `test/`, `src/test/`, `src/it/`, `integration-tests/`, `cypress/`, `playwright/`, `features/`, `specs/`, `qa/`, `automation/`, `perf/`, `load/`.
- File names: `*.spec.*`, `*.test.*`, `*.cy.*`, `*.e2e.*`, `test_*.py`, `*_test.py`, `*_test.go`, `*Test.java`, `*IT.java`, `*Tests.cs`, `*_spec.rb`, `*.feature`, `*.jmx`, k6 scripts importing `k6/http`.
- Monorepos: `workspaces` in `package.json`, `pnpm-workspace.yaml`, `nx.json`/`project.json`, `turbo.json`, `lerna.json`, Maven `<modules>`, Gradle `settings.gradle(.kts)` `include(...)`. A package/module named `e2e`, `tests`, `*-tests`, `acceptance`, `qa` is a strong candidate.
- Count files per candidate; the e2e/API/integration suite is usually what QA automation extends.

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

### Mobile
Appium (capabilities in config/JSON, `wdio.conf` with appium service, java-client), Detox (`.detoxrc`, `e2e/` with jest), Maestro (`.maestro/*.yaml`), Espresso/XCUITest (inside the app's `androidTest`/`UITests` targets).

### Performance
k6 (`import http from 'k6/http'`, `options` with stages/thresholds), JMeter (`*.jmx`, `user.properties`, jmeter-maven-plugin), Gatling (`simulations/`), Locust, Artillery (`*.yml` with `scenarios`).

## Cross-cutting
- **CI:** `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`, `.circleci/config.yml`. Read for the real run command, toolchain version, env vars/secrets *names*, sharding, schedule, artifacts/reports.
- **Containers / app startup:** `docker-compose*.yml`, `Dockerfile`, `Makefile`, `Procfile`, `webServer` in Playwright config, `start-server-and-test` in scripts, README "running locally". In a product repo, also `seeds/`, `migrations/`, `fixtures/` used by tests.
- **Env:** `.env.example`/`.env.sample`/`.env.template` (names only), `process.env.X`, `os.environ`/`os.getenv`, `System.getenv`/`System.getProperty`, `Cypress.env`, `karate.env`. Grep for them to build the variable table.
- **Reporting:** reporter config, `allure-*`, `junit` xml paths, `mochawesome`, `extent`, `pytest-html`; where reports are written (often gitignored).
- **Docs:** README/CONTRIBUTING/`docs/` of the test module, and repo-specific agent context files (`AGENTS.md`, `CLAUDE.md`, `project-context.md`, `.github/copilot-instructions.md`, `.cursor/rules/`) — conventions written down beat conventions inferred, but check that the code still follows them (stale docs are common; when they disagree, report both).

## Sampling tips
- Recently changed files: `git log --name-only --since=<~6 months> -- <test dir>` and pick frequent ones; they reflect the current style.
- Most imported helpers: grep import lines in specs, normalize paths, count, read the top 3–5.
- Convention counts: `grep -c` over the test folder (e.g. `getByRole` vs `getByTestId` vs `locator('css`), `@pytest.mark.` names, `@Tag(`, `test.skip`, `.only`.
- Old vs new style: compare an old file (first commits) with a recent one; if the style changed, the recent one is the model unless the user says otherwise — and that's a fair ❓ question if they're evenly mixed.
- Skip generated or vendor content: `node_modules`, `target`, `build`, `dist`, `.venv`, `__pycache__`, `playwright-report`, `test-results`, `allure-results`, `cypress/videos|screenshots`, lockfile bodies (search them, don't read them).
- Skip AI-agent libraries and output when counting and sampling: `.claude/`, `.agents/`, `.cursor/` (except rules), `.github/copilot-*` (except instructions), `_bmad/`, `_bmad-output/`, `.windsurf/`, similar skill/knowledge folders. Filter them out of `git ls-files` before counting, e.g. `git ls-files | grep -vE '^(\.claude|\.agents|_bmad|_bmad-output)/'`.

## Never read or copy
Values from `.env*` (other than the `.example` templates), storage-state / cookie / session files (`**/.auth/*.json`, `storageState*.json`), keystores and certificates (`*.jks`, `*.p12`, `*.pem`), cloud credential files, `secrets.*`, CI secret values. Hardcoded credentials in test code: record the location and that they're hardcoded, never the value.
