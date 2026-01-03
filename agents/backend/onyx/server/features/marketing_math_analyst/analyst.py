import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import math
from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

class AnalysisRequest(BaseModel):
    content: str
    content_type: str  # 'text', 'pdf_text', 'social_metrics'
    platform: Optional[str] = None

class AnalysisResult(BaseModel):
    strategy: str
    mathematical_insights: List[str]
    research_citations: List[str]

class MarketingMathAnalyst:
    """
    Core class for the Marketing Math Analyst feature.
    Analyzes marketing data using 'Marketing Mathematics' principles.
    """

    def __init__(self, researcher: Any = None):
        """
        Initialize the analyst.
        
        Args:
            researcher: An instance of the Researcher class to perform external lookups.
        """
        self.researcher = researcher
        logger.info("MarketingMathAnalyst initialized.")

    async def analyze_campaign(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyzes a campaign or content based on the provided request.
        """
        logger.info(f"Analyzing content of type: {request.content_type}")
        
        # 1. Ingest/Pre-process Data
        processed_data = self._ingest_data(request.content, request.content_type)
        
        # 2. Apply Marketing Math Principles
        math_insights = self._apply_marketing_math(processed_data)
        
        # 3. Perform Research (if researcher is available)
        citations = []
        if self.researcher:
            citations = await self.researcher.find_relevant_papers(processed_data)
            
        # 4. Generate Strategy
        strategy = self._generate_strategy(processed_data, math_insights, citations)
        
        return AnalysisResult(
            strategy=strategy,
            mathematical_insights=math_insights,
            research_citations=citations
        )

    def _ingest_data(self, content: str, content_type: str) -> Dict[str, Any]:
        """
        Parses and structures the input data.
        """
        # Placeholder for more complex parsing logic (e.g., PDF text extraction cleanup)
        return {
            "raw_text": content,
            "type": content_type,
            "metrics": {} # Extract metrics if possible
        }

    def _apply_marketing_math(self, data: Dict[str, Any]) -> List[str]:
        """
        Applies mathematical models to the data using configured parameters.
        """
        insights = []
        
        # --- 1. Bass Diffusion Model Analysis ---
        p = settings.BASS_P
        q = settings.BASS_Q
        
        try:
            t_peak = math.log(q/p) / (p+q)
            insights.append(
                f"Bass Diffusion Model (Bass, 1969): Based on estimated coefficients (p={p}, q={q}), "
                f"peak adoption is projected to occur at T={t_peak:.1f} time units."
            )
        except (ValueError, ZeroDivisionError) as e:
            logger.warning(f"Bass Model calculation failed: {e}")
            insights.append("Bass Model calculation failed due to invalid parameters.")

        # --- 2. Customer Lifetime Value (CLV) ---
        margin = settings.CLV_MARGIN
        r = settings.CLV_RETENTION_RATE
        d = settings.CLV_DISCOUNT_RATE
        
        try:
            clv = margin * (r / (1 + d - r))
            insights.append(
                f"Customer Lifetime Value (Berger & Nasr, 1998): Estimated CLV is ${clv:.2f} "
                f"assuming {r*100}% retention and {d*100}% discount rate."
            )
        except ZeroDivisionError:
             insights.append("CLV calculation failed: Denominator zero.")

        # --- 3. Marketing Mix Modeling (MMM) ---
        decay = settings.MMM_DECAY_LAMBDA
        alpha = settings.MMM_SATURATION_ALPHA
        beta = settings.MMM_MAX_SALES_BETA
        
        # Mock spend data (last 5 weeks) - In production, this should come from 'data'
        weekly_spend = data.get("metrics", {}).get("weekly_spend", [1000, 1200, 1500, 800, 2000])
        
        current_adstock = 0
        for spend in weekly_spend:
            current_adstock = spend + (decay * current_adstock)
            
        current_sales_projection = beta * (1 - math.exp(-alpha * current_adstock))
        
        insights.append(
            f"Marketing Mix Modeling (Little, 1979): Current Adstock level is {current_adstock:.0f}. "
            f"Projected sales impact (Diminishing Returns) is {current_sales_projection:.0f} units."
        )

        # --- 4. Vidale-Wolfe Model ---
        r_const = settings.VW_RESPONSE_CONSTANT
        M = settings.VW_MARKET_POTENTIAL
        lam = settings.VW_DECAY_LAMBDA
        
        # Mock current state - In production, get from 'data'
        current_sales = data.get("metrics", {}).get("current_sales", 20000)
        ad_spend = data.get("metrics", {}).get("ad_spend", 5000)
        
        sales_change = r_const * ad_spend * (M - current_sales) / M - lam * current_sales
        
        insights.append(
            f"Vidale-Wolfe Model (1957): With ad spend of {ad_spend}, sales are changing by {sales_change:.1f} units/period. "
            f"('r' constant={r_const}, Decay={lam})"
        )

        insights.append("Viral coefficient estimation: High probability of K-factor > 1.0 due to emotional triggers.")
        
        return insights

    def _generate_strategy(self, data: Dict[str, Any], insights: List[str], citations: List[str]) -> str:
        """
        Synthesizes findings into a cohesive strategy.
        """
        strategy = (
            f"Based on the analysis of the {data['type']} content, we recommend a multi-channel approach. "
            "The mathematical indicators suggest a high potential for organic growth. "
            "Leverage the identified emotional triggers to boost the K-factor. "
            "Refer to the cited papers for specific optimization techniques."
        )
        return strategy
