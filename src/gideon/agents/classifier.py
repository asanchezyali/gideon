from typing import Optional
from ..utils.bcolors import print_error, print_info
from ..llm.factory import LLMServiceFactory, LLMServiceType
from langchain_core.prompts import PromptTemplate
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings
from ..models.document import TOPIC_LIST


class ClassifierWizard:
    def __init__(
        self,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[dict] = None,
    ):
        self.llm_service = LLMServiceFactory.create(llm_service_type, service_config)
        self.output_parser = CleanJsonOutputParser()
        self.prompt = PromptTemplate.from_template(
            """
            +++SchemaOutput(format=json, schema=strict)
            +++Precision(level=high)
            +++RuleFollowing(priority=absolute)
            +++ExtractMetadata(fields=topic)
            +++DirectResponse(field=topic)
            You are to classify the following document title into one of the predefined topics.

            Document title: {title}
            Available topics: {TOPIC_LIST}

            Respond with a JSON object in this format:
            {{
              "topic": "Topic_Name",
              "confidence": 0.0
            }}

            Rules:
            1. The topic must exactly match one from the provided list.
            2. If no topic fits, use "Unknown_Topic".
            3. "confidence" should be a float between 0.0 and 1.0, reflecting certainty.
            4. Format the topic as "Topic_Name" (underscores for spaces).
            5. Output only the JSON object, no extra text.
            6. Do not include any reasoning, tags, or troubleshooting information.
            """
        )

    async def classify(self, title: str) -> dict:
        try:
            print_info(f"Classifying document: {title}")
            chain = await self.llm_service.create_chain(prompt=self.prompt, output_parser=self.output_parser)
            result = await chain.ainvoke({"title": title, "TOPIC_LIST": TOPIC_LIST})
            print_info(f"Classification result: {result}")
            return result
        except Exception as e:
            print_error(f"Error during classification: {e}")
            return {"topic": "Unknown", "confidence": 0.0}
