"""
Semantic Search Engine with RAG capabilities.

This module provides semantic search over document collections using
embeddings and vector similarity. It also includes RAG (Retrieval-Augmented
Generation) for answering questions based on document content.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
import asyncio

try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..core.config import settings
from ..utils.logging import log_info, log_error, log_success


@dataclass
class SearchResult:
    """Result from semantic search."""
    document_path: Path
    chunk_text: str
    similarity_score: float
    metadata: Dict[str, Any]
    chunk_id: int = 0
    total_chunks: int = 0


class SemanticSearchEngine:
    """
    Semantic search engine for document collections.

    Features:
    - Index documents with embeddings
    - Semantic similarity search
    - RAG-based Q&A
    - Filter by metadata (topic, author, year, etc.)
    - Batch indexing with progress tracking

    Example:
        engine = SemanticSearchEngine()
        await engine.index_document(path, content, metadata)
        results = await engine.search("neural networks", k=5)
        answer = await engine.ask("What are transformers?")
    """

    def __init__(
        self,
        persist_directory: Optional[Path] = None,
        embedding_model: str = "nomic-embed-text",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        llm_service_type: LLMServiceType = None,
    ):
        """
        Initialize semantic search engine.

        Args:
            persist_directory: Directory to persist vector store
            embedding_model: Embedding model to use (Ollama)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            llm_service_type: LLM service for RAG (defaults to settings)
        """
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "ChromaDB not installed. Install with: pip install chromadb sentence-transformers"
            )

        if persist_directory is None:
            persist_directory = settings.BASE_DIR / ".gideon" / "vectorstore"

        self.persist_directory = persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize embeddings
        try:
            self.embeddings = OllamaEmbeddings(model=embedding_model)
        except Exception as e:
            log_error(f"Failed to initialize embeddings: {e}")
            log_error("Make sure Ollama is running: ollama serve")
            raise

        # Initialize vector store
        self.vectorstore = Chroma(
            persist_directory=str(persist_directory),
            embedding_function=self.embeddings,
            collection_name="gideon_documents"
        )

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # LLM for Q&A
        self.llm_service_type = llm_service_type or LLMServiceType(settings.DEFAULT_LLM_SERVICE_TYPE)
        self.llm = None  # Lazy initialization

    def _get_llm(self):
        """Lazy load LLM service."""
        if self.llm is None:
            self.llm = LLMServiceFactory.create(
                service_type=self.llm_service_type,
                config=settings.DEFAULT_LLM_CONFIG
            )
        return self.llm

    async def index_document(
        self,
        file_path: Path,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Index a document for semantic search.

        Args:
            file_path: Path to document
            content: Document content text
            metadata: Optional metadata (authors, year, topic, etc.)

        Returns:
            Number of chunks created
        """
        if not content or not content.strip():
            log_error(f"Empty content for {file_path}")
            return 0

        try:
            # Create chunks
            chunks = self.text_splitter.split_text(content)

            if not chunks:
                log_error(f"No chunks created for {file_path}")
                return 0

            # Prepare metadata
            doc_metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "num_chunks": len(chunks),
                **(metadata or {})
            }

            # Create metadata for each chunk
            chunk_metadatas = []
            for i, chunk in enumerate(chunks):
                chunk_meta = doc_metadata.copy()
                chunk_meta["chunk_id"] = i
                chunk_meta["chunk_total"] = len(chunks)
                chunk_metadatas.append(chunk_meta)

            # Add to vector store
            self.vectorstore.add_texts(
                texts=chunks,
                metadatas=chunk_metadatas
            )

            # Persist
            self.vectorstore.persist()

            log_info(f"Indexed {file_path.name} ({len(chunks)} chunks)")
            return len(chunks)

        except Exception as e:
            log_error(f"Error indexing {file_path}: {e}")
            return 0

    async def index_directory(
        self,
        directory: Path,
        file_service: Any,
        progress_callback: Optional[Callable[[Path, float], None]] = None,
        max_concurrent: int = 3
    ) -> Dict[str, int]:
        """
        Index all documents in a directory.

        Args:
            directory: Directory containing documents
            file_service: FileService instance for content extraction
            progress_callback: Optional callback(file_path, progress_ratio)
            max_concurrent: Maximum concurrent indexing operations

        Returns:
            Statistics: {indexed: int, failed: int, total_chunks: int}
        """
        stats = {"indexed": 0, "failed": 0, "total_chunks": 0}

        files = file_service.get_files_by_extension(directory, ".pdf")

        if not files:
            log_error(f"No PDF files found in {directory}")
            return stats

        log_info(f"Indexing {len(files)} documents...")

        # Semaphore for concurrent control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def index_one(i: int, file_path: Path):
            async with semaphore:
                try:
                    # Extract content
                    content = await file_service.extract_pdf_content(file_path)

                    if not content:
                        stats["failed"] += 1
                        return

                    # Index document
                    num_chunks = await self.index_document(file_path, content)

                    if num_chunks > 0:
                        stats["indexed"] += 1
                        stats["total_chunks"] += num_chunks
                    else:
                        stats["failed"] += 1

                    if progress_callback:
                        progress_callback(file_path, (i + 1) / len(files))

                except Exception as e:
                    log_error(f"Error indexing {file_path}: {e}")
                    stats["failed"] += 1

        # Index all files concurrently
        tasks = [index_one(i, file_path) for i, file_path in enumerate(files)]
        await asyncio.gather(*tasks)

        log_success(
            f"Indexing complete: {stats['indexed']} indexed, "
            f"{stats['failed']} failed, {stats['total_chunks']} total chunks"
        )

        return stats

    async def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Semantic search for relevant documents.

        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional filters (e.g., {"topic": "AI"})

        Returns:
            List of search results sorted by relevance
        """
        try:
            # Perform similarity search
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k,
                filter=filter_metadata
            )

            # Convert to SearchResult objects
            search_results = []
            for doc, score in results:
                result = SearchResult(
                    document_path=Path(doc.metadata["source"]),
                    chunk_text=doc.page_content,
                    similarity_score=1 - score,  # Convert distance to similarity
                    metadata=doc.metadata,
                    chunk_id=doc.metadata.get("chunk_id", 0),
                    total_chunks=doc.metadata.get("chunk_total", 1)
                )
                search_results.append(result)

            return search_results

        except Exception as e:
            log_error(f"Search error: {e}")
            return []

    async def ask(
        self,
        question: str,
        k: int = 3,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        RAG: Answer questions about document collection.

        Args:
            question: Question to answer
            k: Number of relevant chunks to retrieve
            return_sources: Include source documents in response

        Returns:
            {
                "answer": str,
                "sources": List[SearchResult],  # if return_sources=True
                "confidence": float
            }
        """
        try:
            # Retrieve relevant chunks
            results = await self.search(question, k=k)

            if not results:
                return {
                    "answer": "I couldn't find relevant information in your documents.",
                    "sources": [],
                    "confidence": 0.0
                }

            # Build context from retrieved chunks
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(
                    f"[Document {i}: {result.metadata['filename']}]\n{result.chunk_text}"
                )

            context = "\n\n".join(context_parts)

            # Create prompt
            prompt_text = f"""You are a helpful research assistant. Answer the question based ONLY on the provided context from the user's document collection.

Context from documents:
{context}

Question: {question}

Instructions:
1. Provide a clear, concise answer based on the context
2. If the context doesn't contain enough information, say so
3. Cite which documents you're referencing
4. Be specific and factual

Answer:"""

            # Get LLM service
            llm = self._get_llm()
            from langchain_core.prompts import PromptTemplate
            prompt = PromptTemplate.from_template(prompt_text)
            chain = await llm.create_chain(prompt)

            # Generate answer
            response = await chain.ainvoke({"text": ""})  # Context already in prompt
            answer = response.content if hasattr(response, 'content') else str(response)

            # Calculate confidence based on similarity scores
            avg_similarity = sum(r.similarity_score for r in results) / len(results)

            result_dict = {
                "answer": answer,
                "confidence": avg_similarity
            }

            if return_sources:
                result_dict["sources"] = results

            return result_dict

        except Exception as e:
            log_error(f"Q&A error: {e}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }

    async def find_similar_documents(
        self,
        document_path: Path,
        k: int = 5
    ) -> List[SearchResult]:
        """
        Find documents similar to a given document.

        Args:
            document_path: Path to reference document
            k: Number of similar documents to return

        Returns:
            List of similar documents
        """
        try:
            # Get chunks from the document
            collection = self.vectorstore._collection
            results = collection.get(
                where={"source": str(document_path)}
            )

            if not results or not results.get("documents"):
                raise ValueError(f"Document {document_path} not found in index")

            # Use first chunk as query
            query_text = results["documents"][0]

            # Search for similar documents (excluding the source document)
            all_results = await self.search(query_text, k=k + 10)

            # Filter out the source document
            similar_docs = [
                r for r in all_results
                if r.document_path != document_path
            ][:k]

            return similar_docs

        except Exception as e:
            log_error(f"Error finding similar documents: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            collection = self.vectorstore._collection
            count = collection.count()

            return {
                "total_chunks": count,
                "persist_directory": str(self.persist_directory),
                "embedding_model": "nomic-embed-text",
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            log_error(f"Error getting statistics: {e}")
            return {"total_chunks": 0, "status": "error"}

    def clear_index(self):
        """Clear all indexed documents."""
        try:
            self.vectorstore._client.delete_collection("gideon_documents")
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
                collection_name="gideon_documents"
            )
            log_success("Index cleared")
        except Exception as e:
            log_error(f"Error clearing index: {e}")
