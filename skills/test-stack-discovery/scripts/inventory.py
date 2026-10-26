#!/usr/bin/env python3
"""Read-only inventory of a test repository, printed as compact Markdown.

Replaces dozens of ad-hoc ls/grep/git calls in session 0 with one command:
file counts (without vendor and AI-agent folders), suite candidates, declared
versions, test/scenario counts, most imported modules, recent changes,
documented-rules files and CI. It never prints file contents or env values.

Usage: python3 inventory.py <repo> [--product <product repo>]
"""
import collections
import json
import os
import re
import subprocess
import sys

VENDOR = {"node_modules", "target", "build", "dist", ".venv", "venv", "__pycache__", ".git",
          "playwright-report", "test-results", "allure-results", "allure-report", "blob-report",
          ".gradle", ".idea", ".vscode", "coverage", ".next", ".nuxt", "out", "bin", "obj",
          ".pytest_cache", ".mypy_cache", ".tox", ".yarn"}
AI_DIRS = {".claude", ".agents", "_bmad", "_bmad-output", ".windsurf", ".cursor", ".github/agents",
           ".github/chatmodes", ".github/prompts", ".bmad-core", ".roo", ".clinerules"}
AGENT_CONTEXT = ["AGENTS.md", "CLAUDE.md", "project-context.md", ".github/copilot-instructions.md",
                 ".cursor/rules", ".cursorrules"]
RULE_DOCS = ["README.md", "CONTRIBUTING.md", ".github/pull_request_template.md",
             "commitlint.config.js", "commitlint.config.cjs", ".editorconfig"]
CI_FILES = [".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml",
            ".circleci/config.yml"]
TEST_FILE = re.compile(r"(\.spec\.|\.test\.|\.cy\.|\.e2e\.|(^|/)test_[^/]*\.py$|_test\.(py|go)$|Test\.java$|IT\.java$|"
                       r"Tests?\.cs$|_spec\.rb$|\.feature$|\.robot$|\.jmx$|\.setup\.)")
TEST_COUNT = {
    "js/ts test()/it()": (re.compile(r"\.(spec|test|cy|e2e|setup)\.[cm]?[jt]sx?$"),
                          re.compile(r"^\s*(test|it)(\.only|\.skip|\.fixme|\.fail)?\s*\(\s*[`'\"]", re.M)),
    "java @Test": (re.compile(r"\.java$"), re.compile(r"@(Test|ParameterizedTest)\b")),
    "python def test_": (re.compile(r"\.py$"), re.compile(r"^\s*(async\s+)?def test_", re.M)),
    "go func Test": (re.compile(r"_test\.go$"), re.compile(r"^func Test", re.M)),
}
GHERKIN_KW = re.compile(r"^\s*(Feature|Funcionalidade|Característica|Background|Contexto|Antecedentes|Scenario Outline|"
                        r"Scenario Template|Esquema do Cenário|Esquema del escenario|Scenario|Cenário|Escenario|Example|Exemplo)\s*:",
                        re.M)
IMPORT_RE = {
    "js": re.compile(r"""(?:import\s[^'"]*?from\s*|require\()\s*['"]([^'"]+)['"]"""),
    "java": re.compile(r"^import\s+(?:static\s+)?([\w.]+)\s*;", re.M),
    "py": re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.M),
}


def sh(args, cwd):
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return ""


def is_excluded(path):
    parts = path.split("/")
    if any(p in VENDOR for p in parts[:-1]):
        return "vendor"
    for ai in AI_DIRS:
        if path == ai or path.startswith(ai + "/"):
            return "ai"
    return None


def list_files(root):
    if os.path.isdir(os.path.join(root, ".git")) or sh(["git", "rev-parse", "--is-inside-work-tree"], root).strip() == "true":
        out = sh(["git", "ls-files"], root)
        if out:
            return out.splitlines(), True
    files = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if x not in VENDOR]
        for f in fs:
            files.append(os.path.relpath(os.path.join(d, f), root))
    return files, False


def read(root, rel, limit=400_000):
    try:
        with open(os.path.join(root, rel), encoding="utf-8", errors="ignore") as fh:
            return fh.read(limit)
    except OSError:
        return ""


def manifests(root, files):
    out = []
    fs = set(files)
    if "package.json" in fs or any(f.endswith("/package.json") for f in files):
        for pj in sorted(f for f in files if f.endswith("package.json"))[:5]:
            try:
                data = json.loads(read(root, pj))
            except ValueError:
                continue
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            out.append(f"- `{pj}`: " + ", ".join(f"{k} {v}" for k, v in sorted(deps.items())))
            for key in ("engines", "packageManager", "workspaces"):
                if key in data:
                    out.append(f"  - {key}: {json.dumps(data[key])}")
            if data.get("scripts"):
                out.append("  - scripts: " + "; ".join(f"{k}=`{v}`" for k, v in data["scripts"].items()))
    for pom in sorted(f for f in files if f.endswith("pom.xml"))[:3]:
        text = read(root, pom)
        props = dict(re.findall(r"<([\w.\-]+)>([^<]{1,40})</\1>", text.split("<dependencies>")[0]))
        java = {k: v for k, v in props.items() if "java" in k or "compiler" in k}
        deps = re.findall(r"<artifactId>([^<]+)</artifactId>\s*(?:<version>([^<]+)</version>)?", text)
        out.append(f"- `{pom}`: java props {java}; artifacts: " + ", ".join(f"{a} {v}".strip() for a, v in deps))
    for g in sorted(f for f in files if re.search(r"build\.gradle(\.kts)?$|libs\.versions\.toml$", f))[:3]:
        deps = re.findall(r"""['"]([\w.\-]+:[\w.\-]+:[\w.\-]+)['"]""", read(root, g))
        out.append(f"- `{g}`: " + ", ".join(deps))
    for p in sorted(f for f in files if re.search(r"(^|/)(requirements[\w\-]*\.txt|pyproject\.toml|Pipfile|Gemfile|go\.mod|.*\.csproj)$", f))[:5]:
        lines = [l.strip() for l in read(root, p).splitlines() if l.strip() and not l.strip().startswith("#")]
        out.append(f"- `{p}`: " + " | ".join(lines[:40]))
    locks = [f for f in files if re.search(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|bun\.lockb|poetry\.lock|uv\.lock|Pipfile\.lock|Gemfile\.lock|go\.sum)$", f)]
    if locks:
        notes = []
        for l in locks[:4]:
            head = read(root, l, 300)
            kind = "yarn v1" if "yarn lockfile v1" in head else ("yarn berry" if "__metadata" in read(root, l, 2000) else "")
            notes.append(f"`{l}`{' (' + kind + ')' if kind else ''}")
        out.append("- lockfiles: " + ", ".join(notes))
    tool = [f for f in files if re.search(r"(^|/)(\.nvmrc|\.node-version|\.tool-versions|\.python-version|\.java-version|\.sdkmanrc|mvnw|gradlew|\.yarnrc\.yml)$", f)]
    out.append("- toolchain files: " + (", ".join(f"`{t}`" for t in tool) if tool else "none found"))
    return out


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    root = os.path.abspath(args[0])
    product = os.path.abspath(args[args.index("--product") + 1]) if "--product" in args else None

    all_files, is_git = list_files(root)
    kept, excl = [], collections.Counter()
    for f in all_files:
        why = is_excluded(f)
        if why:
            excl[why] += 1
        else:
            kept.append(f)

    head = sh(["git", "rev-parse", "--short", "HEAD"], root).strip() if is_git else "not a git repo"
    print(f"# Inventory: {root}\n\ncommit: {head} · tracked files: {len(all_files)} · analyzed: {len(kept)} · "
          f"excluded: {excl['ai']} in AI-agent folders, {excl['vendor']} vendor/generated")
    ai_present = sorted({a for a in AI_DIRS for f in all_files if f.startswith(a + "/")})
    if ai_present:
        print("AI-agent folders (excluded from counts): " + ", ".join(f"`{a}/`" for a in ai_present))

    print("\n## Folders (2 levels, files)")
    by_dir = collections.Counter("/".join(os.path.dirname(f).split("/")[:2]) or "." for f in kept)
    for d, n in sorted(by_dir.items(), key=lambda x: (-x[1], x[0]))[:40]:
        print(f"- {d}: {n}")
    print("\n## Extensions")
    ext = collections.Counter(os.path.splitext(f)[1] or "(none)" for f in kept)
    print(", ".join(f"{e} {n}" for e, n in ext.most_common(20)))

    tests = [f for f in kept if TEST_FILE.search(f)]
    print(f"\n## Test files ({len(tests)}) by folder")
    tdir = collections.Counter(os.path.dirname(f) or "." for f in tests)
    for d, n in sorted(tdir.items()):
        print(f"- {d}: {n}")

    print("\n## Test counts")
    for label, (fpat, cpat) in TEST_COUNT.items():
        n_files = n = 0
        for f in kept:
            if fpat.search(f) and (label != "java @Test" or "/test/" in f or f.startswith("test")):
                c = len(cpat.findall(read(root, f)))
                if c:
                    n_files += 1
                    n += c
        if n:
            print(f"- {label}: {n} in {n_files} files")
    feats = [f for f in kept if f.endswith(".feature")]
    if feats:
        kw = collections.Counter()
        langs = collections.Counter()
        tags = collections.Counter()
        for f in feats:
            text = read(root, f)
            kw.update(m.group(1) for m in GHERKIN_KW.finditer(text))
            m = re.search(r"#\s*language:\s*([\w\-]+)", text)
            langs[m.group(1) if m else "en (no header)"] += 1
            tags.update(re.findall(r"(?<!\w)@[\w\-=.:]+", text))
        print(f"- gherkin: {len(feats)} feature files; keywords {dict(kw)}; language {dict(langs)}")
        shapes = collections.Counter()
        for t, n in tags.items():
            shapes[re.sub(r"\d+", "N", t)] += n
        print(f"- gherkin tags by pattern: " + ", ".join(f"{t} {n}" for t, n in shapes.most_common(25)))
    robots = [f for f in kept if f.endswith(".robot")]
    if robots:
        print(f"- robot: {len(robots)} .robot files")

    print("\n## Most imported modules in test code (top 25)")
    imp = collections.Counter()
    code = [f for f in kept if re.search(r"\.(m?[jt]sx?|java|py)$", f) and
            (TEST_FILE.search(f) or re.search(r"(^|/)(tests?|e2e|spec|specs|src/test|cypress|playwright|steps?|support|pages?|fixtures?)/", f))]
    for f in code:
        text = read(root, f, 60_000)
        lang = "java" if f.endswith(".java") else "py" if f.endswith(".py") else "js"
        for m in IMPORT_RE[lang].finditer(text):
            name = next(g for g in m.groups() if g) if lang == "py" else m.group(1)
            if lang == "java":
                name = ".".join(name.split(".")[:-1]) or name
            imp[name] += 1
    print(", ".join(f"`{k}` {n}" for k, n in imp.most_common(25)) or "none found")

    print("\n## Manifests and versions")
    for line in manifests(root, kept):
        print(line[:1500])

    print("\n## Documented rules and CI")
    docs = [p for p in RULE_DOCS + AGENT_CONTEXT if any(f == p or f.startswith(p + "/") for f in all_files)]
    print("- rule/context files: " + (", ".join(f"`{d}`" for d in docs) or "none found"))
    custom_ai = [f for f in all_files if is_excluded(f) == "ai" and "/skills/" not in f and
                 re.search(r"((^|/)custom/[^/]+|(rules?|context|conventions?|instructions)[^/]*)\.(md|toml|ya?ml|json|mdc)$", f, re.I)]
    # Agent files that cite this repo's own test/support paths were written for this repo, not copied from a library.
    own_paths = {f for f in tests + code if "/" in f}
    for f in all_files:
        if is_excluded(f) == "ai" and f not in custom_ai and re.search(r"\.(md|toml|ya?ml|mdc)$", f):
            text = read(root, f, 100_000)
            if sum(1 for p in own_paths if p in text) >= 2:
                custom_ai.append(f)
    if custom_ai:
        print("- repo-specific files inside AI folders (custom config or citing this repo's paths — read as written rules): "
              + ", ".join(f"`{f}`" for f in custom_ai[:15]))
    docs_dir = [f for f in kept if f.startswith("docs/") and re.search(r"\.(md|txt|adoc|rst|feature|csv)$", f)]
    if docs_dir:
        print(f"- docs/: {len(docs_dir)} files — " + ", ".join(f"`{f}`" for f in docs_dir[:15]))
    ci = [f for f in all_files if f.startswith(".github/workflows/") or f in CI_FILES]
    print("- CI: " + (", ".join(f"`{c}`" for c in ci) or "none found"))
    envs = [f for f in all_files if re.search(r"(^|/)\.env(\.[\w]+)?$", f)]
    print("- env files tracked (names only): " + (", ".join(f"`{e}`" for e in envs) or "none"))

    if is_git:
        print("\n## Recent history")
        print(sh(["git", "log", "--date=short", "--format=%h %ad %s", "-12"], root).rstrip())
        recent = sh(["git", "log", "--since=6 months ago", "--name-only", "--format="], root).splitlines()
        rc = collections.Counter(f for f in recent if f in set(tests))
        if rc:
            print("Most changed test files (6 months): " + ", ".join(f"`{f}` {n}" for f, n in rc.most_common(10)))

    if product:
        p_files, p_git = list_files(product)
        p_kept = [f for f in p_files if not is_excluded(f)]
        print(f"\n## Product: {product}\n\ngit: {'yes' if p_git else 'no'} · files: {len(p_kept)}")
        pd = collections.Counter("/".join(os.path.dirname(f).split("/")[:2]) or "." for f in p_kept)
        print("Folders: " + ", ".join(f"{d} {n}" for d, n in pd.most_common(20)))
        routes = [f for f in p_kept if re.search(r"(^|/)(routes?|controllers?|api|pages)/|Controller\.|router|openapi|swagger|(^|/)app/.*(page|route)\.[jt]sx?$", f, re.I)
                  and not re.search(r"(^|/)(public|assets|static)/|\.(map|css|png|jpe?g|svg|webp)$", f)]
        print(f"Route/controller/OpenAPI candidates ({len(routes)}, first 15): " + ", ".join(f"`{r}`" for r in routes[:15]))
        migr = [f for f in p_kept if re.search(r"migrations?/|seeds?/|schema\.(sql|prisma)$", f)]
        print(f"Migrations/seeds ({len(migr)}): " + ", ".join(f"`{m}`" for m in migr[:20]))


if __name__ == "__main__":
    main()
