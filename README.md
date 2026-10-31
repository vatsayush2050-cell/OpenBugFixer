# 🤖 OpenBugFixer Agent

> An autonomous AI agent that scans open-source GitHub repositories, diagnoses issues, and opens pull requests with real code fixes — built for Hacktoberfest.

---

## What it does

```
GitHub Issues → Triage → Code Analysis → Patch Generation → Pull Request
```

1. **Fetches open issues** from any public GitHub repository
2. **Triages each issue** using an LLM to decide if it's autonomously fixable (bug, docs, test)
3. **Reads the relevant source files** from the repo
4. **Generates corrected file content** with an AI model
5. **Opens a pull request** on a new branch — ready for human review

---

## Tech Stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| AI (cloud) | OpenRouter → Mistral 7B / Gemma 7B / Llama 3 8B |
| AI (local) | Ollama → `mistral` |
| GitHub | REST API v3 (no external SDK) |
| Dependencies | `requests`, `python-dotenv` |

Zero LangChain overhead — the agent loop is a simple, readable Python class.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/OpenBugFixer.git
cd OpenBugFixer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — add GITHUB_TOKEN and OPENROUTER_API_KEY (or leave key empty for Ollama)

# 4. Run (dry-run mode — no real PR opened)
python main.py --repo python/mypy --dry-run

# 5. Run for real
python main.py --repo owner/repo --issue 42
```

### CLI Options

```
--repo          owner/repo          Target repository (required)
--issue         <number>            Fix a specific issue (optional)
--dry-run                           Analyse and generate fix, but don't open PR
--max-issues    <int>   (default 5) How many issues to scan when no --issue given
--model         <string>            OpenRouter model string to use
```

---

## Configuration

Copy `.env.example` → `.env` and fill in:

```env
GITHUB_TOKEN=ghp_...          # Fine-grained token: repo + pull-requests write
OPENROUTER_API_KEY=sk-or-...  # Leave empty to use local Ollama instead
```

### Using Ollama (fully offline)

```bash
ollama pull mistral
# leave OPENROUTER_API_KEY empty in .env — agent auto-detects and switches
python main.py --repo owner/repo --dry-run
```

---

## Project Structure

```
OpenBugFixer/
├── main.py                   # CLI entry point
├── config/
│   └── settings.py           # Env-var config dataclass
├── agent/
│   ├── orchestrator.py       # Top-level agent loop
│   ├── issue_analyzer.py     # LLM-powered issue triage
│   ├── code_fixer.py         # LLM-powered patch generation
│   ├── pr_builder.py         # Branch + commit + PR creation
│   └── model_client.py       # OpenRouter / Ollama client
├── github/
│   └── client.py             # GitHub REST API wrapper
└── utils/
    └── logger.py             # Structured console logger
```

---

## Example Run

```
12:03:01 [INFO] 🤖 OpenBugFixer Agent starting up
12:03:01 [INFO]    Model  : mistralai/mistral-7b-instruct
12:03:01 [INFO]    Dry run: False
12:03:01 [INFO] Repository: pallets/flask
12:03:01 [INFO] Default branch: main
12:03:04 [INFO] Fetched 5 open issues
12:03:05 [INFO]   Issue #5821 — fixable=False conf=0.20 — Feature request, not a bug
12:03:07 [INFO]   Issue #5817 — fixable=True  conf=0.85 — Missing return type hint causes mypy failure
12:03:07 [INFO] Selected issue #5817: Add return type to `make_response` helper (confidence 85%)
12:03:12 [INFO] Generating fix for issue #5817 across 1 file(s)
12:03:19 [INFO] Fix generated — 1 file(s) changed
12:03:19 [INFO]   • src/flask/helpers.py: Added `-> Response` return type annotation
12:03:20 [INFO] Created branch: bugfix/openbugfixer-issue-5817
12:03:21 [INFO]   Committed: src/flask/helpers.py
12:03:22 [INFO]   PR opened: https://github.com/pallets/flask/pull/5822
12:03:22 [INFO] ✅ Done! PR opened: https://github.com/pallets/flask/pull/5822
```

---

## How the Agent Works

### Issue Triage (`IssueAnalyzer`)

Sends issue title, body, comments, and repo file tree to the LLM. The model returns:
- `fixable`: boolean
- `confidence`: 0.0–1.0
- `fix_type`: `bug | docs | test | refactor`
- `relevant_files`: list of file paths to inspect

Only issues with `fixable=true` and `confidence ≥ 0.5` proceed.

### Fix Generation (`CodeFixer`)

Fetches the relevant file contents from GitHub, sends them to the LLM alongside the issue, and receives complete corrected file content back — not diffs, to avoid off-by-one patch errors.

### PR Creation (`PRBuilder`)

Creates a new branch from `HEAD`, commits each changed file, and opens a PR with:
- Auto-generated title (`fix:`, `docs:`, `test:`)
- Full PR body explaining the change
- Labels: `hacktoberfest`, `bug`, `automated-fix`

---

## Limitations

- Works best on small, well-scoped issues (type hints, docstrings, simple logic bugs)
- Large files (>100 KB) are skipped
- The model may hallucinate file paths — the agent validates all paths against the real file tree
- Not a replacement for human code review — always review before merging

---

## Contributing

PRs welcome! Good first issues:
- Add support for creating new test files
- Add a `--label` filter to only scan issues with specific labels
- Stream model output for faster feedback

---

## License

MIT

---

*Built for [Hacktoberfest](https://hacktoberfest.com) · Powered by open-weight AI models*
