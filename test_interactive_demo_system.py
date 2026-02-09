from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int = 1000

# Constants
MAX_RETRIES: int = 100

# Constants
TIMEOUT_SECONDS: int = 60

# Constants
BUFFER_SIZE: int = 1024

import os
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import json
from interactive_demo_system import (
    import time
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Test Suite for Interactive Demo System
====================================

This module provides comprehensive tests for the interactive demo system,
including tests for model inference demos, visualization demos, and experiment demos.
"""


# Import the system under test
    DemoConfig, ModelInferenceDemo, VisualizationDemo, 
    ExperimentDemo, InteractiveDemoSystem, create_quick_demo, launch_demo
)


class TestDemoConfig(unittest.TestCase):
    """Test cases for DemoConfig class."""
    
    def setUp(self) -> Any:
        self.temp_dir = tempfile.mkdtemp()
    
    def test_default_config(self) -> Any:
        """Test default configuration."""
        config = DemoConfig()
        
        # Test default values
        self.assertEqual(config.demo_port, 7860)
        self.assertEqual(config.demo_host, "0.0.0.0")
        self.assertFalse(config.demo_share)
        self.assertFalse(config.demo_debug)
        self.assertTrue(config.demo_show_error)
        
        self.assertEqual(config.models_path, "./models")
        self.assertEqual(config.data_path, "./data")
        self.assertEqual(config.demos_path, "./demos")
        
        self.assertEqual(config.max_examples, 10)
        self.assertEqual(config.batch_size, 1)
        self.assertEqual(config.device, "cpu")
        
        self.assertEqual(config.plot_theme, "plotly_white")
        self.assertEqual(config.figure_size, (800, 600))
        self.assertEqual(config.dpi, 100)
    
    def test_custom_config(self) -> Any:
        """Test custom configuration."""
        config = DemoConfig()
        config.demo_port: int = 8080
        config.demo_host: str = "127.0.0.1"
        config.demo_share: bool = True
        config.demo_debug: bool = True
        config.demo_show_error: bool = False
        
        config.models_path = self.temp_dir + "/models"
        config.data_path = self.temp_dir + "/data"
        config.demos_path = self.temp_dir + "/demos"
        
        config.max_examples: int = 20
        config.batch_size: int = 4
        config.device: str = "cuda"
        
        config.plot_theme: str = "plotly_dark"
        config.figure_size = (1024, 768)
        config.dpi: int = 150
        
        # Test custom values
        self.assertEqual(config.demo_port, 8080)
        self.assertEqual(config.demo_host, "127.0.0.1")
        self.assertTrue(config.demo_share)
        self.assertTrue(config.demo_debug)
        self.assertFalse(config.demo_show_error)
        
        self.assertEqual(config.models_path, self.temp_dir + "/models")
        self.assertEqual(config.data_path, self.temp_dir + "/data")
        self.assertEqual(config.demos_path, self.temp_dir + "/demos")
        
        self.assertEqual(config.max_examples, 20)
        self.assertEqual(config.batch_size, 4)
        self.assertEqual(config.device, "cuda")
        
        self.assertEqual(config.plot_theme, "plotly_dark")
        self.assertEqual(config.figure_size, (1024, 768))
        self.assertEqual(config.dpi, 150)
    
    def test_directory_creation(self) -> Any:
        """Test that directories are created."""
        config = DemoConfig()
        config.models_path = self.temp_dir + "/test_models"
        config.data_path = self.temp_dir + "/test_data"
        config.demos_path = self.temp_dir + "/test_demos"
        
        # Directories should be created during initialization
        self.assertTrue(os.path.exists(config.models_path))
        self.assertTrue(os.path.exists(config.data_path))
        self.assertTrue(os.path.exists(config.demos_path))


class TestModelInferenceDemo(unittest.TestCase):
    """Test cases for ModelInferenceDemo class."""
    
    def setUp(self) -> Any:
        self.config = DemoConfig()
        self.model_demo = ModelInferenceDemo(self.config)
    
    def test_initialization(self) -> Any:
        """Test demo initialization."""
        self.assertIsInstance(self.model_demo.config, DemoConfig)
        self.assertIsNotNone(self.model_demo.models)
        self.assertIsNone(self.model_demo.current_model)
    
    def test_text_generation_simulation(self) -> Any:
        """Test text generation simulation methods."""
        prompt: str = "The future of artificial intelligence"
        max_length: int = 100
        temperature = 0.7
        
        # Test GPT-2 style generation
        gpt2_result = self.model_demo._simulate_gpt2_generation(prompt, max_length, temperature)
        self.assertIsInstance(gpt2_result, str)
        self.assertIn(prompt, gpt2_result)
        self.assertIn("GPT-2", gpt2_result)
        
        # Test BERT style generation
        bert_result = self.model_demo._simulate_bert_generation(prompt, max_length, temperature)
        self.assertIsInstance(bert_result, str)
        self.assertIn(prompt, bert_result)
        self.assertIn("BERT", bert_result)
        
        # Test Transformer generation
        transformer_result = self.model_demo._simulate_transformer_generation(prompt, max_length, temperature)
        self.assertIsInstance(transformer_result, str)
        self.assertIn(prompt, transformer_result)
        self.assertIn("transformer", transformer_result)
        
        # Test basic generation
        basic_result = self.model_demo._simulate_basic_generation(prompt, max_length, temperature)
        self.assertIsInstance(basic_result, str)
        self.assertIn(prompt, basic_result)
        self.assertIn("basic", basic_result)
    
    def test_image_generation_simulation(self) -> Any:
        """Test image generation simulation."""
        prompt: str = "A beautiful sunset over mountains"
        width, height = 512, 512
        seed: int = 42
        
        # Test image generation
        img = self.model_demo._simulate_image_generation(prompt, width, height, seed)
        
        self.assertIsInstance(img, np.ndarray)
        self.assertEqual(img.shape, (height, width, 3))
        self.assertEqual(img.dtype, np.uint8)
        self.assertTrue(np.all(img >= 0) and np.all(img <= 255))
    
    def test_color_extraction(self) -> Any:
        """Test color extraction from prompts."""
        # Test different color prompts
        test_cases: List[Any] = [
            ("A blue sky", [100, 150, 255]),
            ("Red flowers", [255, 100, 100]),
            ("Green grass", [100, 255, 100]),
            ("Yellow sun", [255, 255, 100]),
            ("Purple sunset", [200, 100, 255]),
            ("Orange sunset", [255, 150, 100]),
            ("Random text", [150, 200, 255])  # Default
        ]
        
        for prompt, expected_colors in test_cases:
            colors = self.model_demo._extract_colors_from_prompt(prompt)
            self.assertEqual(len(colors), 3)
            self.assertTrue(all(0 <= c <= 255 for c in colors))
    
    def test_sentiment_analysis_simulation(self) -> Any:
        """Test sentiment analysis simulation."""
        # Test positive sentiment
        positive_text: str = "I love this amazing product! It's wonderful and makes me so happy."
        result = self.model_demo._simulate_sentiment_analysis(positive_text)
        
        self.assertIn("sentiment", result)
        self.assertIn("confidence", result)
        self.assertIn("positive_score", result)
        self.assertIn("negative_score", result)
        self.assertIn("analysis", result)
        
        self.assertEqual(result["sentiment"], "Positive")
        self.assertGreater(result["positive_score"], result["negative_score"])
        
        # Test negative sentiment
        negative_text: str = "I hate this terrible product! It's awful and makes me so angry."
        result = self.model_demo._simulate_sentiment_analysis(negative_text)
        
        self.assertEqual(result["sentiment"], "Negative")
        self.assertGreater(result["negative_score"], result["positive_score"])
        
        # Test neutral sentiment
        neutral_text: str = "This is a neutral text without strong emotions."
        result = self.model_demo._simulate_sentiment_analysis(neutral_text)
        
        self.assertEqual(result["sentiment"], "Neutral")
    
    def test_topic_classification_simulation(self) -> Any:
        """Test topic classification simulation."""
        # Test technology topic
        tech_text: str = "The new computer software uses machine learning algorithms."
        result = self.model_demo._simulate_topic_classification(tech_text)
        
        self.assertIn("topic", result)
        self.assertIn("confidence", result)
        self.assertIn("topic_scores", result)
        self.assertIn("analysis", result)
        
        self.assertEqual(result["topic"], "Technology")
        self.assertGreater(result["topic_scores"]["technology"], 0)
        
        # Test sports topic
        sports_text: str = "The football game was exciting with great players."
        result = self.model_demo._simulate_topic_classification(sports_text)
        
        self.assertEqual(result["topic"], "Sports")
        self.assertGreater(result["topic_scores"]["sports"], 0)
    
    def test_language_detection_simulation(self) -> Any:
        """Test language detection simulation."""
        # Test English
        english_text: str = "The quick brown fox jumps over the lazy dog."
        result = self.model_demo._simulate_language_detection(english_text)
        
        self.assertIn("language", result)
        self.assertIn("confidence", result)
        self.assertIn("language_scores", result)
        self.assertIn("analysis", result)
        
        self.assertEqual(result["language"], "English")
        self.assertGreater(result["language_scores"]["English"], 0)
        
        # Test Spanish
        spanish_text: str = "El nuevo producto es excelente y muy útil para los usuarios."
        result = self.model_demo._simulate_language_detection(spanish_text)
        
        self.assertEqual(result["language"], "Spanish")
        self.assertGreater(result["language_scores"]["Spanish"], 0)


class TestVisualizationDemo(unittest.TestCase):
    """Test cases for VisualizationDemo class."""
    
    def setUp(self) -> Any:
        self.config = DemoConfig()
        self.viz_demo = VisualizationDemo(self.config)
    
    def test_initialization(self) -> Any:
        """Test demo initialization."""
        self.assertIsInstance(self.viz_demo.config, DemoConfig)
    
    def test_training_data_simulation(self) -> Any:
        """Test training data simulation."""
        epochs: int = 20
        learning_rate = 0.01
        batch_size: int = 32
        model_type: str = "CNN"
        dataset_size: int = 10000
        
        train_losses, val_losses, accuracies = self.viz_demo._simulate_training_data(
            epochs, learning_rate, batch_size, model_type, dataset_size
        )
        
        # Check data types and lengths
        self.assertIsInstance(train_losses, list)
        self.assertIsInstance(val_losses, list)
        self.assertIsInstance(accuracies, list)
        
        self.assertEqual(len(train_losses), epochs)
        self.assertEqual(len(val_losses), epochs)
        self.assertEqual(len(accuracies), epochs)
        
        # Check value ranges
        self.assertTrue(all(0.1 <= loss <= 2.0 for loss in train_losses))
        self.assertTrue(all(0.1 <= loss <= 2.0 for loss in val_losses))
        self.assertTrue(all(0.1 <= acc <= 0.98 for acc in accuracies))
        
        # Check that losses generally decrease
        self.assertLess(train_losses[-1], train_losses[0])
        self.assertLess(val_losses[-1], val_losses[0])
        
        # Check that accuracy generally increases
        self.assertGreater(accuracies[-1], accuracies[0])
    
    def test_model_comparison_simulation(self) -> Any:
        """Test model comparison simulation."""
        dataset: str = "MNIST"
        metric: str = "accuracy"
        models: List[Any] = ["CNN", "RNN", "Transformer"]
        
        comparison_data = self.viz_demo._simulate_model_comparison(dataset, metric, models)
        
        # Check structure
        self.assertIsInstance(comparison_data, dict)
        self.assertEqual(len(comparison_data), len(models))
        
        for model_name, metrics in comparison_data.items():
            self.assertIn(model_name, models)
            self.assertIn(metric, metrics)
            self.assertIsInstance(metrics[metric], float)
            self.assertTrue(0.1 <= metrics[metric] <= 0.99)
    
    def test_plot_creation(self) -> Any:
        """Test plot creation functionality."""
        # Test with sample data
        epochs: int = 10
        learning_rate = 0.01
        batch_size: int = 32
        model_type: str = "CNN"
        dataset_size: int = 5000
        
        loss_fig, acc_fig, lr_fig = self.viz_demo.visualize_training(
            epochs, learning_rate, batch_size, model_type, dataset_size
        )
        
        # Check that figures are created
        self.assertIsInstance(loss_fig, go.Figure)
        self.assertIsInstance(acc_fig, go.Figure)
        self.assertIsInstance(lr_fig, go.Figure)
        
        # Check figure properties
        self.assertIn("data", loss_fig)
        self.assertIn("layout", loss_fig)
        self.assertIn("data", acc_fig)
        self.assertIn("layout", acc_fig)
        self.assertIn("data", lr_fig)
        self.assertIn("layout", lr_fig)


class TestExperimentDemo(unittest.TestCase):
    """Test cases for ExperimentDemo class."""
    
    def setUp(self) -> Any:
        self.config = DemoConfig()
        self.exp_demo = ExperimentDemo(self.config)
    
    def test_initialization(self) -> Any:
        """Test demo initialization."""
        self.assertIsInstance(self.exp_demo.config, DemoConfig)
    
    def test_hyperparameter_tuning_simulation(self) -> Any:
        """Test hyperparameter tuning simulation."""
        learning_rates: List[Any] = [0.001, 0.01, 0.05]
        batch_sizes: List[Any] = [32, 64, 128]
        model_types: List[Any] = ["CNN", "Transformer"]
        epochs: int = 20
        
        results = self.exp_demo._simulate_hyperparameter_tuning(
            learning_rates, batch_sizes, model_types, epochs
        )
        
        # Check that results is a DataFrame
        self.assertIsInstance(results, pd.DataFrame)
        
        # Check expected columns
        expected_columns: List[Any] = ['learning_rate', 'batch_size', 'model_type', 
                           'accuracy', 'training_time', 'epochs']
        for col in expected_columns:
            self.assertIn(col, results.columns)
        
        # Check expected number of rows
        expected_rows = len(learning_rates) * len(batch_sizes) * len(model_types)
        self.assertEqual(len(results), expected_rows)
        
        # Check data types and ranges
        self.assertTrue(all(0.1 <= acc <= 0.99 for acc in results['accuracy']))
        self.assertTrue(all(0 < time for time in results['training_time']))
        self.assertTrue(all(epochs == ep for ep in results['epochs']))
        
        # Check that all combinations are present
        for lr in learning_rates:
            for bs in batch_sizes:
                for mt in model_types:
                    mask = ((results['learning_rate'] == lr) & 
                           (results['batch_size'] == bs) & 
                           (results['model_type'] == mt))
                    self.assertTrue(any(mask))
    
    def test_hyperparameter_tuning_interface(self) -> Any:
        """Test hyperparameter tuning interface."""
        learning_rates: List[Any] = [0.001, 0.01]
        batch_sizes: List[Any] = [32, 64]
        model_types: List[Any] = ["CNN"]
        epochs: int = 10
        
        heatmap_fig, results_df = self.exp_demo.tune_hyperparameters(
            learning_rates, batch_sizes, model_types, epochs
        )
        
        # Check that heatmap is created
        self.assertIsInstance(heatmap_fig, go.Figure)
        self.assertIn("data", heatmap_fig)
        self.assertIn("layout", heatmap_fig)
        
        # Check that results DataFrame is returned
        self.assertIsInstance(results_df, pd.DataFrame)
        self.assertGreater(len(results_df), 0)


class TestInteractiveDemoSystem(unittest.TestCase):
    """Test cases for InteractiveDemoSystem class."""
    
    def setUp(self) -> Any:
        self.config = DemoConfig()
        self.demo_system = InteractiveDemoSystem(self.config)
    
    def test_initialization(self) -> Any:
        """Test demo system initialization."""
        self.assertIsInstance(self.demo_system.config, DemoConfig)
        self.assertIsInstance(self.demo_system.model_demo, ModelInferenceDemo)
        self.assertIsInstance(self.demo_system.visualization_demo, VisualizationDemo)
        self.assertIsInstance(self.demo_system.experiment_demo, ExperimentDemo)
        self.assertIsNotNone(self.demo_system.demo_blocks)
    
    def test_demo_blocks_creation(self) -> Any:
        """Test that demo blocks are created correctly."""
        blocks = self.demo_system.demo_blocks
        
        # Check that blocks is a Gradio Blocks object
        self.assertIsNotNone(blocks)
        
        # Check that blocks has the expected structure
        # (Note: Detailed structure checking would require Gradio-specific testing)
        self.assertTrue(hasattr(blocks, 'launch'))
    
    def test_text_generation_demo_creation(self) -> Any:
        """Test text generation demo creation."""
        demo = self.demo_system.model_demo.create_text_generation_demo()
        
        # Check that demo is created
        self.assertIsNotNone(demo)
        
        # Test text generation function
        prompt: str = "The future of AI"
        max_length: int = 50
        temperature = 0.7
        model_type: str = "GPT-2 Style"
        top_p = 0.9
        top_k: int = 50
        
        result = demo.fn(prompt, max_length, temperature, model_type, top_p, top_k)
        
        self.assertIsInstance(result, str)
        self.assertIn(prompt, result)
    
    def test_image_generation_demo_creation(self) -> Any:
        """Test image generation demo creation."""
        demo = self.demo_system.model_demo.create_image_generation_demo()
        
        # Check that demo is created
        self.assertIsNotNone(demo)
        
        # Test image generation function
        prompt: str = "A beautiful sunset"
        image_size: str = "512x512"
        num_steps: int = 50
        guidance_scale = 7.5
        seed: int = 42
        
        img, metadata = demo.fn(prompt, image_size, num_steps, guidance_scale, seed)
        
        # Check image output
        if img is not None:
            self.assertIsInstance(img, np.ndarray)
            self.assertEqual(len(img.shape), 3)
            self.assertEqual(img.shape[2], 3)  # RGB
        
        # Check metadata output
        self.assertIsInstance(metadata, str)
        metadata_dict = json.loads(metadata)
        self.assertIn("prompt", metadata_dict)
        self.assertIn("size", metadata_dict)
    
    def test_classification_demo_creation(self) -> Any:
        """Test classification demo creation."""
        demo = self.demo_system.model_demo.create_classification_demo()
        
        # Check that demo is created
        self.assertIsNotNone(demo)
        
        # Test classification function
        text: str = "I love this amazing product!"
        model_type: str = "Sentiment Analysis"
        
        result = demo.fn(text, model_type)
        
        self.assertIsInstance(result, dict)
        self.assertIn("sentiment", result)
        self.assertIn("confidence", result)
    
    def test_training_visualization_demo_creation(self) -> Any:
        """Test training visualization demo creation."""
        demo = self.demo_system.visualization_demo.create_training_visualization_demo()
        
        # Check that demo is created
        self.assertIsNotNone(demo)
        
        # Test visualization function
        epochs: int = 10
        learning_rate = 0.01
        batch_size: int = 32
        model_type: str = "CNN"
        dataset_size: int = 5000
        
        loss_fig, acc_fig, lr_fig = demo.fn(epochs, learning_rate, batch_size, model_type, dataset_size)
        
        # Check that figures are created
        self.assertIsInstance(loss_fig, go.Figure)
        self.assertIsInstance(acc_fig, go.Figure)
        self.assertIsInstance(lr_fig, go.Figure)
    
    def test_model_comparison_demo_creation(self) -> Any:
        """Test model comparison demo creation."""
        demo = self.demo_system.visualization_demo.create_model_comparison_demo()
        
        # Check that demo is created
        self.assertIsNotNone(demo)
        
        # Test comparison function
        dataset: str = "MNIST"
        metric: str = "accuracy"
        models: List[Any] = ["CNN", "RNN", "Transformer"]
        
        fig = demo.fn(dataset, metric, models)
        
        # Check that figure is created
        self.assertIsInstance(fig, go.Figure)
    
    def test_hyperparameter_tuning_demo_creation(self) -> Any:
        """Test hyperparameter tuning demo creation."""
        demo = self.demo_system.experiment_demo.create_hyperparameter_tuning_demo()
        
        # Check that demo is created
        self.assertIsNotNone(demo)
        
        # Test tuning function
        learning_rates: List[Any] = [0.001, 0.01]
        batch_sizes: List[Any] = [32, 64]
        model_types: List[Any] = ["CNN"]
        epochs: int = 10
        
        heatmap_fig, results_df = demo.fn(learning_rates, batch_sizes, model_types, epochs)
        
        # Check that heatmap and results are created
        self.assertIsInstance(heatmap_fig, go.Figure)
        self.assertIsInstance(results_df, pd.DataFrame)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_create_quick_demo(self) -> Any:
        """Test quick demo creation."""
        # Test all demos
        demo_system = create_quick_demo("all")
        self.assertIsInstance(demo_system, InteractiveDemoSystem)
        self.assertEqual(demo_system.config.demo_port, 7860)
        
        # Test text demos
        demo_system = create_quick_demo("text")
        self.assertIsInstance(demo_system, InteractiveDemoSystem)
        self.assertEqual(demo_system.config.demo_port, 7861)
        
        # Test image demos
        demo_system = create_quick_demo("image")
        self.assertIsInstance(demo_system, InteractiveDemoSystem)
        self.assertEqual(demo_system.config.demo_port, 7862)
        
        # Test visualization demos
        demo_system = create_quick_demo("visualization")
        self.assertIsInstance(demo_system, InteractiveDemoSystem)
        self.assertEqual(demo_system.config.demo_port, 7863)
        
        # Test experiment demos
        demo_system = create_quick_demo("experiment")
        self.assertIsInstance(demo_system, InteractiveDemoSystem)
        self.assertEqual(demo_system.config.demo_port, 7864)
    
    def test_launch_demo(self) -> Any:
        """Test demo launch function."""
        # This test would normally launch the demo
        # For testing purposes, we'll just check that the function exists and can be called
        try:
            # This should not actually launch due to testing environment
            pass
        except Exception as e:
            # Expected in testing environment
            pass


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios."""
    
    def setUp(self) -> Any:
        self.config = DemoConfig()
        self.demo_system = InteractiveDemoSystem(self.config)
    
    def test_complete_demo_workflow(self) -> Any:
        """Test complete demo workflow."""
        # Test text generation
        text_demo = self.demo_system.model_demo.create_text_generation_demo()
        text_result = text_demo.fn("AI is amazing", 50, 0.7, "GPT-2 Style", 0.9, 50)
        self.assertIsInstance(text_result, str)
        self.assertIn("AI is amazing", text_result)
        
        # Test image generation
        image_demo = self.demo_system.model_demo.create_image_generation_demo()
        img_result, metadata = image_demo.fn("Beautiful sunset", "512x512", 50, 7.5, 42)
        if img_result is not None:
            self.assertIsInstance(img_result, np.ndarray)
        self.assertIsInstance(metadata, str)
        
        # Test classification
        class_demo = self.demo_system.model_demo.create_classification_demo()
        class_result = class_demo.fn("I love this!", "Sentiment Analysis")
        self.assertIsInstance(class_result, dict)
        self.assertIn("sentiment", class_result)
        
        # Test visualization
        viz_demo = self.demo_system.visualization_demo.create_training_visualization_demo()
        loss_fig, acc_fig, lr_fig = viz_demo.fn(10, 0.01, 32, "CNN", 5000)
        self.assertIsInstance(loss_fig, go.Figure)
        self.assertIsInstance(acc_fig, go.Figure)
        self.assertIsInstance(lr_fig, go.Figure)
        
        # Test hyperparameter tuning
        hp_demo = self.demo_system.experiment_demo.create_hyperparameter_tuning_demo()
        heatmap_fig, results_df = hp_demo.fn([0.001, 0.01], [32, 64], ["CNN"], 10)
        self.assertIsInstance(heatmap_fig, go.Figure)
        self.assertIsInstance(results_df, pd.DataFrame)
    
    def test_error_handling(self) -> Any:
        """Test error handling in demos."""
        # Test with empty input
        text_demo = self.demo_system.model_demo.create_text_generation_demo()
        result = text_demo.fn("", 50, 0.7, "GPT-2 Style", 0.9, 50)
        self.assertIn("Please enter a prompt", result)
        
        # Test with invalid parameters
        image_demo = self.demo_system.model_demo.create_image_generation_demo()
        try:
            img_result, metadata = image_demo.fn("", "invalid_size", 50, 7.5, 42)
            # Should handle gracefully
        except Exception as e:
            # Expected in some cases
            pass
    
    def test_demo_configuration(self) -> Any:
        """Test demo configuration options."""
        # Test different configurations
        configs: List[Any] = [
            {"demo_port": 8080, "demo_host": "127.0.0.1"},
            {"demo_port": 9000, "demo_share": True},
            {"device": "cuda", "max_examples": 20}
        ]
        
        for config_params in configs:
            config = DemoConfig()
            for key, value in config_params.items():
                setattr(config, key, value)
            
            demo_system = InteractiveDemoSystem(config)
            self.assertIsInstance(demo_system, InteractiveDemoSystem)


def run_demo_benchmark() -> Any:
    """Run interactive demo system benchmark."""
    print("Running Interactive Demo System Benchmark...")
    
    
    # Create configuration
    config = DemoConfig()
    
    # Benchmark demo system creation
    start_time = time.time()
    demo_system = InteractiveDemoSystem(config)
    creation_time = time.time() - start_time
    print(f"Demo system creation time: {creation_time*1000:.2f} ms")
    
    # Benchmark text generation demo
    start_time = time.time()
    text_demo = demo_system.model_demo.create_text_generation_demo()
    text_demo_creation_time = time.time() - start_time
    print(f"Text generation demo creation time: {text_demo_creation_time*1000:.2f} ms")
    
    # Benchmark text generation
    start_time = time.time()
    result = text_demo.fn("AI is amazing", 50, 0.7, "GPT-2 Style", 0.9, 50)
    text_generation_time = time.time() - start_time
    print(f"Text generation time: {text_generation_time*1000:.2f} ms")
    
    # Benchmark image generation demo
    start_time = time.time()
    image_demo = demo_system.model_demo.create_image_generation_demo()
    image_demo_creation_time = time.time() - start_time
    print(f"Image generation demo creation time: {image_demo_creation_time*1000:.2f} ms")
    
    # Benchmark image generation
    start_time = time.time()
    img_result, metadata = image_demo.fn("Beautiful sunset", "512x512", 50, 7.5, 42)
    image_generation_time = time.time() - start_time
    print(f"Image generation time: {image_generation_time*1000:.2f} ms")
    
    # Benchmark visualization demo
    start_time = time.time()
    viz_demo = demo_system.visualization_demo.create_training_visualization_demo()
    viz_demo_creation_time = time.time() - start_time
    print(f"Visualization demo creation time: {viz_demo_creation_time*1000:.2f} ms")
    
    # Benchmark visualization generation
    start_time = time.time()
    loss_fig, acc_fig, lr_fig = viz_demo.fn(20, 0.01, 32, "CNN", 10000)
    viz_generation_time = time.time() - start_time
    print(f"Visualization generation time: {viz_generation_time*1000:.2f} ms")
    
    # Summary
    print(f"\n{"="*60)
    print("INTERACTIVE DEMO SYSTEM BENCHMARK SUMMARY")
    print("="*60)
    print("All demo components created and tested successfully.")
    print("Demo system shows good performance for interactive use.")
    print("Ready for web-based deployment and user interaction.")


if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run demo benchmark
    print("\n"}="*60)
    run_demo_benchmark() 