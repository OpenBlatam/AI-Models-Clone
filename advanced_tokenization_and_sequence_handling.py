# ADVANCED TOKENIZATION AND SEQUENCE HANDLING

# ============================================================================
# ADVANCED TOKENIZER IMPLEMENTATIONS
# ============================================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
import re
import json
import pickle
import os
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Iterator
from dataclasses import dataclass, field
from collections import Counter, defaultdict
import numpy as np
from pathlib import Path
import unicodedata

class Vocabulary:
    """Advanced vocabulary management for tokenization."""
    
    def __init__(self, min_freq: int = 1, max_vocab_size: Optional[int] = None,
                 special_tokens: Optional[List[str]] = None):
        self.min_freq = min_freq
        self.max_vocab_size = max_vocab_size
        self.special_tokens = special_tokens or ['<PAD>', '<UNK>', '<BOS>', '<EOS>', '<SEP>', '<CLS>', '<MASK>']
        
        # Token mappings
        self.token_to_id = {}
        self.id_to_token = {}
        self.token_freq = Counter()
        
        # Initialize with special tokens
        self._init_special_tokens()
    
    def _init_special_tokens(self):
        """Initialize special tokens with reserved IDs."""
        for i, token in enumerate(self.special_tokens):
            self.token_to_id[token] = i
            self.id_to_token[i] = token
    
    def build_vocab(self, texts: List[str], tokenizer_func: Callable = None):
        """Build vocabulary from text corpus."""
        if tokenizer_func is None:
            tokenizer_func = lambda x: x.split()
        
        # Count token frequencies
        for text in texts:
            tokens = tokenizer_func(text)
            self.token_freq.update(tokens)
        
        # Filter by minimum frequency
        filtered_tokens = [(token, freq) for token, freq in self.token_freq.items() 
                          if freq >= self.min_freq]
        
        # Sort by frequency (descending)
        filtered_tokens.sort(key=lambda x: x[1], reverse=True)
        
        # Apply maximum vocabulary size
        if self.max_vocab_size:
            filtered_tokens = filtered_tokens[:self.max_vocab_size - len(self.special_tokens)]
        
        # Add tokens to vocabulary
        for i, (token, _) in enumerate(filtered_tokens):
            token_id = len(self.special_tokens) + i
            self.token_to_id[token] = token_id
            self.id_to_token[token_id] = token
    
    def encode(self, tokens: List[str]) -> List[int]:
        """Encode tokens to IDs."""
        return [self.token_to_id.get(token, self.token_to_id['<UNK>']) for token in tokens]
    
    def decode(self, ids: List[int]) -> List[str]:
        """Decode IDs to tokens."""
        return [self.id_to_token.get(id_, '<UNK>') for id_ in ids]
    
    def __len__(self) -> int:
        return len(self.token_to_id)
    
    def save(self, path: str):
        """Save vocabulary to file."""
        vocab_data = {
            'token_to_id': self.token_to_id,
            'id_to_token': self.id_to_token,
            'token_freq': dict(self.token_freq),
            'special_tokens': self.special_tokens,
            'min_freq': self.min_freq,
            'max_vocab_size': self.max_vocab_size
        }
        
        with open(path, 'wb') as f:
            pickle.dump(vocab_data, f)
    
    def load(self, path: str):
        """Load vocabulary from file."""
        with open(path, 'rb') as f:
            vocab_data = pickle.load(f)
        
        self.token_to_id = vocab_data['token_to_id']
        self.id_to_token = vocab_data['id_to_token']
        self.token_freq = Counter(vocab_data['token_freq'])
        self.special_tokens = vocab_data['special_tokens']
        self.min_freq = vocab_data['min_freq']
        self.max_vocab_size = vocab_data['max_vocab_size']

class AdvancedTokenizer:
    """Advanced tokenizer with multiple tokenization strategies."""
    
    def __init__(self, vocab: Vocabulary, max_length: int = 512, 
                 padding_strategy: str = 'longest', truncation_strategy: str = 'longest_first'):
        self.vocab = vocab
        self.max_length = max_length
        self.padding_strategy = padding_strategy
        self.truncation_strategy = truncation_strategy
        
        # Special token IDs
        self.pad_token_id = self.vocab.token_to_id.get('<PAD>', 0)
        self.unk_token_id = self.vocab.token_to_id.get('<UNK>', 1)
        self.bos_token_id = self.vocab.token_to_id.get('<BOS>', 2)
        self.eos_token_id = self.vocab.token_to_id.get('<EOS>', 3)
        self.sep_token_id = self.vocab.token_to_id.get('<SEP>', 4)
        self.cls_token_id = self.vocab.token_to_id.get('<CLS>', 5)
        self.mask_token_id = self.vocab.token_to_id.get('<MASK>', 6)
    
    def tokenize(self, text: str, strategy: str = 'word') -> List[str]:
        """Tokenize text using specified strategy."""
        if strategy == 'word':
            return self._word_tokenize(text)
        elif strategy == 'subword':
            return self._subword_tokenize(text)
        elif strategy == 'character':
            return self._character_tokenize(text)
        elif strategy == 'sentence':
            return self._sentence_tokenize(text)
        else:
            raise ValueError(f"Unknown tokenization strategy: {strategy}")
    
    def _word_tokenize(self, text: str) -> List[str]:
        """Word-level tokenization with preprocessing."""
        # Normalize text
        text = self._normalize_text(text)
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        
        # Filter empty tokens
        tokens = [token for token in tokens if token.strip()]
        
        return tokens
    
    def _subword_tokenize(self, text: str) -> List[str]:
        """Subword tokenization using BPE-like approach."""
        # Simple BPE implementation
        text = self._normalize_text(text)
        words = text.split()
        subwords = []
        
        for word in words:
            if word in self.vocab.token_to_id:
                subwords.append(word)
            else:
                # Break down unknown words
                word_subwords = self._break_word(word)
                subwords.extend(word_subwords)
        
        return subwords
    
    def _character_tokenize(self, text: str) -> List[str]:
        """Character-level tokenization."""
        text = self._normalize_text(text)
        return list(text)
    
    def _sentence_tokenize(self, text: str) -> List[str]:
        """Sentence-level tokenization."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent tokenization."""
        # Convert to lowercase
        text = text.lower()
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _break_word(self, word: str) -> List[str]:
        """Break down unknown words into subwords."""
        # Simple character n-gram approach
        n = 3
        subwords = []
        
        for i in range(0, len(word) - n + 1):
            subword = word[i:i+n]
            if subword in self.vocab.token_to_id:
                subwords.append(subword)
        
        # If no subwords found, use character-level
        if not subwords:
            subwords = list(word)
        
        return subwords
    
    def encode(self, text: str, strategy: str = 'word', 
               add_special_tokens: bool = True, return_tensors: str = None) -> Dict[str, Any]:
        """Encode text to token IDs."""
        # Tokenize
        tokens = self.tokenize(text, strategy)
        
        # Add special tokens
        if add_special_tokens:
            tokens = ['<BOS>'] + tokens + ['<EOS>']
        
        # Convert to IDs
        token_ids = self.vocab.encode(tokens)
        
        # Truncate if necessary
        if len(token_ids) > self.max_length:
            token_ids = self._truncate_sequence(token_ids)
        
        # Pad if necessary
        if len(token_ids) < self.max_length:
            token_ids = self._pad_sequence(token_ids)
        
        # Create attention mask
        attention_mask = [1 if id_ != self.pad_token_id else 0 for id_ in token_ids]
        
        result = {
            'input_ids': token_ids,
            'attention_mask': attention_mask,
            'token_type_ids': [0] * len(token_ids)
        }
        
        # Convert to tensors if requested
        if return_tensors == 'pt':
            result = {k: torch.tensor(v) for k, v in result.items()}
        
        return result
    
    def _truncate_sequence(self, token_ids: List[int]) -> List[int]:
        """Truncate sequence according to strategy."""
        if self.truncation_strategy == 'longest_first':
            # Remove tokens from the middle, keeping BOS and EOS
            if len(token_ids) > self.max_length:
                keep_start = 1  # Keep BOS
                keep_end = 1    # Keep EOS
                remove_count = len(token_ids) - self.max_length
                
                # Remove from middle
                start_idx = keep_start
                end_idx = len(token_ids) - keep_end - remove_count
                
                token_ids = token_ids[:start_idx] + token_ids[end_idx:]
        
        return token_ids[:self.max_length]
    
    def _pad_sequence(self, token_ids: List[int]) -> List[int]:
        """Pad sequence according to strategy."""
        if self.padding_strategy == 'longest':
            padding_length = self.max_length - len(token_ids)
            token_ids.extend([self.pad_token_id] * padding_length)
        
        return token_ids
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs back to text."""
        tokens = self.vocab.decode(token_ids)
        
        if skip_special_tokens:
            tokens = [token for token in tokens if token not in self.vocab.special_tokens]
        
        return ' '.join(tokens)

class SubwordTokenizer:
    """Byte Pair Encoding (BPE) tokenizer implementation."""
    
    def __init__(self, vocab_size: int = 50000, min_freq: int = 2):
        self.vocab_size = vocab_size
        self.min_freq = min_freq
        self.vocab = {}
        self.merges = {}
        self.reverse_merges = {}
    
    def train(self, texts: List[str]):
        """Train BPE tokenizer on text corpus."""
        # Initialize vocabulary with characters
        word_freq = Counter()
        for text in texts:
            words = text.split()
            word_freq.update(words)
        
        # Start with character vocabulary
        char_vocab = set()
        for word in word_freq:
            char_vocab.update(word)
        
        self.vocab = {char: i for i, char in enumerate(char_vocab)}
        
        # BPE training
        for i in range(self.vocab_size - len(self.vocab)):
            # Find most frequent pair
            pair_freq = self._get_pair_frequencies(word_freq)
            if not pair_freq:
                break
            
            # Get most frequent pair
            best_pair = max(pair_freq.items(), key=lambda x: x[1])[0]
            
            # Add merge rule
            self.merges[best_pair] = len(self.vocab)
            self.reverse_merges[len(self.vocab)] = best_pair
            
            # Add merged token to vocabulary
            merged_token = ''.join(best_pair)
            self.vocab[merged_token] = len(self.vocab)
            
            # Update word frequencies
            word_freq = self._apply_merge(word_freq, best_pair)
    
    def _get_pair_frequencies(self, word_freq: Counter) -> Counter:
        """Get frequencies of adjacent character pairs."""
        pair_freq = Counter()
        
        for word, freq in word_freq.items():
            for i in range(len(word) - 1):
                pair = (word[i], word[i + 1])
                pair_freq[pair] += freq
        
        return pair_freq
    
    def _apply_merge(self, word_freq: Counter, pair: Tuple[str, str]) -> Counter:
        """Apply merge rule to word frequencies."""
        new_word_freq = Counter()
        
        for word, freq in word_freq.items():
            new_word = self._merge_word(word, pair)
            new_word_freq[new_word] += freq
        
        return new_word_freq
    
    def _merge_word(self, word: str, pair: Tuple[str, str]) -> str:
        """Merge pair in word."""
        return word.replace(''.join(pair), ''.join(pair))
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using trained BPE."""
        words = text.split()
        tokens = []
        
        for word in words:
            word_tokens = self._tokenize_word(word)
            tokens.extend(word_tokens)
        
        return tokens
    
    def _tokenize_word(self, word: str) -> List[str]:
        """Tokenize single word using BPE."""
        # Apply merges in order
        current_word = word
        
        while len(current_word) > 1:
            # Find best merge
            best_merge = None
            best_pos = -1
            
            for pair, merge_id in self.merges.items():
                pos = current_word.find(''.join(pair))
                if pos != -1:
                    if best_pos == -1 or pos < best_pos:
                        best_merge = pair
                        best_pos = pos
            
            if best_merge is None:
                break
            
            # Apply merge
            current_word = current_word.replace(''.join(best_merge), ''.join(best_merge))
        
        # Split into tokens
        tokens = []
        i = 0
        while i < len(current_word):
            # Find longest token starting at position i
            longest_token = None
            for j in range(len(current_word), i, -1):
                candidate = current_word[i:j]
                if candidate in self.vocab:
                    longest_token = candidate
                    break
            
            if longest_token:
                tokens.append(longest_token)
                i += len(longest_token)
            else:
                # Unknown character
                tokens.append(current_word[i])
                i += 1
        
        return tokens

# ============================================================================
# SEQUENCE PROCESSING AND HANDLING
# ============================================================================

class SequenceProcessor:
    """Advanced sequence processing utilities."""
    
    def __init__(self, max_length: int = 512, padding_token: str = '<PAD>',
                 truncation_token: str = '<TRUNC>'):
        self.max_length = max_length
        self.padding_token = padding_token
        self.truncation_token = truncation_token
    
    def pad_sequences(self, sequences: List[List[Any]], 
                     padding: str = 'post', truncating: str = 'post',
                     value: Any = None) -> List[List[Any]]:
        """Pad sequences to uniform length."""
        if not sequences:
            return sequences
        
        # Find maximum length
        max_len = max(len(seq) for seq in sequences)
        
        # Limit to max_length
        if max_len > self.max_length:
            max_len = self.max_length
        
        padded_sequences = []
        
        for seq in sequences:
            # Truncate if necessary
            if len(seq) > max_len:
                if truncating == 'post':
                    seq = seq[:max_len]
                elif truncating == 'pre':
                    seq = seq[max_len:]
                else:  # truncating == 'middle'
                    remove_count = len(seq) - max_len
                    start_remove = remove_count // 2
                    end_remove = remove_count - start_remove
                    seq = seq[start_remove:len(seq) - end_remove]
            
            # Pad if necessary
            if len(seq) < max_len:
                pad_value = value if value is not None else self.padding_token
                padding_length = max_len - len(seq)
                
                if padding == 'post':
                    seq = seq + [pad_value] * padding_length
                elif padding == 'pre':
                    seq = [pad_value] * padding_length + seq
                else:  # padding == 'middle'
                    left_pad = padding_length // 2
                    right_pad = padding_length - left_pad
                    seq = [pad_value] * left_pad + seq + [pad_value] * right_pad
            
            padded_sequences.append(seq)
        
        return padded_sequences
    
    def create_attention_mask(self, sequences: List[List[Any]], 
                            padding_value: Any = None) -> List[List[int]]:
        """Create attention masks for padded sequences."""
        if padding_value is None:
            padding_value = self.padding_token
        
        attention_masks = []
        
        for seq in sequences:
            mask = [1 if token != padding_value else 0 for token in seq]
            attention_masks.append(mask)
        
        return attention_masks
    
    def create_token_type_ids(self, sequences: List[List[Any]], 
                            segment_lengths: List[int] = None) -> List[List[int]]:
        """Create token type IDs for sequence pairs."""
        if segment_lengths is None:
            # Single sequence
            return [[0] * len(seq) for seq in sequences]
        
        token_type_ids = []
        
        for seq, seg_len in zip(sequences, segment_lengths):
            type_ids = [0] * seg_len + [1] * (len(seq) - seg_len)
            token_type_ids.append(type_ids)
        
        return token_type_ids
    
    def sliding_window(self, sequence: List[Any], window_size: int, 
                      stride: int = 1) -> List[List[Any]]:
        """Create sliding windows over sequence."""
        windows = []
        
        for i in range(0, len(sequence) - window_size + 1, stride):
            window = sequence[i:i + window_size]
            windows.append(window)
        
        return windows
    
    def create_ngrams(self, sequence: List[Any], n: int) -> List[Tuple[Any, ...]]:
        """Create n-grams from sequence."""
        ngrams = []
        
        for i in range(len(sequence) - n + 1):
            ngram = tuple(sequence[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    def apply_augmentation(self, sequence: List[Any], 
                          augmentation_funcs: List[Callable]) -> List[List[Any]]:
        """Apply multiple augmentation functions to sequence."""
        augmented_sequences = [sequence]
        
        for aug_func in augmentation_funcs:
            augmented = aug_func(sequence)
            if isinstance(augmented, list):
                augmented_sequences.append(augmented)
            else:
                augmented_sequences.append([augmented])
        
        return augmented_sequences

class TextDataset:
    """PyTorch Dataset for text data with advanced features."""
    
    def __init__(self, texts: List[str], labels: Optional[List[Any]] = None,
                 tokenizer: AdvancedTokenizer = None, max_length: int = 512,
                 augmentation_funcs: Optional[List[Callable]] = None):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.augmentation_funcs = augmentation_funcs or []
        
        # Validate inputs
        if labels is not None and len(texts) != len(labels):
            raise ValueError("Texts and labels must have the same length")
    
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        text = self.texts[idx]
        
        # Apply augmentations
        if self.augmentation_funcs:
            augmented_texts = self._apply_augmentations(text)
            # Use first augmented version for now
            text = augmented_texts[0] if augmented_texts else text
        
        # Tokenize
        if self.tokenizer:
            encoded = self.tokenizer.encode(
                text, 
                add_special_tokens=True,
                return_tensors='pt'
            )
        else:
            # Simple character-level encoding
            encoded = {
                'input_ids': torch.tensor([ord(c) for c in text[:self.max_length]]),
                'attention_mask': torch.ones(min(len(text), self.max_length))
            }
        
        result = encoded.copy()
        
        # Add labels if available
        if self.labels is not None:
            result['labels'] = torch.tensor(self.labels[idx])
        
        return result
    
    def _apply_augmentations(self, text: str) -> List[str]:
        """Apply augmentation functions to text."""
        augmented_texts = [text]
        
        for aug_func in self.augmentation_funcs:
            try:
                augmented = aug_func(text)
                if isinstance(augmented, str):
                    augmented_texts.append(augmented)
                elif isinstance(augmented, list):
                    augmented_texts.extend(augmented)
            except Exception as e:
                # Skip failed augmentations
                continue
        
        return augmented_texts

class TextDataLoader:
    """Advanced DataLoader for text data with custom collation."""
    
    def __init__(self, dataset: TextDataset, batch_size: int = 32, 
                 shuffle: bool = True, num_workers: int = 0,
                 collate_fn: Optional[Callable] = None):
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.num_workers = num_workers
        
        # Use custom collate function if provided
        if collate_fn is None:
            collate_fn = self._default_collate
        
        self.collate_fn = collate_fn
    
    def _default_collate(self, batch: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """Default collation function for text batches."""
        # Separate different types of data
        input_ids = []
        attention_masks = []
        labels = []
        
        for item in batch:
            input_ids.append(item['input_ids'])
            attention_masks.append(item['attention_mask'])
            
            if 'labels' in item:
                labels.append(item['labels'])
        
        # Stack tensors
        result = {
            'input_ids': torch.stack(input_ids),
            'attention_mask': torch.stack(attention_masks)
        }
        
        if labels:
            result['labels'] = torch.stack(labels)
        
        return result
    
    def __iter__(self) -> Iterator[Dict[str, torch.Tensor]]:
        """Iterate over batches."""
        # Simple batch iteration (in production, use PyTorch's DataLoader)
        indices = list(range(len(self.dataset)))
        
        if self.shuffle:
            np.random.shuffle(indices)
        
        for i in range(0, len(indices), self.batch_size):
            batch_indices = indices[i:i + self.batch_size]
            batch = [self.dataset[idx] for idx in batch_indices]
            yield self.collate_fn(batch)

# ============================================================================
# TEXT AUGMENTATION FUNCTIONS
# ============================================================================

class TextAugmenter:
    """Text augmentation utilities."""
    
    @staticmethod
    def synonym_replacement(text: str, n: int = 1) -> str:
        """Replace words with synonyms."""
        # Simple synonym dictionary (in practice, use WordNet or similar)
        synonyms = {
            'good': ['great', 'excellent', 'fine', 'nice'],
            'bad': ['terrible', 'awful', 'horrible', 'poor'],
            'big': ['large', 'huge', 'enormous', 'massive'],
            'small': ['tiny', 'little', 'mini', 'petite']
        }
        
        words = text.split()
        n = min(n, len(words))
        
        for _ in range(n):
            idx = np.random.randint(len(words))
            word = words[idx].lower()
            
            if word in synonyms:
                synonym = np.random.choice(synonyms[word])
                words[idx] = synonym
        
        return ' '.join(words)
    
    @staticmethod
    def random_insertion(text: str, n: int = 1) -> str:
        """Insert random words into text."""
        words = text.split()
        n = min(n, len(words))
        
        # Simple word bank for insertion
        word_bank = ['very', 'really', 'quite', 'extremely', 'especially']
        
        for _ in range(n):
            idx = np.random.randint(len(words) + 1)
            word = np.random.choice(word_bank)
            words.insert(idx, word)
        
        return ' '.join(words)
    
    @staticmethod
    def random_deletion(text: str, p: float = 0.1) -> str:
        """Randomly delete words with probability p."""
        words = text.split()
        
        # Keep words with probability 1-p
        kept_words = [word for word in words if np.random.random() > p]
        
        # Ensure at least one word remains
        if not kept_words:
            kept_words = [words[0]]
        
        return ' '.join(kept_words)
    
    @staticmethod
    def random_swap(text: str, n: int = 1) -> str:
        """Randomly swap adjacent words."""
        words = text.split()
        n = min(n, len(words) - 1)
        
        for _ in range(n):
            idx = np.random.randint(len(words) - 1)
            words[idx], words[idx + 1] = words[idx + 1], words[idx]
        
        return ' '.join(words)
    
    @staticmethod
    def back_translation(text: str, forward_translator: Callable = None,
                        backward_translator: Callable = None) -> str:
        """Back-translation augmentation (simplified)."""
        # In practice, use actual translation models
        # This is a simplified version that just adds some variation
        
        # Simulate translation by adding some word variations
        variations = {
            'the': ['a', 'an'],
            'is': ['was', 'will be'],
            'are': ['were', 'will be'],
            'have': ['had', 'will have']
        }
        
        words = text.split()
        augmented_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in variations and np.random.random() < 0.3:
                variation = np.random.choice(variations[word_lower])
                augmented_words.append(variation)
            else:
                augmented_words.append(word)
        
        return ' '.join(augmented_words)

# ============================================================================
# ADVANCED SEQUENCE HANDLING
# ============================================================================

class SequenceBatchProcessor:
    """Process batches of sequences with advanced features."""
    
    def __init__(self, tokenizer: AdvancedTokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def process_batch(self, texts: List[str], 
                     add_special_tokens: bool = True,
                     return_tensors: str = 'pt') -> Dict[str, torch.Tensor]:
        """Process a batch of texts."""
        # Tokenize all texts
        encoded_texts = []
        for text in texts:
            encoded = self.tokenizer.encode(
                text,
                add_special_tokens=add_special_tokens,
                return_tensors=None
            )
            encoded_texts.append(encoded)
        
        # Pad sequences
        input_ids = [encoded['input_ids'] for encoded in encoded_texts]
        attention_masks = [encoded['attention_mask'] for encoded in encoded_texts]
        
        # Pad to maximum length in batch
        max_len = min(max(len(ids) for ids in input_ids), self.max_length)
        
        padded_input_ids = []
        padded_attention_masks = []
        
        for ids, mask in zip(input_ids, attention_masks):
            # Truncate if necessary
            if len(ids) > max_len:
                ids = ids[:max_len]
                mask = mask[:max_len]
            
            # Pad if necessary
            if len(ids) < max_len:
                padding_length = max_len - len(ids)
                ids.extend([self.tokenizer.pad_token_id] * padding_length)
                mask.extend([0] * padding_length)
            
            padded_input_ids.append(ids)
            padded_attention_masks.append(mask)
        
        # Convert to tensors
        if return_tensors == 'pt':
            result = {
                'input_ids': torch.tensor(padded_input_ids),
                'attention_mask': torch.tensor(padded_attention_masks)
            }
        else:
            result = {
                'input_ids': padded_input_ids,
                'attention_mask': padded_attention_masks
            }
        
        return result
    
    def create_position_ids(self, batch_size: int, seq_length: int) -> torch.Tensor:
        """Create position IDs for sequences."""
        position_ids = torch.arange(seq_length, dtype=torch.long)
        position_ids = position_ids.unsqueeze(0).expand(batch_size, -1)
        return position_ids
    
    def create_token_type_ids(self, batch_size: int, seq_length: int,
                            segment_lengths: List[int] = None) -> torch.Tensor:
        """Create token type IDs for sequence pairs."""
        if segment_lengths is None:
            # Single sequence
            token_type_ids = torch.zeros(batch_size, seq_length, dtype=torch.long)
        else:
            token_type_ids = torch.zeros(batch_size, seq_length, dtype=torch.long)
            
            for i, seg_len in enumerate(segment_lengths):
                if seg_len < seq_length:
                    token_type_ids[i, seg_len:] = 1
        
        return token_type_ids

# ============================================================================
# DEMO AND TESTING
# ============================================================================

def test_tokenization_and_sequence_handling():
    """Test the tokenization and sequence handling implementation."""
    
    print("Testing Advanced Tokenization and Sequence Handling")
    print("=" * 70)
    
    # Sample texts
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is a subset of artificial intelligence.",
        "Natural language processing enables computers to understand human language.",
        "Deep learning models require large amounts of training data."
    ]
    
    print(f"Sample texts: {len(texts)}")
    for i, text in enumerate(texts):
        print(f"  {i+1}. {text}")
    
    # Test Vocabulary
    print("\n1. Testing Vocabulary:")
    vocab = Vocabulary(min_freq=1, max_vocab_size=100)
    vocab.build_vocab(texts)
    print(f"   Vocabulary size: {len(vocab):,}")
    print(f"   Special tokens: {vocab.special_tokens}")
    
    # Test Advanced Tokenizer
    print("\n2. Testing Advanced Tokenizer:")
    tokenizer = AdvancedTokenizer(vocab, max_length=20)
    
    # Test different tokenization strategies
    strategies = ['word', 'subword', 'character', 'sentence']
    for strategy in strategies:
        try:
            tokens = tokenizer.tokenize(texts[0], strategy=strategy)
            print(f"   {strategy.capitalize()} tokenization: {len(tokens)} tokens")
            print(f"     Tokens: {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
        except Exception as e:
            print(f"   {strategy.capitalize()} tokenization failed: {e}")
    
    # Test encoding
    try:
        encoded = tokenizer.encode(texts[0], strategy='word', add_special_tokens=True)
        print(f"   Encoding successful: {len(encoded['input_ids'])} tokens")
        print(f"   Input IDs: {encoded['input_ids'][:10]}{'...' if len(encoded['input_ids']) > 10 else ''}")
    except Exception as e:
        print(f"   Encoding failed: {e}")
    
    # Test Subword Tokenizer
    print("\n3. Testing Subword Tokenizer:")
    try:
        subword_tokenizer = SubwordTokenizer(vocab_size=100)
        subword_tokenizer.train(texts)
        
        tokens = subword_tokenizer.tokenize(texts[0])
        print(f"   Subword tokenization: {len(tokens)} tokens")
        print(f"   Tokens: {tokens[:10]}{'...' if len(tokens) > 10 else ''}")
    except Exception as e:
        print(f"   Subword tokenization failed: {e}")
    
    # Test Sequence Processor
    print("\n4. Testing Sequence Processor:")
    processor = SequenceProcessor(max_length=15)
    
    # Create sample sequences
    sequences = [
        [1, 2, 3, 4, 5],
        [1, 2, 3],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ]
    
    padded = processor.pad_sequences(sequences, padding='post', truncating='post')
    print(f"   Padded sequences: {len(padded)} sequences")
    for i, seq in enumerate(padded):
        print(f"     Sequence {i+1}: {len(seq)} tokens - {seq}")
    
    # Test attention masks
    attention_masks = processor.create_attention_mask(padded, padding_value=0)
    print(f"   Attention masks created: {len(attention_masks)} masks")
    
    # Test Text Dataset
    print("\n5. Testing Text Dataset:")
    try:
        dataset = TextDataset(texts, labels=[0, 1, 0, 1], tokenizer=tokenizer)
        print(f"   Dataset created: {len(dataset)} samples")
        
        # Get first sample
        sample = dataset[0]
        print(f"   Sample keys: {list(sample.keys())}")
        if 'input_ids' in sample:
            print(f"   Input IDs shape: {sample['input_ids'].shape}")
        
    except Exception as e:
        print(f"   Dataset creation failed: {e}")
    
    # Test Text Augmenter
    print("\n6. Testing Text Augmenter:")
    text = "The quick brown fox jumps over the lazy dog."
    
    augmentations = [
        ('Synonym replacement', lambda x: TextAugmenter.synonym_replacement(x, n=2)),
        ('Random insertion', lambda x: TextAugmenter.random_insertion(x, n=2)),
        ('Random deletion', lambda x: TextAugmenter.random_deletion(x, p=0.2)),
        ('Random swap', lambda x: TextAugmenter.random_swap(x, n=2))
    ]
    
    for name, aug_func in augmentations:
        try:
            augmented = aug_func(text)
            print(f"   {name}: {augmented}")
        except Exception as e:
            print(f"   {name} failed: {e}")
    
    # Test Sequence Batch Processor
    print("\n7. Testing Sequence Batch Processor:")
    try:
        batch_processor = SequenceBatchProcessor(tokenizer, max_length=25)
        
        # Process batch
        batch_result = batch_processor.process_batch(texts[:2])
        print(f"   Batch processing successful")
        print(f"   Input IDs shape: {batch_result['input_ids'].shape}")
        print(f"   Attention mask shape: {batch_result['attention_mask'].shape}")
        
        # Create position IDs
        position_ids = batch_processor.create_position_ids(2, 25)
        print(f"   Position IDs shape: {position_ids.shape}")
        
    except Exception as e:
        print(f"   Batch processing failed: {e}")
    
    print("\n" + "=" * 70)
    print("All tokenization and sequence handling tests completed!")

if __name__ == "__main__":
    test_tokenization_and_sequence_handling()
