#!/usr/bin/env python3
"""Reuse index for a test automation repo — read-only, stdlib only.

Prints what a new test can reuse before anything is written:
  * BDD step definitions (Cucumber JVM/JS, playwright-bdd, behave, pytest-bdd,
    SpecFlow/Reqnroll, Robot keywords) with file:line and how many feature steps
    use each one, plus unused definitions and undefined feature steps;
  * classes, their public methods and fields, exported functions, and
    Playwright-style fixtures (test.extend keys).

With --check FILE.feature [...] it instead resolves every step of those feature
files against the existing definitions: REUSES <def>, UNDEFINED or AMBIGUOUS.
It is a static dry run: it never runs the test runner.

Usage:
  python3 -I reuse_index.py <repo> [--paths dir ...] [--check f.feature ...]
                             [--grep word ...] [--max N]
"""
import argparse
import difflib
import os
import re
import sys
from collections import defaultdict

SKIP_DIRS = {
    ".git", "node_modules", "target", "build", "dist", "out", ".venv", "venv",
    "__pycache__", ".gradle", ".idea", ".vscode", "coverage", "playwright-report",
    "test-results", "allure-results", "allure-report", "reports", ".pytest_cache",
    "bin", "obj", ".next", ".nuxt", ".cache", "vendor",
    # AI-agent folders: never part of the suite
    ".claude", ".agents", ".cursor", "_bmad", "_bmad-output", ".qa-skills",
    ".playwright-mcp", "exploratory-sessions",
}
CODE_EXT = {".ts", ".tsx", ".js", ".mjs", ".cjs", ".jsx", ".java", ".kt", ".py",
            ".cs", ".rb", ".robot", ".resource"}

STEP_WORDS = (
    # en, pt, es — Gherkin keywords that start a step
    r"Given|When|Then|And|But|\*|"
    r"Dado|Dada|Dados|Dadas|Quando|Então|Entao|E|Mas|Cenário|"
    r"Cuando|Entonces|Y|Pero|Dado que"
)
FEATURE_STEP_RE = re.compile(r"^\s*(" + STEP_WORDS + r")\s+(.+?)\s*$")
DEF_PATTERNS = [
    # Java / Kotlin annotations, any Gherkin language: @Given("..."), @Dado("...")
    ("java", re.compile(r'@(\w+)\(\s*"((?:[^"\\]|\\.)*)"')),
    # JS/TS cucumber, playwright-bdd: Given('...'), When(/regex/), Then(`...`)
    ("js", re.compile(r"\b(Given|When|Then|And|But|Step|defineStep|Dado|Quando|Entao|Então|Cuando|Entonces)"
                      r"\(\s*(?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"|`([^`]*)`|/((?:[^/\\]|\\.)+)/)")),
    # Python behave / pytest-bdd: @given('...'), @when(parsers.parse("..."))
    ("py", re.compile(r"@(given|when|then|step)\(\s*(?:parsers\.\w+\(\s*)?[rubfRUBF]*(?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\")")),
    # C# SpecFlow / Reqnroll: [Given(@"...")]
    ("cs", re.compile(r'\[(Given|When|Then|And|But|StepDefinition)\(\s*@?"((?:[^"\\]|\\.|"")*)"')),
    # Ruby cucumber: Given(/^...$/) or Given('...')
    ("rb", re.compile(r"^\s*(Given|When|Then|And|But)\s*\(?\s*(?:/(.+?)/|'([^']*)'|\"([^\"]*)\")")),
]
JAVA_STEP_ANNOT = {"Given", "When", "Then", "And", "But", "Dado", "Quando", "Entao", "Então", "E", "Mas",
                   "Cuando", "Entonces", "Y", "Pero", "Step"}

CUKE_PARAM = {
    "string": r"(?:\"[^\"]*\"|'[^']*')", "int": r"-?\d+", "float": r"-?\d*[.,]?\d+",
    "word": r"[^\s]+", "": r".*", "double": r"-?\d*[.,]?\d+", "long": r"-?\d+",
    "biginteger": r"-?\d+", "bigdecimal": r"-?\d*[.,]?\d+", "byte": r"-?\d+", "short": r"-?\d+",
}


def walk(root, subpaths):
    bases = [os.path.join(root, p) for p in subpaths] if subpaths else [root]
    for base in bases:
        if os.path.isfile(base):
            yield base
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for f in sorted(filenames):
                yield os.path.join(dirpath, f)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def cuke_to_regex(expr):
    """Cucumber expression (or regex) -> compiled regex matching a whole step text."""
    looks_regex = expr.startswith("^") or expr.endswith("$") or re.search(r"\(\.\*\)|\\d|\\s|\(\?", expr)
    if looks_regex:
        pat = expr
        if not pat.startswith("^"):
            pat = "^" + pat
        if not pat.endswith("$"):
            pat += "$"
        try:
            return re.compile(pat)
        except re.error:
            return None
    out, i = [], 0
    tokens = re.split(r"(\{[^}]*\}|\([^)]*\)|\S+/\S+)", expr)
    for tok in tokens:
        if not tok:
            continue
        m = re.fullmatch(r"\{([^}]*)\}", tok)
        if m:
            out.append(CUKE_PARAM.get(m.group(1).lower(), r".+?"))
        elif re.fullmatch(r"\([^)]*\)", tok):  # optional text: cat(s)
            out.append("(?:" + re.escape(tok[1:-1]) + ")?")
        elif "/" in tok and not tok.startswith("/") and " " not in tok:  # alternation: a/b
            out.append("(?:" + "|".join(re.escape(p) for p in tok.split("/")) + ")")
        else:
            out.append(re.escape(tok).replace(r"\ ", " "))
    try:
        return re.compile("^" + "".join(out) + "$")
    except re.error:
        return None


def find_step_defs(root, subpaths):
    defs = []  # dict(file, line, kw, expr, rx)
    robot_keywords = []
    for path in walk(root, subpaths):
        ext = os.path.splitext(path)[1]
        if ext not in CODE_EXT:
            continue
        rel = os.path.relpath(path, root)
        text = read(path)
        if ext in (".robot", ".resource"):
            in_kw = False
            for n, line in enumerate(text.splitlines(), 1):
                if line.startswith("***"):
                    in_kw = "keyword" in line.lower()
                    continue
                if in_kw and line and not line[0].isspace() and not line.startswith("#"):
                    robot_keywords.append((rel, n, line.strip()))
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for lang, rx in DEF_PATTERNS:
                if lang == "java" and ext not in (".java", ".kt"):
                    continue
                if lang == "js" and ext not in (".ts", ".tsx", ".js", ".mjs", ".cjs", ".jsx"):
                    continue
                if lang == "py" and ext != ".py":
                    continue
                if lang == "cs" and ext != ".cs":
                    continue
                if lang == "rb" and ext != ".rb":
                    continue
                for m in rx.finditer(line):
                    kw = m.group(1)
                    if lang == "java" and kw not in JAVA_STEP_ANNOT:
                        continue
                    expr = next((g for g in m.groups()[1:] if g is not None), "")
                    if lang == "js" and m.group(5) is not None:
                        expr = "^" + expr.strip("^$") + "$"
                    if lang in ("java", "cs"):
                        expr = expr.replace('\\"', '"').replace('""', '"').replace("\\\\", "\\")
                    defs.append({"file": rel, "line": n, "kw": kw, "expr": expr,
                                 "rx": cuke_to_regex(expr), "uses": 0})
    return defs, robot_keywords


def feature_steps(path):
    """Yield (line_no, keyword, text) for each step, skipping tables and docstrings."""
    in_doc = False
    for n, line in enumerate(read(path).splitlines(), 1):
        s = line.strip()
        if s.startswith('"""') or s.startswith("```"):
            in_doc = not in_doc
            continue
        if in_doc or not s or s.startswith("#") or s.startswith("|") or s.startswith("@"):
            continue
        if re.match(r"^(Feature|Funcionalidade|Característica|Caracteristica|Background|Contexto|Antecedentes|"
                    r"Scenario|Cenário|Cenario|Escenario|Scenario Outline|Scenario Template|Esquema do Cenário|"
                    r"Esquema del escenario|Examples|Exemplos|Ejemplos|Rule|Regra|Regla)\b.*:", s):
            continue
        m = FEATURE_STEP_RE.match(line)
        if m:
            yield n, m.group(1), m.group(2)


def candidates(text):
    """Outline steps carry <param>; try plausible substitutions."""
    if "<" not in text:
        return [text]
    return [re.sub(r"<[^>]+>", sub, text) for sub in ("0", '"x"', "x")]


def resolve(defs, text):
    hits = []
    for d in defs:
        if d["rx"] is None:
            continue
        if any(d["rx"].match(c) for c in candidates(text)):
            hits.append(d)
    return hits


def closest(defs, text, n=3, cutoff=0.6):
    """Definitions worded almost like this step: the usual source of duplicated steps."""
    plain = lambda e: re.sub(r"\{[^}]*\}|\(\.\*\)|[\^$\\]", "", e).lower()
    scored = [(difflib.SequenceMatcher(None, text.lower(), plain(d["expr"])).ratio(), d) for d in defs]
    return [d for r, d in sorted(scored, key=lambda x: -x[0]) if r >= cutoff][:n]


def find_code_units(root, subpaths, step_files):
    """Classes with public methods/fields, exported functions, fixture keys."""
    units, fixtures = [], []
    for path in walk(root, subpaths):
        ext = os.path.splitext(path)[1]
        if ext not in CODE_EXT or ext in (".robot", ".resource"):
            continue
        rel = os.path.relpath(path, root)
        if rel in step_files or re.search(r"\.(spec|test)\.[jt]sx?$|_test\.py$|^test_.*\.py$", os.path.basename(path)):
            continue
        text = read(path)
        lines = text.splitlines()
        if ext in (".ts", ".tsx", ".js", ".mjs", ".cjs", ".jsx"):
            cur = None
            for n, line in enumerate(lines, 1):
                m = re.match(r"\s*export\s+(?:default\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?", line)
                if m:
                    cur = {"file": rel, "line": n, "name": m.group(1), "base": m.group(2), "methods": [], "fields": []}
                    units.append(cur)
                    continue
                if cur is not None:
                    mm = re.match(r"\s{2,}(?:public\s+|static\s+)*(?:async\s+)?(?!if\b|for\b|while\b|switch\b|return\b|constructor\b)(\w+)\s*\([^)]*\)\s*(?::[^{]+)?\{", line)
                    if mm and not line.strip().startswith(("private", "#")):
                        cur["methods"].append(mm.group(1))
                    mf = re.match(r"\s{2,}(?:public\s+)?readonly\s+(\w+)\s*:", line)
                    if mf:
                        cur["fields"].append(mf.group(1))
                mfn = re.match(r"\s*export\s+(?:async\s+)?function\s+(\w+)|\s*export\s+const\s+(\w+)\s*=\s*(?:async\s*)?\(?", line)
                if mfn and not re.match(r"\s*export\s+const\s+test\b", line):
                    units.append({"file": rel, "line": n, "name": mfn.group(1) or mfn.group(2), "kind": "function"})
            if ".extend" in text:
                for n, line in enumerate(lines, 1):
                    mk = re.match(r"\s{2,8}(\w+)\s*:\s*\[?\s*async\s*\(", line)
                    if mk:
                        fixtures.append((rel, n, mk.group(1)))
        elif ext in (".java", ".kt", ".cs"):
            cur = None
            for n, line in enumerate(lines, 1):
                m = re.match(r"\s*(?:public\s+)?(?:abstract\s+|final\s+|static\s+)*(?:class|interface|enum|record)\s+(\w+)(?:\s+extends\s+(\w+))?", line)
                if m:
                    cur = {"file": rel, "line": n, "name": m.group(1), "base": m.group(2), "methods": [], "fields": []}
                    units.append(cur)
                    continue
                if cur is not None:
                    mm = re.match(r"\s+public\s+(?:static\s+)?(?:final\s+)?[\w<>\[\],.? ]+\s+(\w+)\s*\(", line)
                    if mm and mm.group(1) != cur["name"]:
                        cur["methods"].append(mm.group(1))
                    mf = re.match(r"\s+(?:public|protected)\s+(?:static\s+)?(?:final\s+)?[\w<>\[\],.? ]+\s+(\w+)\s*(?:=|;)", line)
                    if mf:
                        cur["fields"].append(mf.group(1))
        elif ext == ".py":
            cur = None
            for n, line in enumerate(lines, 1):
                m = re.match(r"class\s+(\w+)(?:\((\w+)\))?", line)
                if m:
                    cur = {"file": rel, "line": n, "name": m.group(1), "base": m.group(2), "methods": [], "fields": []}
                    units.append(cur)
                    continue
                mm = re.match(r"(\s*)(?:async\s+)?def\s+(\w+)", line)
                if mm:
                    if mm.group(1) and cur is not None and not mm.group(2).startswith("_"):
                        cur["methods"].append(mm.group(2))
                    elif not mm.group(1):
                        cur = None
                        units.append({"file": rel, "line": n, "name": mm.group(2), "kind": "function"})
                if re.match(r"@pytest\.fixture", line) and n < len(lines):
                    mf = re.match(r"\s*(?:async\s+)?def\s+(\w+)", lines[n])
                    if mf:
                        fixtures.append((rel, n + 1, mf.group(1)))
    return units, fixtures


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--paths", nargs="*", default=[], help="test module dirs relative to repo (default: whole repo)")
    ap.add_argument("--check", nargs="*", default=[], help="feature files to resolve against existing step definitions")
    ap.add_argument("--grep", nargs="*", default=[], help="only print definitions/units containing any of these words")
    ap.add_argument("--max", type=int, default=400, help="max lines per section")
    a = ap.parse_args()
    root = os.path.abspath(a.repo)

    defs, robot_kw = find_step_defs(root, a.paths)
    features = [p for p in walk(root, a.paths) if p.endswith(".feature")]

    if a.check:
        status = 0
        for f in a.check:
            path = f if os.path.isabs(f) else os.path.join(root, f)
            rel = os.path.relpath(path, root) if path.startswith(root + os.sep) else path
            print(f"== {rel}")
            for n, kw, text in feature_steps(path):
                hits = resolve(defs, text)
                if len(hits) == 1:
                    h = hits[0]
                    print(f"  {rel}:{n}  REUSES     {kw} {text}\n             -> {h['file']}:{h['line']} @{h['kw']}(\"{h['expr']}\")")
                elif not hits:
                    status = 1
                    print(f"  {rel}:{n}  UNDEFINED  {kw} {text}")
                    for c in closest(defs, text):
                        print(f"             ~ similar: {c['file']}:{c['line']} \"{c['expr']}\"")
                else:
                    status = 1
                    print(f"  {rel}:{n}  AMBIGUOUS  {kw} {text}")
                    for h in hits:
                        print(f"             -> {h['file']}:{h['line']} @{h['kw']}(\"{h['expr']}\")")
        print("\nStatic check only (no runner executed). UNDEFINED = no existing definition matches; "
              "verify custom parameter types by hand.")
        sys.exit(status)

    undefined = defaultdict(list)
    total_steps = 0
    for f in features:
        rel = os.path.relpath(f, root)
        for n, kw, text in feature_steps(f):
            total_steps += 1
            hits = resolve(defs, text)
            for h in hits:
                h["uses"] += 1
            if not hits:
                undefined[text].append(f"{rel}:{n}")

    words = [w.lower() for w in a.grep]
    keep = (lambda s: any(w in s.lower() for w in words)) if words else (lambda s: True)

    print(f"# Reuse index: {root}")
    print(f"feature files: {len(features)} · feature steps: {total_steps} · step definitions: {len(defs)}"
          + (f" · robot keywords: {len(robot_kw)}" if robot_kw else ""))

    if defs:
        print("\n## Step definitions (file:line · keyword · expression · uses in features)")
        by_file = defaultdict(list)
        for d in defs:
            by_file[d["file"]].append(d)
        shown = 0
        for f in sorted(by_file):
            rows = [d for d in by_file[f] if keep(d["expr"])]
            if not rows:
                continue
            print(f"### {f}")
            for d in rows:
                if shown >= a.max:
                    break
                flag = "" if d["rx"] else "  (pattern not parsed — check by hand)"
                print(f"  :{d['line']}  @{d['kw']}  \"{d['expr']}\"  · {d['uses']}x{flag}")
                shown += 1
        unused = [d for d in defs if d["uses"] == 0 and keep(d["expr"])]
        if unused and features:
            print(f"\n## Step definitions used by no feature ({len(unused)}) — reuse candidates or dead code")
            for d in unused[: a.max]:
                print(f"  {d['file']}:{d['line']}  \"{d['expr']}\"")
        und = [(t, locs) for t, locs in undefined.items() if keep(t)]
        if und:
            print(f"\n## Feature steps matching no definition ({len(und)}) — custom parameter types or truly undefined")
            for t, locs in und[: a.max]:
                print(f"  \"{t}\"  · {locs[0]}" + (f" (+{len(locs) - 1})" if len(locs) > 1 else ""))
    if robot_kw:
        print("\n## Robot keywords")
        for rel, n, name in [k for k in robot_kw if keep(k[2])][: a.max]:
            print(f"  {rel}:{n}  {name}")

    step_files = {d["file"] for d in defs}
    units, fixtures = find_code_units(root, a.paths, step_files)
    if fixtures:
        print("\n## Fixtures")
        for rel, n, name in [x for x in fixtures if keep(x[2])][: a.max]:
            print(f"  {rel}:{n}  {name}")
    classes = [u for u in units if "methods" in u]
    funcs = [u for u in units if u.get("kind") == "function"]
    if classes:
        print("\n## Classes (public methods · fields)")
        shown = 0
        for u in classes:
            blob = " ".join([u["name"]] + u["methods"] + u["fields"])
            if not keep(blob) or shown >= a.max:
                continue
            base = f" extends {u['base']}" if u.get("base") else ""
            ms = ", ".join(dict.fromkeys(u["methods"])) or "-"
            fs = f" · fields: {', '.join(u['fields'])}" if u["fields"] else ""
            print(f"  {u['file']}:{u['line']}  {u['name']}{base} — {ms}{fs}")
            shown += 1
    if funcs:
        print("\n## Exported / module-level functions")
        rows = [u for u in funcs if keep(u["name"])]
        by_file = defaultdict(list)
        for u in rows:
            by_file[u["file"]].append(f"{u['name']}:{u['line']}")
        for f in sorted(by_file)[: a.max]:
            print(f"  {f}  {', '.join(by_file[f])}")


if __name__ == "__main__":
    main()
