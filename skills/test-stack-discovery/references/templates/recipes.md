# `.qa-skills/test-stack/recipes.md` — session 6 template

Rules shared by all session files and the markers are in [../output-index.md](../output-index.md). Keep titles, order, fixed rows and markers exactly as below.

````markdown
<!-- qa-skills:test-stack-recipes v2 -->
# Recipes
Index: `../test-stack.md` · only artifacts this repo actually has.

## Suite: <suite>

### Recipe: <new test in an existing file | new test file | new page object | new component | new step definition | new feature file | new fixture | new data factory | new API service | new DB helper …>
**When:** <the situation this recipe is for.>
**Copy from:** <path:lines of the real example>

1. <first file to create/touch, where, and what goes in it>
2. <how it's wired: fixture registry, export, glue path, runner config>
3. <…>

```<language>
<skeleton derived from the example, business parts as <placeholders>; only things that exist in the repo>
```
Derived from: <path:lines>.

**Checklist:** <3–6 bullets a reviewer from this team would check — naming, cleanup, tags, step titles…>

### Reference tests
| Test | Why imitate it | Shows |
|---|---|---|
| <path, or `path:lines — "test title"` for one test in a big file> | <recent, dominant fixtures/pages/factories, not skipped> | <patterns> |

### Don't imitate
- <path or path:line — legacy style or in-file anti-pattern, and why.>
````

### Filled example (excerpt, fictional repo)

````markdown
### Recipe: new test file
**When:** a new screen or flow that has no spec yet.
**Copy from:** `tests/ui/cart/cart.spec.ts:1-24`

1. Create `tests/ui/<area>/<area>.spec.ts` (observed 22/22 specs follow this path).
2. If the screen has no page object, follow "Recipe: new page object" first, then register it in `support/fixtures.ts` (Recipe: new fixture).
3. Seed data through the `seed` fixture, never through the UI (written: `CONTRIBUTING.md:31`).

```ts
import { test, expect } from '@support/fixtures';
import { productFactory } from '@support/factories/product';

test('<JIRA-KEY> - deve <resultado> quando <condição>', async ({ <areaPage>, seed }) => {
  const product = await seed.product(productFactory.build({ <campos> }));

  await test.step('<ação>', async () => {
    await <areaPage>.<acao>(product.name);
  });

  await expect(<areaPage>.<locator>).<assertion>;
});
```
Derived from: `tests/ui/cart/cart.spec.ts:1-24`.

**Checklist:** Jira key in the title · every action inside a `test.step` · no `page.locator` in the spec · data created through `seed` (auto-cleaned).
````
