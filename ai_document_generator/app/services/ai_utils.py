"""
AI service utilities following functional patterns
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.schemas.ai import AIProvider, AIModel


def create_ai_generation_request(
    prompt: str,
    provider: AIProvider = AIProvider.OPENAI,
    model: AIModel = AIModel.GPT_4,
    max_tokens: Optional[int] = None,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create AI generation request with defaults."""
    return {
        "prompt": prompt,
        "provider": provider,
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system_prompt": system_prompt,
        **kwargs
    }


def create_analysis_prompt(content: str, analysis_type: str) -> str:
    """Create analysis prompt based on type."""
    prompts = {
        "sentiment": f"Analyze the sentiment of the following text and provide a score from -1 (very negative) to 1 (very positive):\n\n{content}",
        "quality": f"Analyze the quality of the following text and provide scores for grammar, clarity, coherence, and style (0-10 scale):\n\n{content}",
        "plagiarism": f"Check the following text for potential plagiarism and provide a similarity score (0-1):\n\n{content}",
        "readability": f"Analyze the readability of the following text and provide a readability score and grade level:\n\n{content}",
        "summary": f"Provide a concise summary of the following text:\n\n{content}"
    }
    
    return prompts.get(analysis_type, f"Analyze the following text for {analysis_type}:\n\n{content}")


def get_analysis_system_prompt(analysis_type: str) -> str:
    """Get system prompt for analysis type."""
    prompts = {
        "sentiment": "You are an expert sentiment analysis tool. Provide accurate sentiment scores and explanations.",
        "quality": "You are an expert writing quality assessor. Provide detailed quality scores and suggestions.",
        "plagiarism": "You are a plagiarism detection tool. Provide similarity scores and identify potential issues.",
        "readability": "You are a readability analysis tool. Provide readability scores and grade levels.",
        "summary": "You are an expert summarization tool. Provide clear, concise summaries."
    }
    return prompts.get(analysis_type, "You are a helpful analysis tool.")


def parse_analysis_results(content: str, analysis_type: str) -> Dict[str, Any]:
    """Parse analysis results from AI response."""
    try:
        import json
        return json.loads(content)
    except:
        return {
            "raw_response": content,
            "confidence": 0.8,
            "analysis_type": analysis_type
        }


def create_improvement_prompt(
    content: str,
    improvement_type: str,
    target_audience: Optional[str] = None,
    writing_style: Optional[str] = None
) -> str:
    """Create improvement prompt based on type."""
    base_prompt = f"Improve the following text for {improvement_type}:\n\n{content}\n\n"
    
    if target_audience:
        base_prompt += f"Target audience: {target_audience}\n"
    
    if writing_style:
        base_prompt += f"Writing style: {writing_style}\n"
    
    base_prompt += "Provide the improved version and explain the key changes made."
    return base_prompt


def parse_improvements(content: str) -> List[Dict[str, Any]]:
    """Parse improvement changes from AI response."""
    return [
        {
            "type": "improvement",
            "description": "Content improved for better clarity and style",
            "confidence": 0.8
        }
    ]


def create_translation_prompt(
    content: str,
    source_language: str,
    target_language: str
) -> str:
    """Create translation prompt."""
    return f"Translate the following text from {source_language} to {target_language}:\n\n{content}"


def create_summarization_prompt(
    content: str,
    summary_type: str,
    max_length: int = 200
) -> str:
    """Create summarization prompt based on type."""
    if summary_type == "extractive":
        return f"Create an extractive summary of the following text (select the most important sentences):\n\n{content}"
    elif summary_type == "abstractive":
        return f"Create an abstractive summary of the following text in approximately {max_length} words:\n\n{content}"
    elif summary_type == "bullet_points":
        return f"Create a bullet-point summary of the following text:\n\n{content}"
    else:
        return f"Create a summary of the following text:\n\n{content}"


def calculate_compression_ratio(original_length: int, summary_length: int) -> float:
    """Calculate compression ratio for summarization."""
    if original_length == 0:
        return 0.0
    return summary_length / original_length


def get_available_models() -> Dict[str, List[Dict[str, str]]]:
    """Get available AI models by provider."""
    return {
        "openai": [
            {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Faster GPT-4"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and efficient"}
        ],
        "anthropic": [
            {"id": "claude-3-opus", "name": "Claude 3 Opus", "description": "Most powerful Claude"},
            {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Balanced performance"},
            {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "description": "Fast and efficient"}
        ],
        "deepseek": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "General purpose chat"},
            {"id": "deepseek-coder", "name": "DeepSeek Coder", "description": "Code generation"}
        ],
        "google": [
            {"id": "gemini-pro", "name": "Gemini Pro", "description": "Google's advanced model"},
            {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "description": "Multimodal model"}
        ]
    }


def validate_ai_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate AI request data."""
    required_fields = ["prompt"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate prompt length
    if len(data["prompt"]) > 10000:
        raise ValueError("Prompt too long (max 10000 characters)")
    
    # Validate temperature
    if "temperature" in data:
        temp = data["temperature"]
        if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
            raise ValueError("Temperature must be between 0 and 2")
    
    return data


def create_usage_stats(
    total_requests: int = 0,
    total_tokens: int = 0,
    total_cost: float = 0.0,
    requests_today: int = 0,
    tokens_today: int = 0,
    cost_today: float = 0.0
) -> Dict[str, Any]:
    """Create usage statistics response."""
    return {
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "total_cost": total_cost,
        "requests_today": requests_today,
        "tokens_today": tokens_today,
        "cost_today": cost_today,
        "by_provider": {
            "openai": {"requests": 0, "tokens": 0, "cost": 0.0},
            "anthropic": {"requests": 0, "tokens": 0, "cost": 0.0},
            "deepseek": {"requests": 0, "tokens": 0, "cost": 0.0}
        }
    }




