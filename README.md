<div align="center">

# 🔮 Gideon

### AI-Powered Research Assistant for Academic Document Management

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#-features) • [Quick Start](#-quick-start) • [Examples](#-examples) • [Architecture](#-architecture) • [Roadmap](#-roadmap)

---

**Gideon transforms your research workflow with AI-powered document organization, semantic search, and intelligent Q&A.**

Tired of manually organizing hundreds of research papers? Let Gideon do it for you.

</div>

---

## ✨ Features

### 🔍 **Semantic Search & RAG**
Search your document collection using natural language. Ask questions and get AI-powered answers backed by your research papers.

```bash
gideon search ask "What are the latest advances in transformer architectures?"
```

### 🤖 **Multi-LLM Support**
Choose the best AI model for your needs:
- **OpenAI** (GPT-4 Turbo, GPT-4) - Fast, high-quality
- **Anthropic** (Claude 3.5 Sonnet) - Large context, excellent reasoning
- **Ollama** (Local models) - Privacy-first, free, offline

### 📄 **Intelligent Document Management**
- **AI-Powered Renaming**: Extract metadata (authors, year, title) and generate clean filenames
- **Topic Classification**: Auto-categorize papers into 30+ topics
- **Duplicate Detection**: Find and remove duplicates intelligently
- **Auto-Organization**: Sort files into topic-based folders

### 🎯 **Key Capabilities**

| Feature | Description | Status |
|---------|-------------|--------|
| 🔎 **Semantic Search** | Find relevant papers using natural language queries | ✅ **Ready** |
| 💬 **RAG Q&A** | Ask questions, get answers from your research collection | ✅ **Ready** |
| 📊 **Smart Organization** | Auto-categorize and rename based on content | ✅ **Ready** |
| 🔄 **Duplicate Detection** | Identify identical or similar documents | ✅ **Ready** |
| 🏷️ **Topic Classification** | 30+ predefined academic topics | ✅ **Ready** |
| 🌐 **Multi-Format Support** | PDF, Word, PowerPoint, EPUB, Markdown, Images (OCR) | ✅ **Ready** |
| 📝 **Document Summarization** | Generate briefs, structured summaries, Cornell notes | ✅ **Ready** |
| 📚 **Reference Extraction** | Extract bibliographies, export to BibTeX/APA | ✅ **Ready** |
| 📖 **Literature Reviews** | Auto-generate literature reviews on topics | ✅ **Ready** |
| 🕸️ **Knowledge Graphs** | Build citation and topic networks | ✅ **Ready** |
| 📈 **Analytics Dashboard** | Visualize collection insights | ✅ **Ready** |
| 💾 **Local-First** | Privacy-focused with local LLM support | ✅ **Ready** |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/asanchezyali/gideon.git
cd gideon

# Install dependencies
pip install -e .

# Configure (copy and edit .env)
cp .env.example .env
```

### Configuration

Edit `.env` with your settings:

```bash
# Choose your LLM provider
DEFAULT_LLM_SERVICE_TYPE=openai  # or: ollama, anthropic

# Model selection
DEFAULT_LLM_MODEL=gpt-4-turbo-preview

# API Keys (if using cloud providers)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

### Usage

#### 1️⃣ **Index Your Documents**

```bash
gideon search index ./research-papers/
```

#### 2️⃣ **Search Semantically**

```bash
gideon search search "attention mechanisms in neural networks" --top-k 5
```

#### 3️⃣ **Ask Questions (RAG)**

```bash
gideon search ask "What papers discuss few-shot learning?"
```

#### 4️⃣ **Rename Files with AI**

```bash
gideon rename auto ./documents/
```

#### 5️⃣ **Organize by Topics**

```bash
gideon organize ./documents/
```

---

## 💡 Examples

### Semantic Search

```bash
$ gideon search search "transformer attention mechanisms" --top-k 3

┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ # ┃ Document                     ┃ Similarity ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1 │ Attention_Is_All_You_Need... │ 94.2%      │
│ 2 │ BERT_Pretraining...          │ 89.7%      │
│ 3 │ GPT3_Language_Models...      │ 87.3%      │
└───┴──────────────────────────────┴────────────┘
```

### Q&A with RAG

```bash
$ gideon search ask "How do transformers handle long sequences?"

╭─ Answer (confidence: 91.5%) ─────────────────────────────╮
│                                                           │
│ Transformers handle long sequences through several       │
│ techniques:                                               │
│                                                           │
│ 1. **Self-Attention Mechanism**: Allows the model to     │
│    attend to all positions in the sequence...            │
│                                                           │
│ 2. **Positional Encoding**: Adds position information... │
│                                                           │
│ Sources:                                                  │
│ - Attention Is All You Need (Vaswani et al., 2017)      │
│ - Longformer (Beltagy et al., 2020)                     │
╰───────────────────────────────────────────────────────────╯
```

### Auto-Renaming Documents

**Before:**
```
paper1.pdf
download (3).pdf
untitled-document-final-v2.pdf
```

**After:**
```
Vaswani.2017.Attention_Is_All_You_Need.Deep_Learning.pdf
Devlin.2018.BERT_Pretraining_Deep_Bidirectional.NLP.pdf
Brown.2020.GPT3_Language_Models_Few_Shot.AI.pdf
```

---

## 🏗️ Architecture

```
Gideon
├── 🔍 Search Engine (ChromaDB + Embeddings)
│   ├── Document indexing with vector embeddings
│   ├── Semantic similarity search
│   └── RAG-based Q&A system
│
├── 🤖 Multi-LLM Support
│   ├── OpenAI (GPT-4, GPT-3.5)
│   ├── Anthropic (Claude 3.5, Opus, Sonnet)
│   ├── Ollama (Local models: Llama, Mistral, DeepSeek)
│   └── LLM Router (auto-select best model)
│
├── 📄 Document Processing
│   ├── PDF extraction (PyPDF2)
│   ├── Metadata extraction
│   ├── Topic classification (30+ categories)
│   └── Content analysis
│
└── 🛠️ Utilities
    ├── Smart duplicate detection
    ├── File organization
    └── Batch processing
```

---

## 🎯 Use Cases

### For Researchers
- **Literature Review**: Quickly find relevant papers on a topic
- **Paper Organization**: Auto-categorize and rename papers
- **Knowledge Q&A**: Ask questions across your entire research collection

### For Students
- **Study Material Management**: Organize papers by subject
- **Quick Reference**: Find specific information across documents
- **Citation Discovery**: Find related papers automatically

### For Teams
- **Shared Knowledge Base**: Centralized document search
- **Onboarding**: New members can query the research repository
- **Collaboration**: Consistent naming and organization

---

## 🆚 Comparison

| Feature | Gideon | Zotero | Mendeley | Papers |
|---------|--------|--------|----------|--------|
| **Semantic Search** | ✅ | ❌ | ❌ | ❌ |
| **AI Q&A (RAG)** | ✅ | ❌ | ❌ | ❌ |
| **Auto-Rename** | ✅ | ❌ | ⚠️ Limited | ⚠️ Limited |
| **Local LLM** | ✅ | N/A | N/A | N/A |
| **CLI Interface** | ✅ | ❌ | ❌ | ❌ |
| **Free & Open Source** | ✅ | ✅ | ❌ | ❌ |
| **Privacy-First** | ✅ | ✅ | ⚠️ | ⚠️ |

---

## 📚 Documentation

### Commands

#### Search Commands

```bash
# Index documents for semantic search
gideon search index <directory> [--concurrent N] [--clear]

# Semantic search
gideon search search <query> [--top-k N] [--topic TOPIC] [--author AUTHOR]

# Ask questions (RAG)
gideon search ask <question> [--top-k N] [--sources/--no-sources]

# Find similar documents
gideon search similar <document> [--top-k N]

# Show index statistics
gideon search stats

# Clear index
gideon search clear [--yes]
```

#### Document Management

```bash
# Rename files with AI
gideon rename auto <directory> [--llm-type TYPE] [--model MODEL]

# Remove duplicates
gideon deduplicate scan <directory> [--threshold FLOAT]

# Organize files
gideon organize <directory> [--dry-run] [--ignore PATTERNS]
```

#### Summarization

```bash
# Summarize a document
gideon summarize file <document> [--type brief|structured|detailed|cornell|tweet]

# Batch summarization
gideon summarize batch <directory> [--type TYPE] [--output FILE]

# List summary types
gideon summarize types
```

#### References

```bash
# Extract references from document
gideon references extract <document> [--llm/--no-llm] [--output FILE] [--format bibtex|apa|json]
```

#### Literature Reviews

```bash
# Generate literature review
gideon review generate "<topic>" [--max-papers N] [--output FILE]
```

#### Analytics

```bash
# Create analytics dashboard
gideon analytics dashboard [--output dashboard.html]

# Build knowledge graph
gideon analytics knowledge-graph [--output graph.gexf]
```

---

## 🗺️ Roadmap

### ✅ **Phase 1: Foundation** (Completed)
- [x] Multi-LLM support (OpenAI, Anthropic, Ollama)
- [x] Semantic search with ChromaDB
- [x] RAG-based Q&A
- [x] Document renaming and organization
- [x] Topic classification

### ✅ **Phase 2: Enhancement** (Completed)
- [x] Multi-format support (Word, PowerPoint, EPUB, Markdown, Images with OCR)
- [x] Smart duplicate detection (exact, version patterns)
- [x] Document summarization (brief, structured, detailed, Cornell notes)
- [x] Reference extraction (BibTeX, APA, JSON export)

### ✅ **Phase 3: Advanced Features** (Completed)
- [x] Literature review generator
- [x] Knowledge graph builder
- [x] Analytics dashboard
- [x] Citation network analysis
- [ ] Improved metadata extraction
- [ ] Batch processing optimization
- [ ] Web interface

### 🔮 **Phase 3: Advanced Features** (Planned)
- [ ] Research assistant chatbot
- [ ] Literature review generator
- [ ] Citation network analysis
- [ ] Knowledge graph visualization
- [ ] Collaborative features
- [ ] Cloud synchronization
- [ ] Mobile app

---

## 🤝 Contributing

We love contributions! Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

### Development Setup

```bash
# Clone and install dev dependencies
git clone https://github.com/asanchezyali/gideon.git
cd gideon
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/
```

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- ⭐ Star the project

---

## 📊 Stats

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/asanchezyali/gideon?style=social)
![GitHub forks](https://img.shields.io/github/forks/asanchezyali/gideon?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/asanchezyali/gideon?style=social)

</div>

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [ChromaDB](https://github.com/chroma-core/chroma) - Vector database
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Typer](https://github.com/tiangolo/typer) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting

---

## 💬 Community

- **Discussions**: [GitHub Discussions](https://github.com/asanchezyali/gideon/discussions)
- **Issues**: [Bug Reports & Feature Requests](https://github.com/asanchezyali/gideon/issues)
- **Email**: [asanchezyali@gmail.com](mailto:asanchezyali@gmail.com)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=asanchezyali/gideon&type=Date)](https://star-history.com/#asanchezyali/gideon&Date)

---

<div align="center">

**Built with ❤️ by [Alejandro Sánchez Yalí](https://github.com/asanchezyali)**

If you find Gideon useful, please consider giving it a ⭐!

</div>
