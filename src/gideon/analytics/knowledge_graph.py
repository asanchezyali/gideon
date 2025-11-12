"""Knowledge graph builder for document collections."""

from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
from dataclasses import dataclass
import networkx as nx
import json


@dataclass
class DocumentNode:
    """Node representing a document."""
    id: str
    title: str
    authors: List[str]
    year: Optional[str] = None
    topics: List[str] = None

    def __post_init__(self):
        """Validate and set defaults."""
        if self.topics is None:
            self.topics = []
        if not self.id:
            raise ValueError("Document ID cannot be empty")
        if not self.title:
            raise ValueError("Document title cannot be empty")


class KnowledgeGraphBuilder:
    """Build knowledge graphs from document metadata."""

    def __init__(self):
        """Initialize knowledge graph."""
        self.graph = nx.DiGraph()

    def add_document(self, doc: DocumentNode):
        """
        Add document node to graph.

        Args:
            doc: Document node to add

        Raises:
            ValueError: If doc is invalid
        """
        if not isinstance(doc, DocumentNode):
            raise ValueError("doc must be a DocumentNode instance")

        self.graph.add_node(
            doc.id,
            type="document",
            title=doc.title,
            authors=doc.authors,
            year=doc.year,
            topics=doc.topics
        )

        # Add author nodes and edges
        for author in doc.authors:
            if not author:
                continue
            author_id = f"author_{author.replace(' ', '_')}"
            self.graph.add_node(author_id, type="author", name=author)
            self.graph.add_edge(author_id, doc.id, relation="authored")

        # Add topic nodes and edges
        for topic in doc.topics:
            if not topic:
                continue
            topic_id = f"topic_{topic.replace(' ', '_')}"
            self.graph.add_node(topic_id, type="topic", name=topic)
            self.graph.add_edge(doc.id, topic_id, relation="about")

    def add_citation(self, from_doc: str, to_doc: str):
        """
        Add citation relationship.

        Args:
            from_doc: ID of citing document
            to_doc: ID of cited document

        Raises:
            ValueError: If document IDs don't exist in graph
        """
        if from_doc not in self.graph.nodes:
            raise ValueError(f"Document {from_doc} not in graph")
        if to_doc not in self.graph.nodes:
            raise ValueError(f"Document {to_doc} not in graph")

        self.graph.add_edge(from_doc, to_doc, relation="cites")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get graph statistics.

        Returns:
            Dictionary with graph statistics
        """
        if len(self.graph) == 0:
            return {
                "num_documents": 0,
                "num_authors": 0,
                "num_topics": 0,
                "num_citations": 0,
                "density": 0.0,
            }

        return {
            "num_documents": sum(1 for _, d in self.graph.nodes(data=True) if d.get('type') == 'document'),
            "num_authors": sum(1 for _, d in self.graph.nodes(data=True) if d.get('type') == 'author'),
            "num_topics": sum(1 for _, d in self.graph.nodes(data=True) if d.get('type') == 'topic'),
            "num_citations": sum(1 for _, _, d in self.graph.edges(data=True) if d.get('relation') == 'cites'),
            "density": nx.density(self.graph),
        }

    def find_central_documents(self, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find most central documents using PageRank.

        Args:
            top_k: Number of top documents to return

        Returns:
            List of (document_id, score) tuples

        Raises:
            ValueError: If graph is empty
        """
        if len(self.graph) == 0:
            return []

        try:
            pagerank = nx.pagerank(self.graph)
            docs = [(node, score) for node, score in pagerank.items()
                    if self.graph.nodes[node].get('type') == 'document']
            docs.sort(key=lambda x: x[1], reverse=True)
            return docs[:top_k]
        except Exception as e:
            raise ValueError(f"Failed to compute PageRank: {str(e)}")

    def export_graph(self, output_path: Path, format: str = "gexf"):
        """
        Export graph to file.

        Args:
            output_path: Path to output file
            format: Export format ('gexf' or 'json')

        Raises:
            ValueError: If format is unsupported or export fails
        """
        if len(self.graph) == 0:
            raise ValueError("Cannot export empty graph")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format == "gexf":
                # GEXF doesn't handle list attributes well, convert to strings
                graph_copy = self.graph.copy()
                for node, data in graph_copy.nodes(data=True):
                    for key, value in list(data.items()):
                        if isinstance(value, list):
                            data[key] = ", ".join(str(v) for v in value)

                nx.write_gexf(graph_copy, str(output_path))
            elif format == "json":
                data = nx.node_link_data(self.graph)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'gexf' or 'json'")
        except Exception as e:
            raise ValueError(f"Failed to export graph: {str(e)}")

