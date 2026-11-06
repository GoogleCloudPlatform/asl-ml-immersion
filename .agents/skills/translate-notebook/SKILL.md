---
name: translate-notebook
description: >-
  Translate Jupyter notebooks (.ipynb) into a target language, preserving
  code cells, metadata, IDs, execution structure, and validating the resulting
  notebook using nbformat and AST parsers.
metadata:
  icon: translate
---

# Translate Notebook Skill

This skill guides the agent in translating Jupyter Notebooks (`.ipynb`) into any target language while strictly maintaining structural integrity, valid JSON format, code execution correctness, and consistent technical terminology.

---

## Workflow

### 1. Identify Target & Preferences

Before translating, clarify or confirm the following (use `ask_question` if ambiguous):
1. **Target Language**: Confirm the target language and its ISO language code (e.g., `ja`, `es`, `fr`, `pt`, `ko`, `zh`) if not explicitly specified by the user.
2. **Output Location**:
   - Save as a new file appending the language code: `<original_name>_<lang>.ipynb` (e.g. `building_agent_with_mcp_ja.ipynb`, `building_agent_with_mcp_es.ipynb`).
   - Or overwrite the original if explicitly requested.
3. **Translation Scope**:
   - **Recommended**: Markdown cells + code comments and docstrings.
   - Or Markdown cells only (leaving code comments in the source language).

---

### 2. Translation & Formatting Guidelines

#### Preserving Code & Execution Integrity (Strict Anti-Hallucination Rules)
- **STRICT PROHIBITION on Rewriting Code Cells**:
  - **NEVER rewrite, refactor, or regenerate a code cell from scratch.** Replacing an entire code cell's `source` with a newly generated string is strictly prohibited because it leads to hallucinated variable names, altered prompt templates, or broken logic.
  - Always start from the original cell's `source` and apply targeted in-place replacements **only** to comments and docstrings.
- **Do NOT alter runnable code**: Keep all variable names, function names, imports, parameters, type annotations, shell/magic commands (`!gcloud`, `%bash`, `%%writefile`, `%%bigquery`), and API calls 100% identical to the original notebook.
- **Do NOT alter string literals in code**: Never translate or modify string literals used in execution, including LLM prompt templates (`PromptTemplate`, system instructions), dictionary keys/values, mock data, CLI argument `help="..."` strings, plot titles/labels, or `print()` / `logging` messages unless explicitly requested by the user.
- **Do NOT solve or alter `# TODO` placeholders**: In lab notebooks, keep student `# TODO` markers and placeholder expressions (`None # TODO`, `...`) intact. Only the descriptive text following `# TODO:` may be translated.
- **Code Comments & Docstrings ONLY**: Translate inline/standalone `#` comments (and SQL `--` comments in `%%bigquery`) and Python module/class/function docstrings (`"""..."""`) naturally into the target language. Leave commented-out runnable code (e.g. `# output = chain.invoke(...)`) untouched.
- **JSON & Notebook Structure**:
  - Load the original `.ipynb` via Python `json.load()` and clone its dictionary structure.
  - Preserve all cell metadata, cell `id`s, `execution_count`, and `outputs`.
  - Preserve notebook-level `metadata` (such as `kernelspec` and `language_info`).
  - Preserve newline endings in cell `source` lists (`\n` at the end of lines).
  - Dump output JSON with `ensure_ascii=False, indent=1` to keep UTF-8 characters human-readable without escape sequences.

#### Technical Terminology & Localization Conventions
- **Standard ML / Cloud Terms**:
  - Keep standard product, library, and API names in their canonical English form: BigQuery, Vertex AI, Google Maps, ADK, Gemini, Cloud Run, GCS, LangChain, TensorFlow, PyTorch.
  - Preserve standard abbreviations alongside localized or full terms (e.g., `Model Context Protocol (MCP)`, `Agent Development Kit (ADK)`).
- **User Prompt Samples in Markdown**:
  - When a notebook includes example prompts/questions to send to an agent or LLM, keep the original prompt text and append the target-language translation in parentheses so users can copy-paste the original prompt while understanding its meaning immediately.
- **Licenses & Legal Disclaimers**:
  - Leave standard Apache 2.0 / open source license headers in English.
  - Translate section headings such as citations, overview notes, and disclaimers into the target language.

---

### 3. Execution Pattern

Write and execute a Python script to perform the translation. **Never overwrite a code cell with a re-typed block of code**—use targeted `str.replace()` on the original code cell's source so executable code cannot be hallucinated or altered:

```python
import copy
import json

with open("path/to/original.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)


def to_source_lines(text):
    return text.splitlines(keepends=True)


def replace_code_comments(orig_lines, replacements):
    """Safely replace only specific comments/docstrings in an original code cell."""
    src = "".join(orig_lines)
    for orig_text, translated_text in replacements.items():
        assert (
            orig_text in src
        ), f"Original comment/docstring not found: {orig_text!r}"
        src = src.replace(orig_text, translated_text, 1)
    return src.splitlines(keepends=True)


# Deep copy notebook structure
new_nb = copy.deepcopy(nb)

# 1. Replace Markdown cells by index with translated markdown text:
# new_nb["cells"][md_idx]["source"] = to_source_lines(translated_markdown)

# 2. For Code cells, apply targeted comment/docstring replacements ONLY:
# new_nb["cells"][code_idx]["source"] = replace_code_comments(
#     nb["cells"][code_idx]["source"],
#     {
#         "# Original comment": "# <Translated comment>",
#         '"""Original docstring."""': '"""<Translated docstring>"""',
#     },
# )

with open("path/to/translated.ipynb", "w", encoding="utf-8") as f:
    json.dump(new_nb, f, ensure_ascii=False, indent=1)
    f.write("\n")
```

---

### 4. Automated Validation

Immediately after generating the translated notebook, run the validation utility (always pass `--orig`):

```bash
python .agents/skills/translate-notebook/scripts/validate_notebook.py <path/to/translated.ipynb> --orig <path/to/original.ipynb>
```

The script verifies:
1. **JSON Syntax**: The file is valid UTF-8 JSON.
2. **Notebook Schema**: Validates against `nbformat` (v4).
3. **Python / IPython Syntax**: Runs IPython `TransformerManager` and Python `ast.parse` on every code cell.
4. **Markdown Formatting**: Ensures code fences (```` ``` ````) are balanced and links are formatted properly.
5. **Structural Parity**: Compares cell counts, cell types, and cell IDs 1-to-1 against the original notebook.
6. **Executable Code & AST Parity (Anti-Hallucination Check)**: Normalizes comments and docstrings and compares the AST and non-comment lines of every code cell against the original notebook, failing if any runnable code, variable names, string literals, prompt templates, or `# TODO` placeholders were altered.

---

### 5. Post-Translation Notes for Users

When reporting completion to the user:
- Provide clickable markdown links to both the original and translated files.
- Summarize the translation scope (markdown cells translated, code comments localized, execution code untouched).
- Note that in VS Code, if the notebook initially opens in raw JSON format, they can right-click the tab and select **"Reopen Editor With..." -> "Jupyter Notebook"**.
