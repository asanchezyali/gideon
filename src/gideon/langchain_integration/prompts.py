"""Document analysis prompts."""

from langchain_core.prompts import PromptTemplate


def get_document_analysis_prompt() -> PromptTemplate:
    template = """
        You are a document analysis expert specialized in metadata extraction.
        Your task is to analyze the following document content and extract key metadata fields.

        Document Content:
        {content}

        Instructions:
        Extract and return a JSON object with exactly these fields:
        {
            "author": "AuthorName",
            "year": "YYYY",
            "title": "DocumentTitle",
            "topic": "MainTopic"
        }

        Specific Rules:
        1. Author:
          - Extract a single author name in CamelCase (e.g., "JohnDoe")
          - Use first/primary author if multiple authors exist
          - Remove titles, degrees, and affiliations
          - Return "" if no author found

        2. Year:
          - Extract exactly 4 digits representing publication year
          - Must be between 1900 and current year
          - Use most likely publication year if multiple years found
          - Return "" if no valid year found

        3. Title:
          - Convert title to CamelCase format (e.g., "QuantumMechanicsBasics")
          - Remove special characters and punctuation
          - Keep alphanumeric characters only
          - Return "" if no title found

        4. Topic:
          - Extract single main subject in CamelCase (e.g., "Physics")
          - Use broad category that best describes content
          - Prefer established academic/scientific fields
          - Return "" if topic cannot be determined

        Response Format:
        - Return only the JSON object
        - Use double quotes for strings
        - No additional text or explanations
        - Fields must match exactly as specified
    """
    return PromptTemplate(input_variables=["content"], template=template.strip())
