---
name: translate-notebook
description: >-
  Translate Jupyter notebooks (.ipynb) to Japanese (or other target languages),
  preserving code cells, metadata, IDs, execution structure, and validating
  the resulting notebook using nbformat and AST parsers.
metadata:
  icon: translate
---

# Translate Notebook Skill

This skill guides the agent in translating Jupyter Notebooks (`.ipynb`) while strictly maintaining structural integrity, valid JSON format, code execution correctness, and consistent technical terminology.

---

## Workflow

### 1. Identify Target & Preferences

Before translating, clarify or confirm the following (use `ask_question` if ambiguous):
1. **Target Language**: Default is Japanese (`ja`) for ASL immersion notebooks unless specified otherwise.
2. **Output Location**:
   - Save as a new file appending the language code: `<original_name>_<lang>.ipynb` (e.g. `building_agent_with_mcp_ja.ipynb`).
   - Or overwrite the original if explicitly requested.
3. **Translation Scope**:
   - **Recommended**: Markdown cells + code comments and docstrings.
   - Or Markdown cells only (leaving code comments in English).

---

### 2. Translation & Formatting Guidelines

#### Preserving Code & Execution Integrity
- **Do NOT alter runnable code**: Keep variable names, function names, imports, parameters, shell commands (`!gcloud`, `%bash`), and API calls intact.
- **Code Comments**: Translate inline `#` comments and docstrings naturally into the target language.
- **JSON & Notebook Structure**:
  - Load the original `.ipynb` via Python `json.load()` and clone its dictionary structure.
  - Preserve all cell metadata, cell `id`s, `execution_count`, and `outputs`.
  - Preserve notebook-level `metadata` (such as `kernelspec` and `language_info`).
  - Preserve newline endings in cell `source` lists (`\n` at the end of lines).
  - Dump output JSON with `ensure_ascii=False, indent=1` to keep UTF-8 characters human-readable without escape sequences.

#### Technical Terminology & Localization Conventions (Japanese)
- **Standard ML / Cloud Terms**:
  - Keep standard product and API names in English: BigQuery, Vertex AI, Google Maps, ADK, Gemini, Cloud Run, GCS.
  - Model Context Protocol (MCP) -> Model Context Protocol（MCP）
  - Agent Development Kit -> Agent Development Kit（ADK）
- **User Prompt Samples in Markdown**:
  - When a notebook includes example questions to ask an agent, keep the original English text and append the Japanese translation in parentheses:
    > e.g., `"Which zip code in Los Angeles has the highest morning foot traffic?"（ロサンゼルスで朝の人出が最も多い郵便番号はどこですか？）`
  - This allows users to either copy-paste the English prompt into the agent or understand its meaning immediately.
- **Licenses & Legal Disclaimers**:
  - Leave standard Apache 2.0 / open source license headers in English.
  - Translate citations and overview notes (e.g., `Citation & Disclaimer` -> `引用および免責事項`).

---

### 3. Execution Pattern

Write and execute a Python script to perform the cell-by-cell translation:

```python
import json
import copy

with open("path/to/original.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Helper to format lines preserving newlines
def to_source_lines(text):
    return text.splitlines(keepends=True)

# Deep copy notebook structure
new_nb = copy.deepcopy(nb)

# Replace cell sources by index with translated text
# new_nb['cells'][idx]['source'] = to_source_lines(translated_text)

with open("path/to/translated.ipynb", "w", encoding="utf-8") as f:
    json.dump(new_nb, f, ensure_ascii=False, indent=1)
    f.write("\n")
```

---

### 4. Automated Validation

Immediately after generating the translated notebook, run the validation utility:

```bash
python .agents/skills/translate-notebook/scripts/validate_notebook.py <path/to/translated.ipynb> --orig <path/to/original.ipynb>
```

The script verifies:
1. **JSON Syntax**: The file is valid UTF-8 JSON.
2. **Notebook Schema**: Validates against `nbformat` (v4).
3. **Python / IPython Syntax**: Runs IPython `TransformerManager` and Python `ast.parse` on every code cell.
4. **Markdown Formatting**: Ensures code fences (```` ``` ````) are balanced and links are formatted properly.
5. **Structural Parity**: Compares cell counts, cell types, and cell IDs 1-to-1 against the original notebook.

---

### 5. Post-Translation Notes for Users

When reporting completion to the user:
- Provide clickable markdown links to both the original and translated files.
- Summarize the translation scope (markdown cells translated, code comments localized, execution code untouched).
- Note that in VS Code, if the notebook initially opens in raw JSON format, they can right-click the tab and select **"Reopen Editor With..." (エディターの表示形式を選択...) -> "Jupyter Notebook"**.
