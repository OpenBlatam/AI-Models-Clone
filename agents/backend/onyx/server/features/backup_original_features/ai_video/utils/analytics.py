import msgspec
from typing import List, Optional

class AnalyticsInfo(msgspec.Struct, frozen=True, slots=True):
    """
    Información de analytics y engagement.
    """
    analytics: Optional[dict] = None
    engagement_metrics: Optional[dict] = None
    auto_tags: List[str] = msgspec.field(default_factory=list)

    def with_analytics(self, analytics: dict) -> 'AnalyticsInfo':
        return self.update(analytics=analytics)

    def with_engagement_metrics(self, metrics: dict) -> 'AnalyticsInfo':
        return self.update(engagement_metrics=metrics)

    def with_auto_tags(self, tags: List[str]) -> 'AnalyticsInfo':
        return self.update(auto_tags=tags) 