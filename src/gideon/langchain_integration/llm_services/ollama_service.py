"""Ollama LLM service implementation."""
from typing import Optional, List, Union, Dict, Any

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence

from .base import LLMServiceInterface


class OllamaService(LLMServiceInterface):
    """Implementation of LLMServiceInterface using Ollama."""

    def __init__(self, model_name: str = "deepseek-r1:latest", **kwargs):
        """Initialize the Ollama service.

        Args:
            model_name: Name of the Ollama model to use
            **kwargs: Additional arguments to pass to ChatOllama
        """
        self._model_name = model_name
        self._config = {
            "temperature": kwargs.get("temperature", 0),
            "format": kwargs.get("format"),
            "num_ctx": kwargs.get("num_ctx", 4096),
            "repeat_penalty": kwargs.get("repeat_penalty", 1.1),
            "seed": kwargs.get("seed", None),
        }
        self._model = ChatOllama(model=model_name, **self._config)

    async def generate(
        self,
        prompt: Union[str, List[BaseMessage], ChatPromptTemplate],
        system_message: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate a response from Ollama.

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

    async def create_chain(
        self,
        prompt_template: ChatPromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
        **kwargs
    ) -> RunnableSequence:
        """Create a LangChain chain with Ollama.

        Args:
            prompt_template: The prompt template to use
            output_parser: Optional parser for the output
            **kwargs: Additional arguments for chain creation

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

    def get_model(self) -> ChatOllama:
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
        self._model = ChatOllama(model=self._model_name, **self._config)
