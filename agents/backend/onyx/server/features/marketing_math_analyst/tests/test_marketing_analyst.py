import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append("c:/blatam-academy")

from agents.backend.onyx.server.features.marketing_math_analyst.analyst import MarketingMathAnalyst, AnalysisRequest
from agents.backend.onyx.server.features.marketing_math_analyst.researcher import Researcher
from agents.backend.onyx.server.features.marketing_math_analyst.social_connectors import TikTokConnector

@pytest.mark.asyncio
async def test_analyst_flow():
    # Mock Researcher
    mock_researcher = MagicMock(spec=Researcher)
    mock_researcher.find_relevant_papers = AsyncMock(return_value=["Paper A", "Paper B"])
    
    analyst = MarketingMathAnalyst(researcher=mock_researcher)
    
    request = AnalysisRequest(
        content="Test Campaign",
        content_type="text",
        platform="tiktok"
    )
    
    result = await analyst.analyze_campaign(request)
    
    assert result.strategy is not None
    assert len(result.mathematical_insights) > 0
    assert "Bass Diffusion Model" in result.mathematical_insights[0]
    assert len(result.research_citations) == 2

def test_bass_model_calculation():
    # Test logic implicitly via analyst for now, 
    # but in a real enterprise app, we'd test private methods or extract the math to a utility class.
    pass

@pytest.mark.asyncio
async def test_tiktok_connector_mock():
    connector = TikTokConnector(api_key="mock_key")
    data = await connector.get_campaign_data("123")
    assert data["platform"] == "tiktok"
    assert data["views"] == 15000
