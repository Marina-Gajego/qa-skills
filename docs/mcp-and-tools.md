# MCP Servers & Tools

MCP servers and tools the skills can use. Each skill works without them — they add integrations on top. Add a row here whenever a new skill relies on a tool.

| Category | MCP / Tool | Used by skills | Notes |
|---|---|---|---|
| Issue tracking | Jira / Azure DevOps / GitHub Issues / GitLab / Linear | `bug-report-writer` | Optional. Creates the ticket only after the user reviews and confirms the report. See [tracker-integration.md](../skills/bug-report-writer/references/tracker-integration.md). |
| Browser automation | [Playwright MCP](https://github.com/microsoft/playwright-mcp) | `exploratory-testing`, `test-automation` | **Required for web targets** (default). `claude mcp add playwright -- npx -y @playwright/mcp@latest`. The skill warns and stops if it isn't connected. This repo ships a `.mcp.json` with it, so opening Claude Code here loads it (approve the server on first use). `test-automation` uses it only optionally, to confirm selectors on the live page. |
| HTTP / API | Shell with `curl` + `jq`, or an HTTP/API MCP | `exploratory-testing` | Required for API targets. `curl` needs no setup; an MCP adds guardrails (allowlisted base URL, auth from env vars, request logging). |
| Mobile / desktop automation | A mobile (e.g. Appium-based) or desktop automation MCP | `exploratory-testing` | Required for non-web apps — the skill needs a tool that can tap/click and read the real app. Not validated in a real session yet. |
| Shell | Shell with `git`, `grep` and Python 3 (stdlib only) | `test-stack-discovery` | Required to read the repo. Python runs the bundled read-only `scripts/inventory.py` (one call instead of dozens of `ls`/`grep`); without Python the skill does the inventory by hand, at a higher token cost. |
| Shell | Shell with `git`, Python 3 (stdlib only) and the suite's own toolchain (Node, JDK + Maven/Gradle, Python…) | `test-automation` | Python runs the bundled read-only `scripts/reuse_index.py` (step definitions, near-duplicate steps, page objects, services, fixtures). The toolchain runs the compile/dry-run checks and, when the environment allows, the new tests. The skill never installs dependencies. |
| Database | A database MCP with a read-only user | `exploratory-testing` | Optional. Lets the session follow the data to where it's stored. |
