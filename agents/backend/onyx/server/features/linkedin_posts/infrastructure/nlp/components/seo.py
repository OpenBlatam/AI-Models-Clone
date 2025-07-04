from typing import Dict, Any
from ..seo_analyser import analyse_seo

class SEOComponent:
    def analyse(self, text: str) -> Dict[str, Any]:
        return analyse_seo(text) 