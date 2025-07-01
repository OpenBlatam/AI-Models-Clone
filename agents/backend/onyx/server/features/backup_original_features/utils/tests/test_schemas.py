import pytest
from agents.backend.onyx.server.features.utils.schemas import GenerationRequest, BatchGenerationRequest, GenerationResponse, BatchGenerationResponse, TokenResponse, RefreshTokenRequest
import orjson

def test_generation_request_example():
    obj = GenerationRequest.example()
    assert isinstance(obj, GenerationRequest)
    assert obj.prompt
    assert isinstance(orjson.loads(obj.json()), dict)

def test_generation_request_random():
    obj = GenerationRequest.random()
    assert isinstance(obj, GenerationRequest)
    assert obj.prompt


def test_batch_generation_request_example():
    obj = BatchGenerationRequest.example()
    assert isinstance(obj, BatchGenerationRequest)
    assert obj.prompts
    assert isinstance(orjson.loads(obj.json()), dict)

def test_batch_generation_request_random():
    obj = BatchGenerationRequest.random()
    assert isinstance(obj, BatchGenerationRequest)
    assert obj.prompts


def test_generation_response_example():
    obj = GenerationResponse.example()
    assert isinstance(obj, GenerationResponse)
    assert obj.result
    assert isinstance(orjson.loads(obj.json()), dict)

def test_generation_response_random():
    obj = GenerationResponse.random()
    assert isinstance(obj, GenerationResponse)
    assert obj.result


def test_batch_generation_response_example():
    obj = BatchGenerationResponse.example()
    assert isinstance(obj, BatchGenerationResponse)
    assert obj.results
    assert isinstance(orjson.loads(obj.json()), dict)

def test_batch_generation_response_random():
    obj = BatchGenerationResponse.random()
    assert isinstance(obj, BatchGenerationResponse)
    assert obj.results


def test_token_response_example():
    obj = TokenResponse.example()
    assert isinstance(obj, TokenResponse)
    assert obj.access_token
    assert isinstance(orjson.loads(obj.json()), dict)

def test_token_response_random():
    obj = TokenResponse.random()
    assert isinstance(obj, TokenResponse)
    assert obj.access_token


def test_refresh_token_request_example():
    obj = RefreshTokenRequest.example()
    assert isinstance(obj, RefreshTokenRequest)
    assert obj.refresh_token
    assert isinstance(orjson.loads(obj.json()), dict)

def test_refresh_token_request_random():
    obj = RefreshTokenRequest.random()
    assert isinstance(obj, RefreshTokenRequest)
    assert obj.refresh_token 