"""Quick test to verify OpenAI integration works."""

import asyncio
from src.gideon.llm.factory import LLMServiceFactory, LLMServiceType
from langchain_core.prompts import PromptTemplate


async def test_openai():
    """Test OpenAI integration."""
    print("Testing OpenAI integration...")

    # Create OpenAI service
    service = LLMServiceFactory.create(
        service_type=LLMServiceType.OPENAI,
        config={
            "model": "gpt-4-turbo-preview",
            "temperature": 0.1
        }
    )

    # Simple test prompt
    prompt = PromptTemplate.from_template(
        "Extract the title, authors and year from this paper text:\n\n{text}\n\nReturn as JSON."
    )

    # Create chain
    chain = await service.create_chain(prompt)

    # Test with sample text
    sample_text = """
    Attention Is All You Need

    Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones,
    Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin

    2017

    Abstract: The dominant sequence transduction models are based on complex
    recurrent or convolutional neural networks...
    """

    print("\nSample text:")
    print(sample_text[:200] + "...")

    print("\nSending to GPT-4...")
    result = await chain.ainvoke({"text": sample_text})

    print("\nResult:")
    print(result.content if hasattr(result, 'content') else result)

    print("\n✅ OpenAI integration working!")


if __name__ == "__main__":
    asyncio.run(test_openai())
