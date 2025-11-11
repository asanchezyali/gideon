"""
Ejemplo: Sistema de Búsqueda Semántica con RAG
================================================

Este ejemplo muestra cómo implementar búsqueda semántica y Q&A
sobre la colección de documentos usando embeddings y RAG.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_ollama import ChatOllama


@dataclass
class SearchResult:
    """Result from semantic search."""
    document_path: Path
    chunk_text: str
    similarity_score: float
    metadata: Dict[str, Any]


class SemanticSearchEngine:
    """
    Semantic search engine for document collections.

    Features:
    - Index documents with embeddings
    - Semantic similarity search
    - RAG-based Q&A
    - Hybrid search (keyword + semantic)
    """

    def __init__(
        self,
        persist_directory: Path = Path(".gideon/vectorstore"),
        embedding_model: str = "nomic-embed-text",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.persist_directory = persist_directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(model=embedding_model)

        # Initialize vector store
        self.vectorstore = Chroma(
            persist_directory=str(persist_directory),
            embedding_function=self.embeddings,
            collection_name="documents"
        )

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # LLM for Q&A
        self.llm = ChatOllama(model="deepseek-r1:latest", temperature=0.1)

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
        # Create chunks
        chunks = self.text_splitter.split_text(content)

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

        return len(chunks)

    async def index_directory(
        self,
        directory: Path,
        file_service: Any,  # FileService instance
        progress_callback: Optional[callable] = None
    ) -> Dict[str, int]:
        """
        Index all documents in a directory.

        Args:
            directory: Directory containing documents
            file_service: FileService for content extraction
            progress_callback: Optional callback(file_path, progress)

        Returns:
            Statistics: {indexed: int, failed: int, total_chunks: int}
        """
        stats = {"indexed": 0, "failed": 0, "total_chunks": 0}

        files = file_service.get_files_by_extension(directory, ".pdf")

        for i, file_path in enumerate(files):
            try:
                # Extract content
                content = await file_service.extract_pdf_content(file_path)

                if not content:
                    stats["failed"] += 1
                    continue

                # Index document
                num_chunks = await self.index_document(file_path, content)

                stats["indexed"] += 1
                stats["total_chunks"] += num_chunks

                if progress_callback:
                    progress_callback(file_path, (i + 1) / len(files))

            except Exception as e:
                print(f"Error indexing {file_path}: {e}")
                stats["failed"] += 1

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
            filter_metadata: Optional metadata filters (e.g., {"topic": "AI"})

        Returns:
            List of search results sorted by relevance
        """
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
                metadata=doc.metadata
            )
            search_results.append(result)

        return search_results

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
        prompt = f"""You are a helpful research assistant. Answer the question based ONLY on the provided context from the user's document collection.

Context from documents:
{context}

Question: {question}

Instructions:
1. Provide a clear, concise answer based on the context
2. If the context doesn't contain enough information, say so
3. Cite which documents you're referencing
4. Be specific and factual

Answer:"""

        # Generate answer
        response = await self.llm.ainvoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)

        # Calculate confidence based on similarity scores
        avg_similarity = sum(r.similarity_score for r in results) / len(results)

        result = {
            "answer": answer,
            "confidence": avg_similarity
        }

        if return_sources:
            result["sources"] = results

        return result

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
        # Get chunks from the document
        docs = self.vectorstore.get(
            where={"source": str(document_path)}
        )

        if not docs or not docs["documents"]:
            raise ValueError(f"Document {document_path} not found in index")

        # Use first chunk as query
        query_text = docs["documents"][0]

        # Search for similar documents (excluding the source document)
        results = await self.search(query_text, k=k + 1)

        # Filter out the source document
        similar_docs = [
            r for r in results
            if r.document_path != document_path
        ][:k]

        return similar_docs

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        collection = self.vectorstore._collection
        count = collection.count()

        return {
            "total_chunks": count,
            "persist_directory": str(self.persist_directory),
            "embedding_model": "nomic-embed-text"
        }


# ============================================================================
# CLI Command Examples
# ============================================================================

async def index_command(directory: Path):
    """Example: Index command."""
    from gideon.services.file_service import FileService

    print(f"Indexing documents in {directory}...")

    search_engine = SemanticSearchEngine()
    file_service = FileService()

    def progress_callback(file_path, progress):
        print(f"[{progress*100:.1f}%] Indexed: {file_path.name}")

    stats = await search_engine.index_directory(
        directory,
        file_service,
        progress_callback
    )

    print(f"\n✅ Indexing complete!")
    print(f"   Indexed: {stats['indexed']} documents")
    print(f"   Failed: {stats['failed']} documents")
    print(f"   Total chunks: {stats['total_chunks']}")


async def search_command(query: str, top_k: int = 5):
    """Example: Search command."""
    search_engine = SemanticSearchEngine()

    print(f"Searching for: '{query}'\n")

    results = await search_engine.search(query, k=top_k)

    if not results:
        print("No results found.")
        return

    for i, result in enumerate(results, 1):
        print(f"{i}. {result.document_path.name}")
        print(f"   Similarity: {result.similarity_score:.2%}")
        print(f"   Preview: {result.chunk_text[:200]}...")
        print()


async def ask_command(question: str):
    """Example: Ask command."""
    search_engine = SemanticSearchEngine()

    print(f"Question: {question}\n")

    result = await search_engine.ask(question)

    print(f"Answer (confidence: {result['confidence']:.2%}):")
    print(result['answer'])
    print("\nSources:")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source.metadata['filename']}")


# Example usage
if __name__ == "__main__":
    import asyncio

    # Example 1: Index documents
    # asyncio.run(index_command(Path("./documents")))

    # Example 2: Semantic search
    # asyncio.run(search_command("neural networks optimization"))

    # Example 3: Q&A
    # asyncio.run(ask_command("What papers discuss transformer architectures?"))

    pass
