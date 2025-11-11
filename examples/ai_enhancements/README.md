# AI Enhancements - Code Examples

Este directorio contiene ejemplos de implementación concretos para las mejoras de AI propuestas en el análisis principal.

## 📁 Archivos

### 1. `semantic_search_example.py`
**Búsqueda Semántica y RAG**

Implementa un sistema completo de búsqueda semántica usando embeddings y RAG.

**Características:**
- Indexación de documentos con ChromaDB
- Búsqueda por similitud semántica
- Sistema Q&A sobre colección de documentos
- Búsqueda de documentos similares
- Estadísticas de índice

**Clases principales:**
- `SemanticSearchEngine`: Motor de búsqueda principal
- `SearchResult`: Resultado de búsqueda

**Comandos propuestos:**
```bash
gideon index ./documents/
gideon search "neural networks optimization" --top-k 5
gideon ask "What papers discuss transformers?"
gideon find-similar document.pdf
```

**Dependencias:**
```bash
pip install chromadb sentence-transformers langchain-community
```

---

### 2. `smart_duplicate_detector.py`
**Detección Inteligente de Duplicados**

Sistema multi-nivel para detectar duplicados exactos, fuzzy, semánticos y versiones.

**Características:**
- 4 niveles de detección:
  - **Exacto**: Hash SHA-256
  - **Fuzzy**: ssdeep fuzzy hashing
  - **Semántico**: Embeddings + cosine similarity
  - **Versiones**: Detección de draft, v1, v2, final
- Selección automática del mejor archivo a mantener
- Cálculo de espacio ahorrado

**Clases principales:**
- `SmartDuplicateDetector`: Detector principal
- `DuplicateGroup`: Grupo de duplicados
- `DuplicateType`: Tipos de duplicación

**Comandos propuestos:**
```bash
gideon deduplicate ./documents/ --mode all --threshold 0.95
gideon deduplicate ./documents/ --mode semantic --auto-remove
```

**Dependencias:**
```bash
pip install ssdeep scikit-learn numpy
```

---

### 3. `research_assistant.py`
**Asistente de Investigación Interactivo**

Asistente conversacional AI con memoria y herramientas.

**Características:**
- Chat interactivo con contexto
- Uso de herramientas (search, summarize, etc.)
- Memoria de conversación
- Generación de literatura reviews
- Análisis de colección

**Clases principales:**
- `ResearchAssistant`: Asistente principal
- `AgentTool`: Herramientas disponibles
- `ToolResult`: Resultado de herramienta

**Comandos propuestos:**
```bash
gideon chat
gideon research "transformers in NLP" --generate-report
gideon literature-review "meta-learning" --output review.md
```

**Ejemplo de conversación:**
```
You: What papers do I have on transformers?
Gideon: [Searches collection] I found 15 papers on transformers...

You: Summarize the most relevant one
Gideon: [Executes summarize tool] Here's a summary of...

You: Find related papers
Gideon: [Executes find_related] Based on that paper, here are 5 related...
```

---

### 4. `multi_format_extractor.py`
**Soporte Multi-Formato**

Sistema extensible para extraer contenido de múltiples formatos de documentos.

**Formatos soportados:**
- ✅ PDF (PyPDF2)
- ✅ Word (.docx) - python-docx
- ✅ PowerPoint (.pptx) - python-pptx
- ✅ EPUB - ebooklib
- ✅ Text/Markdown (.txt, .md)
- ✅ HTML - BeautifulSoup
- ✅ Images (.jpg, .png) - OCR con Tesseract

**Clases principales:**
- `BaseExtractor`: Clase base abstracta
- `ExtractorFactory`: Factory pattern para crear extractores
- `EnhancedFileService`: Servicio mejorado de archivos
- Extractors específicos: `PDFExtractor`, `WordExtractor`, etc.

**Arquitectura:**
```python
BaseExtractor (abstract)
├── PDFExtractor
├── WordExtractor
├── PowerPointExtractor
├── EPUBExtractor
├── TextExtractor
├── HTMLExtractor
└── ImageOCRExtractor

ExtractorFactory.get_extractor(file_path) -> BaseExtractor
```

**Uso:**
```python
# Detectar formato automáticamente
extractor = ExtractorFactory.get_extractor(Path("document.docx"))
doc = await extractor.extract(Path("document.docx"))

print(doc.content)         # Texto extraído
print(doc.metadata)        # Metadatos
print(doc.format)          # .docx
print(doc.extraction_quality)  # 0.0-1.0
```

**Dependencias:**
```bash
pip install python-docx python-pptx ebooklib beautifulsoup4 pytesseract pillow
```

---

## 🚀 Integración con Gideon

### Paso 1: Instalar dependencias

Agregar a `pyproject.toml`:
```toml
dependencies = [
    # ... existing ...

    # Search & embeddings
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",

    # Multi-format
    "python-docx>=1.1.0",
    "python-pptx>=0.6.23",
    "ebooklib>=0.18",
    "beautifulsoup4>=4.12.0",
    "pytesseract>=0.3.10",
    "Pillow>=10.0.0",

    # Fuzzy matching
    "ssdeep>=3.4",

    # ML utilities
    "scikit-learn>=1.3.0",
    "numpy>=1.24.0",
]
```

### Paso 2: Mover código a src/

```bash
# Crear nuevos módulos
mkdir -p src/gideon/search
mkdir -p src/gideon/extractors
mkdir -p src/gideon/assistants

# Mover código
cp semantic_search_example.py src/gideon/search/semantic_search.py
cp smart_duplicate_detector.py src/gideon/agents/duplicate_detector.py
cp research_assistant.py src/gideon/assistants/research_assistant.py
cp multi_format_extractor.py src/gideon/extractors/multi_format.py
```

### Paso 3: Crear comandos CLI

Agregar a `src/gideon/cli/commands/`:

```python
# search.py
from ...search.semantic_search import SemanticSearchEngine

@search_app.command("index")
def index_documents(directory: Path):
    """Index documents for semantic search."""
    # Implementation

@search_app.command("search")
def search_documents(query: str, k: int = 5):
    """Search documents semantically."""
    # Implementation

@search_app.command("ask")
def ask_question(question: str):
    """Ask questions about your documents."""
    # Implementation
```

### Paso 4: Registrar comandos

En `src/gideon/cli/main.py`:
```python
from .commands.search import search_app
from .commands.chat import chat_app

app.add_typer(search_app, name="search", help="Semantic search commands")
app.add_typer(chat_app, name="chat", help="Research assistant")
```

---

## 🧪 Testing

### Unit Tests

```python
# tests/test_semantic_search.py
import pytest
from gideon.search.semantic_search import SemanticSearchEngine

@pytest.mark.asyncio
async def test_index_document():
    engine = SemanticSearchEngine(persist_directory=Path("/tmp/test_db"))
    num_chunks = await engine.index_document(
        Path("test.pdf"),
        "Test content here"
    )
    assert num_chunks > 0

@pytest.mark.asyncio
async def test_search():
    engine = SemanticSearchEngine()
    results = await engine.search("neural networks", k=5)
    assert len(results) <= 5
```

### Integration Tests

```bash
# Test full workflow
pytest tests/integration/test_search_workflow.py -v

# Test with mock LLM
pytest tests/integration/ --mock-llm
```

---

## 📊 Performance Considerations

### Indexing
- **Small collections (< 100 docs)**: ~2-5 minutes
- **Medium collections (100-1000 docs)**: ~10-30 minutes
- **Large collections (> 1000 docs)**: Consider batch processing

### Search
- **Query latency**: < 1 second for most queries
- **Memory usage**: ~500MB for 1000 documents
- **Disk usage**: ~100-200MB for vector store

### Optimization tips:
1. Use `max_concurrent` parameter for parallel processing
2. Cache embeddings to avoid recomputation
3. Use smaller embedding models for faster indexing
4. Consider GPU acceleration for large batches

---

## 🎯 Next Steps

### High Priority
1. [ ] Implement semantic search in production
2. [ ] Add multi-format support for docx and pptx
3. [ ] Create smart duplicate detection command
4. [ ] Build interactive chat interface

### Medium Priority
1. [ ] Literature review generator
2. [ ] Citation extraction
3. [ ] Knowledge graph builder
4. [ ] Analytics dashboard

### Future Enhancements
1. [ ] Web interface
2. [ ] Collaborative features
3. [ ] Cloud sync
4. [ ] Mobile app

---

## 📚 Resources

### Documentation
- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)

### Related Projects
- [Zotero](https://www.zotero.org/) - Reference management
- [Semantic Scholar](https://www.semanticscholar.org/) - Research corpus
- [Connected Papers](https://www.connectedpapers.com/) - Citation graphs

---

## 🤝 Contributing

To contribute to these enhancements:

1. Pick a feature from the roadmap
2. Create a branch: `git checkout -b feature/semantic-search`
3. Implement with tests
4. Submit PR with clear description

---

## 📝 License

MIT License - Same as parent project

---

## ✨ Credits

AI Enhancement Analysis and Examples
Generated: 2025-01-11
For: Gideon CLI Project
