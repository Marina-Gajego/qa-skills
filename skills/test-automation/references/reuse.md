# Reuse — finding what exists before writing anything

The goal of session 2 is that every line of the new test is either a call to something that already exists or a new piece that provably didn't exist. This file says where to look, how to decide, and how far you may change existing code to make reuse possible.

## The reuse index
`scripts/reuse_index.py` (stdlib Python, read-only) prints, in one call:
- every BDD step definition with `file:line`, keyword, expression and how many feature steps use it;
- definitions no feature uses (reuse candidates, or dead code), and feature steps no definition matches;
- fixtures (`test.extend` keys, `@pytest.fixture`), classes with their public methods and fields, exported functions.

```bash
python3 -I <skill>/scripts/reuse_index.py <test repo>                       # full index
python3 -I <skill>/scripts/reuse_index.py <test repo> --paths e2e src/test  # only the test module(s)
python3 -I <skill>/scripts/reuse_index.py <test repo> --grep cart purchase  # only entries mentioning these words
python3 -I <skill>/scripts/reuse_index.py <test repo> --check path/new.feature  # REUSES / UNDEFINED (+ ~similar) / AMBIGUOUS
```

It's a lead, not proof: it matches step text with regexes built from Cucumber expressions and reads classes with regexes, so custom parameter types, decorators or unusual formatting can hide something. Before you decide `create`, also grep the repo for the domain words and the endpoint/route/label involved. If Python isn't available, do the same with `grep -rn` on step annotations, `class`, `export` and fixture definitions.

## Where to look, by layer

| Need | Look for | Typical places |
|---|---|---|
| A Gherkin step | the step's action and object (`--grep`), then `--check` | step-definition folders, `Commons`/`Common`/`shared` step classes first — generic steps (status code, message, contract/schema) live there |
| A page / screen action | a page object or component with the screen's name, the route in `goto` calls, the label/test id in locators | `pages/`, `page-objects/`, `components/`, `screens/` |
| A UI element seen on several pages | component classes (navbar, toast, modal, table, form) | `components/`, `componentes/`, fields composed inside page objects |
| An HTTP call | the endpoint path in a paths/routes constants class, service/client classes | `services/`, `clients/`, `api/`, `paths`/`endpoints` constants |
| Test data | factories, builders, fixture files, faker helpers, `valid<X>()` functions | `factory/`, `factories/`, `builders/`, `data/`, `support/*Data.*`, `fixtures/*.json` |
| Setup / cleanup | fixtures, hooks, DB helpers, API setup helpers | `fixtures.*`, `hooks/`, `support/db.*`, `@Before/@After` |
| Assertions | shared assertion steps, custom matchers, schema files | `Commons` steps, `matchers/`, `schemas/` |
| Auth | setup projects, storage state, login helpers, token steps | `auth.setup.*`, `login*` fixtures/steps |

Search by **behavior**, not only by name: the method that fills the form you need may be called `fillMissionData`, `preencherFormulario` or `create`, and live in a page named after a different route that renders the same form.

## Deciding

| Situation | Decision |
|---|---|
| Something does exactly this | **reuse** as is |
| A step exists with different words for the same action | **reuse** — rewrite your step to its exact wording |
| It does almost this; one value is hard-coded where you need another | **extend** — add a parameter with a default, an overload, or a new method beside it; current callers keep working unchanged |
| A class for this screen/endpoint exists but lacks the action | **extend** — add the method/locator to that class, not a new class |
| Two pages render the same widget and only one class models it | **extend** — reuse the existing class; if it's tied to one page, move the shared part into a component the team's style already uses (see below) |
| Nothing does it, and the closest thing belongs to another domain | **create**, following the recipe for that artifact |

Never copy a method, locator, payload or step body into a new place and adapt it. That's the duplication this skill exists to prevent, even when it's "just three lines".

## Changing existing code
Reuse sometimes needs a small change to code other tests use. That's fine — it's what the team would do — within these limits:
- **Allowed:** adding a method, field, locator, optional parameter, overload, factory variant or constant; adding a fixture to the registry; moving a block that two pages share into a component *when the repo already uses components* (and the old class delegates to it, keeping its public members so existing tests don't change).
- **Not without asking:** renaming or removing anything public, changing a method's behavior or required parameters, changing a shared step's wording, restructuring a base class, touching runner/build config beyond what a recipe says to wire.
- **Allowed runner change:** isolating a new test that destroys shared state (see SKILL.md → "Don't break the suite") — e.g. a separate Playwright project with `dependencies` on the main one, or `testIgnore` for that file in the main project. Keep it minimal and report it.
- **The one behavior change allowed:** fixing a clear bug in existing test code that the new test depends on (see SKILL.md, session 3) — small, backed by a source, and reported on its own with the existing tests it affects.
- Every change to an existing file is listed in the delivery with the reason, and validation must show the existing tests still compile/list.

If the right reuse needs a refactor beyond these limits, do the most reuse you can within them, and propose the refactor in the delivery questions.

## Red flags in your own diff
- a new step whose text differs from an existing one by a word or two;
- a locator, test id, URL, endpoint or message string that already appears somewhere in the repo;
- a new class whose name differs from an existing one only by suffix/prefix (`CartService` vs `CartsService`, `EditMissionPage` next to a `MissionFormPage`);
- a payload built by hand where a factory/builder for that model exists;
- setup/cleanup written inside a test when a fixture or hook already does it;
- a new helper in a test file that other tests could use (move it where the team keeps helpers) — or the opposite: extracting something the team always keeps inline.
