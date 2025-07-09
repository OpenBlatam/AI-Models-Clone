"""
Sequence Handler for Email Sequence System

Manages tokenized sequences, batch processing, and sequence optimization
for efficient text processing and model training.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, Sampler

from .tokenization_engine import AdvancedTokenizer, SequenceInfo, TokenizationConfig
from ..models.sequence import EmailSequence, SequenceStep
from ..models.subscriber import Subscriber
from ..models.template import EmailTemplate

logger = logging.getLogger(__name__)


@dataclass
class SequenceBatch:
    """Batch of tokenized sequences"""
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    token_type_ids: Optional[torch.Tensor] = None
    labels: Optional[torch.Tensor] = None
    metadata: Dict[str, Any] = None


@dataclass
class SequenceConfig:
    """Configuration for sequence handling"""
    batch_size: int = 32
    max_sequence_length: int = 512
    shuffle: bool = True
    num_workers: int = 4
    pin_memory: bool = True
    drop_last: bool = False
    collate_fn: Optional[callable] = None


class EmailSequenceDataset(Dataset):
    """Custom dataset for email sequences"""
    
    def __init__(
        self, 
        sequences: List[EmailSequence],
        subscribers: List[Subscriber],
        templates: List[EmailTemplate],
        tokenizer: AdvancedTokenizer,
        config: SequenceConfig
    ):
        self.sequences = sequences
        self.subscribers = subscribers
        self.templates = templates
        self.tokenizer = tokenizer
        self.config = config
        
        # Pre-tokenize all sequences
        self.tokenized_data = []
        self._preprocess_sequences()
    
    def _preprocess_sequences(self):
        """Preprocess and tokenize all sequences"""
        
        for i, sequence in enumerate(self.sequences):
            subscriber = self.subscribers[i % len(self.subscribers)]
            template = self.templates[i % len(self.templates)]
            
            # Tokenize each step
            for step in sequence.steps:
                context_text = self.tokenizer._create_context_text(step, subscriber, template)
                
                # Use email-specific tokenization
                sequence_info = asyncio.run(
                    self.tokenizer.tokenize_text(context_text, "email_specific")
                )
                
                self.tokenized_data.append({
                    "sequence_id": sequence.id,
                    "step_order": step.order,
                    "subscriber_id": subscriber.id,
                    "template_id": template.id,
                    "sequence_info": sequence_info,
                    "metadata": {
                        "sequence_name": sequence.name,
                        "subscriber_email": subscriber.email,
                        "template_name": template.name,
                        "step_content_length": len(step.content or ""),
                        "delay_hours": step.delay_hours
                    }
                })
    
    def __len__(self):
        return len(self.tokenized_data)
    
    def __getitem__(self, idx):
        data = self.tokenized_data[idx]
        sequence_info = data["sequence_info"]
        
        return {
            "input_ids": sequence_info.input_ids.squeeze(),
            "attention_mask": sequence_info.attention_mask.squeeze(),
            "token_type_ids": sequence_info.token_type_ids.squeeze() if sequence_info.token_type_ids is not None else None,
            "labels": torch.tensor(1.0),  # Placeholder for optimization target
            "metadata": data["metadata"]
        }


class SmartBatchSampler(Sampler):
    """Smart batch sampler for efficient sequence processing"""
    
    def __init__(self, dataset: EmailSequenceDataset, batch_size: int, shuffle: bool = True):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        
        # Group sequences by length for efficient batching
        self.length_groups = self._group_by_length()
    
    def _group_by_length(self) -> Dict[int, List[int]]:
        """Group sequences by length for efficient batching"""
        
        length_groups = defaultdict(list)
        
        for idx, data in enumerate(self.dataset.tokenized_data):
            length = data["sequence_info"].length
            length_groups[length].append(idx)
        
        return dict(length_groups)
    
    def __iter__(self):
        if self.shuffle:
            # Shuffle within each length group
            for length in self.length_groups:
                np.random.shuffle(self.length_groups[length])
        
        # Create batches from each length group
        batches = []
        for length, indices in self.length_groups.items():
            for i in range(0, len(indices), self.batch_size):
                batch_indices = indices[i:i + self.batch_size]
                batches.extend(batch_indices)
        
        if self.shuffle:
            np.random.shuffle(batches)
        
        return iter(batches)
    
    def __len__(self):
        return len(self.dataset)


class SequenceHandler:
    """Handles sequence processing and batch management"""
    
    def __init__(self, config: SequenceConfig):
        self.config = config
        self.tokenizer = AdvancedTokenizer(TokenizationConfig())
        
        # Sequence processing statistics
        self.processing_stats = defaultdict(int)
        self.batch_stats = defaultdict(int)
        
        logger.info("Sequence Handler initialized")
    
    async def create_sequence_dataset(
        self,
        sequences: List[EmailSequence],
        subscribers: List[Subscriber],
        templates: List[EmailTemplate]
    ) -> EmailSequenceDataset:
        """Create dataset from email sequences"""
        
        dataset = EmailSequenceDataset(
            sequences=sequences,
            subscribers=subscribers,
            templates=templates,
            tokenizer=self.tokenizer,
            config=self.config
        )
        
        self.processing_stats["datasets_created"] += 1
        self.processing_stats["total_sequences"] += len(sequences)
        
        return dataset
    
    def create_dataloader(
        self, 
        dataset: EmailSequenceDataset,
        use_smart_sampling: bool = True
    ) -> DataLoader:
        """Create DataLoader with optional smart sampling"""
        
        if use_smart_sampling:
            sampler = SmartBatchSampler(
                dataset, 
                self.config.batch_size, 
                self.config.shuffle
            )
            
            dataloader = DataLoader(
                dataset,
                batch_sampler=sampler,
                num_workers=self.config.num_workers,
                pin_memory=self.config.pin_memory,
                collate_fn=self._collate_fn
            )
        else:
            dataloader = DataLoader(
                dataset,
                batch_size=self.config.batch_size,
                shuffle=self.config.shuffle,
                num_workers=self.config.num_workers,
                pin_memory=self.config.pin_memory,
                drop_last=self.config.drop_last,
                collate_fn=self._collate_fn
            )
        
        self.batch_stats["dataloaders_created"] += 1
        
        return dataloader
    
    def _collate_fn(self, batch: List[Dict[str, Any]]) -> SequenceBatch:
        """Custom collate function for sequence batching"""
        
        # Extract tensors
        input_ids = [item["input_ids"] for item in batch]
        attention_masks = [item["attention_mask"] for item in batch]
        token_type_ids = [item["token_type_ids"] for item in batch if item["token_type_ids"] is not None]
        labels = [item["labels"] for item in batch]
        metadata = [item["metadata"] for item in batch]
        
        # Pad sequences to max length in batch
        max_length = max(len(ids) for ids in input_ids)
        
        # Pad input_ids
        padded_input_ids = []
        for ids in input_ids:
            padding_length = max_length - len(ids)
            padded_ids = torch.cat([ids, torch.zeros(padding_length, dtype=ids.dtype)])
            padded_input_ids.append(padded_ids)
        
        # Pad attention masks
        padded_attention_masks = []
        for mask in attention_masks:
            padding_length = max_length - len(mask)
            padded_mask = torch.cat([mask, torch.zeros(padding_length, dtype=mask.dtype)])
            padded_attention_masks.append(padded_mask)
        
        # Pad token_type_ids if present
        padded_token_type_ids = None
        if token_type_ids:
            padded_token_type_ids = []
            for type_ids in token_type_ids:
                padding_length = max_length - len(type_ids)
                padded_type_ids = torch.cat([type_ids, torch.zeros(padding_length, dtype=type_ids.dtype)])
                padded_token_type_ids.append(padded_type_ids)
        
        # Stack tensors
        batch_input_ids = torch.stack(padded_input_ids)
        batch_attention_masks = torch.stack(padded_attention_masks)
        batch_token_type_ids = torch.stack(padded_token_type_ids) if padded_token_type_ids else None
        batch_labels = torch.stack(labels)
        
        return SequenceBatch(
            input_ids=batch_input_ids,
            attention_mask=batch_attention_masks,
            token_type_ids=batch_token_type_ids,
            labels=batch_labels,
            metadata=metadata
        )
    
    async def process_sequence_batch(
        self, 
        batch: SequenceBatch
    ) -> Dict[str, Any]:
        """Process a batch of sequences"""
        
        batch_size = batch.input_ids.size(0)
        sequence_length = batch.input_ids.size(1)
        
        # Calculate batch statistics
        batch_stats = {
            "batch_size": batch_size,
            "sequence_length": sequence_length,
            "total_tokens": batch.attention_mask.sum().item(),
            "padding_ratio": 1 - (batch.attention_mask.sum().item() / (batch_size * sequence_length)),
            "unique_tokens": len(torch.unique(batch.input_ids)),
            "special_tokens": self._count_special_tokens_batch(batch.input_ids)
        }
        
        # Update processing statistics
        self.batch_stats["batches_processed"] += 1
        self.batch_stats["total_tokens_processed"] += batch_stats["total_tokens"]
        
        return {
            "batch_data": batch,
            "batch_stats": batch_stats,
            "processing_metadata": {
                "timestamp": asyncio.get_event_loop().time(),
                "batch_id": self.batch_stats["batches_processed"]
            }
        }
    
    def _count_special_tokens_batch(self, input_ids: torch.Tensor) -> Dict[str, int]:
        """Count special tokens in a batch"""
        
        special_tokens = {
            "pad": (input_ids == self.tokenizer.tokenizer.pad_token_id).sum().item(),
            "unk": (input_ids == self.tokenizer.tokenizer.unk_token_id).sum().item(),
            "cls": (input_ids == self.tokenizer.tokenizer.cls_token_id).sum().item(),
            "sep": (input_ids == self.tokenizer.tokenizer.sep_token_id).sum().item(),
            "mask": (input_ids == self.tokenizer.tokenizer.mask_token_id).sum().item()
        }
        
        return special_tokens
    
    async def optimize_sequence_length(
        self, 
        sequences: List[EmailSequence],
        target_length: int = 512
    ) -> List[EmailSequence]:
        """Optimize sequence length for efficient processing"""
        
        optimized_sequences = []
        
        for sequence in sequences:
            optimized_sequence = sequence.copy()
            
            # Optimize each step
            for step in optimized_sequence.steps:
                if step.content and len(step.content) > target_length:
                    # Truncate content to target length
                    step.content = step.content[:target_length] + "..."
                
                # Optimize delay timing
                if step.delay_hours and step.delay_hours > 168:  # > 1 week
                    step.delay_hours = 168
            
            optimized_sequences.append(optimized_sequence)
        
        self.processing_stats["sequences_optimized"] += len(sequences)
        
        return optimized_sequences
    
    async def create_sequence_embeddings(
        self, 
        batch: SequenceBatch
    ) -> torch.Tensor:
        """Create embeddings for sequence batch"""
        
        # This would typically use a pre-trained model
        # For now, return a placeholder embedding
        batch_size = batch.input_ids.size(0)
        embedding_dim = 768  # Standard BERT embedding dimension
        
        # Create random embeddings (replace with actual model)
        embeddings = torch.randn(batch_size, embedding_dim)
        
        return embeddings
    
    async def analyze_sequence_patterns(
        self, 
        sequences: List[EmailSequence]
    ) -> Dict[str, Any]:
        """Analyze patterns in email sequences"""
        
        pattern_analysis = {
            "total_sequences": len(sequences),
            "avg_steps_per_sequence": np.mean([len(s.steps) for s in sequences]),
            "step_distribution": defaultdict(int),
            "delay_distribution": defaultdict(int),
            "content_length_distribution": defaultdict(int),
            "common_patterns": []
        }
        
        for sequence in sequences:
            # Analyze step distribution
            pattern_analysis["step_distribution"][len(sequence.steps)] += 1
            
            for step in sequence.steps:
                # Analyze delays
                delay = step.delay_hours or 0
                delay_category = self._categorize_delay(delay)
                pattern_analysis["delay_distribution"][delay_category] += 1
                
                # Analyze content length
                content_length = len(step.content or "")
                length_category = self._categorize_content_length(content_length)
                pattern_analysis["content_length_distribution"][length_category] += 1
        
        # Find common patterns
        pattern_analysis["common_patterns"] = self._find_common_patterns(sequences)
        
        return pattern_analysis
    
    def _categorize_delay(self, delay_hours: int) -> str:
        """Categorize delay into ranges"""
        if delay_hours == 0:
            return "immediate"
        elif delay_hours <= 24:
            return "same_day"
        elif delay_hours <= 72:
            return "1_3_days"
        elif delay_hours <= 168:
            return "1_week"
        else:
            return "long_term"
    
    def _categorize_content_length(self, length: int) -> str:
        """Categorize content length"""
        if length == 0:
            return "empty"
        elif length <= 100:
            return "short"
        elif length <= 500:
            return "medium"
        elif length <= 1000:
            return "long"
        else:
            return "very_long"
    
    def _find_common_patterns(self, sequences: List[EmailSequence]) -> List[Dict[str, Any]]:
        """Find common patterns in sequences"""
        
        patterns = []
        
        # Pattern 1: Welcome + Follow-up + CTA
        welcome_pattern_count = 0
        for sequence in sequences:
            if len(sequence.steps) >= 3:
                # Check if first step is welcome-like
                first_step = sequence.steps[0]
                if "welcome" in (first_step.content or "").lower():
                    welcome_pattern_count += 1
        
        if welcome_pattern_count > 0:
            patterns.append({
                "pattern_type": "welcome_sequence",
                "frequency": welcome_pattern_count,
                "percentage": (welcome_pattern_count / len(sequences)) * 100
            })
        
        # Pattern 2: Short sequences (1-2 steps)
        short_sequence_count = sum(1 for s in sequences if len(s.steps) <= 2)
        if short_sequence_count > 0:
            patterns.append({
                "pattern_type": "short_sequence",
                "frequency": short_sequence_count,
                "percentage": (short_sequence_count / len(sequences)) * 100
            })
        
        return patterns
    
    async def get_processing_report(self) -> Dict[str, Any]:
        """Generate comprehensive processing report"""
        
        return {
            "processing_stats": dict(self.processing_stats),
            "batch_stats": dict(self.batch_stats),
            "performance_metrics": {
                "avg_batch_size": self.batch_stats["total_tokens_processed"] / max(self.batch_stats["batches_processed"], 1),
                "efficiency_score": self._calculate_efficiency_score(),
                "optimization_rate": self.processing_stats["sequences_optimized"] / max(self.processing_stats["total_sequences"], 1)
            },
            "recommendations": self._generate_processing_recommendations()
        }
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate processing efficiency score"""
        
        if self.batch_stats["batches_processed"] == 0:
            return 0.0
        
        # Calculate efficiency based on batch utilization and processing speed
        avg_batch_size = self.batch_stats["total_tokens_processed"] / self.batch_stats["batches_processed"]
        target_batch_size = self.config.batch_size * self.config.max_sequence_length
        
        efficiency = min(avg_batch_size / target_batch_size, 1.0)
        
        return efficiency
    
    def _generate_processing_recommendations(self) -> List[str]:
        """Generate processing recommendations"""
        
        recommendations = []
        
        # Batch size recommendations
        if self.batch_stats["batches_processed"] > 0:
            avg_batch_size = self.batch_stats["total_tokens_processed"] / self.batch_stats["batches_processed"]
            target_batch_size = self.config.batch_size * self.config.max_sequence_length
            
            if avg_batch_size < target_batch_size * 0.8:
                recommendations.append("Consider reducing batch size for better memory efficiency")
            elif avg_batch_size > target_batch_size * 0.95:
                recommendations.append("Consider increasing batch size for better GPU utilization")
        
        # Optimization recommendations
        optimization_rate = self.processing_stats["sequences_optimized"] / max(self.processing_stats["total_sequences"], 1)
        if optimization_rate < 0.5:
            recommendations.append("Many sequences could benefit from length optimization")
        
        return recommendations 