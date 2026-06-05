#!/usr/bin/env python3
"""Code generator for FateStar Ziwei CLI scripts.

Reads constants.json from scripts/shared/ and injects the API endpoint
constants and the `doc` renderer into each CLI script, so all four language
implementations stay in sync from a single source of truth.

Usage:
    python scripts/generate.py          # Generate all scripts
    python scripts/generate.py --check  # Verify scripts are up-to-date (for CI)
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.join(SCRIPT_DIR, "shared")
SCRIPT_STEM = "ziwei_cli"

# Paired comment markers delimiting generated sections in each language.
MARKERS = {
    ".py": ("# BEGIN GENERATED:{name}", "# END GENERATED:{name}"),
    ".js": ("// BEGIN GENERATED:{name}", "// END GENERATED:{name}"),
    ".ps1": ("# BEGIN GENERATED:{name}", "# END GENERATED:{name}"),
    ".sh": ("# BEGIN GENERATED:{name}", "# END GENERATED:{name}"),
}

LANG_INVOKE = {
    ".py": "python scripts/ziwei_cli.py",
    ".js": "node scripts/ziwei_cli.js",
    ".ps1": "powershell -ExecutionPolicy Bypass -File scripts/ziwei_cli.ps1",
    ".sh": "bash scripts/ziwei_cli.sh",
}
LANG_NAME = {".py": "Python", ".js": "Node.js", ".ps1": "PowerShell", ".sh": "Bash"}
LANG_CODEBLOCK = {".py": "", ".js": "", ".ps1": "powershell", ".sh": "bash"}


def load_constants():
    with open(os.path.join(SHARED_DIR, "constants.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def render_constants(ext, c):
    base, chart, reading = c["api_base"], c["chart_path"], c["reading_path"]
    if ext == ".py":
        return (
            f'DEFAULT_API_BASE = "{base}"\n'
            f'CHART_PATH = "{chart}"\n'
            f'READING_PATH = "{reading}"'
        )
    if ext == ".js":
        return (
            f'const DEFAULT_API_BASE = "{base}";\n'
            f'const CHART_PATH = "{chart}";\n'
            f'const READING_PATH = "{reading}";'
        )
    if ext == ".ps1":
        return (
            f'$DEFAULT_API_BASE = "{base}"\n'
            f'$CHART_PATH = "{chart}"\n'
            f'$READING_PATH = "{reading}"'
        )
    if ext == ".sh":
        return (
            f'DEFAULT_API_BASE="{base}"\n'
            f'CHART_PATH="{chart}"\n'
            f'READING_PATH="{reading}"'
        )
    raise ValueError(f"Unsupported extension: {ext}")


def render_doc_block(ext, c):
    name, invoke, codeblock = LANG_NAME[ext], LANG_INVOKE[ext], LANG_CODEBLOCK[ext]
    if ext == ".py":
        return (
            'def _render_doc():\n'
            '    _dir = os.path.dirname(os.path.abspath(__file__))\n'
            '    _shared = os.path.join(_dir, "shared")\n'
            '    with open(os.path.join(_shared, "doc_spec.md"), "r", encoding="utf-8") as _f:\n'
            '        _tpl = _f.read()\n'
            f'    _tpl = _tpl.replace("{{{{LANG_NAME}}}}", "{name}")\n'
            f'    _tpl = _tpl.replace("{{{{LANG_CODEBLOCK}}}}", "{codeblock}")\n'
            f'    _tpl = _tpl.replace("{{{{LANG_INVOKE}}}}", "{invoke}")\n'
            '    return _tpl'
        )
    if ext == ".js":
        return (
            'function renderDoc() {\n'
            '  const shared = path.join(__dirname, "shared");\n'
            '  let tpl = fs.readFileSync(path.join(shared, "doc_spec.md"), "utf-8");\n'
            f'  tpl = tpl.replace(/\\{{\\{{LANG_NAME\\}}\\}}/g, "{name}");\n'
            f'  tpl = tpl.replace(/\\{{\\{{LANG_CODEBLOCK\\}}\\}}/g, "{codeblock}");\n'
            f'  tpl = tpl.replace(/\\{{\\{{LANG_INVOKE\\}}\\}}/g, "{invoke}");\n'
            '  return tpl;\n'
            '}'
        )
    if ext == ".ps1":
        return (
            'function Render-Doc {\n'
            '    $shared = Join-Path $PSScriptRoot "shared"\n'
            '    $tpl = Get-Content (Join-Path $shared "doc_spec.md") -Raw -Encoding UTF8\n'
            f'    $tpl = $tpl.Replace("{{{{LANG_NAME}}}}", "{name}")\n'
            f'    $tpl = $tpl.Replace("{{{{LANG_CODEBLOCK}}}}", "{codeblock}")\n'
            f'    $tpl = $tpl.Replace("{{{{LANG_INVOKE}}}}", "{invoke}")\n'
            '    return $tpl\n'
            '}'
        )
    if ext == ".sh":
        return (
            '_cmd_doc() {\n'
            '  local tpl\n'
            '  tpl=$(cat "$SCRIPT_DIR/shared/doc_spec.md")\n'
            f'  tpl="${{tpl//\\{{\\{{LANG_NAME\\}}\\}}/{name}}}"\n'
            f'  tpl="${{tpl//\\{{\\{{LANG_CODEBLOCK\\}}\\}}/{codeblock}}}"\n'
            f'  tpl="${{tpl//\\{{\\{{LANG_INVOKE\\}}\\}}/{invoke}}}"\n'
            '  printf \'%s\\n\' "$tpl"\n'
            '}'
        )
    raise ValueError(f"Unsupported extension: {ext}")


def replace_marker_section(content, ext, section_name, new_text):
    begin_tag, end_tag = MARKERS[ext]
    begin = begin_tag.format(name=section_name)
    end = end_tag.format(name=section_name)
    if begin not in content:
        raise ValueError(f"BEGIN marker '{begin}' not found")
    if end not in content:
        raise ValueError(f"END marker '{end}' not found")
    before, rest = content.split(begin, 1)
    _, after = rest.split(end, 1)
    return before + begin + "\n" + new_text + "\n" + end + after


def _read_encoding(ext):
    # PowerShell 5.1 needs a BOM to read non-ASCII .ps1 correctly; utf-8-sig
    # round-trips files with or without a BOM and strips it on read so content
    # comparisons stay stable.
    return "utf-8-sig"


def _write_encoding(ext):
    return "utf-8-sig" if ext == ".ps1" else "utf-8"


def generate_script(script_path, c):
    ext = os.path.splitext(script_path)[1]
    with open(script_path, "r", encoding=_read_encoding(ext)) as f:
        content = f.read()
    content = replace_marker_section(content, ext, "CONSTANTS", render_constants(ext, c))
    content = replace_marker_section(content, ext, "DOC_SPEC", render_doc_block(ext, c))
    return content


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate FateStar Ziwei CLI scripts from shared data")
    parser.add_argument("--check", action="store_true", help="Verify scripts are up-to-date (for CI)")
    args = parser.parse_args()

    c = load_constants()
    changed = False
    for ext in [".py", ".js", ".ps1", ".sh"]:
        name = f"{SCRIPT_STEM}{ext}"
        path = os.path.join(SCRIPT_DIR, name)
        try:
            new_content = generate_script(path, c)
            with open(path, "r", encoding=_read_encoding(ext)) as f:
                old_content = f.read()
            if new_content != old_content:
                changed = True
                if not args.check:
                    with open(path, "w", encoding=_write_encoding(ext), newline="") as f:
                        f.write(new_content)
                    print(f"Generated: {name}")
                else:
                    print(f"CHANGED: {name} (run generate.py to update)")
            else:
                print(f"OK: {name}")
        except Exception as e:
            print(f"ERROR in {name}: {e}", file=sys.stderr)
            sys.exit(1)

    if args.check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
