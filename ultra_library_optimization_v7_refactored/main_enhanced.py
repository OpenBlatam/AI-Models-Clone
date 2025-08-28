#!/usr/bin/env python3
"""
Ultra Library Optimization V7 Enhanced - Main Application
=======================================================

Enhanced main entry point integrating all advanced features:
- Advanced IoC Container with dependency injection
- Event-Driven Architecture with event bus
- Advanced CQRS with command/query buses
- Advanced Configuration Management
- Enterprise-grade monitoring and metrics
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import advanced infrastructure components
from infrastructure.dependency_injection.container import (
    container, AdvancedIoCContainer, LifecycleAware, singleton, prototype, inject
)
from infrastructure.events.event_bus import (
    event_bus, DomainEvent, PostCreatedEvent, PostOptimizedEvent, 
    PostPublishedEvent, OptimizationStrategyChangedEvent, event_handler
)
from infrastructure.events.event_bus import EventHandler
from application.cqrs.command_bus import (
    command_bus, query_bus, Command, Query, CommandResult, QueryResult,
    CommandHandler, QueryHandler, command_handler, query_handler
)
from infrastructure.configuration.config_manager import (
    config_manager, ApplicationConfig, Environment, feature_flag, config_value
)

# Import domain components
from domain.entities.linkedin_post import LinkedInPost
from domain.value_objects.post_tone import PostTone
from domain.value_objects.post_length import PostLength
from domain.value_objects.optimization_strategy import OptimizationStrategy
from domain.repositories.post_repository import PostRepository

# Import application components
from application.use_cases.generate_post_use_case import (
    GeneratePostUseCaseImpl, GeneratePostRequest, GeneratePostResponse
)

# Import infrastructure components
from infrastructure.repositories.postgresql_repository import PostgreSQLPostRepository


# Enhanced event handlers
@event_handler(["post.created", "post.optimized", "post.published"], priority=10)
class PostEventLogger:
    """Event handler for logging post-related events."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle post events."""
        self.logger.info(f"Post event: {event.event_name} - ID: {event.event_id}")
        
        # Additional processing based on event type
        if event.event_type == "post.created":
            await self._handle_post_created(event)
        elif event.event_type == "post.optimized":
            await self._handle_post_optimized(event)
        elif event.event_type == "post.published":
            await self._handle_post_published(event)
    
    async def _handle_post_created(self, event: DomainEvent) -> None:
        """Handle post created event."""
        self.logger.info(f"New post created: {event.aggregate_id}")
    
    async def _handle_post_optimized(self, event: DomainEvent) -> None:
        """Handle post optimized event."""
        optimization_score = event.data.get('optimization_score', 0.0)
        self.logger.info(f"Post optimized: {event.aggregate_id} - Score: {optimization_score}")
    
    async def _handle_post_published(self, event: DomainEvent) -> None:
        """Handle post published event."""
        self.logger.info(f"Post published: {event.aggregate_id}")


@event_handler(["optimization.strategy_changed"], priority=20)
class OptimizationStrategyHandler:
    """Event handler for optimization strategy changes."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle optimization strategy changes."""
        strategy = event.data.get('strategy', 'unknown')
        self.logger.info(f"Optimization strategy changed to: {strategy}")
        
        # Update configuration or trigger other actions
        config_manager.set(f"optimization.strategy", strategy)


# Enhanced command handlers
@dataclass
class CreatePostCommand(Command):
    """Command to create a new LinkedIn post."""
    
    topic: str
    content: str
    tone: str
    length: str
    optimization_strategy: str = "default"
    user_id: Optional[str] = None


@dataclass
class OptimizePostCommand(Command):
    """Command to optimize an existing LinkedIn post."""
    
    post_id: str
    optimization_strategy: str
    user_id: Optional[str] = None


@command_handler(CreatePostCommand, priority=10)
class CreatePostCommandHandler:
    """Handler for creating LinkedIn posts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.use_case = None  # Will be injected
    
    async def handle(self, command: CreatePostCommand) -> CommandResult:
        """Handle create post command."""
        try:
            # Create use case request
            request = GeneratePostRequest(
                topic=command.topic,
                tone=command.tone,
                length=command.length,
                optimization_strategy=command.optimization_strategy
            )
            
            # Execute use case
            response = await self.use_case.execute(request)
            
            # Publish event
            event = PostCreatedEvent(
                aggregate_id=str(response.post.id),
                data={
                    'topic': response.post.topic,
                    'optimization_score': response.optimization_score,
                    'strategy': response.post.optimization_strategy.value
                }
            )
            await event_bus.publish(event)
            
            return CommandResult(
                success=True,
                command_id=command.command_id,
                result=response.post.to_dict()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create post: {e}")
            return CommandResult(
                success=False,
                command_id=command.command_id,
                error_message=str(e)
            )


@command_handler(OptimizePostCommand, priority=20)
class OptimizePostCommandHandler:
    """Handler for optimizing LinkedIn posts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.repository = None  # Will be injected
    
    async def handle(self, command: OptimizePostCommand) -> CommandResult:
        """Handle optimize post command."""
        try:
            # Get post from repository
            post = await self.repository.find_by_id(command.post_id)
            if not post:
                return CommandResult(
                    success=False,
                    command_id=command.command_id,
                    error_message="Post not found"
                )
            
            # Apply optimization
            strategy = OptimizationStrategy(command.optimization_strategy)
            post.apply_optimization(strategy, 0.85, {'optimized_by': 'command_handler'})
            
            # Save updated post
            await self.repository.save(post)
            
            # Publish event
            event = PostOptimizedEvent(
                aggregate_id=str(post.id),
                data={
                    'optimization_score': post.optimization_score,
                    'strategy': post.optimization_strategy.value
                }
            )
            await event_bus.publish(event)
            
            return CommandResult(
                success=True,
                command_id=command.command_id,
                result=post.to_dict()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to optimize post: {e}")
            return CommandResult(
                success=False,
                command_id=command.command_id,
                error_message=str(e)
            )


# Enhanced query handlers
@dataclass
class GetPostQuery(Query):
    """Query to get a LinkedIn post by ID."""
    
    post_id: str
    include_metadata: bool = True


@dataclass
class GetPostsByStrategyQuery(Query):
    """Query to get posts by optimization strategy."""
    
    strategy: str
    limit: int = 100
    offset: int = 0


@query_handler(GetPostQuery, priority=10)
class GetPostQueryHandler:
    """Handler for getting LinkedIn posts."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.repository = None  # Will be injected
    
    async def handle(self, query: GetPostQuery) -> QueryResult:
        """Handle get post query."""
        try:
            # Set cache key
            query.cache_key = f"post:{query.post_id}"
            
            # Get post from repository
            post = await self.repository.find_by_id(query.post_id)
            if not post:
                return QueryResult(
                    success=False,
                    query_id=query.query_id,
                    error_message="Post not found"
                )
            
            result = post.to_dict()
            if not query.include_metadata:
                # Remove metadata fields
                result.pop('optimization_metadata', None)
            
            return QueryResult(
                success=True,
                query_id=query.query_id,
                result=result
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get post: {e}")
            return QueryResult(
                success=False,
                query_id=query.query_id,
                error_message=str(e)
            )


@query_handler(GetPostsByStrategyQuery, priority=20)
class GetPostsByStrategyQueryHandler:
    """Handler for getting posts by strategy."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.repository = None  # Will be injected
    
    async def handle(self, query: GetPostsByStrategyQuery) -> QueryResult:
        """Handle get posts by strategy query."""
        try:
            # Set cache key
            query.cache_key = f"posts:strategy:{query.strategy}:{query.limit}:{query.offset}"
            
            # Get posts from repository
            posts = await self.repository.find_by_optimization_strategy(query.strategy)
            
            # Apply pagination
            paginated_posts = posts[query.offset:query.offset + query.limit]
            
            result = {
                'posts': [post.to_dict() for post in paginated_posts],
                'total_count': len(posts),
                'limit': query.limit,
                'offset': query.offset
            }
            
            return QueryResult(
                success=True,
                query_id=query.query_id,
                result=result
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get posts by strategy: {e}")
            return QueryResult(
                success=False,
                query_id=query.query_id,
                error_message=str(e)
            )


# Enhanced lifecycle-aware components
@singleton(PostRepository, tags=["repository", "database"], priority=100)
class EnhancedPostRepository(PostgreSQLPostRepository, LifecycleAware):
    """Enhanced PostgreSQL repository with lifecycle management."""
    
    async def on_construct(self) -> None:
        """Called after construction."""
        self.logger.info("EnhancedPostRepository constructed")
    
    async def on_initialize(self) -> None:
        """Called during initialization."""
        self.logger.info("EnhancedPostRepository initializing...")
        await self.initialize()
    
    async def on_start(self) -> None:
        """Called when starting."""
        self.logger.info("EnhancedPostRepository started")
    
    async def on_stop(self) -> None:
        """Called when stopping."""
        self.logger.info("EnhancedPostRepository stopping...")
    
    async def on_destroy(self) -> None:
        """Called during destruction."""
        self.logger.info("EnhancedPostRepository destroyed")
        await self.close()


@singleton(GeneratePostUseCaseImpl, tags=["use_case", "business"], priority=50)
class EnhancedGeneratePostUseCase(GeneratePostUseCaseImpl, LifecycleAware):
    """Enhanced use case with lifecycle management."""
    
    async def on_construct(self) -> None:
        """Called after construction."""
        self.logger.info("EnhancedGeneratePostUseCase constructed")
    
    async def on_initialize(self) -> None:
        """Called during initialization."""
        self.logger.info("EnhancedGeneratePostUseCase initializing...")
    
    async def on_start(self) -> None:
        """Called when starting."""
        self.logger.info("EnhancedGeneratePostUseCase started")
    
    async def on_stop(self) -> None:
        """Called when stopping."""
        self.logger.info("EnhancedGeneratePostUseCase stopping...")
    
    async def on_destroy(self) -> None:
        """Called during destruction."""
        self.logger.info("EnhancedGeneratePostUseCase destroyed")


# Enhanced application class
class UltraLibraryOptimizationApp:
    """
    Enhanced Ultra Library Optimization application.
    
    Integrates all advanced features:
    - IoC Container with dependency injection
    - Event-Driven Architecture
    - CQRS with command/query buses
    - Advanced configuration management
    - Enterprise-grade monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.container = container
        self.event_bus = event_bus
        self.command_bus = command_bus
        self.query_bus = query_bus
        self.config_manager = config_manager
        self.running = False
        self.start_time = None
    
    async def initialize(self) -> None:
        """Initialize the application."""
        self.logger.info("Initializing Ultra Library Optimization V7 Enhanced...")
        
        # Register components with IoC container
        await self._register_components()
        
        # Initialize IoC container
        await self.container.initialize_all()
        
        # Start event bus
        await self.event_bus.start()
        
        # Start command bus
        await self.command_bus.start()
        
        # Set up configuration watchers
        self._setup_configuration_watchers()
        
        # Set up feature flags
        self._setup_feature_flags()
        
        self.start_time = time.time()
        self.running = True
        
        self.logger.info("Ultra Library Optimization V7 Enhanced initialized successfully")
    
    async def shutdown(self) -> None:
        """Shutdown the application."""
        self.logger.info("Shutting down Ultra Library Optimization V7 Enhanced...")
        
        self.running = False
        
        # Stop command bus
        await self.command_bus.stop()
        
        # Stop event bus
        await self.event_bus.stop()
        
        # Shutdown IoC container
        await self.container.shutdown()
        
        self.logger.info("Ultra Library Optimization V7 Enhanced shutdown complete")
    
    async def _register_components(self) -> None:
        """Register components with IoC container."""
        # Register repositories
        self.container.register_singleton(
            PostRepository,
            EnhancedPostRepository,
            tags=["repository", "database"],
            priority=100
        )
        
        # Register use cases
        self.container.register_singleton(
            GeneratePostUseCaseImpl,
            EnhancedGeneratePostUseCase,
            tags=["use_case", "business"],
            priority=50
        )
        
        # Register command handlers
        self.container.register_prototype(
            CreatePostCommandHandler,
            tags=["command_handler"],
            priority=10
        )
        
        self.container.register_prototype(
            OptimizePostCommandHandler,
            tags=["command_handler"],
            priority=20
        )
        
        # Register query handlers
        self.container.register_prototype(
            GetPostQueryHandler,
            tags=["query_handler"],
            priority=10
        )
        
        self.container.register_prototype(
            GetPostsByStrategyQueryHandler,
            tags=["query_handler"],
            priority=20
        )
        
        # Register event handlers
        self.container.register_prototype(
            PostEventLogger,
            tags=["event_handler"],
            priority=10
        )
        
        self.container.register_prototype(
            OptimizationStrategyHandler,
            tags=["event_handler"],
            priority=20
        )
    
    def _setup_configuration_watchers(self) -> None:
        """Set up configuration change watchers."""
        def config_change_handler(key: str, value: Any) -> None:
            self.logger.info(f"Configuration changed: {key} = {value}")
            
            # Handle specific configuration changes
            if key == "optimization.strategy":
                # Publish strategy change event
                event = OptimizationStrategyChangedEvent(
                    data={'strategy': value}
                )
                asyncio.create_task(self.event_bus.publish(event))
        
        self.config_manager.watch(config_change_handler)
    
    def _setup_feature_flags(self) -> None:
        """Set up feature flags."""
        # Enable quantum optimization
        self.config_manager.set_feature_flag(
            "quantum_optimization",
            enabled=True,
            rollout_percentage=50.0
        )
        
        # Enable neuromorphic processing
        self.config_manager.set_feature_flag(
            "neuromorphic_processing",
            enabled=True,
            rollout_percentage=25.0
        )
        
        # Enable advanced analytics
        self.config_manager.set_feature_flag(
            "advanced_analytics",
            enabled=True,
            rollout_percentage=100.0
        )
    
    async def create_post(self, topic: str, content: str, tone: str = "professional",
                         length: str = "medium", strategy: str = "default",
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new LinkedIn post using CQRS."""
        command = CreatePostCommand(
            topic=topic,
            content=content,
            tone=tone,
            length=length,
            optimization_strategy=strategy,
            user_id=user_id
        )
        
        result = await self.command_bus.send(command)
        
        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to create post: {result.error_message}")
    
    async def optimize_post(self, post_id: str, strategy: str = "quantum",
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """Optimize an existing LinkedIn post using CQRS."""
        command = OptimizePostCommand(
            post_id=post_id,
            optimization_strategy=strategy,
            user_id=user_id
        )
        
        result = await self.command_bus.send(command)
        
        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to optimize post: {result.error_message}")
    
    async def get_post(self, post_id: str, include_metadata: bool = True) -> Dict[str, Any]:
        """Get a LinkedIn post using CQRS."""
        query = GetPostQuery(
            post_id=post_id,
            include_metadata=include_metadata
        )
        
        result = await self.query_bus.execute(query)
        
        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to get post: {result.error_message}")
    
    async def get_posts_by_strategy(self, strategy: str, limit: int = 100,
                                  offset: int = 0) -> Dict[str, Any]:
        """Get posts by optimization strategy using CQRS."""
        query = GetPostsByStrategyQuery(
            strategy=strategy,
            limit=limit,
            offset=offset
        )
        
        result = await self.query_bus.execute(query)
        
        if result.success:
            return result.result
        else:
            raise Exception(f"Failed to get posts: {result.error_message}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get application metrics."""
        return {
            'uptime_seconds': time.time() - self.start_time if self.start_time else 0,
            'running': self.running,
            'container_metrics': self.container.get_metrics(),
            'event_bus_metrics': self.event_bus.get_metrics(),
            'command_bus_metrics': self.command_bus.get_metrics(),
            'query_bus_metrics': self.query_bus.get_metrics(),
            'feature_flags': self.config_manager.get_feature_flags()
        }
    
    @feature_flag("quantum_optimization")
    async def quantum_optimize_post(self, post_id: str) -> Dict[str, Any]:
        """Quantum-optimize a post (feature flag protected)."""
        return await self.optimize_post(post_id, "quantum")
    
    @feature_flag("neuromorphic_processing")
    async def neuromorphic_optimize_post(self, post_id: str) -> Dict[str, Any]:
        """Neuromorphic-optimize a post (feature flag protected)."""
        return await self.optimize_post(post_id, "neuromorphic")


async def demonstrate_enhanced_features():
    """Demonstrate all enhanced features."""
    print("\n" + "="*80)
    print("🚀 ULTRA LIBRARY OPTIMIZATION V7 ENHANCED - FEATURE DEMONSTRATION")
    print("="*80)
    
    # Initialize application
    app = UltraLibraryOptimizationApp()
    await app.initialize()
    
    try:
        # Demonstrate IoC Container
        print("\n🏗️  IoC Container Demonstration:")
        print("-" * 40)
        
        # Resolve components
        repository = await app.container.resolve(PostRepository)
        use_case = await app.container.resolve(GeneratePostUseCaseImpl)
        
        print(f"✅ Resolved PostRepository: {type(repository).__name__}")
        print(f"✅ Resolved GeneratePostUseCase: {type(use_case).__name__}")
        
        # Demonstrate Event-Driven Architecture
        print("\n📡 Event-Driven Architecture Demonstration:")
        print("-" * 40)
        
        # Create a post and watch events
        post_data = await app.create_post(
            topic="Advanced AI in Enterprise",
            content="Enterprise AI is revolutionizing how businesses operate. Companies are seeing unprecedented efficiency gains through intelligent automation and data-driven decision making.",
            tone="professional",
            length="medium",
            strategy="quantum"
        )
        
        print(f"✅ Created post: {post_data['id']}")
        print(f"✅ Events published and processed")
        
        # Demonstrate CQRS
        print("\n⚡ CQRS Demonstration:")
        print("-" * 40)
        
        # Query the post
        retrieved_post = await app.get_post(post_data['id'])
        print(f"✅ Retrieved post via CQRS: {retrieved_post['topic']}")
        
        # Optimize the post
        optimized_post = await app.optimize_post(post_data['id'], "neuromorphic")
        print(f"✅ Optimized post via CQRS: Score {optimized_post['optimization_score']:.2f}")
        
        # Demonstrate Configuration Management
        print("\n⚙️  Configuration Management Demonstration:")
        print("-" * 40)
        
        # Get configuration
        app_name = app.config_manager.get("app_name", "Unknown")
        environment = app.config_manager.environment.value
        print(f"✅ App Name: {app_name}")
        print(f"✅ Environment: {environment}")
        
        # Demonstrate Feature Flags
        print("\n🚩 Feature Flags Demonstration:")
        print("-" * 40)
        
        quantum_enabled = app.config_manager.is_feature_enabled("quantum_optimization")
        neuromorphic_enabled = app.config_manager.is_feature_enabled("neuromorphic_processing")
        
        print(f"✅ Quantum Optimization: {'Enabled' if quantum_enabled else 'Disabled'}")
        print(f"✅ Neuromorphic Processing: {'Enabled' if neuromorphic_enabled else 'Disabled'}")
        
        # Demonstrate Metrics
        print("\n📊 Metrics Demonstration:")
        print("-" * 40)
        
        metrics = app.get_metrics()
        print(f"✅ Uptime: {metrics['uptime_seconds']:.2f} seconds")
        print(f"✅ Event Bus Events: {metrics['event_bus_metrics']['events_published']}")
        print(f"✅ Command Bus Commands: {metrics['command_bus_metrics']['commands_sent']}")
        print(f"✅ Query Bus Queries: {metrics['query_bus_metrics']['queries_sent']}")
        
        # Demonstrate Advanced Features
        print("\n🎯 Advanced Features Demonstration:")
        print("-" * 40)
        
        # Try quantum optimization (feature flag protected)
        try:
            quantum_result = await app.quantum_optimize_post(post_data['id'])
            print(f"✅ Quantum optimization successful: {quantum_result['optimization_score']:.2f}")
        except Exception as e:
            print(f"⚠️  Quantum optimization not available: {e}")
        
        # Try neuromorphic optimization (feature flag protected)
        try:
            neuromorphic_result = await app.neuromorphic_optimize_post(post_data['id'])
            print(f"✅ Neuromorphic optimization successful: {neuromorphic_result['optimization_score']:.2f}")
        except Exception as e:
            print(f"⚠️  Neuromorphic optimization not available: {e}")
        
        print("\n🎉 All enhanced features demonstrated successfully!")
        
    finally:
        # Shutdown application
        await app.shutdown()


async def main():
    """Main application entry point."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run demonstration
    await demonstrate_enhanced_features()


if __name__ == "__main__":
    asyncio.run(main()) 