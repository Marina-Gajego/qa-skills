# MCP Servers & Tools

MCP servers and tools the skills can use. Each skill works without them — they add integrations on top. Add a row here whenever a new skill relies on a tool.

| Category | MCP / Tool | Used by skills | Notes |
|---|---|---|---|
| Issue tracking | Jira / Azure DevOps / GitHub Issues / GitLab / Linear | `bug-report-writer` | Optional. Creates the ticket only after the user reviews and confirms the report. See [tracker-integration.md](../skills/bug-report-writer/references/tracker-integration.md). |
| Browser automation | [Playwright MCP](https://github.com/microsoft/playwright-mcp) | `exploratory-testing` | **Required for web targets** (default). `claude mcp add playwright -- npx -y @playwright/mcp@latest`. The skill warns and stops if it isn't connected. |
| HTTP / API | Shell with `curl` + `jq`, or an HTTP/API MCP | `exploratory-testing` | Required for API targets. `curl` needs no setup; an MCP adds guardrails (allowlisted base URL, auth from env vars, request logging). |
| Mobile / desktop automation | A mobile (e.g. Appium-based) or desktop automation MCP | `exploratory-testing` | Required for non-web apps — the skill needs a tool that can tap/click and read the real app. |
| Database | A database MCP with a read-only user | `exploratory-testing` | Optional. Lets the session follow the data to where it's stored. |
