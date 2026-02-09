"""
Advanced Metaverse Service with Virtual Worlds and Digital Assets
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import math
from collections import defaultdict, deque
import random

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class MetaverseType(Enum):
    """Metaverse types"""
    VIRTUAL_WORLD = "virtual_world"
    GAMING_METAVERSE = "gaming_metaverse"
    SOCIAL_METAVERSE = "social_metaverse"
    EDUCATIONAL_METAVERSE = "educational_metaverse"
    BUSINESS_METAVERSE = "business_metaverse"
    CREATIVE_METAVERSE = "creative_metaverse"
    HYBRID_METAVERSE = "hybrid_metaverse"

class AssetType(Enum):
    """Digital asset types"""
    AVATAR = "avatar"
    LAND = "land"
    BUILDING = "building"
    VEHICLE = "vehicle"
    WEAPON = "weapon"
    CLOTHING = "clothing"
    ACCESSORY = "accessory"
    TOOL = "tool"
    DECORATION = "decoration"
    NFT = "nft"
    CURRENCY = "currency"
    TOKEN = "token"

class InteractionType(Enum):
    """Metaverse interaction types"""
    CHAT = "chat"
    VOICE = "voice"
    GESTURE = "gesture"
    MOVEMENT = "movement"
    TRADE = "trade"
    COLLABORATE = "collaborate"
    GAME = "game"
    LEARN = "learn"
    CREATE = "create"
    SHARE = "share"

class WorldStatus(Enum):
    """World status"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    DEVELOPMENT = "development"
    TESTING = "testing"

@dataclass
class MetaverseWorld:
    """Metaverse world definition"""
    id: str
    name: str
    world_type: MetaverseType
    description: str
    status: WorldStatus
    max_players: int = 100
    current_players: int = 0
    world_size: Tuple[float, float, float] = (1000.0, 1000.0, 1000.0)
    spawn_point: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    physics_enabled: bool = True
    gravity: float = -9.81
    lighting: Dict[str, Any] = field(default_factory=dict)
    weather: Dict[str, Any] = field(default_factory=dict)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DigitalAsset:
    """Digital asset definition"""
    id: str
    name: str
    asset_type: AssetType
    world_id: str
    owner_id: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    properties: Dict[str, Any] = field(default_factory=dict)
    rarity: str = "common"
    value: float = 0.0
    is_tradeable: bool = True
    is_transferable: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetaverseUser:
    """Metaverse user definition"""
    id: str
    username: str
    avatar_id: str
    current_world_id: Optional[str] = None
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    inventory: List[str] = field(default_factory=list)
    wallet: Dict[str, float] = field(default_factory=dict)
    reputation: float = 0.0
    level: int = 1
    experience: int = 0
    status: str = "online"
    last_seen: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetaverseEvent:
    """Metaverse event definition"""
    id: str
    world_id: str
    event_type: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    max_participants: int = 100
    current_participants: int = 0
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    requirements: List[Dict[str, Any]] = field(default_factory=list)
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetaverseInteraction:
    """Metaverse interaction definition"""
    id: str
    user_id: str
    world_id: str
    interaction_type: InteractionType
    target_id: Optional[str] = None
    position: Optional[Tuple[float, float, float]] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedMetaverseService:
    """Advanced Metaverse Service with Virtual Worlds and Digital Assets"""
    
    def __init__(self):
        self.worlds = {}
        self.assets = {}
        self.users = {}
        self.events = {}
        self.interactions = {}
        self.world_instances = {}
        self.asset_marketplace = {}
        self.social_networks = {}
        
        # Background processing
        self.world_update_queue = asyncio.Queue()
        self.interaction_queue = asyncio.Queue()
        self.economy_queue = asyncio.Queue()
        
        # Initialize metaverse components
        self._initialize_metaverse_components()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced Metaverse Service initialized")
    
    def _initialize_metaverse_components(self):
        """Initialize metaverse components"""
        try:
            # Initialize world processors
            self.world_processors = {
                MetaverseType.VIRTUAL_WORLD: self._process_virtual_world,
                MetaverseType.GAMING_METAVERSE: self._process_gaming_metaverse,
                MetaverseType.SOCIAL_METAVERSE: self._process_social_metaverse,
                MetaverseType.EDUCATIONAL_METAVERSE: self._process_educational_metaverse,
                MetaverseType.BUSINESS_METAVERSE: self._process_business_metaverse,
                MetaverseType.CREATIVE_METAVERSE: self._process_creative_metaverse,
                MetaverseType.HYBRID_METAVERSE: self._process_hybrid_metaverse
            }
            
            # Initialize interaction handlers
            self.interaction_handlers = {
                InteractionType.CHAT: self._handle_chat_interaction,
                InteractionType.VOICE: self._handle_voice_interaction,
                InteractionType.GESTURE: self._handle_gesture_interaction,
                InteractionType.MOVEMENT: self._handle_movement_interaction,
                InteractionType.TRADE: self._handle_trade_interaction,
                InteractionType.COLLABORATE: self._handle_collaborate_interaction,
                InteractionType.GAME: self._handle_game_interaction,
                InteractionType.LEARN: self._handle_learn_interaction,
                InteractionType.CREATE: self._handle_create_interaction,
                InteractionType.SHARE: self._handle_share_interaction
            }
            
            # Initialize asset processors
            self.asset_processors = {
                AssetType.AVATAR: self._process_avatar_asset,
                AssetType.LAND: self._process_land_asset,
                AssetType.BUILDING: self._process_building_asset,
                AssetType.VEHICLE: self._process_vehicle_asset,
                AssetType.WEAPON: self._process_weapon_asset,
                AssetType.CLOTHING: self._process_clothing_asset,
                AssetType.ACCESSORY: self._process_accessory_asset,
                AssetType.TOOL: self._process_tool_asset,
                AssetType.DECORATION: self._process_decoration_asset,
                AssetType.NFT: self._process_nft_asset,
                AssetType.CURRENCY: self._process_currency_asset,
                AssetType.TOKEN: self._process_token_asset
            }
            
            logger.info("Metaverse components initialized")
            
        except Exception as e:
            logger.error(f"Error initializing metaverse components: {e}")
    
    def _start_background_tasks(self):
        """Start background tasks"""
        try:
            # Start world update processor
            asyncio.create_task(self._process_world_updates())
            
            # Start interaction processor
            asyncio.create_task(self._process_interactions())
            
            # Start economy processor
            asyncio.create_task(self._process_economy())
            
            # Start world monitoring
            asyncio.create_task(self._monitor_worlds())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_world_updates(self):
        """Process world updates"""
        try:
            while True:
                try:
                    await asyncio.sleep(0.1)  # 10 FPS updates
                    await self._update_all_worlds()
                except Exception as e:
                    logger.error(f"Error processing world updates: {e}")
                    
        except Exception as e:
            logger.error(f"Error in world update processor: {e}")
    
    async def _process_interactions(self):
        """Process metaverse interactions"""
        try:
            while True:
                try:
                    interaction = await asyncio.wait_for(self.interaction_queue.get(), timeout=1.0)
                    await self._handle_metaverse_interaction(interaction)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing interaction: {e}")
                    
        except Exception as e:
            logger.error(f"Error in interaction processor: {e}")
    
    async def _process_economy(self):
        """Process metaverse economy"""
        try:
            while True:
                try:
                    await asyncio.sleep(1.0)  # Process economy every second
                    await self._update_economy()
                except Exception as e:
                    logger.error(f"Error processing economy: {e}")
                    
        except Exception as e:
            logger.error(f"Error in economy processor: {e}")
    
    async def _monitor_worlds(self):
        """Monitor metaverse worlds"""
        try:
            while True:
                try:
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                    current_time = datetime.utcnow()
                    
                    for world_id, world in self.worlds.items():
                        # Check world health
                        if world.status == WorldStatus.ACTIVE:
                            # Check player count
                            if world.current_players > world.max_players * 0.9:
                                await self._create_world_alert(world_id, "high_player_count", 
                                                            f"World {world.name} is at {world.current_players}/{world.max_players} capacity")
                            
                            # Check for inactive users
                            await self._cleanup_inactive_users(world_id)
                    
                except Exception as e:
                    logger.error(f"Error monitoring worlds: {e}")
                    
        except Exception as e:
            logger.error(f"Error in world monitor: {e}")
    
    async def create_metaverse_world(self, name: str, world_type: MetaverseType, 
                                   description: str, max_players: int = 100) -> str:
        """Create metaverse world"""
        try:
            world_id = str(uuid.uuid4())
            world = MetaverseWorld(
                id=world_id,
                name=name,
                world_type=world_type,
                description=description,
                status=WorldStatus.ACTIVE,
                max_players=max_players
            )
            
            self.worlds[world_id] = world
            
            # Initialize world instance
            self.world_instances[world_id] = {
                'players': {},
                'assets': {},
                'events': {},
                'chat_history': deque(maxlen=1000),
                'last_update': datetime.utcnow()
            }
            
            logger.info(f"Metaverse world created: {world_id}")
            
            return world_id
            
        except Exception as e:
            logger.error(f"Error creating metaverse world: {e}")
            raise
    
    async def register_metaverse_user(self, username: str, avatar_id: str) -> str:
        """Register metaverse user"""
        try:
            user_id = str(uuid.uuid4())
            user = MetaverseUser(
                id=user_id,
                username=username,
                avatar_id=avatar_id,
                wallet={'metaverse_coin': 1000.0, 'experience_points': 0.0}
            )
            
            self.users[user_id] = user
            
            logger.info(f"Metaverse user registered: {user_id}")
            
            return user_id
            
        except Exception as e:
            logger.error(f"Error registering metaverse user: {e}")
            raise
    
    async def join_world(self, user_id: str, world_id: str, spawn_position: Tuple[float, float, float] = None) -> bool:
        """Join metaverse world"""
        try:
            if user_id not in self.users:
                raise ValueError(f"User not found: {user_id}")
            
            if world_id not in self.worlds:
                raise ValueError(f"World not found: {world_id}")
            
            user = self.users[user_id]
            world = self.worlds[world_id]
            
            # Check if world is full
            if world.current_players >= world.max_players:
                raise ValueError("World is full")
            
            # Leave current world if any
            if user.current_world_id:
                await self.leave_world(user_id)
            
            # Set spawn position
            if spawn_position is None:
                spawn_position = world.spawn_point
            
            user.current_world_id = world_id
            user.position = spawn_position
            user.status = "online"
            user.last_seen = datetime.utcnow()
            
            # Update world
            world.current_players += 1
            
            # Add to world instance
            self.world_instances[world_id]['players'][user_id] = {
                'user': user,
                'last_activity': datetime.utcnow(),
                'session_start': datetime.utcnow()
            }
            
            logger.info(f"User {user_id} joined world {world_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error joining world: {e}")
            raise
    
    async def leave_world(self, user_id: str) -> bool:
        """Leave metaverse world"""
        try:
            if user_id not in self.users:
                raise ValueError(f"User not found: {user_id}")
            
            user = self.users[user_id]
            
            if not user.current_world_id:
                return True
            
            world_id = user.current_world_id
            world = self.worlds[world_id]
            
            # Remove from world instance
            if world_id in self.world_instances:
                if user_id in self.world_instances[world_id]['players']:
                    del self.world_instances[world_id]['players'][user_id]
            
            # Update world
            world.current_players = max(0, world.current_players - 1)
            
            # Update user
            user.current_world_id = None
            user.status = "offline"
            user.last_seen = datetime.utcnow()
            
            logger.info(f"User {user_id} left world {world_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error leaving world: {e}")
            raise
    
    async def create_digital_asset(self, name: str, asset_type: AssetType, 
                                 world_id: str, owner_id: str, 
                                 position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
                                 properties: Dict[str, Any] = None) -> str:
        """Create digital asset"""
        try:
            if world_id not in self.worlds:
                raise ValueError(f"World not found: {world_id}")
            
            if owner_id not in self.users:
                raise ValueError(f"User not found: {owner_id}")
            
            asset_id = str(uuid.uuid4())
            asset = DigitalAsset(
                id=asset_id,
                name=name,
                asset_type=asset_type,
                world_id=world_id,
                owner_id=owner_id,
                position=position,
                properties=properties or {}
            )
            
            self.assets[asset_id] = asset
            
            # Add to world instance
            if world_id in self.world_instances:
                self.world_instances[world_id]['assets'][asset_id] = asset
            
            # Add to user inventory
            self.users[owner_id].inventory.append(asset_id)
            
            logger.info(f"Digital asset created: {asset_id}")
            
            return asset_id
            
        except Exception as e:
            logger.error(f"Error creating digital asset: {e}")
            raise
    
    async def process_interaction(self, user_id: str, world_id: str, 
                                interaction_type: InteractionType,
                                target_id: str = None, position: Tuple[float, float, float] = None,
                                data: Dict[str, Any] = None) -> str:
        """Process metaverse interaction"""
        try:
            if user_id not in self.users:
                raise ValueError(f"User not found: {user_id}")
            
            if world_id not in self.worlds:
                raise ValueError(f"World not found: {world_id}")
            
            interaction_id = str(uuid.uuid4())
            interaction = MetaverseInteraction(
                id=interaction_id,
                user_id=user_id,
                world_id=world_id,
                interaction_type=interaction_type,
                target_id=target_id,
                position=position,
                data=data or {}
            )
            
            self.interactions[interaction_id] = interaction
            
            # Add to interaction queue
            await self.interaction_queue.put(interaction)
            
            logger.info(f"Metaverse interaction processed: {interaction_id}")
            
            return interaction_id
            
        except Exception as e:
            logger.error(f"Error processing interaction: {e}")
            raise
    
    async def _handle_metaverse_interaction(self, interaction: MetaverseInteraction):
        """Handle metaverse interaction"""
        try:
            handler = self.interaction_handlers.get(interaction.interaction_type)
            if handler:
                await handler(interaction)
            
            # Update user activity
            if interaction.user_id in self.users:
                self.users[interaction.user_id].last_seen = datetime.utcnow()
            
            # Update world instance
            world_id = interaction.world_id
            if world_id in self.world_instances:
                if interaction.user_id in self.world_instances[world_id]['players']:
                    self.world_instances[world_id]['players'][interaction.user_id]['last_activity'] = datetime.utcnow()
            
            logger.info(f"Interaction handled: {interaction.id}")
            
        except Exception as e:
            logger.error(f"Error handling interaction: {e}")
    
    async def _handle_chat_interaction(self, interaction: MetaverseInteraction):
        """Handle chat interaction"""
        try:
            message = interaction.data.get('message', '')
            chat_type = interaction.data.get('chat_type', 'global')
            
            # Add to chat history
            world_id = interaction.world_id
            if world_id in self.world_instances:
                chat_entry = {
                    'user_id': interaction.user_id,
                    'username': self.users[interaction.user_id].username,
                    'message': message,
                    'chat_type': chat_type,
                    'timestamp': interaction.timestamp
                }
                self.world_instances[world_id]['chat_history'].append(chat_entry)
            
            logger.info(f"Chat interaction handled: {message[:50]}...")
            
        except Exception as e:
            logger.error(f"Error handling chat interaction: {e}")
    
    async def _handle_voice_interaction(self, interaction: MetaverseInteraction):
        """Handle voice interaction"""
        try:
            voice_data = interaction.data.get('voice_data', {})
            voice_type = voice_data.get('type', 'speech')
            
            # Process voice data
            if voice_type == 'speech':
                # Handle speech recognition
                pass
            elif voice_type == 'command':
                # Handle voice commands
                pass
            
            logger.info(f"Voice interaction handled: {voice_type}")
            
        except Exception as e:
            logger.error(f"Error handling voice interaction: {e}")
    
    async def _handle_gesture_interaction(self, interaction: MetaverseInteraction):
        """Handle gesture interaction"""
        try:
            gesture_data = interaction.data.get('gesture_data', {})
            gesture_type = gesture_data.get('type', 'wave')
            
            # Process gesture
            if gesture_type == 'wave':
                # Handle wave gesture
                pass
            elif gesture_type == 'point':
                # Handle pointing gesture
                pass
            elif gesture_type == 'dance':
                # Handle dance gesture
                pass
            
            logger.info(f"Gesture interaction handled: {gesture_type}")
            
        except Exception as e:
            logger.error(f"Error handling gesture interaction: {e}")
    
    async def _handle_movement_interaction(self, interaction: MetaverseInteraction):
        """Handle movement interaction"""
        try:
            movement_data = interaction.data.get('movement_data', {})
            new_position = movement_data.get('position', interaction.position)
            new_rotation = movement_data.get('rotation', (0.0, 0.0, 0.0))
            
            # Update user position
            if interaction.user_id in self.users:
                user = self.users[interaction.user_id]
                user.position = new_position
                user.rotation = new_rotation
            
            logger.info(f"Movement interaction handled: {new_position}")
            
        except Exception as e:
            logger.error(f"Error handling movement interaction: {e}")
    
    async def _handle_trade_interaction(self, interaction: MetaverseInteraction):
        """Handle trade interaction"""
        try:
            trade_data = interaction.data.get('trade_data', {})
            target_user_id = trade_data.get('target_user_id')
            offered_assets = trade_data.get('offered_assets', [])
            requested_assets = trade_data.get('requested_assets', [])
            
            # Process trade
            if target_user_id and target_user_id in self.users:
                # Validate trade
                trade_valid = await self._validate_trade(interaction.user_id, target_user_id, 
                                                       offered_assets, requested_assets)
                
                if trade_valid:
                    # Execute trade
                    await self._execute_trade(interaction.user_id, target_user_id, 
                                            offered_assets, requested_assets)
            
            logger.info(f"Trade interaction handled")
            
        except Exception as e:
            logger.error(f"Error handling trade interaction: {e}")
    
    async def _handle_collaborate_interaction(self, interaction: MetaverseInteraction):
        """Handle collaborate interaction"""
        try:
            collaboration_data = interaction.data.get('collaboration_data', {})
            collaboration_type = collaboration_data.get('type', 'build')
            target_asset_id = collaboration_data.get('target_asset_id')
            
            # Process collaboration
            if collaboration_type == 'build':
                # Handle building collaboration
                pass
            elif collaboration_type == 'create':
                # Handle creation collaboration
                pass
            elif collaboration_type == 'solve':
                # Handle problem solving collaboration
                pass
            
            logger.info(f"Collaborate interaction handled: {collaboration_type}")
            
        except Exception as e:
            logger.error(f"Error handling collaborate interaction: {e}")
    
    async def _handle_game_interaction(self, interaction: MetaverseInteraction):
        """Handle game interaction"""
        try:
            game_data = interaction.data.get('game_data', {})
            game_type = game_data.get('type', 'puzzle')
            game_action = game_data.get('action', 'start')
            
            # Process game interaction
            if game_type == 'puzzle':
                # Handle puzzle game
                pass
            elif game_type == 'race':
                # Handle racing game
                pass
            elif game_type == 'battle':
                # Handle battle game
                pass
            
            logger.info(f"Game interaction handled: {game_type}")
            
        except Exception as e:
            logger.error(f"Error handling game interaction: {e}")
    
    async def _handle_learn_interaction(self, interaction: MetaverseInteraction):
        """Handle learn interaction"""
        try:
            learning_data = interaction.data.get('learning_data', {})
            learning_type = learning_data.get('type', 'tutorial')
            content_id = learning_data.get('content_id')
            
            # Process learning interaction
            if learning_type == 'tutorial':
                # Handle tutorial
                pass
            elif learning_type == 'course':
                # Handle course
                pass
            elif learning_type == 'workshop':
                # Handle workshop
                pass
            
            logger.info(f"Learn interaction handled: {learning_type}")
            
        except Exception as e:
            logger.error(f"Error handling learn interaction: {e}")
    
    async def _handle_create_interaction(self, interaction: MetaverseInteraction):
        """Handle create interaction"""
        try:
            creation_data = interaction.data.get('creation_data', {})
            creation_type = creation_data.get('type', 'object')
            creation_properties = creation_data.get('properties', {})
            
            # Process creation interaction
            if creation_type == 'object':
                # Handle object creation
                pass
            elif creation_type == 'building':
                # Handle building creation
                pass
            elif creation_type == 'art':
                # Handle art creation
                pass
            
            logger.info(f"Create interaction handled: {creation_type}")
            
        except Exception as e:
            logger.error(f"Error handling create interaction: {e}")
    
    async def _handle_share_interaction(self, interaction: MetaverseInteraction):
        """Handle share interaction"""
        try:
            share_data = interaction.data.get('share_data', {})
            share_type = share_data.get('type', 'asset')
            target_user_id = share_data.get('target_user_id')
            shared_content = share_data.get('content')
            
            # Process share interaction
            if share_type == 'asset':
                # Handle asset sharing
                pass
            elif share_type == 'experience':
                # Handle experience sharing
                pass
            elif share_type == 'knowledge':
                # Handle knowledge sharing
                pass
            
            logger.info(f"Share interaction handled: {share_type}")
            
        except Exception as e:
            logger.error(f"Error handling share interaction: {e}")
    
    async def _update_all_worlds(self):
        """Update all metaverse worlds"""
        try:
            current_time = datetime.utcnow()
            
            for world_id, world in self.worlds.items():
                if world.status == WorldStatus.ACTIVE:
                    # Update world physics
                    await self._update_world_physics(world_id)
                    
                    # Update world events
                    await self._update_world_events(world_id)
                    
                    # Update world economy
                    await self._update_world_economy(world_id)
                    
                    # Update world instance
                    if world_id in self.world_instances:
                        self.world_instances[world_id]['last_update'] = current_time
            
        except Exception as e:
            logger.error(f"Error updating worlds: {e}")
    
    async def _update_world_physics(self, world_id: str):
        """Update world physics"""
        try:
            world = self.worlds[world_id]
            
            if world.physics_enabled and world_id in self.world_instances:
                # Update physics for all objects in world
                for asset_id, asset in self.world_instances[world_id]['assets'].items():
                    # Apply gravity
                    if 'velocity' in asset.properties:
                        velocity = asset.properties['velocity']
                        velocity[1] += world.gravity * 0.1  # Apply gravity
                        asset.properties['velocity'] = velocity
                        
                        # Update position
                        new_position = (
                            asset.position[0] + velocity[0] * 0.1,
                            asset.position[1] + velocity[1] * 0.1,
                            asset.position[2] + velocity[2] * 0.1
                        )
                        asset.position = new_position
            
        except Exception as e:
            logger.error(f"Error updating world physics: {e}")
    
    async def _update_world_events(self, world_id: str):
        """Update world events"""
        try:
            current_time = datetime.utcnow()
            
            # Check for active events
            for event_id, event in self.events.items():
                if event.world_id == world_id:
                    if event.start_time <= current_time <= event.end_time:
                        # Event is active
                        await self._process_active_event(event)
                    elif current_time > event.end_time:
                        # Event has ended
                        await self._process_ended_event(event)
            
        except Exception as e:
            logger.error(f"Error updating world events: {e}")
    
    async def _update_world_economy(self, world_id: str):
        """Update world economy"""
        try:
            # Update asset values based on supply and demand
            for asset_id, asset in self.assets.items():
                if asset.world_id == world_id:
                    # Simple economy simulation
                    demand_factor = random.uniform(0.8, 1.2)
                    asset.value *= demand_factor
                    
                    # Ensure minimum value
                    asset.value = max(asset.value, 0.01)
            
        except Exception as e:
            logger.error(f"Error updating world economy: {e}")
    
    async def _update_economy(self):
        """Update metaverse economy"""
        try:
            # Update global economy metrics
            total_assets = len(self.assets)
            total_users = len(self.users)
            total_worlds = len(self.worlds)
            
            # Calculate economy health
            economy_health = {
                'total_assets': total_assets,
                'total_users': total_users,
                'total_worlds': total_worlds,
                'average_asset_value': sum(asset.value for asset in self.assets.values()) / max(total_assets, 1),
                'total_economy_value': sum(asset.value for asset in self.assets.values()),
                'timestamp': datetime.utcnow()
            }
            
            # Store economy metrics
            self.economy_metrics = economy_health
            
        except Exception as e:
            logger.error(f"Error updating economy: {e}")
    
    async def _cleanup_inactive_users(self, world_id: str):
        """Cleanup inactive users from world"""
        try:
            if world_id not in self.world_instances:
                return
            
            current_time = datetime.utcnow()
            inactive_threshold = timedelta(minutes=5)
            
            inactive_users = []
            for user_id, user_data in self.world_instances[world_id]['players'].items():
                if current_time - user_data['last_activity'] > inactive_threshold:
                    inactive_users.append(user_id)
            
            # Remove inactive users
            for user_id in inactive_users:
                await self.leave_world(user_id)
                logger.info(f"Removed inactive user {user_id} from world {world_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive users: {e}")
    
    async def _create_world_alert(self, world_id: str, alert_type: str, message: str):
        """Create world alert"""
        try:
            logger.warning(f"World alert: {world_id} - {alert_type}: {message}")
            
        except Exception as e:
            logger.error(f"Error creating world alert: {e}")
    
    async def _validate_trade(self, user1_id: str, user2_id: str, 
                            offered_assets: List[str], requested_assets: List[str]) -> bool:
        """Validate trade between users"""
        try:
            user1 = self.users[user1_id]
            user2 = self.users[user2_id]
            
            # Check if users own the offered assets
            for asset_id in offered_assets:
                if asset_id not in user1.inventory:
                    return False
            
            for asset_id in requested_assets:
                if asset_id not in user2.inventory:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating trade: {e}")
            return False
    
    async def _execute_trade(self, user1_id: str, user2_id: str, 
                           offered_assets: List[str], requested_assets: List[str]):
        """Execute trade between users"""
        try:
            user1 = self.users[user1_id]
            user2 = self.users[user2_id]
            
            # Transfer assets
            for asset_id in offered_assets:
                if asset_id in user1.inventory:
                    user1.inventory.remove(asset_id)
                    user2.inventory.append(asset_id)
                    
                    # Update asset owner
                    if asset_id in self.assets:
                        self.assets[asset_id].owner_id = user2_id
            
            for asset_id in requested_assets:
                if asset_id in user2.inventory:
                    user2.inventory.remove(asset_id)
                    user1.inventory.append(asset_id)
                    
                    # Update asset owner
                    if asset_id in self.assets:
                        self.assets[asset_id].owner_id = user1_id
            
            logger.info(f"Trade executed between {user1_id} and {user2_id}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    async def _process_active_event(self, event: MetaverseEvent):
        """Process active event"""
        try:
            # Handle active event logic
            pass
            
        except Exception as e:
            logger.error(f"Error processing active event: {e}")
    
    async def _process_ended_event(self, event: MetaverseEvent):
        """Process ended event"""
        try:
            # Handle ended event logic
            pass
            
        except Exception as e:
            logger.error(f"Error processing ended event: {e}")
    
    async def get_world_status(self, world_id: str) -> Optional[Dict[str, Any]]:
        """Get world status"""
        try:
            if world_id not in self.worlds:
                return None
            
            world = self.worlds[world_id]
            world_instance = self.world_instances.get(world_id, {})
            
            return {
                'id': world.id,
                'name': world.name,
                'type': world.world_type.value,
                'status': world.status.value,
                'current_players': world.current_players,
                'max_players': world.max_players,
                'world_size': world.world_size,
                'spawn_point': world.spawn_point,
                'physics_enabled': world.physics_enabled,
                'gravity': world.gravity,
                'active_players': len(world_instance.get('players', {})),
                'total_assets': len(world_instance.get('assets', {})),
                'created_at': world.created_at.isoformat(),
                'updated_at': world.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting world status: {e}")
            return None
    
    async def get_user_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user status"""
        try:
            if user_id not in self.users:
                return None
            
            user = self.users[user_id]
            
            return {
                'id': user.id,
                'username': user.username,
                'avatar_id': user.avatar_id,
                'current_world_id': user.current_world_id,
                'position': user.position,
                'rotation': user.rotation,
                'inventory_count': len(user.inventory),
                'wallet': user.wallet,
                'reputation': user.reputation,
                'level': user.level,
                'experience': user.experience,
                'status': user.status,
                'last_seen': user.last_seen.isoformat(),
                'created_at': user.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user status: {e}")
            return None
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Metaverse Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'worlds': {
                    'total': len(self.worlds),
                    'active': len([w for w in self.worlds.values() if w.status == WorldStatus.ACTIVE]),
                    'by_type': {}
                },
                'users': {
                    'total': len(self.users),
                    'online': len([u for u in self.users.values() if u.status == 'online']),
                    'offline': len([u for u in self.users.values() if u.status == 'offline'])
                },
                'assets': {
                    'total': len(self.assets),
                    'by_type': {}
                },
                'events': {
                    'total': len(self.events),
                    'active': len([e for e in self.events.values() if e.start_time <= datetime.utcnow() <= e.end_time])
                },
                'interactions': {
                    'total': len(self.interactions),
                    'by_type': {}
                },
                'economy': {
                    'total_assets': len(self.assets),
                    'total_users': len(self.users),
                    'total_worlds': len(self.worlds),
                    'average_asset_value': sum(asset.value for asset in self.assets.values()) / max(len(self.assets), 1),
                    'total_economy_value': sum(asset.value for asset in self.assets.values())
                },
                'world_processors': {
                    'available': len(self.world_processors),
                    'types': [t.value for t in self.world_processors.keys()]
                },
                'interaction_handlers': {
                    'available': len(self.interaction_handlers),
                    'types': [t.value for t in self.interaction_handlers.keys()]
                },
                'asset_processors': {
                    'available': len(self.asset_processors),
                    'types': [t.value for t in self.asset_processors.keys()]
                },
                'queues': {
                    'world_update_queue_size': self.world_update_queue.qsize(),
                    'interaction_queue_size': self.interaction_queue.qsize(),
                    'economy_queue_size': self.economy_queue.qsize()
                }
            }
            
            # Count worlds by type
            for world in self.worlds.values():
                world_type = world.world_type.value
                status['worlds']['by_type'][world_type] = status['worlds']['by_type'].get(world_type, 0) + 1
            
            # Count assets by type
            for asset in self.assets.values():
                asset_type = asset.asset_type.value
                status['assets']['by_type'][asset_type] = status['assets']['by_type'].get(asset_type, 0) + 1
            
            # Count interactions by type
            for interaction in self.interactions.values():
                interaction_type = interaction.interaction_type.value
                status['interactions']['by_type'][interaction_type] = status['interactions']['by_type'].get(interaction_type, 0) + 1
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Metaverse Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























