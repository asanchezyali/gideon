from langchain_core.output_parsers import JsonOutputParser
from langchain_core.outputs import Generation
import json
import re
from typing import Any


class CleanJsonOutputParser(JsonOutputParser):
    def parse_result(self, result: list[Generation], *, partial: bool = False) -> Any:
        text = result[0].text
        try:
            cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
            cleaned_text = re.sub(r"For troubleshooting.*", "", cleaned_text, flags=re.DOTALL)
            match = re.search(r"\{[\s\S]*\}", cleaned_text)
            if not match:
                raise ValueError("No JSON object found in response")
            json_str = match.group()
            return json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in response")
