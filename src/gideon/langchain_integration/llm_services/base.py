"""Base interface for LLM services."""

from abc import ABC, abstractmethod
from typing import Optional, List, Union, Dict, Any
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.runnables import RunnableSequence


class LLMServiceInterface(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    async def generate(
        self,
        prompt: Union[str, List[BaseMessage], ChatPromptTemplate],
        system_message: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt, list of messages, or prompt template to send to the model
            system_message: Optional system message to prepend
            **kwargs: Additional arguments for generation

        Returns:
            The generated text response
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def create_chain(
        self,
        prompt_template: ChatPromptTemplate,
        output_parser: Optional[BaseOutputParser] = None,
        **kwargs
    ) -> RunnableSequence:
        """Create a processing chain with the model.

        Args:
            prompt_template: The prompt template to use
            output_parser: Optional parser for structured output
            **kwargs: Additional chain configuration

        Returns:
            A runnable chain
        """
        pass

    @abstractmethod
    def get_model(self) -> BaseLanguageModel:
        """Get the underlying LangChain model."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the name of the model being used."""
        pass

    @abstractmethod
    def update_config(self, **kwargs) -> None:
        """Update the model configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        pass

    def _prepare_messages(
        self,
        prompt: Union[str, List[BaseMessage]],
        system_message: Optional[str] = None,
    ) -> List[BaseMessage]:
        """Helper method to prepare messages for the model.

        Args:
            prompt: The prompt or list of messages
            system_message: Optional system message to prepend

        Returns:
            List of messages ready for the model
        """
        messages = []

        if system_message:
            messages.append(SystemMessage(content=system_message))

        if isinstance(prompt, str):
            messages.append(HumanMessage(content=prompt))
        elif isinstance(prompt, list):
            messages.extend(prompt)

        return messages
