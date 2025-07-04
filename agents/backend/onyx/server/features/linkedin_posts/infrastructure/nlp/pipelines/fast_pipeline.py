from typing import Dict, Any
from ..components.enhancer import EnhancerComponent, get_fast_nlp_enhancer
from ..components.grammar import GrammarComponent
from ..components.seo import SEOComponent

class FastPipeline:
    """Combines enhancer, grammar and SEO analysis in one call."""
    def __init__(self):
        self.enhancer = get_fast_nlp_enhancer()
        self.grammar = GrammarComponent()
        self.seo = SEOComponent()

    async def enhance(self, text: str) -> Dict[str, Any]:
        base = await self.enhancer.enhance_post_fast(text)
        enhanced = base["enhanced"]
        # Grammar already done inside enhancer; nothing extra.
        seo_res = self.seo.analyse(enhanced["rewritten"])
        enhanced.update(seo_res)
        return {
            **base,
            "enhanced": enhanced
        } 