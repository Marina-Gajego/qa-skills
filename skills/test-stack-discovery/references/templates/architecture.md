# `.qa-skills/test-stack/architecture.md` — session 2 template

Rules shared by all session files and the markers are in [../output-index.md](../output-index.md). Keep titles, order, fixed rows and markers exactly as below.

````markdown
<!-- qa-skills:test-stack-architecture v2 -->
# Architecture
Index: `../test-stack.md`

## Suite: <suite>

### Pattern
<The architectural pattern(s) actually used — Page Object Model, Screenplay, App Actions, service objects / API clients, keyword-driven, BDD with step layer, plain specs — in 2–4 lines, with evidence.>

### Layers
| Layer | Files | Responsibility | Depends on | Evidence |
|---|---|---|---|---|
| <Specs / Features> | <N> | <what lives here> | <fixtures, steps> | <folder> |
| <Fixtures / Step definitions / Hooks> | | | | |
| <Page objects / Components / Services> | | | | |
| <Support: data, DB, API clients, utils> | | | | |

```
<dependency diagram in text, e.g.
spec ──uses──▶ fixtures ──creates──▶ PageObject ──composes──▶ Component
  └────────────uses──────▶ db helpers ◀──── fixtures (cleanup)>
```

### How a test flows
<One real test traced end to end, numbered: the test → the fixture/step that provides X → the page object/service method → framework calls → assertion. Each step with path:line.>

### Object creation and state
<How page objects/services/clients are created and handed to tests (fixture, constructor injection, DI container, `new` in the test, static/singleton); where shared state lives (fixture scope, World, ScenarioContext, module variables); lifecycle (per test, per worker, per scenario).>

### OOP assessment
| Principle | How it shows up | Consistency | Evidence |
|---|---|---|---|
| Encapsulation | <locators/requests private to the class? tests touch raw locators?> | <observed N/M> | |
| Inheritance | <base classes, what they provide, how deep> | | |
| Composition | <components inside pages, clients inside services> | | |
| Abstraction | <methods at business level vs UI level; what a test sees> | | |
| Responsibility split | <assertions in tests vs in page objects; data and DB access separated?> | | |

**Verdict:** <consistent / mostly consistent with deviations / mixed / no clear structure> — <one or two lines with the counts that justify it>.

### Deviations
- <path:line — what deviates from the dominant pattern, and whether it's legacy (old commit) or recent.>

### Assessment notes (opinion, not rules)
<Optional, clearly labeled: risks the design creates for new tests (god class, duplicated locators, layers that leak). Generators don't follow this section; it's for the people.>
````
