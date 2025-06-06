# Gideon

**Gideon** is an AI-powered CLI tool for intelligent file organization, focused on renaming academic documents (PDFs) using LLMs (Large Language Models) such as Ollama, and removing duplicate files.  
It is designed for local, privacy-friendly use, and is easily extensible for future LLM integrations.

---

## Features

- **AI-powered PDF renaming**: Extracts metadata (authors, year, title, topic) and generates clean, consistent filenames.
- **Duplicate file removal**: Quickly find and remove duplicate PDF files in a directory.
- **File organization**: Organize files into topic-based folders based on file naming conventions.
- **Modular architecture**: Easily add new LLM providers or agents.
- **Rich CLI interface**: Beautiful output and flexible options.
- **Local-first**: No cloud required; works with local LLMs like Ollama.

---

## Installation

**Requirements:**
- Python 3.11+
- [Ollama](https://ollama.com/) (for local LLMs, optional but recommended)

**Install in development mode:**
```bash
git clone https://github.com/yourusername/gideon.git
cd gideon
pip install -e .
```

**Configure Gideon:**

Gideon can be configured by creating a `.env` file in the project root:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

---

## Usage

### Rename Files with AI

```bash
gideon rename auto ./documents/
```

#### With custom LLM options

```bash
gideon rename auto ./documents/ --llm-type ollama --model codellama --temperature 0.2
```

- `--llm-type`: The LLM backend to use (default: `ollama`)
- `--model`: The model name (default: `llama2`)
- `--temperature`: Sampling temperature for the LLM (default: `0.1`)

### Remove Duplicate Files

Remove duplicates in a directory:
```bash
gideon remove-duplicates ./documents/
```

- This will scan for duplicate PDF files and remove them, keeping only one copy of each unique file.

### Organize Files

Organize files into topic-based folders:
```bash
gideon organize ./documents/
```

Options:
- `--dry-run` or `-d`: Preview changes without actually moving files
- `--ignore` or `-i`: Comma-separated list of directory patterns to ignore (e.g. '.git,.vscode')

---

## CLI Commands

- `gideon rename auto <directory> [--llm-type TYPE] [--model MODEL] [--temperature FLOAT]`  
  Rename PDF files in a directory using AI analysis.
- `gideon remove-duplicates <directory>`  
  Remove duplicate PDF files in a directory (default mode).
- `gideon organize <directory> [--dry-run] [--ignore PATTERNS]`  
  Organize files into topic-based folders based on file naming conventions.

---

## Project Structure

```
gideon/
│
├── src/gideon/
│   ├── cli/           # CLI commands and entry point
│   ├── core/          # Global configuration
│   ├── llm/           # LLM integrations (Ollama, etc.)
│   ├── agents/        # Specialized agents (RenameWizard, etc.)
│   ├── services/      # File and directory services
│   └── utils/         # Utilities and parsers
│
├── pyproject.toml     # Project metadata and dependencies
└── README.md
```

---

## Configuration

Gideon can be configured using environment variables or a `.env` file in the project root. The available configuration options are:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEFAULT_LLM_TYPE` | The default LLM backend to use | `ollama` |
| `DEFAULT_LLM_MODEL` | The default model name | `deepseek-r1:latest` |
| `DEFAULT_LLM_TEMPERATURE` | The default sampling temperature | `0.1` |
| `MAX_CONTENT_LENGTH` | Maximum content length for processing | `5000` |
| `SUPPORTED_EXTENSIONS` | File extensions that Gideon can process | `[".pdf"]` |

An example configuration file is provided at `.env.example`.

## Extending

- **Add a new LLM**: Implement a new service in `src/gideon/llm/`, register it in the factory.
- **Add a new agent**: Create a new agent in `src/gideon/agents/` and wire it into the CLI.

---

## Development

- Install dev dependencies:  
  `pip install -e .[dev]`
- Run linter:  
  `ruff check src/`
- Run tests:  
  `pytest`

### Test Coverage
- Tests for duplicate removal are located in `src/gideon/services/test_file_service.py` and use `pytest` for isolated, reliable testing.
- Async tests for AI renaming are supported with `pytest-asyncio`.

---

## License

MIT License

---

## Author

Alejandro Sánchez Yalí  
[asanchezyali@gmail.com](mailto:asanchezyali@gmail.com)

---

**Note:**  
Gideon is under active development. Contributions and feedback are welcome!

docker desktop enable model-runner --tcp 11434

