"""Tests for knowledge graph builder."""

import pytest
from pathlib import Path

from src.gideon.analytics.knowledge_graph import KnowledgeGraphBuilder, DocumentNode


class TestDocumentNode:
    """Test DocumentNode dataclass."""

    def test_create_valid_node(self):
        """Test creating a valid document node."""
        node = DocumentNode(
            id="doc1",
            title="Test Document",
            authors=["Author A", "Author B"],
            year="2024",
            topics=["AI", "ML"]
        )
        assert node.id == "doc1"
        assert len(node.authors) == 2
        assert len(node.topics) == 2

    def test_create_node_with_defaults(self):
        """Test creating node with default values."""
        node = DocumentNode(
            id="doc1",
            title="Test Document",
            authors=[]
        )
        assert node.year is None
        assert node.topics == []

    def test_create_node_empty_id(self):
        """Test that empty ID raises error."""
        with pytest.raises(ValueError, match="Document ID cannot be empty"):
            DocumentNode(id="", title="Test", authors=[])

    def test_create_node_empty_title(self):
        """Test that empty title raises error."""
        with pytest.raises(ValueError, match="Document title cannot be empty"):
            DocumentNode(id="doc1", title="", authors=[])


class TestKnowledgeGraphBuilder:
    """Test knowledge graph builder functionality."""

    @pytest.fixture
    def builder(self):
        """Create a knowledge graph builder instance."""
        return KnowledgeGraphBuilder()

    @pytest.fixture
    def sample_doc(self):
        """Create a sample document node."""
        return DocumentNode(
            id="doc1",
            title="Sample Document",
            authors=["John Doe", "Jane Smith"],
            year="2024",
            topics=["AI", "ML"]
        )

    def test_add_document(self, builder, sample_doc):
        """Test adding a document to the graph."""
        builder.add_document(sample_doc)
        assert len(builder.graph) > 0
        assert "doc1" in builder.graph.nodes

    def test_add_invalid_document(self, builder):
        """Test that adding invalid document raises error."""
        with pytest.raises(ValueError, match="doc must be a DocumentNode instance"):
            builder.add_document("not a document node")

    def test_add_citation(self, builder):
        """Test adding citation relationship."""
        doc1 = DocumentNode(id="doc1", title="Doc 1", authors=[])
        doc2 = DocumentNode(id="doc2", title="Doc 2", authors=[])

        builder.add_document(doc1)
        builder.add_document(doc2)
        builder.add_citation("doc1", "doc2")

        assert builder.graph.has_edge("doc1", "doc2")

    def test_add_citation_nonexistent_document(self, builder, sample_doc):
        """Test that citing non-existent document raises error."""
        builder.add_document(sample_doc)
        with pytest.raises(ValueError, match="not in graph"):
            builder.add_citation("doc1", "nonexistent")

    def test_get_statistics_empty_graph(self, builder):
        """Test getting statistics from empty graph."""
        stats = builder.get_statistics()
        assert stats['num_documents'] == 0
        assert stats['num_authors'] == 0
        assert stats['density'] == 0.0

    def test_get_statistics_with_documents(self, builder, sample_doc):
        """Test getting statistics with documents."""
        builder.add_document(sample_doc)
        stats = builder.get_statistics()
        assert stats['num_documents'] == 1
        assert stats['num_authors'] == 2
        assert stats['num_topics'] == 2

    def test_find_central_documents_empty_graph(self, builder):
        """Test finding central documents in empty graph."""
        result = builder.find_central_documents()
        assert result == []

    def test_export_empty_graph(self, builder, tmp_path):
        """Test that exporting empty graph raises error."""
        output_path = tmp_path / "graph.gexf"
        with pytest.raises(ValueError, match="Cannot export empty graph"):
            builder.export_graph(output_path)

    def test_export_graph_gexf(self, builder, sample_doc, tmp_path):
        """Test exporting graph to GEXF format."""
        builder.add_document(sample_doc)
        output_path = tmp_path / "graph.gexf"
        builder.export_graph(output_path, format="gexf")
        assert output_path.exists()

    def test_export_graph_json(self, builder, sample_doc, tmp_path):
        """Test exporting graph to JSON format."""
        builder.add_document(sample_doc)
        output_path = tmp_path / "graph.json"
        builder.export_graph(output_path, format="json")
        assert output_path.exists()

    def test_export_graph_invalid_format(self, builder, sample_doc, tmp_path):
        """Test that invalid format raises error."""
        builder.add_document(sample_doc)
        output_path = tmp_path / "graph.txt"
        with pytest.raises(ValueError, match="Unsupported format"):
            builder.export_graph(output_path, format="invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
