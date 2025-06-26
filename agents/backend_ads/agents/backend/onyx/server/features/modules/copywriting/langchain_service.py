"""
LangChain Integration Service

Advanced AI content generation using LangChain with support for:
- Multiple LLM providers
- Chains and agents 
- Vector stores and embeddings
- Memory and context management
- Tools and function calling
- Structured output parsing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
import time
from datetime import datetime

# LangChain imports
try:
    from langchain.llms import OpenAI, Anthropic
    from langchain.chat_models import ChatOpenAI, ChatAnthropic
    from langchain.chains import LLMChain, ConversationChain, SequentialChain
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.vectorstores import Chroma, FAISS
    from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.tools import DuckDuckGoSearchRun, WikipediaQueryRun
    from langchain.utilities import WikipediaAPIWrapper
    from langchain.callbacks import get_openai_callback
    from langchain.cache import InMemoryCache, SQLiteCache
    from langchain.globals import set_llm_cache
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from .config import CopywritingConfig, AIProviderConfig, ContentType, ContentTone
from .models import ContentRequest, GeneratedContent, ContentMetrics
from .exceptions import ContentGenerationError, ConfigurationError

logger = logging.getLogger(__name__)

class LangChainService:
    """Advanced LangChain service for AI content generation."""
    
    def __init__(self, config: CopywritingConfig, ai_config: AIProviderConfig):
        if not LANGCHAIN_AVAILABLE:
            raise ConfigurationError("LangChain is not installed. Install with: pip install langchain")
        
        self.config = config
        self.ai_config = ai_config
        
        # Initialize LangChain components
        self.llm = None
        self.chat_model = None
        self.memory = None
        self.chains = {}
        self.agents = {}
        self.vector_store = None
        self.embeddings = None
        self.tools = []
        
        # Performance tracking
        self.generation_count = 0
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain components."""
        try:
            # Setup caching
            if self.config.langchain_cache:
                set_llm_cache(InMemoryCache())
            
            # Initialize LLM based on configuration
            self._initialize_llm()
            
            # Initialize memory
            self._initialize_memory()
            
            # Initialize embeddings and vector store
            if self.ai_config.enable_vector_store:
                self._initialize_vector_store()
            
            # Initialize tools
            if self.ai_config.enable_langchain_tools:
                self._initialize_tools()
            
            # Initialize chains
            self._initialize_chains()
            
            # Initialize agents
            if self.ai_config.enable_langchain_agents:
                self._initialize_agents()
            
            logger.info("LangChain service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain service: {e}")
            raise ConfigurationError(f"LangChain initialization failed: {e}")
    
    def _initialize_llm(self):
        """Initialize the Language Model."""
        llm_type = self.ai_config.langchain_llm_type.lower()
        
        if llm_type == "openai":
            # Initialize OpenAI LLM
            if self.ai_config.openai_api_key:
                self.llm = OpenAI(
                    openai_api_key=self.ai_config.openai_api_key,
                    model_name=self.ai_config.langchain_model,
                    temperature=self.ai_config.langchain_temperature,
                    max_tokens=self.ai_config.langchain_max_tokens,
                    verbose=self.config.langchain_verbose
                )
                
                self.chat_model = ChatOpenAI(
                    openai_api_key=self.ai_config.openai_api_key,
                    model_name=self.ai_config.langchain_model,
                    temperature=self.ai_config.langchain_temperature,
                    max_tokens=self.ai_config.langchain_max_tokens,
                    verbose=self.config.langchain_verbose
                )
            else:
                raise ConfigurationError("OpenAI API key is required for LangChain OpenAI provider")
        
        elif llm_type == "anthropic":
            # Initialize Anthropic LLM
            if self.ai_config.anthropic_api_key:
                self.llm = Anthropic(
                    anthropic_api_key=self.ai_config.anthropic_api_key,
                    model=self.ai_config.anthropic_model,
                    max_tokens_to_sample=self.ai_config.langchain_max_tokens,
                    verbose=self.config.langchain_verbose
                )
            else:
                raise ConfigurationError("Anthropic API key is required for LangChain Anthropic provider")
        
        else:
            raise ConfigurationError(f"Unsupported LLM type: {llm_type}")
    
    def _initialize_memory(self):
        """Initialize conversation memory."""
        memory_type = self.ai_config.langchain_memory_type.lower()
        
        if memory_type == "buffer":
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        elif memory_type == "summary":
            self.memory = ConversationSummaryMemory(
                llm=self.llm,
                memory_key="chat_history",
                return_messages=True
            )
        else:
            self.memory = ConversationBufferMemory(memory_key="chat_history")
    
    def _initialize_vector_store(self):
        """Initialize vector store for embeddings and retrieval."""
        try:
            # Initialize embeddings
            if self.ai_config.openai_api_key:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=self.ai_config.openai_api_key
                )
            else:
                # Use HuggingFace embeddings as fallback
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            
            # Initialize vector store
            vector_store_type = self.ai_config.vector_store_type.lower()
            
            if vector_store_type == "chroma":
                self.vector_store = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory="./chroma_db"
                )
            elif vector_store_type == "faiss":
                self.vector_store = FAISS(
                    embedding_function=self.embeddings
                )
            
            logger.info(f"Vector store ({vector_store_type}) initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {e}")
            self.vector_store = None
    
    def _initialize_tools(self):
        """Initialize tools for agents."""
        try:
            # Web search tool
            search_tool = Tool(
                name="web_search",
                description="Search the web for current information",
                func=DuckDuckGoSearchRun().run
            )
            self.tools.append(search_tool)
            
            # Wikipedia tool
            wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
            wiki_tool = Tool(
                name="wikipedia",
                description="Search Wikipedia for factual information",
                func=wikipedia.run
            )
            self.tools.append(wiki_tool)
            
            # Content analysis tool
            def analyze_content_tool(content: str) -> str:
                """Analyze content for readability and engagement."""
                # Simplified analysis
                word_count = len(content.split())
                char_count = len(content)
                
                return f"Content Analysis: {word_count} words, {char_count} characters"
            
            analysis_tool = Tool(
                name="content_analyzer",
                description="Analyze content for quality metrics",
                func=analyze_content_tool
            )
            self.tools.append(analysis_tool)
            
            logger.info(f"Initialized {len(self.tools)} tools")
            
        except Exception as e:
            logger.warning(f"Failed to initialize some tools: {e}")
    
    def _initialize_chains(self):
        """Initialize LangChain chains for different content types."""
        
        # Content generation chain
        content_prompt = PromptTemplate(
            input_variables=["content_type", "audience", "message", "tone", "keywords"],
            template="""Create {content_type} content for {audience}.

Key Message: {message}
Tone: {tone}
Keywords to include: {keywords}

Requirements:
- Make it engaging and compelling
- Include the key message naturally
- Use the specified tone
- Incorporate keywords naturally
- Keep it appropriate for the target audience

Content:"""
        )
        
        self.chains["content_generation"] = LLMChain(
            llm=self.llm,
            prompt=content_prompt,
            verbose=self.config.langchain_verbose
        )
        
        # Content optimization chain
        optimization_prompt = PromptTemplate(
            input_variables=["original_content", "feedback"],
            template="""Optimize the following content based on the feedback:

Original Content:
{original_content}

Feedback:
{feedback}

Provide an improved version that addresses the feedback while maintaining the original message and style.

Optimized Content:"""
        )
        
        self.chains["content_optimization"] = LLMChain(
            llm=self.llm,
            prompt=optimization_prompt,
            verbose=self.config.langchain_verbose
        )
        
        # A/B variant generation chain
        variant_prompt = PromptTemplate(
            input_variables=["original_content", "variation_type"],
            template="""Create a {variation_type} variation of the following content:

Original Content:
{original_content}

Create a variation that:
- Maintains the same core message
- Uses a different approach or angle
- Could be tested against the original
- Is equally compelling but different

Variation:"""
        )
        
        self.chains["variant_generation"] = LLMChain(
            llm=self.llm,
            prompt=variant_prompt,
            verbose=self.config.langchain_verbose
        )
        
        # Conversation chain with memory
        self.chains["conversation"] = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=self.config.langchain_verbose
        )
        
        logger.info(f"Initialized {len(self.chains)} chains")
    
    def _initialize_agents(self):
        """Initialize LangChain agents."""
        if not self.tools:
            logger.warning("No tools available for agents")
            return
        
        try:
            # Content research agent
            self.agents["research"] = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=self.config.langchain_verbose,
                max_iterations=3
            )
            
            logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            logger.warning(f"Failed to initialize agents: {e}")
    
    async def generate_content(self, request: ContentRequest) -> GeneratedContent:
        """Generate content using LangChain."""
        start_time = time.perf_counter()
        
        try:
            # Prepare input variables
            chain_inputs = {
                "content_type": request.content_type.value,
                "audience": request.target_audience,
                "message": request.key_message,
                "tone": request.tone.value,
                "keywords": ", ".join(request.keywords) if request.keywords else "None"
            }
            
            # Generate content using appropriate chain
            with get_openai_callback() as cb:
                if self.ai_config.langchain_chain_type == "conversation" and "conversation" in self.chains:
                    # Use conversation chain for contextual generation
                    prompt = f"Generate {request.content_type.value} content for {request.target_audience}. Message: {request.key_message}. Tone: {request.tone.value}."
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, self.chains["conversation"].predict, input=prompt
                    )
                else:
                    # Use content generation chain
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, self.chains["content_generation"].run, chain_inputs
                    )
                
                # Track token usage and cost
                self.total_tokens_used += cb.total_tokens
                self.total_cost += cb.total_cost
            
            # Generate alternatives using variant chain
            alternatives = await self._generate_alternatives(result, request)
            
            # Analyze content quality
            metrics = await self._analyze_content_quality(result, request.keywords)
            
            generation_time = (time.perf_counter() - start_time) * 1000
            self.generation_count += 1
            
            return GeneratedContent(
                content=result.strip(),
                content_type=request.content_type,
                tone=request.tone,
                language=request.language,
                request_params=request.dict(),
                metrics=metrics,
                alternatives=alternatives,
                generation_time_ms=generation_time,
                model_used=self.ai_config.langchain_model,
                provider_used="langchain",
                confidence_score=metrics.engagement_prediction if metrics else 0.7
            )
            
        except Exception as e:
            logger.error(f"LangChain content generation failed: {e}")
            raise ContentGenerationError(f"LangChain generation failed: {e}")
    
    async def _generate_alternatives(self, original_content: str, request: ContentRequest) -> List[str]:
        """Generate alternative versions using LangChain."""
        alternatives = []
        
        if "variant_generation" not in self.chains:
            return alternatives
        
        try:
            # Generate different types of variations
            variation_types = ["creative", "professional", "concise"]
            
            for variation_type in variation_types[:2]:  # Limit to 2 alternatives
                try:
                    variant = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.chains["variant_generation"].run,
                        {
                            "original_content": original_content,
                            "variation_type": variation_type
                        }
                    )
                    if variant.strip() and variant != original_content:
                        alternatives.append(variant.strip())
                except Exception as e:
                    logger.warning(f"Failed to generate {variation_type} variant: {e}")
            
        except Exception as e:
            logger.warning(f"Failed to generate alternatives: {e}")
        
        return alternatives
    
    async def _analyze_content_quality(self, content: str, keywords: List[str] = None) -> ContentMetrics:
        """Analyze content quality using LangChain and built-in metrics."""
        try:
            # Basic metrics
            word_count = len(content.split())
            character_count = len(content)
            reading_time = word_count / 200  # Average reading speed
            
            # Keyword density
            keyword_density = {}
            if keywords:
                content_lower = content.lower()
                for keyword in keywords:
                    count = content_lower.count(keyword.lower())
                    density = (count / word_count) * 100 if word_count > 0 else 0
                    keyword_density[keyword] = density
            
            # Emotional triggers (simplified)
            emotional_words = {
                'urgency': ['now', 'limited', 'hurry', 'fast', 'urgent'],
                'social_proof': ['popular', 'trending', 'trusted', 'proven'],
                'emotion': ['amazing', 'incredible', 'love', 'excited']
            }
            
            emotional_triggers = []
            content_lower = content.lower()
            for category, words in emotional_words.items():
                if any(word in content_lower for word in words):
                    emotional_triggers.append(category)
            
            # Calculate engagement prediction (simplified)
            engagement_factors = [
                min(1.0, word_count / 50),  # Optimal length factor
                len(emotional_triggers) * 0.2,  # Emotional trigger factor
                min(1.0, sum(keyword_density.values()) / 100),  # Keyword optimization
            ]
            engagement_prediction = min(0.95, sum(engagement_factors) / len(engagement_factors))
            
            return ContentMetrics(
                readability_score=75.0,  # Would use actual readability analysis
                sentiment_score=0.7,     # Would use sentiment analysis
                engagement_prediction=engagement_prediction,
                word_count=word_count,
                character_count=character_count,
                reading_time_minutes=reading_time,
                keyword_density=keyword_density,
                emotional_triggers=emotional_triggers,
                call_to_action_strength=0.8,  # Would analyze CTA strength
                urgency_score=0.6,
                credibility_score=0.8
            )
            
        except Exception as e:
            logger.warning(f"Content analysis failed: {e}")
            return ContentMetrics()
    
    async def optimize_content(self, content: str, feedback: str) -> str:
        """Optimize content based on feedback using LangChain."""
        if "content_optimization" not in self.chains:
            return content
        
        try:
            optimized = await asyncio.get_event_loop().run_in_executor(
                None,
                self.chains["content_optimization"].run,
                {
                    "original_content": content,
                    "feedback": feedback
                }
            )
            return optimized.strip()
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return content
    
    async def research_topic(self, topic: str) -> Dict[str, Any]:
        """Research a topic using LangChain agents and tools."""
        if "research" not in self.agents:
            return {"error": "Research agent not available"}
        
        try:
            research_query = f"Research the topic: {topic}. Provide key facts, trends, and insights."
            
            research_result = await asyncio.get_event_loop().run_in_executor(
                None,
                self.agents["research"].run,
                research_query
            )
            
            return {
                "topic": topic,
                "research": research_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Topic research failed: {e}")
            return {"error": str(e)}
    
    async def add_to_knowledge_base(self, content: str, metadata: Dict[str, Any] = None):
        """Add content to vector store knowledge base."""
        if not self.vector_store:
            logger.warning("Vector store not available")
            return
        
        try:
            # Split content into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_text(content)
            
            # Add to vector store
            metadatas = [metadata or {} for _ in chunks]
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.vector_store.add_texts,
                chunks,
                metadatas
            )
            
            logger.info(f"Added {len(chunks)} chunks to knowledge base")
            
        except Exception as e:
            logger.error(f"Failed to add content to knowledge base: {e}")
    
    async def search_knowledge_base(self, query: str, k: int = 5) -> List[str]:
        """Search the knowledge base for relevant content."""
        if not self.vector_store:
            return []
        
        try:
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.vector_store.similarity_search,
                query,
                k
            )
            
            return [doc.page_content for doc in results]
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get LangChain service performance statistics."""
        return {
            "generation_count": self.generation_count,
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
            "average_cost_per_generation": self.total_cost / max(1, self.generation_count),
            "chains_available": list(self.chains.keys()),
            "agents_available": list(self.agents.keys()),
            "tools_available": [tool.name for tool in self.tools],
            "vector_store_enabled": self.vector_store is not None,
            "memory_type": self.ai_config.langchain_memory_type
        }
    
    async def cleanup(self):
        """Cleanup LangChain resources."""
        try:
            # Persist vector store if applicable
            if hasattr(self.vector_store, 'persist'):
                self.vector_store.persist()
            
            logger.info("LangChain service cleanup completed")
            
        except Exception as e:
            logger.error(f"LangChain cleanup failed: {e}")


def create_langchain_service(config: CopywritingConfig, ai_config: AIProviderConfig) -> Optional[LangChainService]:
    """Factory function to create LangChain service."""
    try:
        if not config.enable_langchain or not LANGCHAIN_AVAILABLE:
            return None
        
        return LangChainService(config, ai_config)
        
    except Exception as e:
        logger.error(f"Failed to create LangChain service: {e}")
        return None 