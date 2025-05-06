"""Gemini LLM service implementation."""
import os
from typing import Dict, Any, Optional, List, Union

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser, JsonOutputParser
from langchain_core.runnables import RunnableSequence

from .base import LLMServiceInterface

class GeminiService(LLMServiceInterface):
    """Implementation of LLMServiceInterface using Google's Gemini model."""
    
    def __init__(self, model_name: str = "gemini-pro", api_key: Optional[str] = None, **kwargs):
        """Initialize the Gemini service.
        
        Args:
            model_name: Name of the Gemini model to use
            api_key: Google API key. If not provided, will look for GOOGLE_API_KEY env var
            **kwargs: Additional arguments to pass to ChatGoogleGenerativeAI
        """
        self._model_name = model_name
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            
        self._config = {
            "temperature": kwargs.get('temperature', 0),
            "top_p": kwargs.get('top_p', 0.95),
            "top_k": kwargs.get('top_k', 40),
            "max_output_tokens": kwargs.get('max_output_tokens', 2048),
            "convert_system_message_to_human": True
        }
        
        self._model = ChatGoogleGenerativeAI(
            model=model_name,
            **self._config
        )
    
    async def generate(
        self,
        prompt: Union[str, List[BaseMessage], ChatPromptTemplate],
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response from Gemini.
        
        Args:
            prompt: The prompt, list of messages, or template to send
            system_message: Optional system message to prepend
            **kwargs: Additional arguments for generation
            
        Returns:
            The generated text response
        """
        if isinstance(prompt, ChatPromptTemplate):
            return await self.generate_with_template(prompt, kwargs.get("variables", {}), system_message)
        
        messages = self._prepare_messages(prompt, system_message)
        response = await self._model.ainvoke(messages, **kwargs)
        return response.content

    async def generate_with_template(
        self,
        template: ChatPromptTemplate,
        input_variables: Dict[str, Any],
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response using a prompt template.
        
        Args:
            template: The prompt template to use
            input_variables: Variables to fill in the template
            system_message: Optional system message to prepend
            **kwargs: Additional generation arguments
            
        Returns:
            The generated text response
        """
        messages = await template.ainvoke(input_variables)
        if system_message:
            messages = self._prepare_messages(messages, system_message)
        response = await self._model.ainvoke(messages, **kwargs)
        return response.content
    
    async def generate_with_json(self, 
                               prompt: Union[str, List[BaseMessage]], 
                               output_schema: Dict[str, Any],
                               system_message: Optional[str] = None) -> Dict[str, Any]:
        """Generate a JSON response from Gemini.
        
        Args:
            prompt: The prompt or list of messages to send to the model
            output_schema: Schema for the expected JSON output
            system_message: Optional system message to prepend
            
        Returns:
            Dictionary containing the structured response
        """
        # Create a parser that enforces the output schema
        parser = JsonOutputParser()
        
        # Prepare messages with schema instruction
        schema_instruction = f"""You must respond with valid JSON that exactly matches this schema:
        {output_schema}
        
        Your response must contain ONLY the JSON object, no other text or explanations.
        Do not include markdown formatting or code blocks."""
        
        messages = self._prepare_messages(
            prompt,
            system_message=schema_instruction if not system_message 
            else f"{system_message}\n\n{schema_instruction}"
        )
        
        # Create and execute chain with retry logic
        chain = RunnableSequence([
            self._model,
            parser.with_retry()  # Enable retry for JSON parsing
        ])
        
        return await chain.ainvoke(messages)
    
    async def create_chain(
        self,
        prompt_template: ChatPromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
        **kwargs
    ) -> RunnableSequence:
        """Create a LangChain chain with Gemini.
        
        Args:
            prompt_template: The prompt template to use
            output_parser: Optional parser for structured output
            **kwargs: Additional chain configuration
            
        Returns:
            A runnable chain
        """
        chain_elements = [prompt_template, self._model]
        
        if output_parser:
            chain_elements.append(
                output_parser.with_retry() if hasattr(output_parser, 'with_retry')
                else output_parser
            )
            
        return RunnableSequence(chain_elements)
    
    def get_model(self) -> ChatGoogleGenerativeAI:
        """Get the underlying LangChain model."""
        return self._model
    
    @property
    def model_name(self) -> str:
        """Get the name of the model being used."""
        return self._model_name
        
    def update_config(self, **kwargs) -> None:
        """Update the model configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        self._config.update(kwargs)
        self._model = ChatGoogleGenerativeAI(
            model=self._model_name,
            **self._config
        )