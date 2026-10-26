# Architecture assessment

How to read a test codebase's design in session 2 and judge, with evidence, how well it holds together. The goal isn't to grade the team — it's to know which pattern a new test must follow and which parts of the code would mislead a generator.

## Contents
- Recognizing the pattern
- Reading each OOP principle
- Signs of a consistent design vs a messy one
- Measuring consistency
- Choosing the pattern new tests follow

## Recognizing the pattern

| Pattern | What you see in the code |
|---|---|
| **Page Object Model** | One class per page/screen holding its locators and actions (`class LoginPage`, constructor receives `page`/`driver`); tests call methods, not raw locators. Variants: components/fragments for shared widgets (navbar, modal, table), a `BasePage` with common helpers, fluent methods returning the next page. |
| **Screenplay** | Actors (`Actor.named`), Tasks/Interactions (`performs`, `attemptsTo`), Questions (`asksFor`, `Ensure.that`), Abilities (`BrowseTheWeb`, `CallAnApi`) — Serenity BDD / Serenity/JS. |
| **App Actions** | Tests set state through the app's own API or internals (`cy.window().its('store')`, custom commands that call APIs) instead of page classes. |
| **Service objects / API clients** | One class or module per resource or endpoint group (`UsersService`, `ordersClient`) wrapping the HTTP client; tests call `service.create(payload)` and assert on the response; often with models/DTOs and builders/factories for payloads. |
| **BDD with a step layer** | `.feature` files → step-definition classes/modules → page objects or services. The quality question is whether steps stay thin (delegate) or hold the logic. |
| **Keyword-driven** | Robot Framework keywords in `resources/`, or homemade keyword tables; tests are lists of keywords. |
| **Plain specs** | Locators and requests directly in the test bodies, maybe with small helper functions. A legitimate choice for small suites — record it as such, not as a failure. |

A repo often combines them (POM for UI + service objects for API + fixtures for wiring). Name each one where it applies.

## Reading each OOP principle

- **Encapsulation** — Are locators/endpoints declared inside the class (fields, getters) and used only there, or do tests reach into them? Count: tests that call page-object *methods* vs tests that use page-object *locators* directly vs raw `page.locator`/`driver.findElement` in specs. Exposed locators used for assertions (`expect(page.alert)`) are a common, acceptable middle ground — record it as the team's style.
- **Inheritance** — Base classes (`BasePage`, `BaseTest`, `BaseService`), what they really provide (navigation, waits, common assertions, HTTP setup), how many classes extend them vs how many could but don't. Deep hierarchies (3+ levels) and base classes that are almost empty are worth noting.
- **Composition** — Components reused inside pages (`this.navbar = new Navbar(page)`), clients inside services, fixtures composed from other fixtures. Note duplicates: the same component created in several places, or the same locator declared in two classes.
- **Abstraction** — Do methods speak business (`fillMissionData`, `createUser`) or UI mechanics (`clickButton3`)? Do tests read as scenarios? Are there methods that exist but tests bypass (a `save()` method while tests click the button directly)?
- **Responsibility split** — Where assertions live (tests only, or also in page objects/steps), where test data is built (factories vs inline literals), where DB/API setup lives (support modules vs inside tests), whether step definitions are thin.

## Signs of a consistent design vs a messy one

| Consistent | Messy |
|---|---|
| Every page/screen used by tests has a class; specs contain no raw locators | Some specs use page objects, others raw locators for the same screens |
| One way to get a page object (fixtures, or DI, or `new` — but one) | Mixed creation: fixtures in some tests, `new` in others, static helpers elsewhere |
| Shared widgets are components reused everywhere | Same locator declared in several classes or specs |
| Methods are used; there is little dead code | Methods nobody calls; tests reimplement what a method does |
| Naming of classes, files and methods follows one pattern | Several naming patterns (`login.page.ts`, `LoginPage.ts`, `pages/login.ts`) |
| Data comes from factories/builders | Literal data scattered in tests; credentials duplicated |
| Step definitions delegate to the layer below | Step definitions full of locators, waits and logic |
| Recent and old code look alike | Clear "eras" in git history with different styles |

## Measuring consistency
Back every judgment with counts from grep, not impressions:
- classes per layer and how many follow the dominant shape (constructor signature, field style, base class);
- raw locator/request calls in specs vs inside the layer that should own them;
- creation style per test file (fixture / `new` / static);
- duplicated locators or credentials (`grep -rn "getByRole('button', { name: 'Sair' })"`, same literal email in several files);
- methods defined vs methods called (`grep -rn "\.methodName("`);
- old vs recent files (`git log --format=%ad --date=short -- <file>`), to tell legacy from current.

**Verdict scale:**
- **Consistent** — the dominant pattern holds in ≥ 90% of what you counted, deviations are isolated.
- **Mostly consistent with deviations** — a clear dominant pattern (≥ 70%), with deviations you can list.
- **Mixed** — two or more patterns in similar proportions; new tests need a decision (ask it).
- **No clear structure** — no dominant pattern; record the most recent style as the model and ask.

The thresholds are guides, not math; say what you counted.

## Choosing the pattern new tests follow
1. A rule written by the team wins (CONTRIBUTING, agent context file), unless the code has clearly moved away from it — then report both and ask.
2. Otherwise the dominant pattern in **recent** code wins over the dominant pattern overall — teams improve over time, and the newest tests show where they're going.
3. When two patterns are evenly split, don't pick: write both in Deviations and ask a ❓ question.
4. Whatever is chosen becomes the Rules for new tests (conventions.md) and the Recipes; everything else goes to Deviations and "Don't imitate".
