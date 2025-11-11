"""Knowledge graph builder for document collections."""

from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import networkx as nx


@dataclass
class DocumentNode:
    """Node representing a document."""
    id: str
    title: str
    authors: List[str]
    year: Optional[str]
    topics: List[str]


class KnowledgeGraphBuilder:
    """Build knowledge graphs from document metadata."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_document(self, doc: DocumentNode):
        """Add document node to graph."""
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
            author_id = f"author_{author}"
            self.graph.add_node(author_id, type="author", name=author)
            self.graph.add_edge(author_id, doc.id, relation="authored")

        # Add topic nodes and edges
        for topic in doc.topics:
            topic_id = f"topic_{topic}"
            self.graph.add_node(topic_id, type="topic", name=topic)
            self.graph.add_edge(doc.id, topic_id, relation="about")

    def add_citation(self, from_doc: str, to_doc: str):
        """Add citation relationship."""
        self.graph.add_edge(from_doc, to_doc, relation="cites")

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "num_documents": sum(1 for _, d in self.graph.nodes(data=True) if d.get('type') == 'document'),
            "num_authors": sum(1 for _, d in self.graph.nodes(data=True) if d.get('type') == 'author'),
            "num_topics": sum(1 for _, d in self.graph.nodes(data=True) if d.get('type') == 'topic'),
            "num_citations": sum(1 for _, _, d in self.graph.edges(data=True) if d.get('relation') == 'cites'),
            "density": nx.density(self.graph),
        }

    def find_central_documents(self, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find most central documents using PageRank."""
        pagerank = nx.pagerank(self.graph)
        docs = [(node, score) for node, score in pagerank.items()
                if self.graph.nodes[node].get('type') == 'document']
        docs.sort(key=lambda x: x[1], reverse=True)
        return docs[:top_k]

    def export_graph(self, output_path: Path, format: str = "gexf"):
        """Export graph to file."""
        if format == "gexf":
            nx.write_gexf(self.graph, output_path)
        elif format == "json":
            import json
            data = nx.node_link_data(self.graph)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
