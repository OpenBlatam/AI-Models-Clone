"""
OpenClaw Memory -- Long-Term Vector Memory (RAG).

Implements Semantic and Episodic memory retrieval using ChromaDB.
Based on "REMem: Reasoning with Episodic Memory" and long-term memory
architectures for LLM Agents (2024).
"""

import logging
import uuid
import asyncio
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False


class VectorMemory:
    """
    Long-Term Vector Memory subsystem using ChromaDB.

    Maintains two collections:
    1. 'episodic' -- records specific events, interactions and tool usage.
    2. 'semantic' -- factual knowledge, summaries, and learned rules.
    """

    def __init__(self, db_path: str = "./openclaw_chroma_db") -> None:
        self.enabled = HAS_CHROMA
        if not self.enabled:
            logger.warning(
                "ChromaDB not found. VectorMemory is disabled. "
                "Run `pip install chromadb` to enable long-term RAG memory."
            )
            return

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
        
        # Configure Local Embeddings (Sentence Transformers)
        try:
            from chromadb.utils import embedding_functions
            # Uses 'all-MiniLM-L6-v2' by default, which is fast and runs locally
            embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            logger.info("SentenceTransformers loaded for local embeddings.")
        except ImportError:
            embed_fn = None
            logger.warning("Instala 'sentence-transformers' para embeddings locales óptimos.")
        
        # Get or create episodic and semantic collections
        self.episodic = self.client.get_or_create_collection(
            name="openclaw_episodic",
            embedding_function=embed_fn,
            metadata={"description": "Agent episodic memories (events, interactions)"}
        )
        self.semantic = self.client.get_or_create_collection(
            name="openclaw_semantic",
            embedding_function=embed_fn,
            metadata={"description": "Agent semantic memories (factual knowledge, rules)"}
        )

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    async def add_episodic(self, user_id: str, agent_name: str, event: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a specific event or interaction in episodic memory asynchronously."""
        return await asyncio.to_thread(self._add_episodic_sync, user_id, agent_name, event, metadata)

    def _add_episodic_sync(self, user_id: str, agent_name: str, event: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        if not self.enabled:
            return ""
        
        mem_id = f"ep_{uuid.uuid4().hex[:12]}"
        meta = {"user_id": user_id, "agent": agent_name, "type": "episodic"}
        if metadata:
            meta.update(metadata)

        self.episodic.add(
            documents=[event],
            metadatas=[meta],
            ids=[mem_id]
        )
        return mem_id

    async def add_semantic(self, user_id: str, agent_name: str, fact: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a generalized fact or learned rule in semantic memory asynchronously."""
        return await asyncio.to_thread(self._add_semantic_sync, user_id, agent_name, fact, metadata)

    def _add_semantic_sync(self, user_id: str, agent_name: str, fact: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        if not self.enabled:
            return ""
        
        mem_id = f"sm_{uuid.uuid4().hex[:12]}"
        meta = {"user_id": user_id, "agent": agent_name, "type": "semantic"}
        if metadata:
            meta.update(metadata)

        self.semantic.add(
            documents=[fact],
            metadatas=[meta],
            ids=[mem_id]
        )
        return mem_id

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    async def search_episodic(self, query: str, user_id: str, top_k: int = 3) -> List[str]:
        """Retrieve the most relevant past episodes for a user asynchronously."""
        return await asyncio.to_thread(self._search_episodic_sync, query, user_id, top_k)

    def _search_episodic_sync(self, query: str, user_id: str, top_k: int = 3) -> List[str]:
        if not self.enabled:
            return []
        
        results = self.episodic.query(
            query_texts=[query],
            n_results=top_k,
            where={"user_id": user_id}
        )
        
        documents = results.get("documents")
        if not documents or not documents[0]:
            return []
        return documents[0]

    async def search_semantic(self, query: str, user_id: str, top_k: int = 3) -> List[str]:
        """Retrieve the most relevant factual knowledge for a user asynchronously."""
        return await asyncio.to_thread(self._search_semantic_sync, query, user_id, top_k)

    def _search_semantic_sync(self, query: str, user_id: str, top_k: int = 3) -> List[str]:
        if not self.enabled:
            return []
        
        results = self.semantic.query(
            query_texts=[query],
            n_results=top_k,
            where={"user_id": user_id}
        )
        
        documents = results.get("documents")
        if not documents or not documents[0]:
            return []
        return documents[0]

    async def get_context_for_prompt(self, query: str, user_id: str) -> str:
        """
        Builds a context string combining both episodic and semantic memory 
        suitable for LLM prompt injection (RAG overlay) asynchronously.
        """
        if not self.enabled:
            return ""
        
        episodes = await self.search_episodic(query, user_id, top_k=2)
        facts = await self.search_semantic(query, user_id, top_k=2)
        
        if not episodes and not facts:
            return ""
            
        context_parts = ["\n[Long-Term Memory Search Results]"]
        
        if facts:
            context_parts.append("Relevant Semantic Facts / Rules Learned:")
            for i, f in enumerate(facts, 1):
                context_parts.append(f" {i}. {f}")
                
        if episodes:
            context_parts.append("\nRelevant Past Episodes / Interactions:")
            for i, e in enumerate(episodes, 1):
                context_parts.append(f" {i}. {e}")
                
                
        return "\n".join(context_parts) + "\n"

    async def compact_episodic_memory(self, user_id: str, summarize_callback: Any, threshold: int = 15) -> bool:
        """
        Consolidates old episodic memories into a single semantic rule to prevent context bloat.
        Uses the provided summarize_callback (LLM) to extract key facts.
        """
        if not self.enabled:
            return False
            
        try:
            results = self.episodic.get(where={"user_id": user_id})
            ids = results.get("ids", [])
            documents = results.get("documents", [])
            
            if not ids or len(ids) < threshold:
                return False
                
            logger.info(f"Compactando {len(ids)} recuerdos episódicos para {user_id}...")
            
            # Concat all past episodes
            full_text = "\n".join([f"- {doc}" for doc in documents])
            prompt = (
                f"Resume los siguientes eventos episódicos del usuario en un conjunto conciso de hechos semánticos "
                f"o preferencias generales. Extrae solo el conocimiento útil a largo plazo.\n"
                f"Eventos pasados:\n{full_text}"
            )
            
            # Use the LLM to summarize
            summary = await summarize_callback(prompt)
            
            # Add to semantic memory
            await self.add_semantic(user_id=user_id, agent_name="MemoryCompactor", fact=summary, metadata={"compacted_from": len(ids)})
            
            # Delete old episodic memories to free up context
            await asyncio.to_thread(self.episodic.delete, ids=ids)
            logger.info(f"Memoria de {user_id} compactada exitosamente. {len(ids)} episodios consolidados.")
            return True
        except Exception as e:
            logger.error(f"Error compactando memoria: {e}")
            return False
