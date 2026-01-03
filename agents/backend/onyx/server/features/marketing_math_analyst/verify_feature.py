import asyncio
import sys
import os

# Add the project root to sys.path to allow imports
sys.path.append("c:/blatam-academy")

from agents.backend.onyx.server.features.marketing_math_analyst.analyst import MarketingMathAnalyst, AnalysisRequest
from agents.backend.onyx.server.features.marketing_math_analyst.researcher import Researcher

async def main():
    print("Starting Marketing Math Analyst Verification...")

    # 1. Initialize Researcher (Mocked)
    researcher = Researcher(openrouter_api_key="mock_key")
    
    # 2. Initialize Analyst
    analyst = MarketingMathAnalyst(researcher)
    
    # 3. Create a Dummy Request
    request = AnalysisRequest(
        content="We are launching a new energy drink targeting gamers.",
        content_type="text",
        platform="tiktok"
    )
    
    # 4. Run Analysis
    print(f"Analyzing content: {request.content}")
    result = await analyst.analyze_campaign(request)
    
    # 5. Print Results
    print("\n--- Analysis Result ---")
    print(f"Strategy: {result.strategy}")
    print("\nMathematical Insights:")
    for insight in result.mathematical_insights:
        print(f"- {insight}")
        
    print("\nResearch Citations:")
    for citation in result.research_citations:
        print(f"- {citation}")
        
    print("\nVerification Complete!")

if __name__ == "__main__":
    asyncio.run(main())
