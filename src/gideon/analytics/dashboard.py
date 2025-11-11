"""Analytics dashboard for document collections."""

from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class AnalyticsDashboard:
    """Generate analytics and visualizations for document collections."""

    def __init__(self):
        self.stats = {}

    def analyze_collection(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze document collection."""
        # Topic distribution
        all_topics = [topic for doc in documents for topic in doc.get('topics', [])]
        topic_counts = Counter(all_topics)

        # Year distribution
        years = [doc.get('year') for doc in documents if doc.get('year')]
        year_counts = Counter(years)

        # Author analysis
        all_authors = [author for doc in documents for author in doc.get('authors', [])]
        author_counts = Counter(all_authors)

        self.stats = {
            "total_documents": len(documents),
            "topic_distribution": dict(topic_counts.most_common(10)),
            "year_distribution": dict(sorted(year_counts.items())),
            "top_authors": dict(author_counts.most_common(10)),
        }

        return self.stats

    def create_visualizations(self) -> go.Figure:
        """Create visualization dashboard."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Topic Distribution', 'Publications Over Time',
                          'Top Authors', 'Collection Stats'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )

        # Topic distribution
        if 'topic_distribution' in self.stats:
            topics = list(self.stats['topic_distribution'].keys())
            counts = list(self.stats['topic_distribution'].values())
            fig.add_trace(
                go.Bar(x=topics, y=counts, name="Topics"),
                row=1, col=1
            )

        # Publications over time
        if 'year_distribution' in self.stats:
            years = list(self.stats['year_distribution'].keys())
            counts = list(self.stats['year_distribution'].values())
            fig.add_trace(
                go.Scatter(x=years, y=counts, mode='lines+markers', name="Papers"),
                row=1, col=2
            )

        # Top authors
        if 'top_authors' in self.stats:
            authors = list(self.stats['top_authors'].keys())[:5]
            counts = list(self.stats['top_authors'].values())[:5]
            fig.add_trace(
                go.Bar(x=authors, y=counts, name="Authors"),
                row=2, col=1
            )

        # Total count
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=self.stats.get('total_documents', 0),
                title={"text": "Total Documents"},
            ),
            row=2, col=2
        )

        fig.update_layout(height=800, showlegend=False, title_text="Document Collection Analytics")
        return fig

    def export_html(self, output_path: Path):
        """Export dashboard to HTML."""
        fig = self.create_visualizations()
        fig.write_html(output_path)
