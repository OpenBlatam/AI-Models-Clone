"""
Messaging Factory
=================

Factory for creating messaging adapters.
"""

import logging
import os
from typing import Optional
from aws.modules.ports.messaging_port import MessagingPort
from aws.modules.adapters.messaging_adapters import (
    KafkaMessagingAdapter,
    RabbitMQMessagingAdapter,
    SQSMessagingAdapter
)

logger = logging.getLogger(__name__)


class MessagingFactory:
    """Factory for creating messaging adapters."""
    
    @staticmethod
    def create(
        adapter_type: str = "kafka",
        kafka_servers: Optional[str] = None,
        rabbitmq_url: Optional[str] = None,
        sqs_region: Optional[str] = None
    ) -> MessagingPort:
        """
        Create messaging adapter.
        
        Args:
            adapter_type: Type of adapter (kafka, rabbitmq, sqs)
            kafka_servers: Kafka bootstrap servers
            rabbitmq_url: RabbitMQ connection URL
            sqs_region: AWS region for SQS
        
        Returns:
            Messaging adapter instance
        """
        if adapter_type == "kafka":
            servers = kafka_servers or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
            return KafkaMessagingAdapter(bootstrap_servers=servers)
        
        elif adapter_type == "rabbitmq":
            url = rabbitmq_url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
            return RabbitMQMessagingAdapter(connection_url=url)
        
        elif adapter_type == "sqs":
            region = sqs_region or os.getenv("AWS_REGION", "us-east-1")
            return SQSMessagingAdapter(region=region)
        
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
    
    @staticmethod
    def create_from_env() -> Optional[MessagingPort]:
        """Create messaging from environment variables."""
        adapter_type = os.getenv("MESSAGING_TYPE", "kafka")
        
        if adapter_type == "none" or not os.getenv("ENABLE_MESSAGING", "false").lower() == "true":
            return None
        
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        rabbitmq_url = os.getenv("RABBITMQ_URL")
        sqs_region = os.getenv("AWS_REGION")
        
        return MessagingFactory.create(
            adapter_type=adapter_type,
            kafka_servers=kafka_servers,
            rabbitmq_url=rabbitmq_url,
            sqs_region=sqs_region
        )















