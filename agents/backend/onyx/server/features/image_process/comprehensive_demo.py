#!/usr/bin/env python3
"""
Comprehensive Demo System

This module provides a comprehensive demonstration of all integrated components:
- Text tokenization and sequence handling
- Data loading and preprocessing
- Fine-tuning techniques (LoRA, P-tuning)
- Attention mechanisms and positional encodings
- Advanced training system
- Interactive visualization and testing
"""

import gradio as gr
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
import json
import time
import logging
from pathlib import Path
import pandas as pd
from io import BytesIO
import base64

# Import our custom modules
try:
    from text_tokenization import (
        TokenizerConfig, WordTokenizer, SubwordTokenizer, HuggingFaceTokenizer,
        SequenceProcessor, VocabularyManager
    )
    from text_data_loader import (
        DataLoaderConfig, DataLoaderManager, DataPreprocessor
    )
    from lora_finetuning import LoRAFineTuner
    from ptuning_module import PTuningFineTuner
    from advanced_transformer_system import (
        AdvancedTransformerModel, AttentionConfig, AttentionVisualizer
    )
    from advanced_training_system import AdvancedTrainer, TrainingConfig
    from finetuning_integration import apply_lora_to_model, apply_p_tuning_to_model, get_finetuning_stats
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


class ComprehensiveDemoSystem:
    """Comprehensive demo system showcasing all integrated components."""
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.trainer = None
        self.attention_visualizer = None
        self.data_manager = None
        self.preprocessor = None
        self.vocab_manager = None
        
        # Demo data
        self.demo_texts = [
            "Hello world! This is a comprehensive demonstration.",
            "Natural language processing is fascinating and powerful.",
            "Transformers have revolutionized machine learning.",
            "Attention mechanisms allow models to focus on relevant information.",
            "Fine-tuning techniques make models more efficient.",
            "Tokenization is the foundation of text processing.",
            "Data loading and preprocessing are crucial for training.",
            "Advanced training systems enable better model development."
        ]
        
        self.demo_labels = [0, 1, 1, 1, 1, 0, 0, 1]  # Binary classification
        
        # Initialize components
        self._setup_components()
    
    def _setup_components(self):
        """Setup all demo components."""
        if not MODULES_AVAILABLE:
            logger.warning("Some modules not available, demo functionality limited")
            return
        
        # Setup tokenizer
        tokenizer_config = TokenizerConfig(
            vocab_size=1000,
            max_length=128,
            do_lower_case=True
        )
        self.tokenizer = WordTokenizer(tokenizer_config)
        self.tokenizer.train(self.demo_texts)
        
        # Setup sequence processor
        self.sequence_processor = SequenceProcessor(self.tokenizer, max_length=64)
        
        # Setup vocabulary manager
        self.vocab_manager = VocabularyManager(self.tokenizer)
        
        # Setup data preprocessor
        self.preprocessor = DataPreprocessor(self.tokenizer)
        
        # Setup data loader manager
        loader_config = DataLoaderConfig(
            batch_size=4,
            max_length=64,
            num_workers=0  # Use 0 for demo
        )
        self.data_manager = DataLoaderManager(self.tokenizer, loader_config)
        
        # Setup attention visualizer
        self.attention_visualizer = AttentionVisualizer()
        
        logger.info("Demo components initialized")
    
    def tokenization_demo(self, text: str, tokenizer_type: str) -> Dict[str, Any]:
        """Demonstrate tokenization capabilities."""
        if not MODULES_AVAILABLE:
            return {"error": "Tokenization modules not available"}
        
        try:
            # Create tokenizer based on type
            if tokenizer_type == "word":
                tokenizer = WordTokenizer(TokenizerConfig(vocab_size=1000, max_length=128))
                tokenizer.train([text])
            elif tokenizer_type == "subword":
                tokenizer = SubwordTokenizer(TokenizerConfig(vocab_size=1000, max_length=128))
                tokenizer.train([text])
            elif tokenizer_type == "huggingface":
                tokenizer = HuggingFaceTokenizer(TokenizerConfig(vocab_size=1000, max_length=128), "bert-base-uncased")
            else:
                return {"error": f"Unknown tokenizer type: {tokenizer_type}"}
            
            # Tokenize
            tokens = tokenizer.tokenize(text)
            token_ids = tokenizer.encode(text)
            decoded = tokenizer.decode(token_ids)
            
            # Process sequence
            processor = SequenceProcessor(tokenizer, max_length=64)
            processed = processor.process_single_sequence(text)
            
            return {
                "original_text": text,
                "tokens": tokens,
                "token_ids": token_ids,
                "decoded_text": decoded,
                "input_ids_shape": processed['input_ids'].shape,
                "attention_mask_shape": processed['attention_mask'].shape,
                "vocab_size": len(tokenizer.vocab),
                "max_length": processor.max_length
            }
        
        except Exception as e:
            return {"error": f"Tokenization error: {str(e)}"}
    
    def data_loading_demo(self, task_type: str) -> Dict[str, Any]:
        """Demonstrate data loading capabilities."""
        if not MODULES_AVAILABLE:
            return {"error": "Data loading modules not available"}
        
        try:
            # Create different types of data loaders
            if task_type == "text":
                loader = self.data_manager.create_text_loader(self.demo_texts, "demo_text")
            elif task_type == "classification":
                loader = self.data_manager.create_classification_loader(
                    self.demo_texts, self.demo_labels, "demo_classification"
                )
            elif task_type == "mlm":
                loader = self.data_manager.create_mlm_loader(self.demo_texts, "demo_mlm")
            else:
                return {"error": f"Unknown task type: {task_type}"}
            
            # Get a batch
            batch = next(iter(loader))
            
            # Get batch statistics
            batch_stats = {
                "batch_size": batch['input_ids'].shape[0],
                "sequence_length": batch['input_ids'].shape[1],
                "input_ids_shape": list(batch['input_ids'].shape),
                "attention_mask_shape": list(batch['attention_mask'].shape)
            }
            
            if 'labels' in batch:
                batch_stats["labels_shape"] = list(batch['labels'].shape)
                batch_stats["labels"] = batch['labels'].tolist()
            
            return batch_stats
        
        except Exception as e:
            return {"error": f"Data loading error: {str(e)}"}
    
    def preprocessing_demo(self, text: str, operations: List[str]) -> Dict[str, Any]:
        """Demonstrate text preprocessing capabilities."""
        if not MODULES_AVAILABLE:
            return {"error": "Preprocessing modules not available"}
        
        try:
            # Apply preprocessing operations
            processed_text = text
            
            if "lowercase" in operations:
                processed_text = self.preprocessor.preprocess_single_text(
                    processed_text, lowercase=True
                )
            
            if "remove_punctuation" in operations:
                processed_text = self.preprocessor.preprocess_single_text(
                    processed_text, remove_punctuation=True
                )
            
            if "remove_numbers" in operations:
                processed_text = self.preprocessor.preprocess_single_text(
                    processed_text, remove_numbers=True
                )
            
            if "remove_stopwords" in operations:
                processed_text = self.preprocessor.preprocess_single_text(
                    processed_text, remove_stopwords=True
                )
            
            # Apply augmentation
            augmented_text = None
            if "augment" in operations:
                augmented_text = self.preprocessor.augment_text(
                    processed_text,
                    synonym_replacement=True,
                    random_insertion=True
                )
            
            return {
                "original_text": text,
                "processed_text": processed_text,
                "augmented_text": augmented_text,
                "operations_applied": operations
            }
        
        except Exception as e:
            return {"error": f"Preprocessing error: {str(e)}"}
    
    def attention_visualization_demo(self, text: str, attention_type: str) -> Dict[str, Any]:
        """Demonstrate attention visualization."""
        if not MODULES_AVAILABLE:
            return {"error": "Attention visualization modules not available"}
        
        try:
            # Create attention model
            attention_config = AttentionConfig(
                hidden_size=256,
                num_heads=8,
                dropout=0.1
            )
            
            model = AdvancedTransformerModel(
                vocab_size=1000,
                hidden_size=256,
                num_layers=2,
                attention_config=attention_config,
                max_length=64
            )
            
            # Process text
            processed = self.sequence_processor.process_single_sequence(text)
            
            # Get attention weights
            with torch.no_grad():
                outputs = model(
                    input_ids=processed['input_ids'],
                    attention_mask=processed['attention_mask'],
                    return_attention_weights=True
                )
            
            # Visualize attention
            attention_weights = outputs.attention_weights[0]  # First layer
            
            if attention_type == "heatmap":
                fig = self.attention_visualizer.plot_attention_heatmap(
                    attention_weights, text.split()
                )
            elif attention_type == "statistics":
                stats = self.attention_visualizer.analyze_attention_statistics(attention_weights)
                return {"attention_statistics": stats}
            else:
                return {"error": f"Unknown attention type: {attention_type}"}
            
            # Convert plot to base64
            buf = BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode()
            plt.close(fig)
            
            return {
                "attention_visualization": f"data:image/png;base64,{img_str}",
                "text": text,
                "attention_type": attention_type
            }
        
        except Exception as e:
            return {"error": f"Attention visualization error: {str(e)}"}
    
    def finetuning_demo(self, technique: str, model_size: str) -> Dict[str, Any]:
        """Demonstrate fine-tuning techniques."""
        if not MODULES_AVAILABLE:
            return {"error": "Fine-tuning modules not available"}
        
        try:
            # Create base model
            if model_size == "small":
                hidden_size, num_layers, num_heads = 256, 4, 8
            elif model_size == "medium":
                hidden_size, num_layers, num_heads = 512, 8, 16
            else:  # large
                hidden_size, num_layers, num_heads = 768, 12, 24
            
            attention_config = AttentionConfig(
                hidden_size=hidden_size,
                num_heads=num_heads,
                dropout=0.1
            )
            
            base_model = AdvancedTransformerModel(
                vocab_size=1000,
                hidden_size=hidden_size,
                num_layers=num_layers,
                attention_config=attention_config,
                max_length=128
            )
            
            # Get base model stats
            base_params = sum(p.numel() for p in base_model.parameters())
            base_trainable = sum(p.numel() for p in base_model.parameters() if p.requires_grad)
            
            # Apply fine-tuning technique
            if technique == "lora":
                target_modules = ["attention", "mlp"]
                fine_tuned_model = apply_lora_to_model(
                    base_model, target_modules, r=16, alpha=32.0
                )
                fine_tuner = LoRAFineTuner(base_model, target_modules, r=16, alpha=32.0)
                fine_tuner.freeze_base_model()
                
            elif technique == "ptuning":
                ptuning_config = {
                    'num_virtual_tokens': 20,
                    'token_dim': hidden_size
                }
                fine_tuner = apply_p_tuning_to_model(base_model, ptuning_config)
                fine_tuned_model = base_model
                
            else:
                return {"error": f"Unknown fine-tuning technique: {technique}"}
            
            # Get fine-tuning stats
            finetuning_stats = get_finetuning_stats(base_model, fine_tuner)
            
            return {
                "technique": technique,
                "model_size": model_size,
                "base_parameters": base_params,
                "base_trainable": base_trainable,
                "finetuning_stats": finetuning_stats
            }
        
        except Exception as e:
            return {"error": f"Fine-tuning demo error: {str(e)}"}
    
    def training_demo(self, config_json: str) -> Dict[str, Any]:
        """Demonstrate training system."""
        if not MODULES_AVAILABLE:
            return {"error": "Training modules not available"}
        
        try:
            # Parse configuration
            config_dict = json.loads(config_json)
            config = TrainingConfig(**config_dict)
            
            # Create trainer
            trainer = AdvancedTrainer(config)
            
            # Setup components
            trainer.setup_tokenizer("word")
            trainer.setup_model()
            trainer.setup_optimizer()
            trainer.setup_data_loaders(self.demo_texts, self.demo_texts[:2])
            
            # Get model info
            model_info = trainer.get_model_info()
            
            # Simulate a few training steps
            trainer.config.num_epochs = 1
            trainer.config.log_interval = 1
            trainer.config.eval_interval = 2
            trainer.config.save_interval = 10
            
            # Train for a few steps
            trainer.train(self.demo_texts, self.demo_texts[:2])
            
            return {
                "model_info": model_info,
                "training_completed": True,
                "final_loss": trainer.metrics.get_latest("loss"),
                "best_metric": trainer.best_metric
            }
        
        except Exception as e:
            return {"error": f"Training demo error: {str(e)}"}
    
    def vocabulary_analysis_demo(self) -> Dict[str, Any]:
        """Demonstrate vocabulary analysis."""
        if not MODULES_AVAILABLE:
            return {"error": "Vocabulary analysis modules not available"}
        
        try:
            # Update vocabulary stats
            for text in self.demo_texts:
                token_ids = self.tokenizer.encode(text)
                self.vocab_manager.update_stats(token_ids)
            
            # Get vocabulary statistics
            vocab_stats = self.vocab_manager.get_vocab_stats()
            coverage_stats = self.vocab_manager.get_coverage_stats(self.demo_texts)
            
            return {
                "vocabulary_statistics": vocab_stats,
                "coverage_statistics": coverage_stats
            }
        
        except Exception as e:
            return {"error": f"Vocabulary analysis error: {str(e)}"}


def create_comprehensive_demo_interface():
    """Create the comprehensive demo interface."""
    demo_system = ComprehensiveDemoSystem()
    
    with gr.Blocks(title="Comprehensive AI System Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 Comprehensive AI System Demo")
        gr.Markdown("""
        This demo showcases all integrated components of the advanced AI system:
        - **Text Tokenization**: Word, subword, and HuggingFace tokenizers
        - **Data Loading**: Various dataset types and preprocessing
        - **Fine-tuning**: LoRA and P-tuning techniques
        - **Attention Mechanisms**: Visualization and analysis
        - **Training System**: Complete training pipeline
        - **Vocabulary Analysis**: Statistics and coverage analysis
        """)
        
        with gr.Tabs():
            # Tokenization Tab
            with gr.Tab("🔤 Tokenization"):
                gr.Markdown("### Text Tokenization Demo")
                
                with gr.Row():
                    with gr.Column():
                        tokenization_text = gr.Textbox(
                            label="Input Text",
                            value="Hello world! This is a comprehensive demonstration.",
                            lines=3
                        )
                        tokenizer_type = gr.Dropdown(
                            choices=["word", "subword", "huggingface"],
                            value="word",
                            label="Tokenizer Type"
                        )
                        tokenize_btn = gr.Button("Tokenize", variant="primary")
                    
                    with gr.Column():
                        tokenization_output = gr.JSON(label="Tokenization Results")
                
                tokenize_btn.click(
                    demo_system.tokenization_demo,
                    inputs=[tokenization_text, tokenizer_type],
                    outputs=tokenization_output
                )
            
            # Data Loading Tab
            with gr.Tab("📊 Data Loading"):
                gr.Markdown("### Data Loading Demo")
                
                with gr.Row():
                    with gr.Column():
                        task_type = gr.Dropdown(
                            choices=["text", "classification", "mlm"],
                            value="text",
                            label="Task Type"
                        )
                        load_data_btn = gr.Button("Load Data", variant="primary")
                    
                    with gr.Column():
                        data_loading_output = gr.JSON(label="Data Loading Results")
                
                load_data_btn.click(
                    demo_system.data_loading_demo,
                    inputs=[task_type],
                    outputs=data_loading_output
                )
            
            # Preprocessing Tab
            with gr.Tab("🛠️ Preprocessing"):
                gr.Markdown("### Text Preprocessing Demo")
                
                with gr.Row():
                    with gr.Column():
                        preprocessing_text = gr.Textbox(
                            label="Input Text",
                            value="Hello World! This is a TEST with numbers 123 and punctuation!!!",
                            lines=3
                        )
                        preprocessing_ops = gr.CheckboxGroup(
                            choices=["lowercase", "remove_punctuation", "remove_numbers", "remove_stopwords", "augment"],
                            value=["lowercase"],
                            label="Preprocessing Operations"
                        )
                        preprocess_btn = gr.Button("Preprocess", variant="primary")
                    
                    with gr.Column():
                        preprocessing_output = gr.JSON(label="Preprocessing Results")
                
                preprocess_btn.click(
                    demo_system.preprocessing_demo,
                    inputs=[preprocessing_text, preprocessing_ops],
                    outputs=preprocessing_output
                )
            
            # Attention Visualization Tab
            with gr.Tab("👁️ Attention Visualization"):
                gr.Markdown("### Attention Mechanism Visualization")
                
                with gr.Row():
                    with gr.Column():
                        attention_text = gr.Textbox(
                            label="Input Text",
                            value="Transformers use attention mechanisms to process text",
                            lines=2
                        )
                        attention_type = gr.Dropdown(
                            choices=["heatmap", "statistics"],
                            value="heatmap",
                            label="Visualization Type"
                        )
                        visualize_btn = gr.Button("Visualize", variant="primary")
                    
                    with gr.Column():
                        attention_output = gr.JSON(label="Attention Results")
                        attention_image = gr.Image(label="Attention Heatmap", visible=False)
                
                def handle_attention_visualization(text, viz_type):
                    result = demo_system.attention_visualization_demo(text, viz_type)
                    if "attention_visualization" in result:
                        return result, result["attention_visualization"], True
                    else:
                        return result, None, False
                
                visualize_btn.click(
                    handle_attention_visualization,
                    inputs=[attention_text, attention_type],
                    outputs=[attention_output, attention_image, attention_image]
                )
            
            # Fine-tuning Tab
            with gr.Tab("🎯 Fine-tuning"):
                gr.Markdown("### Fine-tuning Techniques Demo")
                
                with gr.Row():
                    with gr.Column():
                        finetuning_technique = gr.Dropdown(
                            choices=["lora", "ptuning"],
                            value="lora",
                            label="Fine-tuning Technique"
                        )
                        model_size = gr.Dropdown(
                            choices=["small", "medium", "large"],
                            value="small",
                            label="Model Size"
                        )
                        finetune_btn = gr.Button("Apply Fine-tuning", variant="primary")
                    
                    with gr.Column():
                        finetuning_output = gr.JSON(label="Fine-tuning Results")
                
                finetune_btn.click(
                    demo_system.finetuning_demo,
                    inputs=[finetuning_technique, model_size],
                    outputs=finetuning_output
                )
            
            # Training Tab
            with gr.Tab("🏋️ Training"):
                gr.Markdown("### Training System Demo")
                
                with gr.Row():
                    with gr.Column():
                        training_config = gr.Textbox(
                            label="Training Configuration (JSON)",
                            value=json.dumps({
                                "model_type": "transformer",
                                "vocab_size": 1000,
                                "hidden_size": 256,
                                "num_layers": 4,
                                "num_heads": 8,
                                "max_length": 64,
                                "batch_size": 4,
                                "learning_rate": 1e-4,
                                "num_epochs": 1,
                                "task_type": "language_modeling",
                                "mixed_precision": False
                            }, indent=2),
                            lines=10
                        )
                        train_btn = gr.Button("Start Training", variant="primary")
                    
                    with gr.Column():
                        training_output = gr.JSON(label="Training Results")
                
                train_btn.click(
                    demo_system.training_demo,
                    inputs=[training_config],
                    outputs=training_output
                )
            
            # Vocabulary Analysis Tab
            with gr.Tab("📚 Vocabulary Analysis"):
                gr.Markdown("### Vocabulary Analysis Demo")
                
                with gr.Row():
                    vocab_analyze_btn = gr.Button("Analyze Vocabulary", variant="primary")
                    vocab_output = gr.JSON(label="Vocabulary Analysis Results")
                
                vocab_analyze_btn.click(
                    demo_system.vocabulary_analysis_demo,
                    inputs=[],
                    outputs=vocab_output
                )
        
        # System Status
        with gr.Accordion("System Status", open=False):
            gr.Markdown(f"""
            **Modules Available**: {'✅' if MODULES_AVAILABLE else '❌'}
            
            **Demo Texts**: {len(demo_system.demo_texts)} samples
            **Tokenizer**: {type(demo_system.tokenizer).__name__ if demo_system.tokenizer else 'None'}
            **Device**: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}
            """)
    
    return demo


if __name__ == "__main__":
    # Create and launch the demo
    demo = create_comprehensive_demo_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )


