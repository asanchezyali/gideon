"""Analytics dashboard for document collections."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class AnalyticsDashboard:
    """Generate analytics and visualizations for document collections."""

    def __init__(self):
        """Initialize analytics dashboard."""
        self.stats: Dict[str, Any] = {}

    def analyze_collection(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze document collection.

        Args:
            documents: List of document dictionaries with metadata

        Returns:
            Dictionary with collection statistics

        Raises:
            ValueError: If documents list is empty
        """
        if not documents:
            raise ValueError("Cannot analyze empty document collection")

        # Topic distribution
        all_topics = []
        for doc in documents:
            topics = doc.get('topics', [])
            if isinstance(topics, list):
                all_topics.extend([t for t in topics if t])
            elif isinstance(topics, str):
                all_topics.append(topics)

        topic_counts = Counter(all_topics) if all_topics else Counter()

        # Year distribution
        years = []
        for doc in documents:
            year = doc.get('year')
            if year:
                # Handle different year formats
                year_str = str(year).strip()
                if year_str.isdigit():
                    years.append(year_str)

        year_counts = Counter(years) if years else Counter()

        # Author analysis
        all_authors = []
        for doc in documents:
            authors = doc.get('authors', [])
            if isinstance(authors, list):
                all_authors.extend([a.strip() for a in authors if a and a.strip()])
            elif isinstance(authors, str):
                all_authors.append(authors.strip())

        author_counts = Counter(all_authors) if all_authors else Counter()

        self.stats = {
            "total_documents": len(documents),
            "topic_distribution": dict(topic_counts.most_common(10)),
            "year_distribution": dict(sorted(year_counts.items())),
            "top_authors": dict(author_counts.most_common(10)),
        }

        return self.stats

    def create_visualizations(self) -> go.Figure:
        """
        Create visualization dashboard.

        Returns:
            Plotly figure with dashboard

        Raises:
            ValueError: If no statistics have been computed
        """
        if not self.stats:
            raise ValueError("No statistics available. Run analyze_collection() first.")

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Topic Distribution', 'Publications Over Time',
                          'Top Authors', 'Collection Stats'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )

        # Topic distribution
        if self.stats.get('topic_distribution'):
            topics = list(self.stats['topic_distribution'].keys())
            counts = list(self.stats['topic_distribution'].values())
            if topics and counts:
                fig.add_trace(
                    go.Bar(x=topics, y=counts, name="Topics", marker_color='lightblue'),
                    row=1, col=1
                )

        # Publications over time
        if self.stats.get('year_distribution'):
            years = list(self.stats['year_distribution'].keys())
            counts = list(self.stats['year_distribution'].values())
            if years and counts:
                fig.add_trace(
                    go.Scatter(x=years, y=counts, mode='lines+markers', name="Papers",
                             line=dict(color='green'), marker=dict(size=8)),
                    row=1, col=2
                )

        # Top authors
        if self.stats.get('top_authors'):
            authors = list(self.stats['top_authors'].keys())[:5]
            counts = list(self.stats['top_authors'].values())[:5]
            if authors and counts:
                fig.add_trace(
                    go.Bar(x=authors, y=counts, name="Authors", marker_color='coral'),
                    row=2, col=1
                )

        # Total count
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=self.stats.get('total_documents', 0),
                title={"text": "Total Documents"},
                number={"font": {"size": 50}}
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Document Collection Analytics",
            title_font_size=20
        )

        return fig

    def export_html(self, output_path: Path):
        """
        Export dashboard to HTML.

        Args:
            output_path: Path to output HTML file

        Raises:
            ValueError: If export fails
        """
        if not self.stats:
            raise ValueError("No statistics available. Run analyze_collection() first.")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            fig = self.create_visualizations()
            fig.write_html(str(output_path), auto_open=False)
        except Exception as e:
            raise ValueError(f"Failed to export dashboard: {str(e)}")
