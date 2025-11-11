"""
Gideon Quick Start - Basic Usage
=================================

This example shows the most common use cases for Gideon.
"""

import asyncio
from pathlib import Path


# Example 1: Using OpenAI for document analysis
async def example_openai():
    """Use OpenAI to analyze and rename documents."""
    print("\n" + "="*60)
    print("Example 1: Using OpenAI for Document Analysis")
    print("="*60)

    from src.gideon.llm.factory import LLMServiceFactory, LLMServiceType

    # Create OpenAI service
    service = LLMServiceFactory.create(
        service_type=LLMServiceType.OPENAI,
        config={
            "model": "gpt-4-turbo-preview",
            "temperature": 0.1
        }
    )

    print("✓ OpenAI service created successfully")
    print(f"  Model: gpt-4-turbo-preview")


# Example 2: Semantic search over documents
async def example_search():
    """Index and search documents semantically."""
    print("\n" + "="*60)
    print("Example 2: Semantic Search")
    print("="*60)

    from src.gideon.search import SemanticSearchEngine

    # Create search engine
    engine = SemanticSearchEngine()

    # Index a sample document
    sample_content = """
    Attention Is All You Need

    Ashish Vaswani et al., 2017

    The dominant sequence transduction models are based on complex recurrent
    or convolutional neural networks that include an encoder and a decoder.
    The best performing models also connect the encoder and decoder through
    an attention mechanism. We propose a new simple network architecture, the
    Transformer, based solely on attention mechanisms, dispensing with
    recurrence and convolutions entirely.
    """

    print("Indexing sample document...")
    chunks = await engine.index_document(
        file_path=Path("attention_is_all_you_need.pdf"),
        content=sample_content,
        metadata={
            "authors": ["Vaswani et al."],
            "year": "2017",
            "topic": "Deep Learning"
        }
    )

    print(f"✓ Indexed document: {chunks} chunks created")

    # Search
    print("\nSearching for: 'transformer architecture'")
    results = await engine.search("transformer architecture", k=1)

    if results:
        print(f"✓ Found {len(results)} results")
        print(f"  Top result similarity: {results[0].similarity_score:.2%}")
        print(f"  Preview: {results[0].chunk_text[:100]}...")


# Example 3: Duplicate detection
async def example_duplicates():
    """Detect duplicate files."""
    print("\n" + "="*60)
    print("Example 3: Duplicate Detection")
    print("="*60)

    from src.gideon.services.duplicate_detector import SmartDuplicateDetector
    import tempfile

    # Create test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create some duplicate files
        (tmppath / "paper.pdf").write_text("content")
        (tmppath / "paper_v1.pdf").write_text("different content")
        (tmppath / "paper_v2.pdf").write_text("more content")

        # Detect duplicates
        detector = SmartDuplicateDetector()
        groups = await detector.detect_duplicates(list(tmppath.glob("*.pdf")))

        print(f"✓ Detected {len(groups)} duplicate groups")
        if groups:
            for i, group in enumerate(groups, 1):
                print(f"\n  Group {i} ({group.duplicate_type.value}):")
                print(f"    Primary: {group.primary_file.name}")
                print(f"    Duplicates: {len(group.files) - 1}")


# Example 4: Multi-LLM comparison
async def example_multi_llm():
    """Compare different LLM providers."""
    print("\n" + "="*60)
    print("Example 4: Multi-LLM Comparison")
    print("="*60)

    from src.gideon.llm.factory import LLMServiceFactory, LLMServiceType

    providers = [
        (LLMServiceType.OPENAI, "gpt-4-turbo-preview"),
        (LLMServiceType.ANTHROPIC, "claude-3-5-sonnet-20241022"),
        (LLMServiceType.OLLAMA, "llama2"),
    ]

    print("Available LLM providers:")
    for provider, model in providers:
        try:
            service = LLMServiceFactory.create(
                service_type=provider,
                config={"model": model}
            )
            print(f"  ✓ {provider.value:12} - {model}")
        except Exception as e:
            print(f"  ✗ {provider.value:12} - {model} ({str(e)[:30]}...)")


# Main runner
async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("GIDEON - Quick Start Examples")
    print("="*60)

    try:
        await example_openai()
    except Exception as e:
        print(f"  ✗ Error: {e}")

    try:
        await example_search()
    except Exception as e:
        print(f"  ✗ Error: {e}")

    try:
        await example_duplicates()
    except Exception as e:
        print(f"  ✗ Error: {e}")

    try:
        await example_multi_llm()
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
