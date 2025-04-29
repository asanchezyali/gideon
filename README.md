# Gideon - Intelligent Document Organization System

Gideon is a powerful document organization system that uses artificial intelligence to automatically classify, rename, and organize your documents. It supports both automated and manual processing modes, making it flexible for various use cases.

## Features

- **Intelligent Document Classification**: Automatically identifies document types including:
  - Academic Articles (Art)
  - Books and E-books (Book)
  - Theses and Dissertations (Theses)
  - Commercial Documents (CommDoc)
  - Legal Documents (LegalDoc)
  - Non-Disclosure Agreements (NDA)
  - Personal Documents (PersonalDoc)

- **Smart Duplicate Detection**: Identifies and handles duplicate files using secure hash verification
- **Metadata Extraction**: Automatically extracts metadata like authors, dates, titles, and topics
- **Standardized File Naming**: Enforces consistent naming conventions based on document types
- **Rich Terminal Interface**: Beautiful command-line interface with progress tracking and visual feedback
- **Async Processing**: Handles multiple documents concurrently for better performance

## Installation

1. Ensure you have Python 3.10 or newer installed
2. Clone this repository
3. Install dependencies:
```bash
pip install -e .
```

## Usage

Gideon can be used in two modes: automated (using AI) or manual. Here are the main commands:

### Organize Documents (Recommended)

```bash
gideon organize /path/to/documents --automated --auto-delete
```

Options:
- `--automated`: Use AI for automatic classification (default: True)
- `--auto-delete`: Automatically remove duplicates (default: False)

### Manual File Operations

#### Rename Files
```bash
gideon rename /path/to/documents
```

#### Remove Duplicates
```bash
gideon duplicates /path/to/documents --auto-delete
```

## File Naming Conventions

Gideon uses standardized naming conventions based on document types:

### Academic Documents
Format: `author.year.title.topic.type.ext`
Example: `john_smith.2024.quantum_computing_basics.CompSci.Art.pdf`

### Commercial Documents
Format: `date.company.name.type.ext`
Example: `2024_apr_15.ACME_CORP.project_proposal.CommDoc.pdf`

## Supported File Types

- PDF Documents (.pdf)
- Text Files (.txt)
- Markdown Files (.md)
- ReStructured Text (.rst)

## Supported Topics

Gideon supports various academic and professional topics including:
- Mathematics (Math)
- Computer Science (CompSci)
- Machine Learning/AI (MLAI)
- Physics (Phys)
- Engineering (Eng)
- Business (Bus)
- Economics and Finance (EcoFin)
- And many more...

## Requirements

- Python ≥ 3.10
- Ollama (for AI-powered classification)
- Additional dependencies listed in requirements.txt

## Contributing

We welcome contributions! Please check our contribution guidelines and feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
