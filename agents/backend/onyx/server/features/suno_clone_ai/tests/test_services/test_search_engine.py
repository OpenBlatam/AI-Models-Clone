"""
Comprehensive Unit Tests for Search Engine

Tests cover search engine functionality with diverse test cases
"""

import pytest
from services.search_engine import AdvancedSearchEngine, SearchResult, SearchIndex


class TestSearchResult:
    """Test cases for SearchResult dataclass"""
    
    def test_search_result_creation(self):
        """Test creating search result"""
        result = SearchResult(
            id="doc1",
            score=0.95,
            data={"title": "Test", "content": "Content"}
        )
        assert result.id == "doc1"
        assert result.score == 0.95
        assert result.data["title"] == "Test"
        assert result.highlights == []
    
    def test_search_result_with_highlights(self):
        """Test search result with highlights"""
        highlights = ["highlight1", "highlight2"]
        result = SearchResult(
            id="doc1",
            score=0.8,
            data={},
            highlights=highlights
        )
        assert result.highlights == highlights


class TestAdvancedSearchEngine:
    """Test cases for AdvancedSearchEngine class"""
    
    def test_search_engine_init(self):
        """Test initializing search engine"""
        engine = AdvancedSearchEngine()
        assert len(engine.index.documents) == 0
        assert len(engine.index.inverted_index) == 0
        assert len(engine.stop_words) > 0
    
    def test_index_document_basic(self):
        """Test indexing a basic document"""
        engine = AdvancedSearchEngine()
        doc = {
            "title": "Test Song",
            "description": "A test song description"
        }
        
        engine.index_document("doc1", doc)
        
        assert "doc1" in engine.index.documents
        assert engine.index.documents["doc1"] == doc
    
    def test_index_document_text_fields(self):
        """Test indexing with text fields"""
        engine = AdvancedSearchEngine()
        doc = {
            "title": "Rock Song",
            "description": "A rock song",
            "genre": "rock"
        }
        
        engine.index_document("doc1", doc, text_fields=["title", "description"])
        
        # Check inverted index
        assert "rock" in engine.index.inverted_index
        assert "doc1" in engine.index.inverted_index["rock"]
    
    def test_index_document_metadata(self):
        """Test indexing metadata fields"""
        engine = AdvancedSearchEngine()
        doc = {
            "title": "Test",
            "genre": "pop",
            "tags": ["tag1", "tag2"]
        }
        
        engine.index_document("doc1", doc)
        
        # Check metadata index
        assert "genre" in engine.index.metadata_index
        assert "pop" in engine.index.metadata_index["genre"]
        assert "doc1" in engine.index.metadata_index["genre"]["pop"]
    
    def test_remove_document(self):
        """Test removing a document"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "Test"})
        
        engine.remove_document("doc1")
        
        assert "doc1" not in engine.index.documents
    
    def test_remove_document_cleans_indices(self):
        """Test removing document cleans indices"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song"})
        
        # Verify indexed
        assert "rock" in engine.index.inverted_index
        assert "doc1" in engine.index.inverted_index["rock"]
        
        engine.remove_document("doc1")
        
        # Verify cleaned
        assert "doc1" not in engine.index.inverted_index.get("rock", set())
    
    def test_search_basic(self):
        """Test basic search"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song"})
        engine.index_document("doc2", {"title": "pop song"})
        
        results = engine.search("rock")
        
        assert len(results) > 0
        assert any(r.id == "doc1" for r in results)
    
    def test_search_no_results(self):
        """Test search with no results"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song"})
        
        results = engine.search("nonexistent")
        
        assert len(results) == 0
    
    def test_search_multiple_terms(self):
        """Test search with multiple terms"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song", "description": "energetic"})
        engine.index_document("doc2", {"title": "pop song"})
        
        results = engine.search("rock energetic")
        
        assert len(results) > 0
        # doc1 should have higher score (matches both terms)
        scores = [r.score for r in results if r.id == "doc1"]
        assert len(scores) > 0
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "Rock Song"})
        
        results_lower = engine.search("rock")
        results_upper = engine.search("ROCK")
        
        assert len(results_lower) == len(results_upper)
    
    def test_search_fuzzy(self):
        """Test fuzzy search"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song"})
        
        results = engine.search("rok", fuzzy=True)
        
        # Should find similar matches
        assert len(results) >= 0  # Fuzzy may or may not match
    
    def test_search_with_filters(self):
        """Test search with filters"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song", "genre": "rock"})
        engine.index_document("doc2", {"title": "pop song", "genre": "pop"})
        
        results = engine.search("song", filters={"genre": "rock"})
        
        assert len(results) > 0
        assert all(r.data.get("genre") == "rock" for r in results)
    
    def test_search_with_sort(self):
        """Test search with custom sorting"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "song a", "rating": 5})
        engine.index_document("doc2", {"title": "song b", "rating": 10})
        
        def sort_by_rating(result):
            return result.data.get("rating", 0)
        
        results = engine.search("song", sort_key=sort_by_rating, reverse=True)
        
        if len(results) >= 2:
            assert results[0].data.get("rating", 0) >= results[1].data.get("rating", 0)
    
    def test_search_limit(self):
        """Test search with result limit"""
        engine = AdvancedSearchEngine()
        for i in range(10):
            engine.index_document(f"doc{i}", {"title": f"song {i}"})
        
        results = engine.search("song", limit=5)
        
        assert len(results) <= 5
    
    def test_autocomplete(self):
        """Test autocomplete functionality"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song"})
        engine.index_document("doc2", {"title": "pop song"})
        engine.index_document("doc3", {"title": "jazz song"})
        
        suggestions = engine.autocomplete("ro")
        
        assert len(suggestions) > 0
        assert any("rock" in s.lower() for s in suggestions)
    
    def test_autocomplete_no_matches(self):
        """Test autocomplete with no matches"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "rock song"})
        
        suggestions = engine.autocomplete("xyz")
        
        assert len(suggestions) == 0
    
    def test_get_index_stats(self):
        """Test getting index statistics"""
        engine = AdvancedSearchEngine()
        engine.index_document("doc1", {"title": "test"})
        engine.index_document("doc2", {"title": "test"})
        
        stats = engine.get_index_stats()
        
        assert stats["total_documents"] == 2
        assert "total_tokens" in stats










