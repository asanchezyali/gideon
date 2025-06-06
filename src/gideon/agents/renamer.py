from typing import Optional, Dict, Any
from langchain_core.prompts import PromptTemplate
from ..utils.bcolors import print_info, print_error
from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings
from ..models.document import DocumentInfo, UNKNOWN_TITLE


class DocumentAnalyzer:
    def __init__(
        self,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[Dict[str, Any]] = None,
    ):
        self.llm_service = LLMServiceFactory.create(llm_service_type, service_config)
        self.json_parser = CleanJsonOutputParser()
        self.prompt = PromptTemplate.from_template(
            """
            +++SchemaOutput(format=json, schema=strict)
            +++Precision(level=high)
            +++RuleFollowing(priority=absolute)
            +++ExtractMetadata(fields=authors,year,title,topic)
            +++ArrayOutput(field=authors)
            +++DirectResponse(style=json_only)
            
            You are a document analysis expert. Extract key information from the document content.
            
            Return a JSON object with exactly these fields:
            {{
                "authors": ["Author Name 1", "Author Name 2"],
                "year": "YYYY",
                "title": "Document Title",
            }}            
            # Rules:
            1. Authors must be an array of names
               - Include all authors you can identify
               - Use the original capitalization and format from the document
               - If no authors found, return an empty array []
            2. Year must be exactly 4 digits or empty string if not found
            3. Title should maintain its original formatting (as found in the document)
            5. If any field except authors is not found, return an empty string for that field
            6. All strings must use double quotes
            7. Return only the JSON object, no other text
            8. DO NOT include any <think> tags or intermediate reasoning in your output
            9. DO NOT include any troubleshooting URLs or error messages
            10. Return ONLY the valid JSON object and nothing else

            Document content:
            {content}
            """
        )

    async def analyze(self, content: str, file_name: str) -> Optional[DocumentInfo]:
        try:
            print_info(f"Analyzing document: {file_name}")
            chain = await self.llm_service.create_chain(prompt=self.prompt, output_parser=self.json_parser)
            result = await chain.ainvoke(
                {
                    "content": content[: settings.MAX_CONTENT_LENGTH],
                }
            )

            if not result or not isinstance(result, dict):
                print_error(f"Invalid response format for {file_name}")
                return None

            return DocumentInfo(
                authors=result.get("authors", []),
                year=str(result.get("year", "")),
                title=str(result.get("title", UNKNOWN_TITLE)) or UNKNOWN_TITLE,
            )

        except Exception as e:
            print_error(f"Error analyzing document {file_name}: {str(e)}")
            return None
