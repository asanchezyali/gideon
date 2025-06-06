from typing import Optional
from ..utils.bcolors import print_error, print_info
from ..llm.factory import LLMServiceFactory, LLMServiceType
from langchain_core.prompts import PromptTemplate
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings


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
            +++DirectResponse(style=json_only)
            
            You are an expert classifier. Your task is to assign a topic to the following document title.

            Document title: {title}

            Respond with a JSON object in this format:
            {{
              "topic": "Topic_Name"
            }}

            Classification rules:
            1. Choose the most appropriate topic for the title, using academic knowledge categories.
            2. Format the topic as "Topic_Name" (replace spaces with underscores).
            3. Use proper capitalization for the topic name (e.g., "Experimental_Design" not "experimental_design").
            4. Return ONLY the JSON object with no extra text, explanation, or comments.
            5. DO NOT add any explanations, apologies or additional context.
            6. DO NOT include any reasoning, tags, or troubleshooting information.
            7. Your entire response must be valid JSON and nothing else.
            8. Make sure to include the closing brace '}}' in your response.
            """
        )

    async def classify(self, title: str, max_retries: int = 1) -> dict:
        retries = 0
        while retries <= max_retries:
            try:
                print_info(f"Classifying document: {title}{' (retry ' + str(retries) + ')' if retries > 0 else ''}")
                chain = await self.llm_service.create_chain(prompt=self.prompt, output_parser=self.output_parser)
                result = await chain.ainvoke({"title": title})

                if not result or not isinstance(result, dict) or "topic" not in result:
                    if retries < max_retries:
                        print_error(f"Invalid result format on attempt {retries + 1}, retrying: {result}")
                        retries += 1
                        continue
                    return {"topic": "Unknown_Topic"}
                return result

            except Exception as e:
                print_error(f"Error during classification{' attempt ' + str(retries + 1) if retries > 0 else ''}: {e}")
                if retries < max_retries:
                    retries += 1
                    continue
                return {"topic": "Unknown_Topic"}
