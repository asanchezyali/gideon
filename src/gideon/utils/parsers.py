"""Custom output parsers for Gideon."""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.outputs import Generation
import json
import re
from typing import Any


class CleanJsonOutputParser(JsonOutputParser):
    """A JSON output parser that cleans LLM responses from thinking process and troubleshooting info."""
    
    def parse_result(self, result: list[Generation], *, partial: bool = False) -> Any:
        """Parse and clean the LLM response.
        
        Args:
            result: List of Generation objects containing the LLM response
            partial: Whether to parse partial results
            
        Returns:
            Parsed JSON object
            
        Raises:
            ValueError: If no valid JSON object is found or if the JSON is invalid
        """
        text = result[0].text
        try:
            # Remove thinking process
            cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
            # Remove troubleshooting info
            cleaned_text = re.sub(r"For troubleshooting.*", "", cleaned_text, flags=re.DOTALL)
            
            # First attempt: Try to parse the entire text as JSON directly
            try:
                # Try simple parsing first (handles complete valid JSON responses)
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                # If direct parsing fails, continue with pattern matching
                pass
                
            # Second attempt: Look for JSON object using regex
            match = re.search(r"\{[\s\S]*?\}", cleaned_text)
            if not match:
                # Third attempt: Handle incomplete JSON that's missing closing brace
                if cleaned_text.strip().startswith("{"):
                    # Try to complete the JSON by adding a closing brace
                    fixed_json = cleaned_text.strip() + "}"
                    try:
                        return json.loads(fixed_json)
                    except json.JSONDecodeError:
                        pass
                        
                # If we get here, we couldn't parse the JSON
                raise ValueError("No JSON object found in response")
                
            json_str = match.group()
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in response") 