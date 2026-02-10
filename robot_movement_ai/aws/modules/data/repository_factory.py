"""
Repository Factory
==================

Factory for creating repository adapters.
"""

import logging
import os
from typing import Optional
from aws.modules.ports.repository_port import RepositoryPort
from aws.modules.adapters.repository_adapters import (
    DynamoDBRepositoryAdapter,
    PostgreSQLRepositoryAdapter,
    InMemoryRepositoryAdapter
)

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """Factory for creating repository adapters."""
    
    @staticmethod
    def create(
        adapter_type: str = "dynamodb",
        table_name: Optional[str] = None,
        connection_string: Optional[str] = None
    ) -> RepositoryPort:
        """
        Create repository adapter.
        
        Args:
            adapter_type: Type of adapter (dynamodb, postgresql, memory)
            table_name: Table name for DynamoDB
            connection_string: Connection string for PostgreSQL
        
        Returns:
            Repository adapter instance
        """
        if adapter_type == "dynamodb":
            table = table_name or os.getenv("TABLE_NAME", "default-table")
            return DynamoDBRepositoryAdapter(table_name=table)
        
        elif adapter_type == "postgresql":
            conn_str = connection_string or os.getenv("DATABASE_URL")
            if not conn_str:
                raise ValueError("PostgreSQL connection string required")
            return PostgreSQLRepositoryAdapter(
                connection_string=conn_str,
                table_name=table_name or "default_table"
            )
        
        elif adapter_type == "memory":
            return InMemoryRepositoryAdapter()
        
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    @staticmethod
    def create_from_env(service_name: str) -> RepositoryPort:
        """Create repository from environment variables."""
        adapter_type = os.getenv(
            f"{service_name.upper().replace('-', '_')}_DB_TYPE",
            "dynamodb"
        )
        
        table_name = os.getenv(
            f"{service_name.upper().replace('-', '_')}_TABLE"
        )
        
        connection_string = os.getenv(
            f"{service_name.upper().replace('-', '_')}_DATABASE_URL"
        )
        
        return RepositoryFactory.create(
            adapter_type=adapter_type,
            table_name=table_name,
            connection_string=connection_string
        )















