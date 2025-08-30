#!/usr/bin/env python3
"""
Multi-Agent Swarm Intelligence with Collaborative AI Optimization
================================================================
Cutting-edge multi-agent system with emergent behavior, collaborative optimization,
and swarm intelligence for HeyGen AI.
"""

import asyncio
import time
import json
import structlog
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import defaultdict, deque
import hashlib
import secrets
from pathlib import Path
import pickle
import random
import math
from abc import ABC, abstractmethod

logger = structlog.get_logger()

class AgentType(Enum):
    """Types of AI agents in the swarm."""
    OPTIMIZER = "optimizer"
    EXPLORER = "explorer"
    EXPLOITER = "exploiter"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    GENERALIST = "generalist"
    ADAPTIVE = "adaptive"

class SwarmStrategy(Enum):
    """Swarm intelligence strategies."""
    PARTICLE_SWARM = "particle_swarm"
    ANT_COLONY = "ant_colony"
    BEE_COLONY = "bee_colony"
    FISH_SCHOOL = "fish_school"
    BIRD_FLOCK = "bird_flock"
    EMERGENT_BEHAVIOR = "emergent_behavior"
    COLLABORATIVE_LEARNING = "collaborative_learning"

class CommunicationProtocol(Enum):
    """Inter-agent communication protocols."""
    DIRECT = "direct"
    BROADCAST = "broadcast"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"
    EMERGENT_NETWORK = "emergent_network"
    QUANTUM_ENTANGLED = "quantum_entangled"

class OptimizationObjective(Enum):
    """Optimization objectives for the swarm."""
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    ACCURACY = "accuracy"
    SPEED = "speed"
    MEMORY = "memory"
    ENERGY = "energy"
    MULTI_OBJECTIVE = "multi_objective"

@dataclass
class AgentState:
    """State of an individual agent."""
    agent_id: str
    agent_type: AgentType
    position: np.ndarray
    velocity: np.ndarray
    best_position: np.ndarray
    best_fitness: float
    current_fitness: float
    energy_level: float
    knowledge_base: Dict[str, Any]
    communication_history: List[Dict[str, Any]]
    last_update: float
    is_active: bool = True

@dataclass
class SwarmConfiguration:
    """Configuration for the swarm system."""
    num_agents: int
    swarm_strategy: SwarmStrategy
    communication_protocol: CommunicationProtocol
    optimization_objective: OptimizationObjective
    search_space_dimensions: int
    max_iterations: int
    convergence_threshold: float
    exploration_rate: float
    exploitation_rate: float
    collaboration_strength: float
    emergent_behavior_enabled: bool = True

@dataclass
class SwarmMetrics:
    """Performance metrics for the swarm."""
    total_iterations: int
    best_global_fitness: float
    average_fitness: float
    convergence_rate: float
    exploration_efficiency: float
    collaboration_efficiency: float
    emergent_behavior_count: int
    optimization_time: float
    communication_overhead: float

@dataclass
class CommunicationMessage:
    """Message between agents."""
    message_id: str
    sender_id: str
    receiver_id: Optional[str]  # None for broadcast
    message_type: str
    content: Dict[str, Any]
    timestamp: float
    priority: int
    ttl: float  # Time to live

class BaseAgent(ABC):
    """
    Base class for all agents in the swarm.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        position: np.ndarray,
        search_space_bounds: Tuple[np.ndarray, np.ndarray],
        optimization_objective: OptimizationObjective
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.position = position.copy()
        self.search_space_bounds = search_space_bounds
        self.optimization_objective = optimization_objective
        
        # Initialize state
        self.velocity = np.random.uniform(-1, 1, position.shape)
        self.best_position = position.copy()
        self.best_fitness = float('inf')
        self.current_fitness = float('inf')
        self.energy_level = 1.0
        
        # Knowledge and communication
        self.knowledge_base = {}
        self.communication_history = []
        self.last_update = time.time()
        self.is_active = True
        
        # Agent-specific parameters
        self._init_agent_parameters()
    
    @abstractmethod
    def _init_agent_parameters(self):
        """Initialize agent-specific parameters."""
        pass
    
    @abstractmethod
    async def update_position(self, swarm_state: Dict[str, Any]) -> np.ndarray:
        """Update agent position based on swarm state."""
        pass
    
    @abstractmethod
    async def evaluate_fitness(self, position: np.ndarray) -> float:
        """Evaluate fitness of a position."""
        pass
    
    @abstractmethod
    async def communicate(self, other_agents: List['BaseAgent']) -> List[CommunicationMessage]:
        """Generate communication messages."""
        pass
    
    @abstractmethod
    async def learn_from_communication(self, messages: List[CommunicationMessage]):
        """Learn from received communication messages."""
        pass
    
    def get_state(self) -> AgentState:
        """Get current agent state."""
        return AgentState(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            best_position=self.best_position.copy(),
            best_fitness=self.best_fitness,
            current_fitness=self.current_fitness,
            energy_level=self.energy_level,
            knowledge_base=self.knowledge_base.copy(),
            communication_history=self.communication_history.copy(),
            last_update=self.last_update,
            is_active=self.is_active
        )
    
    def update_state(self, new_position: np.ndarray, new_fitness: float):
        """Update agent state with new position and fitness."""
        self.position = new_position.copy()
        self.current_fitness = new_fitness
        self.last_update = time.time()
        
        # Update best position if better
        if self._is_better_fitness(new_fitness, self.best_fitness):
            self.best_position = new_position.copy()
            self.best_fitness = new_fitness
    
    def _is_better_fitness(self, fitness1: float, fitness2: float) -> bool:
        """Check if fitness1 is better than fitness2 based on objective."""
        if self.optimization_objective == OptimizationObjective.PERFORMANCE:
            return fitness1 > fitness2
        elif self.optimization_objective == OptimizationObjective.EFFICIENCY:
            return fitness1 > fitness2
        elif self.optimization_objective == OptimizationObjective.ACCURACY:
            return fitness1 > fitness2
        else:
            return fitness1 < fitness2  # Default to minimization

class OptimizerAgent(BaseAgent):
    """
    Agent specialized in optimization tasks.
    """
    
    def _init_agent_parameters(self):
        """Initialize optimizer-specific parameters."""
        self.learning_rate = 0.1
        self.momentum = 0.9
        self.adaptation_rate = 0.05
        self.optimization_history = []
    
    async def update_position(self, swarm_state: Dict[str, Any]) -> np.ndarray:
        """Update position using optimization algorithms."""
        try:
            # Get global best position
            global_best = swarm_state.get('global_best_position', self.best_position)
            
            # Calculate new velocity using PSO-like algorithm
            cognitive_component = self.learning_rate * np.random.random() * (self.best_position - self.position)
            social_component = self.learning_rate * np.random.random() * (global_best - self.position)
            
            # Update velocity with momentum
            self.velocity = (self.momentum * self.velocity + 
                           cognitive_component + social_component)
            
            # Update position
            new_position = self.position + self.velocity
            
            # Apply bounds
            new_position = np.clip(new_position, 
                                 self.search_space_bounds[0], 
                                 self.search_space_bounds[1])
            
            return new_position
            
        except Exception as e:
            logger.warning(f"Position update failed for optimizer agent {self.agent_id}: {e}")
            return self.position
    
    async def evaluate_fitness(self, position: np.ndarray) -> float:
        """Evaluate fitness using optimization metrics."""
        try:
            # Calculate fitness based on position quality
            # This is a simplified fitness function
            distance_from_origin = np.linalg.norm(position)
            smoothness = np.sum(np.diff(position)**2)
            
            # Multi-objective fitness
            if self.optimization_objective == OptimizationObjective.MULTI_OBJECTIVE:
                fitness = -distance_from_origin - 0.1 * smoothness
            else:
                fitness = -distance_from_origin
            
            return fitness
            
        except Exception as e:
            logger.warning(f"Fitness evaluation failed for optimizer agent {self.agent_id}: {e}")
            return float('inf')
    
    async def communicate(self, other_agents: List[BaseAgent]) -> List[CommunicationMessage]:
        """Generate optimization insights."""
        messages = []
        
        try:
            # Share optimization insights
            if self.optimization_history:
                best_insight = max(self.optimization_history, key=lambda x: x.get('fitness', 0))
                
                message = CommunicationMessage(
                    message_id=f"opt_{self.agent_id}_{int(time.time())}",
                    sender_id=self.agent_id,
                    receiver_id=None,  # Broadcast
                    message_type="optimization_insight",
                    content={
                        'best_position': self.best_position.tolist(),
                        'best_fitness': self.best_fitness,
                        'optimization_strategy': 'gradient_descent',
                        'learning_rate': self.learning_rate,
                        'momentum': self.momentum
                    },
                    timestamp=time.time(),
                    priority=2,
                    ttl=300.0
                )
                messages.append(message)
            
            # Share knowledge with similar agents
            for agent in other_agents:
                if (agent.agent_type == AgentType.OPTIMIZER and 
                    agent.agent_id != self.agent_id):
                    
                    message = CommunicationMessage(
                        message_id=f"collab_{self.agent_id}_{agent.agent_id}_{int(time.time())}",
                        sender_id=self.agent_id,
                        receiver_id=agent.agent_id,
                        message_type="collaboration_request",
                        content={
                            'proposed_strategy': 'parameter_sharing',
                            'current_parameters': {
                                'learning_rate': self.learning_rate,
                                'momentum': self.momentum
                            }
                        },
                        timestamp=time.time(),
                        priority=1,
                        ttl=180.0
                    )
                    messages.append(message)
            
        except Exception as e:
            logger.warning(f"Communication failed for optimizer agent {self.agent_id}: {e}")
        
        return messages
    
    async def learn_from_communication(self, messages: List[CommunicationMessage]):
        """Learn from optimization insights."""
        try:
            for message in messages:
                if message.message_type == "optimization_insight":
                    # Learn from other agents' insights
                    if message.content.get('best_fitness', 0) > self.best_fitness:
                        # Adapt learning rate based on successful strategies
                        self.learning_rate *= 1.1
                        self.learning_rate = min(self.learning_rate, 0.5)
                
                elif message.message_type == "collaboration_response":
                    # Adapt based on collaboration
                    if 'shared_parameters' in message.content:
                        shared_lr = message.content['shared_parameters'].get('learning_rate')
                        if shared_lr:
                            self.learning_rate = (self.learning_rate + shared_lr) / 2
                
                # Record communication
                self.communication_history.append({
                    'message_id': message.message_id,
                    'sender_id': message.sender_id,
                    'message_type': message.message_type,
                    'timestamp': message.timestamp,
                    'content_summary': str(message.content)[:100]
                })
                
        except Exception as e:
            logger.warning(f"Learning failed for optimizer agent {self.agent_id}: {e}")

class ExplorerAgent(BaseAgent):
    """
    Agent specialized in exploring new areas of the search space.
    """
    
    def _init_agent_parameters(self):
        """Initialize explorer-specific parameters."""
        self.exploration_radius = 2.0
        self.curiosity_factor = 0.8
        self.discovery_threshold = 0.1
        self.exploration_history = []
    
    async def update_position(self, swarm_state: Dict[str, Any]) -> np.ndarray:
        """Update position using exploration strategies."""
        try:
            # Get unexplored areas
            explored_positions = swarm_state.get('explored_positions', [])
            
            # Calculate exploration direction
            if explored_positions:
                # Move away from explored areas
                explored_center = np.mean(explored_positions, axis=0)
                exploration_direction = self.position - explored_center
                exploration_direction = exploration_direction / (np.linalg.norm(exploration_direction) + 1e-8)
            else:
                # Random exploration
                exploration_direction = np.random.uniform(-1, 1, self.position.shape)
                exploration_direction = exploration_direction / np.linalg.norm(exploration_direction)
            
            # Add some randomness for better exploration
            random_component = np.random.uniform(-0.5, 0.5, self.position.shape)
            exploration_direction = exploration_direction + 0.3 * random_component
            exploration_direction = exploration_direction / (np.linalg.norm(exploration_direction) + 1e-8)
            
            # Update position
            step_size = self.exploration_radius * self.curiosity_factor
            new_position = self.position + step_size * exploration_direction
            
            # Apply bounds
            new_position = np.clip(new_position, 
                                 self.search_space_bounds[0], 
                                 self.search_space_bounds[1])
            
            return new_position
            
        except Exception as e:
            logger.warning(f"Position update failed for explorer agent {self.agent_id}: {e}")
            return self.position
    
    async def evaluate_fitness(self, position: np.ndarray) -> float:
        """Evaluate fitness with exploration bonus."""
        try:
            # Base fitness
            base_fitness = -np.linalg.norm(position)
            
            # Add exploration bonus
            exploration_bonus = self.curiosity_factor * self.exploration_radius
            
            # Add novelty bonus for new areas
            if position not in self.exploration_history:
                novelty_bonus = 0.5
                self.exploration_history.append(position.copy())
            else:
                novelty_bonus = 0.0
            
            total_fitness = base_fitness + exploration_bonus + novelty_bonus
            return total_fitness
            
        except Exception as e:
            logger.warning(f"Fitness evaluation failed for explorer agent {self.agent_id}: {e}")
            return float('inf')
    
    async def communicate(self, other_agents: List[BaseAgent]) -> List[CommunicationMessage]:
        """Generate exploration discoveries."""
        messages = []
        
        try:
            # Share exploration discoveries
            if self.exploration_history:
                recent_discoveries = self.exploration_history[-5:]  # Last 5 discoveries
                
                message = CommunicationMessage(
                    message_id=f"explore_{self.agent_id}_{int(time.time())}",
                    sender_id=self.agent_id,
                    receiver_id=None,  # Broadcast
                    message_type="exploration_discovery",
                    content={
                        'discovered_positions': [pos.tolist() for pos in recent_discoveries],
                        'exploration_radius': self.exploration_radius,
                        'curiosity_factor': self.curiosity_factor,
                        'novelty_score': len(set(map(tuple, self.exploration_history)))
                    },
                    timestamp=time.time(),
                    priority=1,
                    ttl=600.0
                )
                messages.append(message)
            
            # Coordinate with other explorers
            for agent in other_agents:
                if (agent.agent_type == AgentType.EXPLORER and 
                    agent.agent_id != self.agent_id):
                    
                    # Calculate distance to coordinate exploration
                    distance = np.linalg.norm(self.position - agent.position)
                    if distance < self.exploration_radius:
                        message = CommunicationMessage(
                            message_id=f"coord_{self.agent_id}_{agent.agent_id}_{int(time.time())}",
                            sender_id=self.agent_id,
                            receiver_id=agent.agent_id,
                            message_type="exploration_coordination",
                            content={
                                'current_position': self.position.tolist(),
                                'exploration_direction': self.velocity.tolist(),
                                'suggested_coordination': 'avoid_overlap'
                            },
                            timestamp=time.time(),
                            priority=2,
                            ttl=120.0
                        )
                        messages.append(message)
            
        except Exception as e:
            logger.warning(f"Communication failed for explorer agent {self.agent_id}: {e}")
        
        return messages
    
    async def learn_from_communication(self, messages: List[CommunicationMessage]):
        """Learn from exploration discoveries."""
        try:
            for message in messages:
                if message.message_type == "exploration_discovery":
                    # Learn about new areas to explore
                    discovered_positions = message.content.get('discovered_positions', [])
                    for pos in discovered_positions:
                        if len(pos) == len(self.position):
                            pos_array = np.array(pos)
                            if pos_array not in self.exploration_history:
                                self.exploration_history.append(pos_array)
                
                elif message.message_type == "exploration_coordination":
                    # Adapt exploration strategy based on coordination
                    if 'suggested_coordination' in message.content:
                        suggestion = message.content['suggested_coordination']
                        if suggestion == 'avoid_overlap':
                            # Increase exploration radius to avoid overlap
                            self.exploration_radius *= 1.1
                
                # Record communication
                self.communication_history.append({
                    'message_id': message.message_id,
                    'sender_id': message.sender_id,
                    'message_type': message.message_type,
                    'timestamp': message.timestamp,
                    'content_summary': str(message.content)[:100]
                })
                
        except Exception as e:
            logger.warning(f"Learning failed for explorer agent {self.agent_id}: {e}")

class SwarmIntelligenceManager:
    """
    Manager for the multi-agent swarm intelligence system.
    """
    
    def __init__(
        self,
        config: SwarmConfiguration,
        fitness_function: Optional[Callable[[np.ndarray], float]] = None
    ):
        self.config = config
        self.fitness_function = fitness_function
        
        # Initialize agents
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_states: Dict[str, AgentState] = {}
        
        # Swarm state
        self.global_best_position = None
        self.global_best_fitness = float('inf')
        self.explored_positions = []
        self.swarm_metrics = SwarmMetrics(
            total_iterations=0,
            best_global_fitness=float('inf'),
            average_fitness=0.0,
            convergence_rate=0.0,
            exploration_efficiency=0.0,
            collaboration_efficiency=0.0,
            emergent_behavior_count=0,
            optimization_time=0.0,
            communication_overhead=0.0
        )
        
        # Communication and coordination
        self.message_queue = deque()
        self.communication_network = defaultdict(list)
        
        # Initialize the swarm
        self._initialize_swarm()
    
    def _initialize_swarm(self):
        """Initialize the swarm with agents."""
        try:
            # Create agents based on configuration
            agent_types = list(AgentType)
            num_agents = self.config.num_agents
            
            for i in range(num_agents):
                # Determine agent type
                if i < num_agents // 3:
                    agent_type = AgentType.OPTIMIZER
                elif i < 2 * num_agents // 3:
                    agent_type = AgentType.EXPLORER
                else:
                    agent_type = AgentType.SPECIALIST
                
                # Generate random position
                position = np.random.uniform(
                    self.config.search_space_bounds[0],
                    self.config.search_space_bounds[1],
                    self.config.search_space_dimensions
                )
                
                # Create agent
                if agent_type == AgentType.OPTIMIZER:
                    agent = OptimizerAgent(
                        agent_id=f"agent_{i}",
                        agent_type=agent_type,
                        position=position,
                        search_space_bounds=self.config.search_space_bounds,
                        optimization_objective=self.config.optimization_objective
                    )
                elif agent_type == AgentType.EXPLORER:
                    agent = ExplorerAgent(
                        agent_id=f"agent_{i}",
                        agent_type=agent_type,
                        position=position,
                        search_space_bounds=self.config.search_space_bounds,
                        optimization_objective=self.config.optimization_objective
                        )
                else:
                    # Create a basic agent for other types
                    agent = OptimizerAgent(
                        agent_id=f"agent_{i}",
                        agent_type=agent_type,
                        position=position,
                        search_space_bounds=self.config.search_space_bounds,
                        optimization_objective=self.config.optimization_objective
                    )
                
                self.agents[agent.agent_id] = agent
                self.agent_states[agent.agent_id] = agent.get_state()
            
            # Initialize global best
            if self.agents:
                first_agent = list(self.agents.values())[0]
                self.global_best_position = first_agent.position.copy()
                
            logger.info(f"Initialized swarm with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize swarm: {e}")
            raise
    
    async def run_swarm_optimization(self) -> Dict[str, Any]:
        """Run the swarm optimization process."""
        try:
            optimization_start = time.time()
            
            for iteration in range(self.config.max_iterations):
                iteration_start = time.time()
                
                # Update swarm state
                swarm_state = self._get_swarm_state()
                
                # Run agent updates
                await self._update_all_agents(swarm_state)
                
                # Handle communication
                await self._handle_agent_communication()
                
                # Update global best
                await self._update_global_best()
                
                # Check convergence
                if await self._check_convergence():
                    logger.info(f"Swarm converged at iteration {iteration}")
                    break
                
                # Update metrics
                await self._update_swarm_metrics(iteration, iteration_start)
                
                # Log progress
                if iteration % 10 == 0:
                    logger.info(f"Iteration {iteration}: Best fitness = {self.global_best_fitness:.6f}")
            
            # Final optimization time
            self.swarm_metrics.optimization_time = time.time() - optimization_start
            
            # Generate results
            results = {
                'global_best_position': self.global_best_position.tolist() if self.global_best_position is not None else None,
                'global_best_fitness': self.global_best_fitness,
                'total_iterations': self.swarm_metrics.total_iterations,
                'swarm_metrics': asdict(self.swarm_metrics),
                'agent_summaries': await self._get_agent_summaries()
            }
            
            logger.info(f"Swarm optimization completed: {results['global_best_fitness']:.6f}")
            return results
            
        except Exception as e:
            logger.error(f"Swarm optimization failed: {e}")
            raise
    
    def _get_swarm_state(self) -> Dict[str, Any]:
        """Get current swarm state for agents."""
        return {
            'global_best_position': self.global_best_position,
            'global_best_fitness': self.global_best_fitness,
            'explored_positions': self.explored_positions,
            'iteration': self.swarm_metrics.total_iterations,
            'convergence_rate': self.swarm_metrics.convergence_rate,
            'exploration_efficiency': self.swarm_metrics.exploration_efficiency
        }
    
    async def _update_all_agents(self, swarm_state: Dict[str, Any]):
        """Update all agents in the swarm."""
        try:
            update_tasks = []
            
            for agent in self.agents.values():
                if agent.is_active:
                    # Update position
                    new_position = await agent.update_position(swarm_state)
                    
                    # Evaluate fitness
                    new_fitness = await agent.evaluate_fitness(new_position)
                    
                    # Update agent state
                    agent.update_state(new_position, new_fitness)
                    
                    # Update agent states
                    self.agent_states[agent.agent_id] = agent.get_state()
                    
                    # Add to explored positions
                    self.explored_positions.append(new_position.copy())
            
        except Exception as e:
            logger.warning(f"Agent updates failed: {e}")
    
    async def _handle_agent_communication(self):
        """Handle communication between agents."""
        try:
            # Generate messages from all agents
            all_messages = []
            for agent in self.agents.values():
                if agent.is_active:
                    other_agents = [a for a in self.agents.values() if a.agent_id != agent.agent_id]
                    messages = await agent.communicate(other_agents)
                    all_messages.extend(messages)
            
            # Process messages
            for message in all_messages:
                # Add to message queue
                self.message_queue.append(message)
                
                # Deliver message to receiver
                if message.receiver_id:
                    if message.receiver_id in self.agents:
                        receiver = self.agents[message.receiver_id]
                        await receiver.learn_from_communication([message])
                else:
                    # Broadcast message
                    for agent in self.agents.values():
                        if agent.agent_id != message.sender_id:
                            await agent.learn_from_communication([message])
            
            # Clean up old messages
            current_time = time.time()
            self.message_queue = deque(
                msg for msg in self.message_queue 
                if current_time - msg.timestamp < msg.ttl
            )
            
        except Exception as e:
            logger.warning(f"Communication handling failed: {e}")
    
    async def _update_global_best(self):
        """Update global best position and fitness."""
        try:
            for agent in self.agents.values():
                if agent.is_active:
                    if self._is_better_fitness(agent.best_fitness, self.global_best_fitness):
                        self.global_best_position = agent.best_position.copy()
                        self.global_best_fitness = agent.best_fitness
                        
        except Exception as e:
            logger.warning(f"Global best update failed: {e}")
    
    async def _check_convergence(self) -> bool:
        """Check if the swarm has converged."""
        try:
            if len(self.explored_positions) < 2:
                return False
            
            # Calculate convergence based on position stability
            recent_positions = self.explored_positions[-10:]  # Last 10 positions
            if len(recent_positions) < 2:
                return False
            
            # Calculate average distance between recent positions
            total_distance = 0
            count = 0
            for i in range(len(recent_positions)):
                for j in range(i + 1, len(recent_positions)):
                    distance = np.linalg.norm(recent_positions[i] - recent_positions[j])
                    total_distance += distance
                    count += 1
            
            if count > 0:
                average_distance = total_distance / count
                return average_distance < self.config.convergence_threshold
            
            return False
            
        except Exception as e:
            logger.warning(f"Convergence check failed: {e}")
            return False
    
    async def _update_swarm_metrics(self, iteration: int, iteration_start: float):
        """Update swarm performance metrics."""
        try:
            # Update basic metrics
            self.swarm_metrics.total_iterations = iteration + 1
            self.swarm_metrics.best_global_fitness = self.global_best_fitness
            
            # Calculate average fitness
            active_agents = [a for a in self.agents.values() if a.is_active]
            if active_agents:
                total_fitness = sum(agent.current_fitness for agent in active_agents)
                self.swarm_metrics.average_fitness = total_fitness / len(active_agents)
            
            # Calculate convergence rate
            if iteration > 0:
                prev_fitness = getattr(self, '_prev_fitness', self.global_best_fitness)
                if prev_fitness != float('inf'):
                    improvement = abs(self.global_best_fitness - prev_fitness)
                    self.swarm_metrics.convergence_rate = improvement / max(abs(prev_fitness), 1e-8)
                self._prev_fitness = self.global_best_fitness
            
            # Calculate exploration efficiency
            if self.explored_positions:
                unique_positions = len(set(map(tuple, self.explored_positions)))
                total_positions = len(self.explored_positions)
                self.swarm_metrics.exploration_efficiency = unique_positions / max(total_positions, 1)
            
            # Calculate collaboration efficiency
            if self.message_queue:
                collaboration_score = len([m for m in self.message_queue if m.message_type in 
                                        ["collaboration_request", "collaboration_response"]])
                total_messages = len(self.message_queue)
                self.swarm_metrics.collaboration_efficiency = collaboration_score / max(total_messages, 1)
            
            # Detect emergent behavior
            if (self.swarm_metrics.exploration_efficiency > 0.8 and 
                self.swarm_metrics.collaboration_efficiency > 0.6):
                self.swarm_metrics.emergent_behavior_count += 1
            
        except Exception as e:
            logger.warning(f"Metrics update failed: {e}")
    
    def _is_better_fitness(self, fitness1: float, fitness2: float) -> bool:
        """Check if fitness1 is better than fitness2."""
        if self.config.optimization_objective == OptimizationObjective.PERFORMANCE:
            return fitness1 > fitness2
        elif self.config.optimization_objective == OptimizationObjective.EFFICIENCY:
            return fitness1 > fitness2
        elif self.config.optimization_objective == OptimizationObjective.ACCURACY:
            return fitness1 > fitness2
        else:
            return fitness1 < fitness2  # Default to minimization
    
    async def _get_agent_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get summaries of all agents."""
        summaries = {}
        
        for agent_id, agent in self.agents.items():
            state = self.agent_states[agent_id]
            summaries[agent_id] = {
                'agent_type': state.agent_type.value,
                'current_position': state.position.tolist(),
                'best_fitness': state.best_fitness,
                'energy_level': state.energy_level,
                'is_active': state.is_active,
                'communication_count': len(state.communication_history)
            }
        
        return summaries
    
    async def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status."""
        return {
            'num_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a.is_active),
            'global_best_fitness': self.global_best_fitness,
            'global_best_position': self.global_best_position.tolist() if self.global_best_position is not None else None,
            'swarm_metrics': asdict(self.swarm_metrics),
            'message_queue_size': len(self.message_queue),
            'explored_positions_count': len(self.explored_positions)
        }

# Example usage and testing
async def test_swarm_intelligence():
    """Test the swarm intelligence system."""
    logger.info("🧪 Testing Multi-Agent Swarm Intelligence")
    
    try:
        # Create swarm configuration
        config = SwarmConfiguration(
            num_agents=20,
            swarm_strategy=SwarmStrategy.PARTICLE_SWARM,
            communication_protocol=CommunicationProtocol.BROADCAST,
            optimization_objective=OptimizationObjective.MULTI_OBJECTIVE,
            search_space_dimensions=10,
            max_iterations=100,
            convergence_threshold=0.01,
            exploration_rate=0.3,
            exploitation_rate=0.7,
            collaboration_strength=0.8,
            emergent_behavior_enabled=True
        )
        
        # Create swarm manager
        swarm_manager = SwarmIntelligenceManager(config)
        
        logger.info(f"✅ Created swarm with {config.num_agents} agents")
        
        # Run optimization
        results = await swarm_manager.run_swarm_optimization()
        
        logger.info(f"✅ Swarm optimization completed")
        logger.info(f"   Best fitness: {results['global_best_fitness']:.6f}")
        logger.info(f"   Total iterations: {results['total_iterations']}")
        logger.info(f"   Optimization time: {results['swarm_metrics']['optimization_time']:.2f}s")
        
        # Get swarm status
        status = await swarm_manager.get_swarm_status()
        logger.info(f"✅ Swarm status: {status['active_agents']}/{status['num_agents']} agents active")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run test
    asyncio.run(test_swarm_intelligence())
