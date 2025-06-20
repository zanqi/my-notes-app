"""
LangGraph RAG Service - Handles AI chat functionality with context retrieval using LangGraph
"""

import os
import logging
from typing import List, Dict, Any, Optional, TypedDict
import uuid
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import START, END, StateGraph
from pydantic import SecretStr

from ..models.chat_models import ChatResponse, Source, ConversationMessage
from .vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """
    Represents the state of the graph.
    
    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to use web search
        documents: list of documents
    """
    question: str
    generation: str
    web_search: str
    documents: List[Any]


class LangGraphRAGService:
    """Service for handling RAG-based AI conversations using LangGraph"""
    
    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service
        self.llm = None
        self.retrieval_grader = None
        self.rag_chain = None
        self.hallucination_grader = None
        self.answer_grader = None
        self.web_search_tool = None
        self.graph = None
        self.conversations = {}  # In-memory conversation storage
        self.max_context_notes = 5
        self.conversation_window = 10  # Keep last 10 messages
        
    async def initialize(self):
        """Initialize the LangGraph RAG service"""
        try:
            # Initialize OpenAI LLM
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            
            model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            
            self.llm = ChatOpenAI(
                api_key=SecretStr(api_key),
                model=model_name,
                temperature=temperature
            )
            
            # Initialize components
            self._initialize_retrieval_grader()
            self._initialize_rag_chain()
            self._initialize_hallucination_grader()
            self._initialize_answer_grader()
            self._initialize_web_search()
            self._build_graph()
            
            logger.info(f"LangGraph RAG service initialized with model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangGraph RAG service: {e}")
            raise
    
    def _initialize_retrieval_grader(self):
        """Initialize retrieval grader"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        llm_json = ChatOpenAI(
            api_key=SecretStr(api_key),
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=0
        )
        
        prompt = PromptTemplate(
            template="""You are a grader assessing relevance of a retrieved document to a user question. 
            Here is the retrieved document: 

            {document} 

            Here is the user question: {question} 

            If the document contains keywords related to the user question, grade it as relevant. 

            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. 

            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. 

            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
            """,
            input_variables=["question", "document"],
        )
        
        self.retrieval_grader = prompt | llm_json | JsonOutputParser()
    
    def _initialize_rag_chain(self):
        """Initialize RAG chain"""
        prompt = PromptTemplate(
            template="""You are an assistant for question-answering tasks. 
            
            Use the following documents to answer the question. 
            
            If you don't know the answer, just say that you don't know.
            
            Use three sentences maximum and keep the answer concise.
            Question: {question}
            Documents: {documents}
            Answer: 
            """,
            input_variables=["question", "documents"],
        )
        
        self.rag_chain = prompt | self.llm | StrOutputParser()
    
    def _initialize_hallucination_grader(self):
        """Initialize hallucination grader"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        llm_json = ChatOpenAI(
            api_key=SecretStr(api_key),
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=0
        )
        
        prompt = PromptTemplate(
            template="""You are a grader assessing whether an answer is grounded in / supported by a set of facts. 
            Here are the facts:
             ------- 

            {documents} 
             ------- 

            Here is the answer: {generation}
            Give a binary score 'yes' or 'no' score to indicate whether the answer is grounded in / supported by a set of facts. 

            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
            input_variables=["generation", "documents"],
        )
        
        self.hallucination_grader = prompt | llm_json | JsonOutputParser()
    
    def _initialize_answer_grader(self):
        """Initialize answer grader"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        llm_json = ChatOpenAI(
            api_key=SecretStr(api_key),
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=0
        )
        
        prompt = PromptTemplate(
            template="""You are a grader assessing whether an answer is useful to resolve a question. 
            Here is the answer:
             ------- 

            {generation} 
             ------- 

            Here is the question: {question}
            Give a binary score 'yes' or 'no' to indicate whether the answer is useful to resolve a question. 

            Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
            input_variables=["generation", "question"],
        )
        
        self.answer_grader = prompt | llm_json | JsonOutputParser()
    
    def _initialize_web_search(self):
        """Initialize web search tool"""
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if tavily_api_key:
            self.web_search_tool = TavilySearchResults(k=3)
        else:
            logger.warning("TAVILY_API_KEY not found, web search will be disabled")
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("grade_documents", self._grade_documents)
        workflow.add_node("generate", self._generate)
        workflow.add_node("search_web", self._web_search)
        
        # Add edges
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self._decide_to_generate,
            {"generate": "generate", "search_web": "search_web"},
        )
        workflow.add_edge("search_web", "generate")
        workflow.add_conditional_edges(
            "generate",
            self._decide_to_regenerate,
            {"useful": END, "not useful": "search_web", "not grounded": "generate"},
        )
        
        self.graph = workflow.compile()
    
    def _retrieve(self, state):
        """Retrieve documents"""
        print("---RETRIEVE---")
        question = state["question"]
        
        # Retrieval - use thread-based approach for async method
        import asyncio
        import threading
        import concurrent.futures
        
        def run_async_search():
            """Run the async search in a new event loop"""
            return asyncio.run(
                self.vector_store_service.search_similar_notes(
                    query=question, 
                    n_results=self.max_context_notes
                )
            )
        
        try:
            # Use thread executor to run the async function
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async_search)
                documents = future.result(timeout=10)  # 10 second timeout
        except Exception as e:
            print(f"Warning: Could not retrieve documents: {e}")
            documents = []
        
        return {"documents": documents, "question": question}
    
    def _grade_documents(self, state):
        """Grade retrieved documents for relevance"""
        print("---GRADE DOCUMENTS---")
        question = state["question"]
        documents = state["documents"]
        
        filtered_docs = []
        search = "No"
        
        for doc in documents:
            score = self.retrieval_grader.invoke({
                "question": question, 
                "document": doc.content_snippet if hasattr(doc, 'content_snippet') else str(doc)
            })
            grade = score["score"]
            
            if grade == "yes":
                filtered_docs.append(doc)
            else:
                search = "Yes"
                continue
        
        return {
            "documents": filtered_docs,
            "question": question,
            "web_search": search,
        }
    
    def _web_search(self, state):
        """Web search for additional context"""
        print("---WEB SEARCH---")
        question = state["question"]
        documents = state.get("documents", [])
        
        if self.web_search_tool:
            web_results = self.web_search_tool.invoke({"query": question})
            # Convert web results to Source objects
            for i, result in enumerate(web_results):
                # Calculate relevance score based on search result ranking and available score
                # Tavily returns results ranked by relevance, so first result is most relevant
                base_score = max(0.95 - (i * 0.15), 0.65)  # 95%, 80%, 65% for top 3 results
                
                # Use Tavily's score if available, otherwise use ranking-based score
                tavily_score = result.get("score", base_score)
                if isinstance(tavily_score, (int, float)) and 0 <= tavily_score <= 1:
                    relevance_score = tavily_score
                else:
                    relevance_score = base_score
                
                web_source = Source(
                    note_id=-1 - i,  # Use negative IDs for web results to distinguish from notes
                    title=result.get("title", "Web Result"),
                    content_snippet=result.get("content", ""),
                    relevance_score=relevance_score,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                documents.append(web_source)
        
        return {"documents": documents, "question": question}
    
    def _generate(self, state):
        """Generate answer"""
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]
        
        # Format documents for the prompt
        formatted_docs = []
        for doc in documents:
            if hasattr(doc, 'content_snippet'):
                formatted_docs.append({"page_content": doc.content_snippet})
            else:
                formatted_docs.append({"page_content": str(doc)})
        
        generation = self.rag_chain.invoke({
            "documents": formatted_docs, 
            "question": question
        })
        
        return {
            "documents": documents,
            "question": question,
            "generation": generation,
        }
    
    def _decide_to_generate(self, state):
        """Decide whether to generate or search web"""
        search = state["web_search"]
        if search == "Yes":
            return "search_web"
        else:
            return "generate"
    
    def _decide_to_regenerate(self, state):
        """Decide whether to regenerate answer"""
        question = state["question"]
        generation = state["generation"]
        documents = state["documents"]
        
        # Format documents for grading
        formatted_docs = []
        for doc in documents:
            if hasattr(doc, 'content_snippet'):
                formatted_docs.append({"page_content": doc.content_snippet})
            else:
                formatted_docs.append({"page_content": str(doc)})
        
        # Check if grounded
        score = self.hallucination_grader.invoke({
            "documents": formatted_docs, 
            "generation": generation
        })
        
        if score["score"] == "yes":
            # Check if useful
            score = self.answer_grader.invoke({
                "question": question, 
                "generation": generation
            })
            if score["score"] == "yes":
                return "useful"
            return "not useful"
        else:
            return "not grounded"
    
    def _format_docs(self, docs: List[Source]) -> List[Dict[str, str]]:
        """Format documents for prompt"""
        return [{"page_content": doc.content_snippet} for doc in docs]
    
    def _get_or_create_conversation(self, conversation_id: Optional[str]) -> str:
        """Get existing conversation or create new one"""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "messages": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        
        return conversation_id
    
    def _add_message_to_conversation(self, conversation_id: str, role: str, content: str, sources: Optional[List[Source]] = None):
        """Add a message to conversation history"""
        if conversation_id in self.conversations:
            message = ConversationMessage(
                role=role,
                content=content,
                timestamp=datetime.now(),
                sources=sources or []
            )
            
            self.conversations[conversation_id]["messages"].append(message)
            self.conversations[conversation_id]["updated_at"] = datetime.now()
            
            # Keep only recent messages to prevent memory overflow
            if len(self.conversations[conversation_id]["messages"]) > self.conversation_window * 2:
                self.conversations[conversation_id]["messages"] = \
                    self.conversations[conversation_id]["messages"][-self.conversation_window * 2:]
    
    async def chat(self, message: str, conversation_id: Optional[str] = None, include_sources: bool = True) -> ChatResponse:
        """Handle a chat request with LangGraph RAG"""
        try:
            # Get or create conversation
            conv_id = self._get_or_create_conversation(conversation_id)
            
            # Add user message to conversation
            self._add_message_to_conversation(conv_id, "user", message)
            
            # Run the graph
            inputs = {"question": message}
            result = self.graph.invoke(inputs)
            
            generation = result["generation"]
            sources = result.get("documents", [])
            
            # Add assistant response to conversation
            self._add_message_to_conversation(conv_id, "assistant", generation, sources)
            
            # Calculate tokens used (approximate)
            total_text = message + generation
            tokens_used = len(total_text.split()) * 1.3  # Rough estimate
            
            return ChatResponse(
                response=generation,
                conversation_id=conv_id,
                sources=sources,
                timestamp=datetime.now(),
                tokens_used=int(tokens_used)
            )
            
        except Exception as e:
            logger.error(f"LangGraph chat request failed: {e}")
            raise
    
    async def get_conversation_history(self, conversation_id: str) -> List[ConversationMessage]:
        """Get conversation history"""
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]["messages"]
        return []
    
    async def clear_conversation(self, conversation_id: str):
        """Clear a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation {conversation_id}")
    
    async def get_all_conversations(self) -> Dict[str, Any]:
        """Get all conversation IDs and metadata"""
        result = {}
        for conv_id, conv_data in self.conversations.items():
            result[conv_id] = {
                "created_at": conv_data["created_at"],
                "updated_at": conv_data["updated_at"],
                "message_count": len(conv_data["messages"])
            }
        return result
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv["messages"]) for conv in self.conversations.values())
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "max_context_notes": self.max_context_notes,
            "conversation_window": self.conversation_window,
            "model": getattr(self.llm, 'model_name', 'Unknown') if self.llm else 'Not initialized',
            "service_type": "langgraph"
        } 