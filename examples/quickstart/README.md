# Gideon Quick Start Examples

This directory contains practical examples to get you started with Gideon.

## Files

- **01_basic_usage.py** - Python examples showing programmatic usage
- **02_cli_examples.sh** - Shell script with CLI command examples

## Running the Examples

### Python Examples

```bash
cd examples/quickstart
python 01_basic_usage.py
```

This will demonstrate:
- Creating LLM services
- Semantic search
- Duplicate detection
- Multi-LLM comparison

### CLI Examples

```bash
# View all CLI examples
bash 02_cli_examples.sh

# Or try commands directly:
gideon search index ./documents/
gideon search search "machine learning"
gideon search ask "What are transformers?"
```

## Prerequisites

1. **Install Gideon**:
   ```bash
   pip install -e .
   ```

2. **Configure API keys** (if using cloud providers):
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **For Ollama** (local LLM):
   ```bash
   # Install Ollama
   curl https://ollama.ai/install.sh | sh

   # Pull a model
   ollama pull llama2
   ```

## Common Workflows

### Workflow 1: Organize New Research Papers

```bash
# 1. Rename files with AI-extracted metadata
gideon rename auto ./new_papers/

# 2. Remove duplicates
gideon deduplicate scan ./new_papers/ --remove

# 3. Organize into topic folders
gideon organize ./new_papers/

# 4. Index for semantic search
gideon search index ./new_papers/
```

### Workflow 2: Literature Review

```bash
# 1. Index your paper collection
gideon search index ./research_library/

# 2. Search for papers on a topic
gideon search search "few-shot learning" --top-k 20

# 3. Ask specific questions
gideon search ask "What are the main challenges in few-shot learning?"

# 4. Find papers similar to a key paper
gideon search similar important_paper.pdf --top-k 10
```

### Workflow 3: Clean Up Messy Downloads

```bash
# 1. Scan for duplicates
gideon deduplicate scan ~/Downloads/ --mode all

# 2. Remove duplicates (interactive)
gideon deduplicate clean ~/Downloads/

# 3. Rename with AI
gideon rename auto ~/Downloads/ --llm-type openai

# 4. Move to organized library
gideon organize ~/Downloads/ --dry-run  # Preview first
gideon organize ~/Downloads/  # Actually move files
```

## Tips

- **Start small**: Test on a small directory first
- **Dry run**: Use `--dry-run` flags to preview changes
- **Check help**: `gideon <command> --help` for more options
- **Multiple LLMs**: Try different providers for best results

## Troubleshooting

### "No documents indexed" error
```bash
# Solution: Index first
gideon search index ./documents/
```

### "API key not found" error
```bash
# Solution: Set API key in .env
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### "Ollama connection refused" error
```bash
# Solution: Start Ollama
ollama serve
```

## Next Steps

- Read the [full documentation](../../README.md)
- Check [AI_ENHANCEMENT_ANALYSIS.md](../../AI_ENHANCEMENT_ANALYSIS.md) for advanced features
- Explore [examples/ai_enhancements/](../ai_enhancements/) for implementation details

## Support

- **Issues**: https://github.com/asanchezyali/gideon/issues
- **Discussions**: https://github.com/asanchezyali/gideon/discussions
- **Email**: asanchezyali@gmail.com
