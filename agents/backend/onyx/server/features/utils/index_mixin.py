"""
Index Mixin - Onyx Integration
Indexing functionality for models.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Type
from dataclasses import dataclass, field
from datetime import datetime
from .base_types import IndexType, IndexStatus

@dataclass
class Index:
    """Index data class."""
    name: str
    type: IndexType
    fields: List[str]
    status: IndexStatus = IndexStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class IndexMixin:
    """Mixin for indexing functionality."""
    
    _indexes: Dict[str, Index] = {}
    _index_values: Dict[str, Dict[str, Set[str]]] = {}
    
    def create_index(self, name: str, type: IndexType, fields: List[str], metadata: Optional[Dict[str, Any]] = None) -> Index:
        """Create an index."""
        if name in self._indexes:
            raise ValueError(f"Index {name} already exists")
        
        index = Index(
            name=name,
            type=type,
            fields=fields,
            metadata=metadata or {}
        )
        
        self._indexes[name] = index
        self._index_values[name] = {}
        
        return index
    
    def drop_index(self, name: str) -> None:
        """Drop an index."""
        if name not in self._indexes:
            raise ValueError(f"Index {name} does not exist")
        
        del self._indexes[name]
        del self._index_values[name]
    
    def get_index(self, name: str) -> Optional[Index]:
        """Get an index."""
        return self._indexes.get(name)
    
    def get_indexes(self) -> Dict[str, Index]:
        """Get all indexes."""
        return self._indexes.copy()
    
    def add_to_index(self, index_name: str, value: str, key: str) -> None:
        """Add a value to an index."""
        if index_name not in self._indexes:
            raise ValueError(f"Index {index_name} does not exist")
        
        if value not in self._index_values[index_name]:
            self._index_values[index_name][value] = set()
        
        self._index_values[index_name][value].add(key)
    
    def remove_from_index(self, index_name: str, value: str, key: str) -> None:
        """Remove a value from an index."""
        if index_name not in self._indexes:
            raise ValueError(f"Index {index_name} does not exist")
        
        if value in self._index_values[index_name]:
            self._index_values[index_name][value].discard(key)
            if not self._index_values[index_name][value]:
                del self._index_values[index_name][value]
    
    def search_index(self, index_name: str, value: str) -> Set[str]:
        """Search an index."""
        if index_name not in self._indexes:
            raise ValueError(f"Index {index_name} does not exist")
        
        return self._index_values[index_name].get(value, set())
    
    def get_index_values(self, index_name: str) -> Dict[str, Set[str]]:
        """Get all values in an index."""
        if index_name not in self._indexes:
            raise ValueError(f"Index {index_name} does not exist")
        
        return self._index_values[index_name].copy()
    
    def clear_index(self, index_name: str) -> None:
        """Clear an index."""
        if index_name not in self._indexes:
            raise ValueError(f"Index {index_name} does not exist")
        
        self._index_values[index_name].clear() 