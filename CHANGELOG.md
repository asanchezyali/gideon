# Changelog

All notable changes to Gideon will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-LLM provider support (OpenAI, Anthropic, Ollama)
- Semantic search engine with ChromaDB
- RAG-based Q&A system
- Search commands: index, search, ask, similar, stats, clear
- Comprehensive documentation and examples
- Professional README for community building

### Changed
- Updated CLI to "AI-powered Research Assistant"
- Enhanced configuration system with API key support
- Improved pyproject.toml with better dependency organization

### Fixed
- None

## [0.1.0] - 2025-01-11

### Added
- Initial release
- AI-powered PDF renaming using LLMs
- Topic classification (30+ categories)
- Duplicate file detection and removal
- File organization by topics
- Support for Ollama and Docker AI Model LLM providers
- Rich CLI interface with progress bars
- Async processing with configurable concurrency
- Comprehensive test suite

### Features
- Extract metadata (authors, year, title, topic) from PDFs
- Generate clean, consistent filenames
- Organize files into topic-based folders
- Remove duplicate files
- Modular architecture for easy extension

---

## Release Notes

### Version 0.1.0 (Initial Release)

First public release of Gideon - AI-powered document organization tool.

**Highlights:**
- Intelligent file renaming using LLMs
- Automated topic classification
- Duplicate detection
- Clean, modular architecture
- Easy to extend with new LLM providers

**Known Limitations:**
- Only supports PDF files
- Limited to 30 predefined topics
- Basic duplicate detection (hash-based only)
- No semantic search yet

---

## Upgrade Guide

### From 0.1.0 to Unreleased

**Breaking Changes:**
- None

**New Dependencies:**
```bash
pip install langchain-anthropic chromadb sentence-transformers
```

**Configuration Updates:**
```bash
# Add to .env
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
DEFAULT_LLM_SERVICE_TYPE=openai  # or anthropic
```

**New Features to Try:**
```bash
# Index your documents
gideon search index ./documents/

# Semantic search
gideon search search "machine learning papers"

# Ask questions
gideon search ask "What are transformers?"
```

---

## Future Plans

See [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) for detailed roadmap.

**Coming Soon:**
- Multi-format support (Word, PowerPoint, EPUB)
- Smart duplicate detection (semantic similarity)
- Research assistant chatbot
- Literature review generator
- Web interface

**Long Term:**
- Citation network analysis
- Knowledge graph visualization
- Collaborative features
- Cloud synchronization
- Mobile app

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to Gideon.

---

[Unreleased]: https://github.com/asanchezyali/gideon/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/asanchezyali/gideon/releases/tag/v0.1.0
