"""
Ejemplo: Asistente de Investigación Interactivo
================================================

Este ejemplo implementa un asistente conversacional AI que puede:
- Responder preguntas sobre tu colección de documentos
- Buscar papers relevantes
- Generar resúmenes y notas
- Crear revisiones de literatura
- Sugerir papers relacionados
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
import json


class AgentTool(Enum):
    """Available tools for the research assistant."""
    SEARCH = "search"
    SUMMARIZE = "summarize"
    EXTRACT_REFS = "extract_references"
    FIND_RELATED = "find_related"
    CLASSIFY = "classify"
    EXPORT = "export"
    ANALYZE_COLLECTION = "analyze_collection"


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool: AgentTool
    success: bool
    data: Any
    message: str


class ResearchAssistant:
    """
    AI-powered research assistant with conversation memory.

    Features:
    - Natural language interaction
    - Context-aware responses
    - Tool use (search, summarize, etc.)
    - Conversation memory
    - Research task automation
    """

    def __init__(
        self,
        llm_model: str = "deepseek-r1:latest",
        temperature: float = 0.3,
        search_engine: Optional[Any] = None,
        file_service: Optional[Any] = None
    ):
        # LLM
        self.llm = ChatOllama(
            model=llm_model,
            temperature=temperature
        )

        # Services
        self.search_engine = search_engine
        self.file_service = file_service

        # Conversation memory
        self.message_history = ChatMessageHistory()

        # System prompt
        self.system_prompt = """You are Gideon, an AI research assistant helping researchers manage and explore their document collections.

Your capabilities:
- Search through document collections using semantic search
- Summarize papers and extract key information
- Find related papers and build citation networks
- Extract and format references
- Classify documents by topic
- Analyze research collections and provide insights
- Generate literature reviews

When a user asks you to perform a task, determine which tools you need and execute them.
Always provide helpful, accurate, and concise responses.

Available tools:
1. search(query: str, k: int) -> List[SearchResult]
   - Semantic search through documents
2. summarize(document_path: str) -> str
   - Summarize a document
3. extract_references(document_path: str) -> List[Reference]
   - Extract bibliography
4. find_related(document_path: str, k: int) -> List[Path]
   - Find semantically similar papers
5. classify(document_path: str) -> Dict
   - Classify document by topic
6. analyze_collection(directory: str) -> Statistics
   - Analyze entire collection

To use a tool, output JSON in this format:
{"tool": "tool_name", "params": {"param1": "value1", ...}}

After tool execution, you'll receive the results and can provide a response to the user."""

        # Add system message
        self.message_history.add_message(SystemMessage(content=self.system_prompt))

    async def chat(self, user_message: str) -> str:
        """
        Process user message and return response.

        Args:
            user_message: User's input

        Returns:
            Assistant's response
        """
        # Add user message to history
        self.message_history.add_user_message(user_message)

        # Get response from LLM
        messages = self.message_history.messages
        response = await self.llm.ainvoke(messages)

        response_text = response.content if hasattr(response, 'content') else str(response)

        # Check if response contains tool calls
        tool_call = self._parse_tool_call(response_text)

        if tool_call:
            # Execute tool
            tool_result = await self._execute_tool(
                tool_call["tool"],
                tool_call["params"]
            )

            # Add tool result to context
            tool_message = f"Tool result: {json.dumps(tool_result.data, default=str)}"
            self.message_history.add_message(AIMessage(content=tool_message))

            # Get final response incorporating tool results
            final_response = await self.llm.ainvoke(self.message_history.messages)
            final_text = final_response.content if hasattr(final_response, 'content') else str(final_response)

            self.message_history.add_ai_message(final_text)
            return final_text

        else:
            # No tool call, use response as-is
            self.message_history.add_ai_message(response_text)
            return response_text

    def _parse_tool_call(self, response: str) -> Optional[Dict]:
        """Parse tool call from LLM response."""
        try:
            # Look for JSON object in response
            start = response.find("{")
            end = response.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)

                if "tool" in data and "params" in data:
                    return data

        except json.JSONDecodeError:
            pass

        return None

    async def _execute_tool(self, tool_name: str, params: Dict) -> ToolResult:
        """Execute a tool and return results."""
        try:
            if tool_name == "search":
                return await self._tool_search(params)
            elif tool_name == "summarize":
                return await self._tool_summarize(params)
            elif tool_name == "extract_references":
                return await self._tool_extract_references(params)
            elif tool_name == "find_related":
                return await self._tool_find_related(params)
            elif tool_name == "classify":
                return await self._tool_classify(params)
            elif tool_name == "analyze_collection":
                return await self._tool_analyze_collection(params)
            else:
                return ToolResult(
                    tool=AgentTool.SEARCH,
                    success=False,
                    data=None,
                    message=f"Unknown tool: {tool_name}"
                )

        except Exception as e:
            return ToolResult(
                tool=AgentTool.SEARCH,
                success=False,
                data=None,
                message=f"Tool execution error: {str(e)}"
            )

    async def _tool_search(self, params: Dict) -> ToolResult:
        """Execute search tool."""
        if not self.search_engine:
            return ToolResult(
                tool=AgentTool.SEARCH,
                success=False,
                data=None,
                message="Search engine not configured"
            )

        query = params.get("query", "")
        k = params.get("k", 5)

        results = await self.search_engine.search(query, k=k)

        data = [
            {
                "filename": r.metadata["filename"],
                "similarity": r.similarity_score,
                "preview": r.chunk_text[:200]
            }
            for r in results
        ]

        return ToolResult(
            tool=AgentTool.SEARCH,
            success=True,
            data=data,
            message=f"Found {len(results)} results"
        )

    async def _tool_summarize(self, params: Dict) -> ToolResult:
        """Execute summarize tool."""
        # Implementation depends on having a summarizer service
        return ToolResult(
            tool=AgentTool.SUMMARIZE,
            success=True,
            data={"summary": "Summary placeholder"},
            message="Summary generated"
        )

    async def _tool_extract_references(self, params: Dict) -> ToolResult:
        """Execute extract references tool."""
        # Implementation depends on having a reference extractor
        return ToolResult(
            tool=AgentTool.EXTRACT_REFS,
            success=True,
            data={"references": []},
            message="References extracted"
        )

    async def _tool_find_related(self, params: Dict) -> ToolResult:
        """Execute find related tool."""
        if not self.search_engine:
            return ToolResult(
                tool=AgentTool.FIND_RELATED,
                success=False,
                data=None,
                message="Search engine not configured"
            )

        document_path = Path(params.get("document_path", ""))
        k = params.get("k", 5)

        results = await self.search_engine.find_similar_documents(document_path, k=k)

        data = [
            {
                "filename": r.metadata["filename"],
                "similarity": r.similarity_score
            }
            for r in results
        ]

        return ToolResult(
            tool=AgentTool.FIND_RELATED,
            success=True,
            data=data,
            message=f"Found {len(results)} related papers"
        )

    async def _tool_classify(self, params: Dict) -> ToolResult:
        """Execute classify tool."""
        return ToolResult(
            tool=AgentTool.CLASSIFY,
            success=True,
            data={"topic": "Computer Science"},
            message="Document classified"
        )

    async def _tool_analyze_collection(self, params: Dict) -> ToolResult:
        """Execute analyze collection tool."""
        # Implementation would analyze the entire collection
        return ToolResult(
            tool=AgentTool.ANALYZE_COLLECTION,
            success=True,
            data={
                "total_documents": 100,
                "topics": {"AI": 40, "ML": 30, "NLP": 20, "CV": 10},
                "years": {"2024": 20, "2023": 30, "2022": 25, "2021": 15, "2020": 10}
            },
            message="Collection analyzed"
        )

    async def generate_literature_review(
        self,
        topic: str,
        directory: Path,
        max_papers: int = 20
    ) -> str:
        """
        Generate literature review for a topic.

        Args:
            topic: Research topic
            directory: Directory containing papers
            max_papers: Maximum number of papers to include

        Returns:
            Markdown-formatted literature review
        """
        if not self.search_engine:
            return "Error: Search engine not configured"

        # Search for relevant papers
        results = await self.search_engine.search(topic, k=max_papers)

        if not results:
            return f"No papers found on topic: {topic}"

        # Group by similarity
        high_relevance = [r for r in results if r.similarity_score > 0.8]
        medium_relevance = [r for r in results if 0.6 < r.similarity_score <= 0.8]

        # Generate review
        review = f"""# Literature Review: {topic}

## Overview
This literature review analyzes {len(results)} papers related to {topic}.

## High Relevance Papers ({len(high_relevance)} papers)

"""
        for i, result in enumerate(high_relevance, 1):
            review += f"""### {i}. {result.metadata.get('filename', 'Unknown')}

**Relevance:** {result.similarity_score:.2%}

**Key Content:**
{result.chunk_text[:500]}...

---

"""

        if medium_relevance:
            review += f"""## Additional Relevant Papers ({len(medium_relevance)} papers)

"""
            for result in medium_relevance:
                review += f"- {result.metadata.get('filename', 'Unknown')} (relevance: {result.similarity_score:.2%})\n"

        review += """
## Synthesis

[Auto-generated synthesis would go here based on LLM analysis of all papers]

## Future Directions

[Identified gaps and future research directions]

## References

[Formatted reference list]
"""

        return review

    def reset_conversation(self):
        """Clear conversation history."""
        self.message_history.clear()
        self.message_history.add_message(SystemMessage(content=self.system_prompt))

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history as list of dicts."""
        history = []
        for msg in self.message_history.messages:
            if isinstance(msg, SystemMessage):
                continue
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            history.append({"role": role, "content": msg.content})
        return history


# ============================================================================
# CLI Command Examples
# ============================================================================

async def interactive_chat():
    """Interactive chat mode."""
    from gideon.services.file_service import FileService
    from examples.ai_enhancements.semantic_search_example import SemanticSearchEngine

    # Initialize services
    search_engine = SemanticSearchEngine()
    file_service = FileService()

    # Create assistant
    assistant = ResearchAssistant(
        search_engine=search_engine,
        file_service=file_service
    )

    print("="*60)
    print("Gideon Research Assistant")
    print("="*60)
    print("\nI can help you explore your document collection.")
    print("Ask me questions, request searches, or ask for analysis.")
    print("\nCommands:")
    print("  /help    - Show available commands")
    print("  /reset   - Clear conversation history")
    print("  /history - Show conversation history")
    print("  /quit    - Exit")
    print("\n" + "="*60 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input == "/quit":
                print("Goodbye!")
                break
            elif user_input == "/help":
                print("""
Available capabilities:
- Search: "Find papers on neural networks"
- Summarize: "Summarize paper X"
- Related: "Find papers related to Y"
- Analyze: "Analyze my collection"
- Literature review: "Generate literature review on Z"
                """)
                continue
            elif user_input == "/reset":
                assistant.reset_conversation()
                print("Conversation history cleared.")
                continue
            elif user_input == "/history":
                history = assistant.get_conversation_history()
                for msg in history:
                    print(f"{msg['role'].capitalize()}: {msg['content'][:100]}...")
                continue

            # Get response
            response = await assistant.chat(user_input)
            print(f"\nGideon: {response}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


async def literature_review_command(topic: str, directory: Path, output: Path):
    """Generate literature review command."""
    from gideon.services.file_service import FileService
    from examples.ai_enhancements.semantic_search_example import SemanticSearchEngine

    search_engine = SemanticSearchEngine()
    assistant = ResearchAssistant(search_engine=search_engine)

    print(f"Generating literature review on: {topic}")

    review = await assistant.generate_literature_review(topic, directory)

    # Save to file
    output.write_text(review)

    print(f"\n✅ Literature review saved to: {output}")


# Example usage
if __name__ == "__main__":
    import asyncio

    # Interactive mode
    # asyncio.run(interactive_chat())

    # Generate literature review
    # asyncio.run(literature_review_command(
    #     topic="transformers in NLP",
    #     directory=Path("./documents"),
    #     output=Path("./review.md")
    # ))

    pass
