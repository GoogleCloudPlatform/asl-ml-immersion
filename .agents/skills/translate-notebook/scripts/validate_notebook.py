#!/usr/bin/env python3
# pylint: skip-file
"""Validation utility for translated Jupyter notebooks."""

import argparse
import ast
import json
import re
import sys
import textwrap


def _normalize_code_for_comparison(source: str, transformer=None) -> str:
    """Normalize a code cell's source so only comments and docstrings are ignored.

    All executable statements, identifiers, arguments, string literals (prompts,
    dict keys/values, print strings, etc.), magic commands, and TODO placeholders
    are preserved in the normalized representation.
    """
    lines = source.splitlines()
    magic_header = ""
    if lines and lines[0].strip().startswith("%%"):
        magic_line = lines[0].strip()
        magic_header = re.sub(r"#.*$", "", magic_line).strip()
        body = "\n".join(lines[1:])
        if magic_header.startswith("%%writefile") and re.search(
            r"\.py\b", magic_header
        ):
            source = textwrap.dedent(body)
        else:
            cleaned = []
            for l in lines:
                l_no_comment = re.sub(r"(#|--).*$", "", l).strip()
                if l_no_comment:
                    cleaned.append(l_no_comment)
            return "MAGIC:\n" + "\n".join(cleaned)

    proc_lines = []
    in_shell_continuation = False
    for l in source.splitlines():
        stripped = l.strip()
        if stripped.startswith(("!", "%")) or in_shell_continuation:
            in_shell_continuation = stripped.endswith("\\")
            l = re.sub(r"#.*$", "", l).rstrip()
        proc_lines.append(l)
    clean = "\n".join(proc_lines)
    clean = re.sub(r"#\s*TODO\b[^\n\"']*", "# TODO", clean, flags=re.IGNORECASE)
    clean = re.sub(
        r"(=\s*)#\s*TODO\b", r"\g<1>None # TODO", clean, flags=re.IGNORECASE
    )
    clean = re.sub(
        r"(:\s*\n\s*)#\s*TODO\b",
        r"\g<1>pass # TODO",
        clean,
        flags=re.IGNORECASE,
    )

    try:
        if transformer:
            transformed = transformer.transform_cell(clean)
            tree = ast.parse(transformed)
        else:
            clean_py_lines = [
                l
                for l in clean.splitlines()
                if not l.strip().startswith(("!", "%", "#"))
                and not re.match(r"^\s*\w+\s*=\s*[!%]", l)
            ]
            magic_lines = [
                re.sub(r"#.*$", "", l).strip()
                for l in clean.splitlines()
                if l.strip().startswith(("!", "%"))
                or re.match(r"^\s*\w+\s*=\s*[!%]", l)
            ]
            tree = ast.parse("\n".join(clean_py_lines))
            magic_header += "\n".join(magic_lines)

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.Module,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                if (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)
                ):
                    node.body[0].value.value = "__DOCSTRING__"
        return f"AST:{magic_header}:{ast.dump(tree)}"
    except Exception:
        cleaned = [re.sub(r"#.*$", "", l).strip() for l in source.splitlines()]
        return f"RAW:{magic_header}:" + "\n".join(c for c in cleaned if c)


def validate_notebook(target_path: str, orig_path: str = None) -> bool:
    all_passed = True
    print(f"=== Validating Notebook: {target_path} ===")

    # 1. JSON parsing
    try:
        with open(target_path, encoding="utf-8") as f:
            nb = json.load(f)
        print(" [PASS] JSON syntax is valid.")
    except Exception as e:
        print(f" [FAIL] JSON parsing failed: {e}")
        return False

    # 2. nbformat schema validation
    try:
        import nbformat

        nb_obj = nbformat.from_dict(nb)
        nbformat.validate(nb_obj)
        print(" [PASS] nbformat schema validation passed.")
    except ImportError:
        # Fallback basic schema checks
        if "cells" in nb and "metadata" in nb and "nbformat" in nb:
            print(
                " [PASS] Basic notebook schema validated (nbformat library not installed)."
            )
        else:
            print(
                " [FAIL] Missing required top-level notebook keys (cells, metadata, nbformat)."
            )
            all_passed = False
    except Exception as e:
        print(f" [FAIL] nbformat schema error: {e}")
        all_passed = False

    # 3. Code cells syntax & AST
    transformer = None
    try:
        from IPython.core.inputtransformer2 import TransformerManager

        transformer = TransformerManager()
    except ImportError:
        pass

    orig_code_errors = set()
    if orig_path:
        try:
            with open(orig_path, encoding="utf-8") as f:
                _orig = json.load(f)
            for _idx, _cell in enumerate(_orig.get("cells", [])):
                if _cell.get("cell_type") == "code":
                    _lines = _cell.get("source", [])
                    _src = (
                        "".join(_lines) if isinstance(_lines, list) else _lines
                    )
                    _clean = re.sub(
                        r"(=\s*)#\s*TODO\b",
                        r"\g<1>None # TODO",
                        _src,
                        flags=re.IGNORECASE,
                    )
                    _clean = re.sub(
                        r"(:\s*\n\s*)#\s*TODO\b",
                        r"\g<1>pass # TODO",
                        _clean,
                        flags=re.IGNORECASE,
                    )
                    try:
                        if transformer:
                            ast.parse(transformer.transform_cell(_clean))
                        else:
                            ast.parse(_clean)
                    except Exception:
                        orig_code_errors.add(_idx)
        except Exception:
            pass

    code_cells_count = 0
    code_errors = []
    for idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "code":
            code_cells_count += 1
            src_lines = cell.get("source", [])
            src = (
                "".join(src_lines) if isinstance(src_lines, list) else src_lines
            )
            # Handle student placeholders in lab notebooks (e.g. `x = #TODO`)
            clean_src = re.sub(
                r"(=\s*)#\s*TODO\b",
                r"\g<1>None # TODO",
                src,
                flags=re.IGNORECASE,
            )
            clean_src = re.sub(
                r"(:\s*\n\s*)#\s*TODO\b",
                r"\g<1>pass # TODO",
                clean_src,
                flags=re.IGNORECASE,
            )
            try:
                if transformer:
                    transformed = transformer.transform_cell(clean_src)
                    ast.parse(transformed)
                else:
                    # Filter basic ipython magic commands if transformer not available
                    clean_lines = [
                        l
                        for l in clean_src.splitlines()
                        if not l.strip().startswith(("!", "%", "#"))
                        and not re.match(r"^\s*\w+\s*=\s*[!%]", l)
                    ]
                    ast.parse("\n".join(clean_lines))
            except Exception as e:
                code_errors.append((idx, str(e)))

    new_code_errors = [e for e in code_errors if e[0] not in orig_code_errors]
    inherited_errors = [e for e in code_errors if e[0] in orig_code_errors]

    if inherited_errors:
        print(
            f" [WARN] {len(inherited_errors)} code cell(s) have syntax errors inherited from original notebook:"
        )
        for idx, err in inherited_errors:
            print(f"        - Cell {idx}: {err}")

    if not new_code_errors:
        print(
            f" [PASS] All {code_cells_count} code cells passed AST syntax checks (no new errors)."
        )
    else:
        all_passed = False
        print(
            f" [FAIL] {len(new_code_errors)} code cell(s) failed syntax checks:"
        )
        for idx, err in new_code_errors:
            print(f"        - Cell {idx}: {err}")

    # 4. Markdown cells formatting
    md_cells_count = 0
    md_errors = []
    for idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "markdown":
            md_cells_count += 1
            src_lines = cell.get("source", [])
            src = (
                "".join(src_lines) if isinstance(src_lines, list) else src_lines
            )
            fences = [m for m in re.finditer(r"```", src)]
            if len(fences) % 2 != 0:
                md_errors.append(
                    (idx, f"Unclosed code fences ({len(fences)} backtick sets)")
                )

    if not md_errors:
        print(
            f" [PASS] All {md_cells_count} markdown cells passed formatting checks."
        )
    else:
        all_passed = False
        print(
            f" [FAIL] {len(md_errors)} markdown cell(s) have formatting issues:"
        )
        for idx, err in md_errors:
            print(f"        - Cell {idx}: {err}")

    # 5. Comparison with original notebook if provided
    if orig_path:
        print(f"\n--- Comparing with Original: {orig_path} ---")
        try:
            with open(orig_path, encoding="utf-8") as f:
                orig_nb = json.load(f)

            orig_cells = orig_nb.get("cells", [])
            target_cells = nb.get("cells", [])

            if len(orig_cells) != len(target_cells):
                print(
                    f" [FAIL] Cell count mismatch: {len(orig_cells)} original vs {len(target_cells)} target."
                )
                all_passed = False
            else:
                print(f" [PASS] Cell count matches: {len(orig_cells)} cells.")

            type_mismatches = []
            id_mismatches = []
            for i in range(min(len(orig_cells), len(target_cells))):
                if orig_cells[i].get("cell_type") != target_cells[i].get(
                    "cell_type"
                ):
                    type_mismatches.append(i)
                if orig_cells[i].get("id") != target_cells[i].get("id"):
                    id_mismatches.append(i)

            if not type_mismatches:
                print(" [PASS] Cell types match 1:1 across all cells.")
            else:
                print(
                    f" [FAIL] Cell type mismatch at indices: {type_mismatches}"
                )
                all_passed = False

            if not id_mismatches:
                print(" [PASS] Cell IDs match 1:1 across all cells.")
            else:
                print(
                    f" [WARN] Cell ID differences at indices: {id_mismatches}"
                )

            code_mismatches = []
            for i in range(min(len(orig_cells), len(target_cells))):
                if (
                    orig_cells[i].get("cell_type") == "code"
                    and target_cells[i].get("cell_type") == "code"
                    and i not in orig_code_errors
                ):
                    orig_lines = orig_cells[i].get("source", [])
                    orig_src = (
                        "".join(orig_lines)
                        if isinstance(orig_lines, list)
                        else orig_lines
                    )
                    target_lines = target_cells[i].get("source", [])
                    target_src = (
                        "".join(target_lines)
                        if isinstance(target_lines, list)
                        else target_lines
                    )
                    if _normalize_code_for_comparison(
                        orig_src, transformer
                    ) != _normalize_code_for_comparison(
                        target_src, transformer
                    ):
                        code_mismatches.append(i)

            if not code_mismatches:
                print(
                    " [PASS] Executable code & AST match 1:1 across all code cells (only comments/docstrings translated)."
                )
            else:
                print(
                    f" [FAIL] Executable code modification / hallucination detected at cell indices: {code_mismatches}"
                )
                all_passed = False

        except Exception as e:
            print(f" [FAIL] Could not load or compare original notebook: {e}")
            all_passed = False

    print("\n" + ("=" * 40))
    if all_passed:
        print("OVERALL RESULT: SUCCESS (Notebook is valid and intact)")
        return True
    else:
        print("OVERALL RESULT: FAILED (Issues detected)")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate a translated Jupyter Notebook."
    )
    parser.add_argument(
        "target", help="Path to the translated notebook (.ipynb)"
    )
    parser.add_argument(
        "--orig",
        help="Path to the original notebook to compare against",
        default=None,
    )
    args = parser.parse_args()

    success = validate_notebook(args.target, args.orig)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
