# `.qa-skills/test-stack/test-case-writing.md` — session 3 template

Rules shared by all session files and the markers are in [../output-index.md](../output-index.md). Keep titles, order, fixed rows and markers exactly as below.

````markdown
<!-- qa-skills:test-stack-test-case-writing v2 -->
# Test case writing
Index: `../test-stack.md`

## Shared
### Test-case documents
<Where written test cases, specs or Gherkin designs for people live (repo folders, external tool named in README), their format and IDs, whether automated tests trace to them — or none found.>
### Traceability
<Requirement/Jira/Xray/TestRail/Zephyr keys in titles, tags or annotations; reporters or CI steps that sync results — or none found.>

## Suite: <suite>
### Format
| Item | Value | Evidence |
|---|---|---|
| Format | <code-only titles / Gherkin `.feature` / keyword-driven / data-driven tables> | |
| Language | <spoken language of titles, scenarios and steps, e.g. pt-BR with `# language: pt`> | |
| Title / scenario pattern | <e.g. "Deve <resultado> quando <condição>", `CT01 - …`, Given/When/Then> | |
| Step titles | <`test.step` phrasing, Gherkin step phrasing, or n/a> | |
| Parametrized cases | <Scenario Outline + Examples, `for … of` loops, `@ParameterizedTest`, `parametrize`…> | |

<2–4 lines quoting typical titles/scenarios exactly as written.>

### Gherkin structure
<Only for BDD suites — otherwise `n/a — no .feature files`. Features per domain, Background usage, Scenario vs Outline counts, tags, step style (declarative business vs imperative UI) with counts, generic vs specific steps, how many steps per scenario.>

### From scenario to code
<Only for BDD suites. How a step text maps to a step-definition method (one class per feature/domain, cucumber expressions vs regex, parameter types), how step classes share state, and what the step method calls in the layer below — with one real example.>
````
