from typing import Optional, Dict, Any
from langchain_core.prompts import PromptTemplate
from ..utils.logging import log_info, log_error, log_warning
from ..llm.factory import LLMServiceFactory, LLMServiceType
from ..utils.parsers import CleanJsonOutputParser
from ..core.config import settings
from ..models.document import DocumentInfo, UNKNOWN_TITLE, TOPIC_LIST, UNKNOWN_TOPIC
import json
import re


def format_topics_list(topics: list) -> str:
    """Format the topics list for use in prompts."""
    return "\n".join(f"- {topic}" for topic in topics)


def validate_topic_in_list(topic: str, topic_list: list) -> tuple[bool, str]:
    """Validate that a topic exists in the predefined list."""
    if topic not in topic_list:
        topic_lower = topic.lower()
        matches = [t for t in topic_list if t.lower() == topic_lower]
        if matches:
            return False, f"Topic '{topic}' has incorrect case, should be '{matches[0]}'"
        
        partial_matches = [t for t in topic_list if topic_lower in t.lower() or t.lower() in topic_lower]
        if partial_matches:
            return False, f"Topic '{topic}' not found, similar topics: {partial_matches[:3]}"
        
        return False, f"Topic '{topic}' not in predefined list"
    
    return True, "Valid topic"


def extract_json_from_response(response_text: str) -> Optional[dict]:
    """Attempt to extract JSON from response text if it contains extra content."""
    if not response_text:
        return None
    
    json_pattern = r'\{[^{}]*"(?:topic|title|authors|year)"[^{}]*\}'
    matches = re.findall(json_pattern, response_text)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    return None


class DocumentAnalyzer:
    def __init__(
        self,
        llm_service_type: LLMServiceType = settings.DEFAULT_LLM_SERVICE_TYPE,
        service_config: Optional[Dict[str, Any]] = None,
    ):
        self.llm_service = LLMServiceFactory.create(llm_service_type, service_config)
        self.json_parser = CleanJsonOutputParser()
        
        # Analysis prompt for extracting document metadata
        self.analysis_prompt = PromptTemplate.from_template(
            """
            +++SchemaOutput(format=json, schema=strict)
            +++Precision(level=high)
            +++RuleFollowing(priority=absolute)
            +++ExtractMetadata(fields=authors,year,title,topic)
            +++ArrayOutput(field=authors)
            +++DirectResponse(style=json_only)
            
            You are a document analysis expert. Extract key information from the document content and classify it.
            
            Return a JSON object with exactly these fields:
            {{
                "authors": ["Author Name 1", "Author Name 2"],
                "year": "YYYY",
                "title": "Document Title",
                "topic": "Topic_Name"
            }}
            
            AVAILABLE TOPICS:
            {topics_formatted}
            
            # Rules:
            1. Authors must be an array of names
               - Include all authors you can identify
               - Use the original capitalization and format from the document
               - If no authors found, return an empty array []
            2. Year must be exactly 4 digits or empty string if not found
            3. Title should maintain its original formatting (as found in the document)
            4. Topic must be exactly ONE from the available list above
               - Choose the topic that best matches the document's subject matter
               - Topic names must match exactly as listed (case-sensitive)
               - If uncertain, use "Other"
            5. If any field except authors is not found, return an empty string for that field (except topic, use "Other")
            6. All strings must use double quotes
            7. Return only the JSON object, no other text
            8. DO NOT include any <think> tags or intermediate reasoning in your output
            9. DO NOT include any troubleshooting URLs or error messages
            10. Return ONLY the valid JSON object and nothing else

            Document content:
            {content}
            """
        )
        
        # Classification prompt for when we only have a title
        self.classification_prompt = PromptTemplate.from_template(
            """
            You are an expert document classifier. Analyze the document title and assign the most appropriate topic from
            the predefined list.
            
            DOCUMENT TITLE: {title}

            AVAILABLE TOPICS:
            {topics_formatted}

            CLASSIFICATION REQUIREMENTS:
            1. Select exactly ONE topic from the available list above
            2. Choose the topic that best matches the document's subject matter
            3. Consider the primary focus and domain of the document
            4. If multiple topics could apply, choose the most specific/relevant one
            5. Topic names must match exactly as listed (case-sensitive with underscores)

            OUTPUT FORMAT:
            Return ONLY a valid JSON object with this exact structure:
            {{"topic": "Topic_Name"}}

            CRITICAL RULES:
            - Your response must be valid JSON only
            - No explanations, comments, or additional text
            - Topic must be from the provided list exactly as written
            - Include both opening and closing braces
            - Use double quotes for JSON strings

            Examples of valid responses:
            {{"topic": "Mathematics"}}
            {{"topic": "Computer Science"}}
            {{"topic": "Artificial Intelligence"}}
            """
        )

    async def analyze(self, content: str, file_name: str) -> Optional[DocumentInfo]:
        """Analyze document content and extract metadata including topic classification."""
        try:
            log_info(f"Analyzing document with classification: {file_name}")
            chain = await self.llm_service.create_chain(
                prompt=self.analysis_prompt, 
                output_parser=self.json_parser
            )
            result = await chain.ainvoke({
                "content": content[:settings.MAX_CONTENT_LENGTH],
                "topics_formatted": format_topics_list(TOPIC_LIST)
            })

            if not result or not isinstance(result, dict):
                log_error(f"Invalid response format for {file_name}")
                return None

            # Validate topic if provided
            topic = result.get("topic", UNKNOWN_TOPIC)
            if topic and topic != UNKNOWN_TOPIC:
                is_valid_topic, topic_error = validate_topic_in_list(topic, TOPIC_LIST)
                if not is_valid_topic:
                    log_warning(f"Invalid topic '{topic}' for {file_name}: {topic_error}. Using 'Other'")
                    topic = "Other"

            return DocumentInfo(
                authors=result.get("authors", []),
                year=str(result.get("year", "")),
                title=str(result.get("title", UNKNOWN_TITLE)) or UNKNOWN_TITLE,
                topic=topic or UNKNOWN_TOPIC,
            )

        except Exception as e:
            log_error(f"Error analyzing document {file_name}: {str(e)}")
            return None

    async def classify(self, title: str, max_retries: int = 2) -> Dict[str, str]:
        """Classify a document by its title only."""
        if not title or not title.strip():
            log_error("Empty or whitespace-only title provided")
            return {"topic": UNKNOWN_TOPIC}

        retries = 0
        last_error = None
        
        while retries <= max_retries:
            try:
                attempt_msg = f" (attempt {retries + 1}/{max_retries + 1})" if retries > 0 else ""
                log_info(f"Classifying document: '{title}'{attempt_msg}")
                
                chain = await self.llm_service.create_chain(
                    prompt=self.classification_prompt, 
                    output_parser=self.json_parser
                )
                
                result = await chain.ainvoke({
                    "title": title.strip(), 
                    "topics_formatted": format_topics_list(TOPIC_LIST)
                })

                # Validate response format
                if not result or not isinstance(result, dict):
                    last_error = f"Invalid response format: got {type(result)}"
                    log_warning(f"{last_error}. Raw result: {result}")
                    
                    # Try to extract JSON if result is a string
                    if isinstance(result, str):
                        extracted = extract_json_from_response(result)
                        if extracted:
                            log_info("Successfully extracted JSON from string response")
                            result = extracted
                    
                    if not result or not isinstance(result, dict):
                        if retries < max_retries:
                            retries += 1
                            continue

                # Validate topic field
                if "topic" not in result:
                    last_error = "Missing 'topic' key in response"
                    log_warning(last_error)
                    if retries < max_retries:
                        retries += 1
                        continue

                topic = result["topic"].strip() if isinstance(result["topic"], str) else ""
                if not topic:
                    last_error = "Topic value is empty"
                    log_warning(last_error)
                    if retries < max_retries:
                        retries += 1
                        continue

                # Validate topic against list
                is_valid_topic, topic_error = validate_topic_in_list(topic, TOPIC_LIST)
                if not is_valid_topic:
                    last_error = f"Invalid topic: {topic_error}"
                    log_warning(last_error)
                    
                    if retries < max_retries:
                        retries += 1
                        continue
                else:
                    log_info(f"Successfully classified '{title}' as '{topic}'")
                    return {"topic": topic}

            except Exception as e:
                last_error = f"Classification error: {str(e)}"
                log_error(f"{last_error}{attempt_msg}")
                
                if retries < max_retries:
                    retries += 1
                    continue

        log_error(f"Classification failed for '{title}' after {max_retries + 1} attempts. Last error: {last_error}")
        return {"topic": UNKNOWN_TOPIC}
