"""
🎯 Facebook LangChain Service
=============================

Servicio LangChain especializado para Facebook posts integrado con Onyx.
Incluye chains, agents, memory y herramientas específicas para Facebook.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import time
from datetime import datetime, timedelta

# LangChain imports
try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import LLMChain, SequentialChain
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.callbacks import get_openai_callback
    from langchain.tools import DuckDuckGoSearchRun
    from langchain.utilities import GoogleSearchAPIWrapper
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chains import RetrievalQA
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Onyx imports
from ...llm.factory import get_default_llm_provider
from ..config.langchain_config import FacebookLangChainConfig

logger = logging.getLogger(__name__)


class FacebookLangChainService:
    """Servicio LangChain especializado para Facebook posts."""
    
    def __init__(self, config: FacebookLangChainConfig):
        self.config = config
        self.llm = None
        self.chat_model = None
        self.memory = None
        self.tools = []
        self.chains = {}
        self.agents = {}
        self.vector_store = None
        
        # Metrics
        self.metrics = {
            'total_generations': 0,
            'total_analyses': 0,
            'total_tokens_used': 0,
            'total_cost': 0.0,
            'avg_generation_time': 0.0,
            'langchain_errors': 0
        }
        
        self.logger = logger
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar el servicio LangChain."""
        try:
            if not LANGCHAIN_AVAILABLE:
                raise ImportError("LangChain not available")
            
            self.logger.info("Initializing Facebook LangChain Service...")
            
            # Initialize LLM
            self._initialize_llm()
            
            # Initialize memory
            self._initialize_memory()
            
            # Initialize tools
            self._initialize_tools()
            
            # Initialize chains
            self._initialize_chains()
            
            # Initialize agents
            self._initialize_agents()
            
            # Initialize vector store
            if self.config.enable_vector_store:
                self._initialize_vector_store()
            
            self.logger.info("Facebook LangChain Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LangChain service: {e}")
            self.metrics['langchain_errors'] += 1
            raise
    
    def _initialize_llm(self):
        """Inicializar LLM con integración Onyx."""
        try:
            # Try to use Onyx LLM provider first
            if hasattr(self.config, 'use_onyx_llm') and self.config.use_onyx_llm:
                try:
                    from ...llm.factory import get_default_llm_provider
                    onyx_provider = get_default_llm_provider()
                    
                    # Adapt Onyx LLM to LangChain interface
                    self.llm = self._adapt_onyx_llm(onyx_provider)
                    self.chat_model = self.llm
                    self.logger.info("Using Onyx LLM provider")
                    return
                except Exception as e:
                    self.logger.warning(f"Could not use Onyx LLM: {e}")
            
            # Fallback to OpenAI
            if self.config.openai_api_key:
                self.llm = OpenAI(
                    openai_api_key=self.config.openai_api_key,
                    model_name=self.config.model_name,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    verbose=self.config.verbose
                )
                
                self.chat_model = ChatOpenAI(
                    openai_api_key=self.config.openai_api_key,
                    model_name=self.config.chat_model_name,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    verbose=self.config.verbose
                )
                
                self.logger.info(f"Using OpenAI models: {self.config.model_name}")
            else:
                raise ValueError("No API key provided for LLM initialization")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _adapt_onyx_llm(self, onyx_provider):
        """Adaptar Onyx LLM para LangChain."""
        # This would be a custom adapter to make Onyx LLM compatible with LangChain
        # For now, we'll use OpenAI as fallback
        class OnyxLLMAdapter:
            def __init__(self, onyx_provider):
                self.onyx_provider = onyx_provider
            
            async def agenerate(self, prompts: List[str], **kwargs) -> Any:
                # Implement async generation using Onyx provider
                results = []
                for prompt in prompts:
                    result = await self.onyx_provider.generate(prompt, **kwargs)
                    results.append(result)
                return results
        
        return OnyxLLMAdapter(onyx_provider)
    
    def _initialize_memory(self):
        """Inicializar memoria conversacional."""
        if self.config.use_memory:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                max_token_limit=self.config.memory_max_tokens
            )
            self.logger.info("Memory initialized")
    
    def _initialize_tools(self):
        """Inicializar herramientas para agents."""
        if not self.config.enable_tools:
            return
        
        try:
            # Web search tool
            if self.config.enable_web_search:
                try:
                    search_tool = DuckDuckGoSearchRun()
                    self.tools.append(
                        Tool(
                            name="Web Search",
                            description="Search the web for current trends and information",
                            func=search_tool.run
                        )
                    )
                except Exception as e:
                    self.logger.warning(f"Could not initialize web search: {e}")
            
            # Facebook trends tool (simulated)
            self.tools.append(
                Tool(
                    name="Facebook Trends",
                    description="Get current Facebook trends and hashtags",
                    func=self._get_facebook_trends
                )
            )
            
            # Engagement predictor tool
            self.tools.append(
                Tool(
                    name="Engagement Predictor",
                    description="Predict engagement for Facebook content",
                    func=self._predict_engagement
                )
            )
            
            # Hashtag generator tool
            self.tools.append(
                Tool(
                    name="Hashtag Generator",
                    description="Generate relevant hashtags for content",
                    func=self._generate_hashtags
                )
            )
            
            self.logger.info(f"Initialized {len(self.tools)} tools")
            
        except Exception as e:
            self.logger.error(f"Error initializing tools: {e}")
    
    def _initialize_chains(self):
        """Inicializar cadenas de LangChain."""
        try:
            # Facebook post generation chain
            post_prompt = PromptTemplate(
                input_variables=[
                    "topic", "tone", "audience", "max_length", 
                    "include_hashtags", "include_emoji", "keywords"
                ],
                template="""
                Create a Facebook post about {topic}.
                
                Requirements:
                - Tone: {tone}
                - Target audience: {audience}
                - Maximum length: {max_length} characters
                - Include hashtags: {include_hashtags}
                - Include emojis: {include_emoji}
                - Keywords to include: {keywords}
                
                The post should be engaging, authentic, and optimized for Facebook's algorithm.
                If hashtags are requested, include 3-5 relevant hashtags.
                If emojis are requested, use them naturally within the text.
                
                Facebook Post:
                """
            )
            
            self.chains['facebook_post'] = LLMChain(
                llm=self.llm,
                prompt=post_prompt,
                verbose=self.config.verbose
            )
            
            # Post analysis chain
            analysis_prompt = PromptTemplate(
                input_variables=["content", "context"],
                template="""
                Analyze this Facebook post for engagement potential:
                
                Content: {content}
                Context: {context}
                
                Provide analysis in JSON format with:
                - engagement_prediction (0.0-1.0)
                - virality_score (0.0-1.0)
                - sentiment_score (0.0-1.0)
                - readability_score (0.0-1.0)
                - brand_alignment (0.0-1.0)
                - predicted_likes (number)
                - predicted_shares (number)
                - predicted_comments (number)
                - predicted_reach (number)
                - strengths (list of strings)
                - improvements (list of strings)
                - hashtag_suggestions (list of strings)
                
                Analysis:
                """
            )
            
            self.chains['post_analysis'] = LLMChain(
                llm=self.llm,
                prompt=analysis_prompt,
                verbose=self.config.verbose
            )
            
            # Recommendations chain
            recommendations_prompt = PromptTemplate(
                input_variables=["content", "analysis_data"],
                template="""
                Based on this Facebook post and its analysis, provide actionable recommendations:
                
                Post: {content}
                Analysis: {analysis_data}
                
                Provide specific, actionable recommendations to improve the post's performance.
                Format as a JSON list of recommendation strings.
                
                Recommendations:
                """
            )
            
            self.chains['recommendations'] = LLMChain(
                llm=self.llm,
                prompt=recommendations_prompt,
                verbose=self.config.verbose
            )
            
            # Timing optimization chain
            timing_prompt = PromptTemplate(
                input_variables=["content_data"],
                template="""
                Predict the optimal posting time for this Facebook content:
                
                Content Data: {content_data}
                
                Consider:
                - Target audience demographics
                - Content type and tone
                - Day of week and time of day patterns
                - Engagement patterns for similar content
                
                Provide optimal posting time as ISO format datetime string.
                
                Optimal Time:
                """
            )
            
            self.chains['timing'] = LLMChain(
                llm=self.llm,
                prompt=timing_prompt,
                verbose=self.config.verbose
            )
            
            self.logger.info(f"Initialized {len(self.chains)} chains")
            
        except Exception as e:
            self.logger.error(f"Error initializing chains: {e}")
    
    def _initialize_agents(self):
        """Inicializar agentes si están habilitados."""
        if not self.config.enable_agents or not self.tools:
            return
        
        try:
            # Facebook content optimization agent
            self.agents['content_optimizer'] = initialize_agent(
                tools=self.tools,
                llm=self.chat_model,
                agent=AgentType.OPENAI_FUNCTIONS,
                memory=self.memory,
                verbose=self.config.verbose,
                max_iterations=3,
                early_stopping_method="generate"
            )
            
            self.logger.info("Agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing agents: {e}")
    
    def _initialize_vector_store(self):
        """Inicializar vector store para knowledge base."""
        try:
            if self.config.openai_api_key:
                embeddings = OpenAIEmbeddings(
                    openai_api_key=self.config.openai_api_key
                )
                
                # Initialize empty FAISS vector store
                self.vector_store = FAISS.from_texts(
                    ["Facebook post knowledge base initialized"],
                    embeddings
                )
                
                self.logger.info("Vector store initialized")
                
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {e}")
    
    async def generate_facebook_post(self, prompt_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generar Facebook post usando LangChain."""
        start_time = time.perf_counter()
        
        try:
            self.logger.info("Generating Facebook post with LangChain")
            
            # Use agent if available and enabled
            if self.config.enable_agents and 'content_optimizer' in self.agents:
                agent_prompt = f"""
                Create an engaging Facebook post about {prompt_context['topic']}.
                Tone: {prompt_context['tone']}
                Audience: {prompt_context['audience']}
                Max length: {prompt_context['max_length']} characters
                Include hashtags: {prompt_context['include_hashtags']}
                Include emoji: {prompt_context['include_emoji']}
                Keywords: {', '.join(prompt_context.get('keywords', []))}
                
                Use your tools to research trends and optimize the content.
                """
                
                with get_openai_callback() as cb:
                    result = await self._run_agent_async(
                        self.agents['content_optimizer'], 
                        agent_prompt
                    )
                
                token_usage = {
                    'total_tokens': cb.total_tokens,
                    'total_cost': cb.total_cost
                }
            else:
                # Use chain for generation
                with get_openai_callback() as cb:
                    result = await self._run_chain_async(
                        self.chains['facebook_post'],
                        prompt_context
                    )
                
                token_usage = {
                    'total_tokens': cb.total_tokens,
                    'total_cost': cb.total_cost
                }
            
            # Update metrics
            generation_time = (time.perf_counter() - start_time) * 1000
            self.metrics['total_generations'] += 1
            self.metrics['total_tokens_used'] += token_usage['total_tokens']
            self.metrics['total_cost'] += token_usage['total_cost']
            self.metrics['avg_generation_time'] = (
                (self.metrics['avg_generation_time'] * (self.metrics['total_generations'] - 1) + generation_time) /
                self.metrics['total_generations']
            )
            
            return {
                'content': result,
                'metadata': {
                    'generation_time_ms': generation_time,
                    'tokens_used': token_usage['total_tokens'],
                    'cost': token_usage['total_cost'],
                    'model': self.config.model_name,
                    'used_agent': self.config.enable_agents
                },
                'metrics': token_usage
            }
            
        except Exception as e:
            self.logger.error(f"Error generating Facebook post: {e}")
            self.metrics['langchain_errors'] += 1
            raise
    
    async def analyze_facebook_post(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar Facebook post usando LangChain."""
        try:
            self.logger.info("Analyzing Facebook post with LangChain")
            
            context_str = str(context)
            
            with get_openai_callback() as cb:
                result = await self._run_chain_async(
                    self.chains['post_analysis'],
                    {'content': content, 'context': context_str}
                )
            
            # Update metrics
            self.metrics['total_analyses'] += 1
            self.metrics['total_tokens_used'] += cb.total_tokens
            self.metrics['total_cost'] += cb.total_cost
            
            # Parse JSON result
            try:
                import json
                analysis_data = json.loads(result)
            except json.JSONDecodeError:
                # Fallback to basic analysis
                analysis_data = self._create_basic_analysis(content)
            
            return analysis_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing Facebook post: {e}")
            self.metrics['langchain_errors'] += 1
            return self._create_basic_analysis(content)
    
    async def get_post_recommendations(self, content: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener recomendaciones para el post."""
        try:
            self.logger.info("Getting post recommendations with LangChain")
            
            with get_openai_callback() as cb:
                result = await self._run_chain_async(
                    self.chains['recommendations'],
                    {
                        'content': content,
                        'analysis_data': str(analysis_data)
                    }
                )
            
            # Update metrics
            self.metrics['total_tokens_used'] += cb.total_tokens
            self.metrics['total_cost'] += cb.total_cost
            
            try:
                import json
                recommendations = json.loads(result)
                return {'recommendations': recommendations}
            except json.JSONDecodeError:
                return {'recommendations': [result]}
                
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return {'recommendations': ['Error generating recommendations']}
    
    async def predict_optimal_timing(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predecir tiempo óptimo de publicación."""
        try:
            self.logger.info("Predicting optimal timing with LangChain")
            
            with get_openai_callback() as cb:
                result = await self._run_chain_async(
                    self.chains['timing'],
                    {'content_data': str(content_data)}
                )
            
            # Update metrics
            self.metrics['total_tokens_used'] += cb.total_tokens
            self.metrics['total_cost'] += cb.total_cost
            
            # Parse datetime
            try:
                from datetime import datetime
                optimal_time = datetime.fromisoformat(result.strip())
                return {'optimal_time': optimal_time}
            except (ValueError, AttributeError):
                # Fallback to default optimal time (2 PM today)
                default_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
                return {'optimal_time': default_time}
                
        except Exception as e:
            self.logger.error(f"Error predicting optimal timing: {e}")
            return {'optimal_time': None}
    
    async def _run_chain_async(self, chain, inputs):
        """Ejecutar cadena de forma asíncrona."""
        # LangChain chains are not natively async, so we run them in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, chain.run, inputs)
    
    async def _run_agent_async(self, agent, prompt):
        """Ejecutar agente de forma asíncrona."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, agent.run, prompt)
    
    def _create_basic_analysis(self, content: str) -> Dict[str, Any]:
        """Crear análisis básico cuando LangChain falla."""
        return {
            'engagement_prediction': 0.5,
            'virality_score': 0.3,
            'sentiment_score': 0.5,
            'readability_score': 0.7,
            'brand_alignment': 0.6,
            'predicted_likes': 100,
            'predicted_shares': 20,
            'predicted_comments': 15,
            'predicted_reach': 1000,
            'strengths': ['Content generated successfully'],
            'improvements': ['Analysis limited due to service issues'],
            'hashtag_suggestions': ['#socialmedia', '#content', '#facebook']
        }
    
    # Tool functions
    def _get_facebook_trends(self, query: str) -> str:
        """Obtener tendencias de Facebook (simulado)."""
        # In a real implementation, this would call Facebook's API
        trends = [
            "#TrendingNow", "#ViralContent", "#FacebookTips",
            "#SocialMedia", "#DigitalMarketing", "#ContentCreator"
        ]
        return f"Current Facebook trends: {', '.join(trends)}"
    
    def _predict_engagement(self, content: str) -> str:
        """Predecir engagement (simulado)."""
        # Basic heuristics for engagement prediction
        words = len(content.split())
        has_question = '?' in content
        has_emoji = any(ord(char) > 127 for char in content)
        
        score = 0.5
        if words < 50:
            score += 0.1
        if has_question:
            score += 0.2
        if has_emoji:
            score += 0.1
        
        return f"Predicted engagement score: {min(score, 1.0):.2f}"
    
    def _generate_hashtags(self, content: str) -> str:
        """Generar hashtags relevantes."""
        # Basic hashtag generation based on content
        words = content.lower().split()
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        hashtags = []
        
        for word in words:
            if len(word) > 3 and word not in common_words and len(hashtags) < 5:
                hashtags.append(f"#{word.capitalize()}")
        
        return f"Suggested hashtags: {', '.join(hashtags)}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del servicio."""
        return {
            **self.metrics,
            'chains_available': len(self.chains),
            'tools_available': len(self.tools),
            'agents_available': len(self.agents),
            'memory_enabled': self.memory is not None,
            'vector_store_enabled': self.vector_store is not None
        } 