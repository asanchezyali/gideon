import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.gideon.agents.renamer import DocumentInfo, DocumentAnalyzer, UNKNOWN_AUTHOR, UNKNOWN_TITLE, UNKNOWN_TOPIC


@pytest.fixture
def wizard():
    with patch("src.gideon.agents.renamer.LLMServiceFactory.create", return_value=MagicMock()):
        yield DocumentAnalyzer()


def test_document_info_init():
    doc = DocumentInfo(["Alice Smith"], "2022", "A Study on Testing", "Mathematics")
    assert doc.authors == ["Alice Smith"]
    assert doc.year == "2022"
    assert doc.title == "A Study on Testing"
    assert doc.topic == "Mathematics"


def test_format_authors_single(wizard):
    assert wizard._format_authors(["Alice Smith"]) == "Alice_Smith"


def test_format_authors_multiple(wizard):
    assert wizard._format_authors(["Alice Smith", "Bob Jones"]) == "Alice_Smith_And_Others"


def test_format_authors_empty(wizard):
    assert wizard._format_authors([]) == UNKNOWN_AUTHOR


def test_format_year(wizard):
    assert wizard._format_year("2022") == "2022"
    assert wizard._format_year("") == ""


def test_format_title(wizard):
    assert wizard._format_title("A Study on Testing!") == "A_study_on_testing"
    assert wizard._format_title("") == UNKNOWN_TITLE


def test_format_topic_valid(wizard):
    assert wizard._format_topic("Mathematics") == "Mathematics"
    assert wizard._format_topic("mathematics") == "Mathematics"


def test_format_topic_invalid(wizard):
    assert wizard._format_topic("UnknownField") == UNKNOWN_TOPIC
    assert wizard._format_topic("") == UNKNOWN_TOPIC


def test_format_authors_special_chars(wizard):
    assert wizard._format_authors(["A!li@ce S#mi$th"]) == "Alice_Smith"
    assert wizard._format_authors(["A!li@ce S#mi$th", "B*ob J(ones)"]) == "Alice_Smith_And_Others"


def test_format_authors_extra_spaces(wizard):
    assert wizard._format_authors(["  alice   smith  "]) == "Alice_Smith"


def test_format_title_special_chars(wizard):
    assert wizard._format_title("!@#$$%^&*()") == ""
    assert wizard._format_title("1234 Testing!") == "1234_testing"


def test_format_year_invalid(wizard):
    assert wizard._format_year("20A2") == "20A2"[:4]
    assert wizard._format_year("20223") == "2022"
    assert wizard._format_year("abcd") == "abcd"


def test_format_topic_spaces_case(wizard):
    assert wizard._format_topic("  mathematics  ") == "Mathematics"  # spaces are handled
    assert wizard._format_topic("MaThEmAtIcS") == "Mathematics"


def test_generate_filename(wizard):
    doc = DocumentInfo(["Alice Smith"], "2022", "A Study on Testing", "Mathematics")
    filename = wizard.generate_filename(doc)
    assert filename.startswith("Alice_Smith.2022.A_study_on_testing.Mathematics.")
    assert filename.endswith(".pdf")


def test_generate_filename_all_unknowns(wizard):
    doc = DocumentInfo([], "", "", "")
    filename = wizard.generate_filename(doc)
    assert filename.startswith(f"{UNKNOWN_AUTHOR}.{UNKNOWN_TITLE}.{UNKNOWN_TOPIC}.") or filename.startswith(
        f"{UNKNOWN_AUTHOR}..{UNKNOWN_TITLE}.{UNKNOWN_TOPIC}."
    )
    assert filename.endswith(".pdf")


@pytest.mark.asyncio
async def test_analyze_document_valid():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = {
        "authors": ["Alice Smith"],
        "year": "2022",
        "title": "A Study on Testing",
        "topic": "Mathematics",
    }
    with patch(
        "src.gideon.agents.renamer.LLMServiceFactory.create",
        return_value=MagicMock(create_chain=AsyncMock(return_value=mock_chain)),
    ):
        wizard = DocumentAnalyzer()
        doc = await wizard.analyze("content", "file.pdf")
        assert isinstance(doc, DocumentInfo)
        assert doc.authors == ["Alice Smith"]
        assert doc.year == "2022"
        assert doc.title == "A Study on Testing"
        assert doc.topic == "Mathematics"


@pytest.mark.asyncio
async def test_analyze_document_missing_fields():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = {"authors": [], "year": "", "title": "", "topic": ""}
    with patch(
        "src.gideon.agents.renamer.LLMServiceFactory.create",
        return_value=MagicMock(create_chain=AsyncMock(return_value=mock_chain)),
    ):
        wizard = DocumentAnalyzer()
        doc = await wizard.analyze("content", "file.pdf")
        assert isinstance(doc, DocumentInfo)
        assert doc.authors == []
        assert doc.year == ""
        assert doc.title == UNKNOWN_TITLE
        assert doc.topic == UNKNOWN_TOPIC


@pytest.mark.asyncio
async def test_analyze_document_invalid_json():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = "not a dict"
    with patch(
        "src.gideon.agents.renamer.LLMServiceFactory.create",
        return_value=MagicMock(create_chain=AsyncMock(return_value=mock_chain)),
    ):
        wizard = DocumentAnalyzer()
        doc = await wizard.analyze("content", "file.pdf")
        assert doc is None


@pytest.mark.asyncio
async def test_analyze_document_exception():
    mock_chain = AsyncMock()
    mock_chain.ainvoke.side_effect = Exception("LLM error")
    with patch(
        "src.gideon.agents.renamer.LLMServiceFactory.create",
        return_value=MagicMock(create_chain=AsyncMock(return_value=mock_chain)),
    ):
        wizard = DocumentAnalyzer()
        doc = await wizard.analyze("content", "file.pdf")
        assert doc is None
