from typing import List, Optional, Dict
from rich.console import Console
from ..llm.factory import LLMServiceFactory, LLMServiceType
from langchain_core.prompts import PromptTemplate
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings

UNKNOWN_TOPIC = "Unknown_Topic"
TOPIC_LIST = [
    "Mathematics",
    "Topology",
    "Geometry",
    "Algebra",
    "Analysis",
    "Probability",
    "Statistics",
    "Combinatorics",
    "Computer Science",d
    "Physics",
    "Chemistry",
    "Biology",
    "Economics",
    "Business",
    "Engineering",
    "Medicine",
    "Psychology",
    "Philosophy",
    "History",
    "Literature",
    "Arts",
    "Law",
    "Education",
    "Marketing",
    "Finance",
    "Accounting",
    "Management",
    "Artificial Intelligence",
    "Machine Learning",
    "Data Science",
    "Software Engineering",
    "Other",
]


class ClassifierWizard:
    def __init__(
        self,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[dict] = None,
    ):
        self.llm_service = LLMServiceFactory.create(llm_service_type, service_config)
        self.console = Console()
        self.output_parser = CleanJsonOutputParser()
        self.prompt = PromptTemplate.from_template(
            """
            +++SchemaOutput(format=json, schema=strict)
            +++Precision(level=high)
            +++RuleFollowing(priority=absolute)
            +++ExtractMetadata(fields=topic)
            +++DirectResponse(field=topic)
            Classify the following document title into one of the predefined topics:
            Title: {document}
            Available topics: {TOPIC_LIST}
            Please return a JSON object with the topic and a confidence score.
            """
        )

    async def classify_document(self, title: str) -> dict:
        try:
            self.console.log(f"Classifying document: {title}")
            chain = await self.llm.service.create_chain(prompt=self.prompt, output_parser=self.output_parser)
            result = await chain.ainvoke({"title": title, "TOPIC_LIST": TOPIC_LIST})
            self.console.log(f"Classification result: {result}")
            return result
        except Exception as e:
            self.console.log(f"Error during classification: {e}")
            return {"topic": "Unknown", "confidence": 0.0}

    def _format_topic(self, topic: str) -> str:
        if not topic:
            return UNKNOWN_TOPIC
        # Convert spaces to underscores
        formatted_topic = "_".join(topic.split())
        # Case-insensitive lookup in TOPIC_LIST
        for valid_topic in TOPIC_LIST:
            if formatted_topic.lower() == valid_topic.lower():
                return valid_topic
        return UNKNOWN_TOPIC
