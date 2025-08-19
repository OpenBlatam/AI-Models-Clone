from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import sys
import os
import logging
from pathlib import Path
from pretrained_models_implementation import (
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Runner script for Pre-trained Models and Tokenizers Implementation
Demonstrates various NLP tasks using HuggingFace Transformers.
"""


# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

    ModelConfig, PreTrainedModelManager, TextClassificationPipeline,
    TextGenerationPipeline, QuestionAnsweringPipeline, TokenClassificationPipeline,
    ModelRegistry, HuggingFacePipeline, demonstrate_pretrained_models
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_text_classification_demo():
    """Demonstrate text classification capabilities."""
    print("\n" + "="*60)
    print("TEXT CLASSIFICATION DEMONSTRATION")
    print("="*60)
    
    # Setup classification pipeline
    config = ModelConfig(
        model_name="distilbert-base-uncased",
        task_type="classification",
        max_length=128
    )
    
    classifier = TextClassificationPipeline(config, num_labels=2)
    
    # Test texts
    texts = [
        "I absolutely love this movie! It's fantastic!",
        "This is the worst film I've ever seen.",
        "The acting was amazing and the plot was engaging.",
        "Terrible waste of time, don't watch it.",
        "Outstanding performance by all actors!"
    ]
    
    print(f"Input texts: {texts}")
    
    # Get predictions
    predictions = classifier.predict(texts)
    probabilities = classifier.predict(texts, return_probs=True)
    
    print(f"\nPredictions: {predictions}")
    print(f"Probabilities shape: {probabilities.shape}")
    
    # Display results
    for i, (text, pred, prob) in enumerate(zip(texts, predictions, probabilities)):
        sentiment = "Positive" if pred == 1 else "Negative"
        confidence = prob[pred] * 100
        print(f"{i+1}. Text: {text[:50]}...")
        print(f"   Sentiment: {sentiment} (Confidence: {confidence:.1f}%)")
        print()

def run_text_generation_demo():
    """Demonstrate text generation capabilities."""
    print("\n" + "="*60)
    print("TEXT GENERATION DEMONSTRATION")
    print("="*60)
    
    # Setup generation pipeline
    config = ModelConfig(
        model_name="gpt2",
        task_type="generation",
        max_length=256
    )
    
    generator = TextGenerationPipeline(config)
    
    # Test prompts
    prompts = [
        "The future of artificial intelligence is",
        "In a world where technology advances rapidly,",
        "The best way to learn programming is",
        "Climate change is one of the biggest challenges",
        "The importance of education in society"
    ]
    
    for i, prompt in enumerate(prompts):
        print(f"\nPrompt {i+1}: {prompt}")
        
        # Generate multiple sequences
        generated_texts = generator.generate(
            prompt,
            max_length=50,
            temperature=0.8,
            top_k=50,
            top_p=0.9,
            repetition_penalty=1.1,
            num_return_sequences=2
        )
        
        for j, generated_text in enumerate(generated_texts):
            print(f"  Generated {j+1}: {generated_text}")
        print()

def run_question_answering_demo():
    """Demonstrate question answering capabilities."""
    print("\n" + "="*60)
    print("QUESTION ANSWERING DEMONSTRATION")
    print("="*60)
    
    # Setup QA pipeline
    config = ModelConfig(
        model_name="distilbert-base-cased-distilled-squad",
        task_type="qa",
        max_length=384
    )
    
    qa_pipeline = QuestionAnsweringPipeline(config)
    
    # Test questions and contexts
    qa_pairs = [
        {
            "question": "What is the capital of France?",
            "context": "Paris is the capital and most populous city of France. It is known for its art, fashion, gastronomy and culture."
        },
        {
            "question": "Who wrote Romeo and Juliet?",
            "context": "Romeo and Juliet is a tragedy written by William Shakespeare early in his career about two young star-crossed lovers."
        },
        {
            "question": "What is the largest planet in our solar system?",
            "context": "Jupiter is the fifth planet from the Sun and the largest in the Solar System. It is a gas giant with a mass more than two and a half times that of all the other planets in the Solar System combined."
        }
    ]
    
    for i, qa_pair in enumerate(qa_pairs):
        print(f"\nQuestion {i+1}: {qa_pair['question']}")
        print(f"Context: {qa_pair['context']}")
        
        answer = qa_pipeline.answer_question(
            qa_pair['question'], 
            qa_pair['context'],
            max_answer_length=30
        )
        
        print(f"Answer: {answer['answer']}")
        print(f"Confidence: {answer['confidence']:.3f}")
        print(f"Start Index: {answer['start_index']}, End Index: {answer['end_index']}")
        print()

def run_token_classification_demo():
    """Demonstrate token classification capabilities."""
    print("\n" + "="*60)
    print("TOKEN CLASSIFICATION DEMONSTRATION")
    print("="*60)
    
    # Setup token classification pipeline
    config = ModelConfig(
        model_name="bert-base-cased",
        task_type="token_classification",
        max_length=512
    )
    
    # Define label mappings for NER
    label2id = {
        "O": 0,           # Outside
        "B-PER": 1,       # Beginning of Person
        "I-PER": 2,       # Inside of Person
        "B-ORG": 3,       # Beginning of Organization
        "I-ORG": 4,       # Inside of Organization
        "B-LOC": 5,       # Beginning of Location
        "I-LOC": 6,       # Inside of Location
        "B-MISC": 7,      # Beginning of Miscellaneous
        "I-MISC": 8       # Inside of Miscellaneous
    }
    
    token_classifier = TokenClassificationPipeline(config, label2id)
    
    # Test texts
    texts = [
        "John Smith works at Microsoft in Seattle.",
        "Apple Inc. was founded by Steve Jobs in California.",
        "The Eiffel Tower is located in Paris, France.",
        "Albert Einstein was a German-born theoretical physicist."
    ]
    
    for i, text in enumerate(texts):
        print(f"\nText {i+1}: {text}")
        
        predictions = token_classifier.predict_tokens(text)
        
        print("Token Predictions:")
        for pred in predictions:
            if pred['label'] != 'O':  # Only show non-O labels
                print(f"  '{pred['token']}' -> {pred['label']}")
        print()

def run_model_registry_demo():
    """Demonstrate model registry capabilities."""
    print("\n" + "="*60)
    print("MODEL REGISTRY DEMONSTRATION")
    print("="*60)
    
    # Setup model registry
    registry = ModelRegistry()
    
    # Register different models
    models_to_register = [
        ("bert-classifier", ModelConfig(
            model_name="bert-base-uncased",
            task_type="classification",
            max_length=128
        )),
        ("gpt2-generator", ModelConfig(
            model_name="gpt2",
            task_type="generation",
            max_length=256
        )),
        ("distilbert-qa", ModelConfig(
            model_name="distilbert-base-cased-distilled-squad",
            task_type="qa",
            max_length=384
        ))
    ]
    
    print("Registering models...")
    for name, config in models_to_register:
        registry.register_model(name, config)
        print(f"  Registered: {name}")
    
    print(f"\nAvailable models: {registry.get_available_models()}")
    
    # Load and test models
    print("\nLoading models...")
    for name in registry.get_available_models():
        model_manager = registry.load_model(name)
        print(f"  Loaded {name}:")
        print(f"    Vocabulary size: {model_manager.get_vocab_size()}")
        print(f"    Device: {model_manager.device}")
        print(f"    Model type: {type(model_manager.model).__name__}")
    
    # Unload models
    print("\nUnloading models...")
    for name in registry.get_available_models():
        registry.unload_model(name)
        print(f"  Unloaded: {name}")

def run_huggingface_pipeline_demo():
    """Demonstrate HuggingFace pipeline wrapper."""
    print("\n" + "="*60)
    print("HUGGINGFACE PIPELINE DEMONSTRATION")
    print("="*60)
    
    try:
        # Setup different pipeline types
        pipelines = [
            ("sentiment-analysis", "distilbert-base-uncased-finetuned-sst-2-english"),
            ("text-generation", "gpt2"),
            ("question-answering", "distilbert-base-cased-distilled-squad")
        ]
        
        for task, model_name in pipelines:
            print(f"\nSetting up {task} pipeline with {model_name}...")
            
            try:
                pipeline_wrapper = HuggingFacePipeline(task, model_name)
                model_info = pipeline_wrapper.get_model_info()
                
                print(f"  Task: {model_info['task']}")
                print(f"  Model: {model_info['model_name']}")
                print(f"  Model Type: {model_info['model_type']}")
                print(f"  Tokenizer Type: {model_info['tokenizer_type']}")
                
                # Test the pipeline
                if task == "sentiment-analysis":
                    result = pipeline_wrapper(["I love this!", "I hate this!"])
                    print(f"  Test results: {result}")
                elif task == "text-generation":
                    result = pipeline_wrapper("The future is", max_length=30)
                    print(f"  Test result: {result}")
                elif task == "question-answering":
                    result = pipeline_wrapper(
                        question="What is the capital of France?",
                        context="Paris is the capital of France."
                    )
                    print(f"  Test result: {result}")
                
            except Exception as e:
                print(f"  Error with {task}: {str(e)}")
    
    except Exception as e:
        print(f"Error setting up HuggingFace pipelines: {str(e)}")

def main():
    """Main demonstration function."""
    print("Pre-trained Models and Tokenizers Implementation Demo")
    print("="*60)
    
    try:
        # Run all demonstrations
        run_text_classification_demo()
        run_text_generation_demo()
        run_question_answering_demo()
        run_token_classification_demo()
        run_model_registry_demo()
        run_huggingface_pipeline_demo()
        
        # Run the comprehensive demonstration
        print("\n" + "="*60)
        print("COMPREHENSIVE DEMONSTRATION")
        print("="*60)
        demonstrate_pretrained_models()
        
    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY")
    print("="*60)
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 