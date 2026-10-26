# `.qa-skills/test-stack/environment-and-data.md` — session 5 template

Rules shared by all session files and the markers are in [../output-index.md](../output-index.md). Keep titles, order, fixed rows and markers exactly as below.

````markdown
<!-- qa-skills:test-stack-environment-and-data v2 -->
# Environment, data and CI
Index: `../test-stack.md`

## Shared
### App under test
<How the tests reach the app (baseURL/host per suite) and how it's started for local runs: from the product repo in layouts A/B, with commands and evidence; in layout C, ⚠️ UNCERTAIN + ❓ question. Prerequisites: services, DB, docker-compose, seeds.>
### Configuration and environments
<Config files and what they set; how an environment is selected (env var, profile, CLI flag, config per env).>

| Variable | Used in | Purpose | Required? |
|---|---|---|---|
| <NAME only — never the value> | <path:line> | | |

<Secret-bearing files present, by name only, and whether they're gitignored.>
### CI
<provider, workflow file(s), which suites run on which trigger, toolchain versions, sharding, artifacts/reports — or none found.>

## Suite: <suite>
### Test data
<factories/builders, fixture files, faker, DB seeding/cleanup, API setup calls; where data is created, who cleans it up and when (even on failure?).>
### Authentication
<how tests log in; where credentials come from — env var names or file locations only, never values; how a test opts out (e.g. empty storage state).>
````
