"""Tests for analytics dashboard."""

import pytest
from pathlib import Path

from src.gideon.analytics.dashboard import AnalyticsDashboard


class TestAnalyticsDashboard:
    """Test analytics dashboard functionality."""

    @pytest.fixture
    def dashboard(self):
        """Create a dashboard instance."""
        return AnalyticsDashboard()

    @pytest.fixture
    def sample_documents(self):
        """Create sample document collection."""
        return [
            {
                "title": "Doc 1",
                "authors": ["Author A", "Author B"],
                "year": "2023",
                "topics": ["AI", "ML"]
            },
            {
                "title": "Doc 2",
                "authors": ["Author A", "Author C"],
                "year": "2024",
                "topics": ["AI", "NLP"]
            },
            {
                "title": "Doc 3",
                "authors": ["Author B"],
                "year": "2024",
                "topics": ["ML"]
            }
        ]

    def test_analyze_empty_collection(self, dashboard):
        """Test that analyzing empty collection raises error."""
        with pytest.raises(ValueError, match="Cannot analyze empty document collection"):
            dashboard.analyze_collection([])

    def test_analyze_collection(self, dashboard, sample_documents):
        """Test analyzing document collection."""
        stats = dashboard.analyze_collection(sample_documents)

        assert stats['total_documents'] == 3
        assert 'topic_distribution' in stats
        assert 'year_distribution' in stats
        assert 'top_authors' in stats
        assert stats['topic_distribution']['AI'] == 2
        assert stats['year_distribution']['2024'] == 2

    def test_analyze_with_string_topics(self, dashboard):
        """Test analyzing with string topics instead of list."""
        docs = [
            {"title": "Doc 1", "authors": ["A"], "year": "2024", "topics": "AI"}
        ]
        stats = dashboard.analyze_collection(docs)
        assert stats['total_documents'] == 1

    def test_create_visualizations_without_analysis(self, dashboard):
        """Test that creating viz without analysis raises error."""
        with pytest.raises(ValueError, match="No statistics available"):
            dashboard.create_visualizations()

    def test_create_visualizations(self, dashboard, sample_documents):
        """Test creating visualizations."""
        dashboard.analyze_collection(sample_documents)
        fig = dashboard.create_visualizations()
        assert fig is not None

    def test_export_html_without_analysis(self, dashboard, tmp_path):
        """Test that exporting without analysis raises error."""
        output_path = tmp_path / "dashboard.html"
        with pytest.raises(ValueError, match="No statistics available"):
            dashboard.export_html(output_path)

    def test_export_html(self, dashboard, sample_documents, tmp_path):
        """Test exporting dashboard to HTML."""
        dashboard.analyze_collection(sample_documents)
        output_path = tmp_path / "dashboard.html"
        dashboard.export_html(output_path)
        assert output_path.exists()

    def test_handle_missing_fields(self, dashboard):
        """Test handling documents with missing fields."""
        docs = [
            {"title": "Doc 1"},  # Missing authors, year, topics
            {"title": "Doc 2", "authors": None, "year": None},
        ]
        stats = dashboard.analyze_collection(docs)
        assert stats['total_documents'] == 2
        assert len(stats['topic_distribution']) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
