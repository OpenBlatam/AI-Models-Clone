from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS = 1000

# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from datetime import datetime
from ..interfaces import (
from typing import Any, List, Dict, Optional
import asyncio
"""
ONYX BLOG POSTS - Presenters
============================

Presentation layer for formatting and presenting blog post data.
Clean Architecture presentation adapters.
"""


    IBlogPresenter, BlogResult, GenerationStatus, BlogContent, 
    SEOData, GenerationMetrics, BlogSpec
)

logger = logging.getLogger(__name__)

class APIResponsePresenter:
    """Presenter for API responses"""
    
    async def present_blog_result(self, result: BlogResult) -> Dict[str, Any]:
        """Present blog result in API format"""
        
        response = {
            "request_id": result.request_id,
            "status": result.status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "success": result.status == GenerationStatus.COMPLETED
        }
        
        # Add content if available
        if result.content:
            response["content"] = {
                "title": result.content.title,
                "introduction": result.content.introduction,
                "sections": [
                    {
                        "title": section.get("title", ""),
                        "content": section.get("content", "")
                    }
                    for section in result.content.sections
                ],
                "conclusion": result.content.conclusion,
                "call_to_action": result.content.call_to_action,
                "word_count": result.content.word_count
            }
        
        # Add SEO data if available
        if result.seo_data:
            response["seo"] = {
                "meta_title": result.seo_data.meta_title,
                "meta_description": result.seo_data.meta_description,
                "keywords": list(result.seo_data.keywords),
                "og_title": result.seo_data.og_title,
                "og_description": result.seo_data.og_description,
                "schema_markup": result.seo_data.schema_markup
            }
        
        # Add metrics if available
        if result.metrics:
            response["metrics"] = {
                "generation_time_ms": result.metrics.generation_time_ms,
                "tokens_used": result.metrics.tokens_used,
                "cost_usd": result.metrics.cost_usd,
                "quality_score": result.metrics.quality_score,
                "model_used": result.metrics.model_used
            }
        
        # Add error if present
        if result.error:
            response["error"] = {
                "message": result.error,
                "type": "generation_error"
            }
        
        return response
    
    async def present_batch_results(self, results: List[BlogResult]) -> Dict[str, Any]:
        """Present batch results in API format"""
        
        # Process each result
        processed_results = []
        for result in results:
            processed_result = await self.present_blog_result(result)
            processed_results.append(processed_result)
        
        # Calculate batch statistics
        total_count = len(results)
        successful_count = sum(1 for r in results if r.status == GenerationStatus.COMPLETED)
        failed_count = total_count - successful_count
        
        batch_metrics = {
            "total_requests": total_count,
            "successful": successful_count,
            "failed": failed_count,
            "success_rate": (successful_count / total_count * 100) if total_count > 0 else 0
        }
        
        # Calculate aggregate metrics if available
        successful_results = [r for r in results if r.status == GenerationStatus.COMPLETED and r.metrics]
        if successful_results:
            total_time = sum(r.metrics.generation_time_ms for r in successful_results)
            total_tokens = sum(r.metrics.tokens_used for r in successful_results)
            total_cost = sum(r.metrics.cost_usd for r in successful_results)
            avg_quality = sum(r.metrics.quality_score for r in successful_results) / len(successful_results)
            
            batch_metrics.update({
                "total_generation_time_ms": total_time,
                "average_generation_time_ms": total_time / len(successful_results),
                "total_tokens_used": total_tokens,
                "total_cost_usd": total_cost,
                "average_quality_score": avg_quality
            })
        
        return {
            "batch_id": f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "summary": batch_metrics,
            "results": processed_results
        }
    
    async def present_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Present metrics in API format"""
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {
                "uptime_seconds": metrics.get("uptime_seconds", 0),
                "total_requests": metrics.get("total_requests", 0),
                "success_rate_percent": metrics.get("success_rate_percent", 0),
                "average_generation_time_ms": metrics.get("average_generation_time_ms", 0)
            },
            "usage_metrics": {
                "total_tokens_used": metrics.get("total_tokens_used", 0),
                "total_cost_usd": metrics.get("total_cost_usd", 0),
                "average_cost_per_request": metrics.get("average_cost_per_request", 0)
            },
            "distribution_metrics": {
                "requests_by_type": metrics.get("requests_by_type", {}),
                "requests_by_model": metrics.get("requests_by_model", {})
            }
        }

class DashboardPresenter:
    """Presenter for dashboard/UI display"""
    
    async def present_blog_result(self, result: BlogResult) -> Dict[str, Any]:
        """Present blog result for dashboard display"""
        
        presentation = {
            "id": result.request_id,
            "status": self._format_status(result.status),
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "success": result.status == GenerationStatus.COMPLETED
        }
        
        if result.content:
            presentation["content"] = {
                "title": result.content.title,
                "preview": self._create_preview(result.content),
                "word_count": result.content.word_count,
                "sections_count": len(result.content.sections),
                "reading_time_minutes": max(1, result.content.word_count // 200)
            }
        
        if result.metrics:
            presentation["performance"] = {
                "generation_time": f"{result.metrics.generation_time_ms / 1000:.1f}s",
                "quality_score": f"{result.metrics.quality_score:.1f}/10",
                "quality_grade": self._get_quality_grade(result.metrics.quality_score),
                "tokens_used": result.metrics.tokens_used,
                "cost": f"${result.metrics.cost_usd:.4f}",
                "model": result.metrics.model_used.split("/")[-1]  # Get model name only
            }
        
        if result.error:
            presentation["error"] = {
                "message": result.error,
                "severity": "error"
            }
        
        return presentation
    
    async def present_batch_summary(self, results: List[BlogResult]) -> Dict[str, Any]:
        """Present batch summary for dashboard"""
        
        total = len(results)
        successful = sum(1 for r in results if r.status == GenerationStatus.COMPLETED)
        
        # Calculate totals
        total_words = 0
        total_time = 0
        total_cost = 0
        quality_scores = []
        
        for result in results:
            if result.status == GenerationStatus.COMPLETED:
                if result.content:
                    total_words += result.content.word_count
                if result.metrics:
                    total_time += result.metrics.generation_time_ms
                    total_cost += result.metrics.cost_usd
                    quality_scores.append(result.metrics.quality_score)
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "batch_summary": {
                "total_blogs": total,
                "successful": successful,
                "failed": total - successful,
                "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%"
            },
            "content_summary": {
                "total_words": total_words,
                "average_words": total_words // successful if successful > 0 else 0,
                "total_reading_time": f"{max(1, total_words // 200)} min"
            },
            "performance_summary": {
                "total_time": f"{total_time/1000:.1f}s",
                "average_time": f"{total_time/successful/1000:.1f}s" if successful > 0 else "0s",
                "total_cost": f"${total_cost:.4f}",
                "average_cost": f"${total_cost/successful:.4f}" if successful > 0 else "$0.00",
                "average_quality": f"{avg_quality:.1f}/10",
                "quality_grade": self._get_quality_grade(avg_quality)
            }
        }
    
    async def present_analytics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Present analytics for dashboard"""
        
        uptime_hours = metrics.get("uptime_seconds", 0) / 3600
        
        return {
            "system_status": {
                "uptime": f"{uptime_hours:.1f} hours",
                "total_requests": metrics.get("total_requests", 0),
                "success_rate": f"{metrics.get('success_rate_percent', 0):.1f}%",
                "status": "healthy" if metrics.get("success_rate_percent", 0) > 80 else "warning"
            },
            "usage_statistics": {
                "tokens_used": f"{metrics.get('total_tokens_used', 0):,}",
                "total_cost": f"${metrics.get('total_cost_usd', 0):.2f}",
                "avg_cost_per_request": f"${metrics.get('average_cost_per_request', 0):.4f}",
                "avg_generation_time": f"{metrics.get('average_generation_time_ms', 0)/1000:.1f}s"
            },
            "popular_types": metrics.get("requests_by_type", {}),
            "model_usage": metrics.get("requests_by_model", {})
        }
    
    def _format_status(self, status: GenerationStatus) -> str:
        """Format status for display"""
        status_map = {
            GenerationStatus.PENDING: "Pending",
            GenerationStatus.GENERATING: "Generating...",
            GenerationStatus.COMPLETED: "Completed",
            GenerationStatus.FAILED: "Failed"
        }
        return status_map.get(status, "Unknown")
    
    def _create_preview(self, content: BlogContent) -> str:
        """Create content preview"""
        preview = content.introduction[:150]
        if len(content.introduction) > 150:
            preview += "..."
        return preview
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to grade"""
        if score >= 9.0:
            return "A+"
        elif score >= 8.0:
            return "A"
        elif score >= 7.0:
            return "B+"
        elif score >= 6.0:
            return "B"
        elif score >= 5.0:
            return "C+"
        elif score >= 4.0:
            return "C"
        elif score >= 3.0:
            return "D"
        else:
            return "F"

class ExportPresenter:
    """Presenter for content export formats"""
    
    async def present_as_markdown(self, result: BlogResult) -> str:
        """Present blog content as Markdown"""
        if not result.content:
            return "# Error\n\nNo content available for export."
        
        content = result.content
        markdown_parts = []
        
        # Title
        markdown_parts.append(f"# {content.title}\n")
        
        # Introduction
        if content.introduction:
            markdown_parts.append(f"{content.introduction}\n")
        
        # Sections
        for section in content.sections:
            title = section.get("title", "")
            section_content = section.get("content", "")
            
            if title:
                markdown_parts.append(f"## {title}\n")
            if section_content:
                markdown_parts.append(f"{section_content}\n")
        
        # Conclusion
        if content.conclusion:
            markdown_parts.append(f"## Conclusión\n\n{content.conclusion}\n")
        
        # Call to Action
        if content.call_to_action:
            markdown_parts.append(f"## ¿Qué sigue?\n\n{content.call_to_action}\n")
        
        # Metadata
        if result.metrics:
            markdown_parts.append("---\n")
            markdown_parts.append("## Metadatos\n")
            markdown_parts.append(f"- **Palabras:** {content.word_count}")
            markdown_parts.append(f"- **Tiempo de lectura:** {max(1, content.word_count // 200)} minutos")
            markdown_parts.append(f"- **Calidad:** {result.metrics.quality_score:.1f}/10")
            markdown_parts.append(f"- **Modelo:** {result.metrics.model_used}")
            markdown_parts.append(f"- **Generado en:** {result.metrics.generation_time_ms/1000:.1f}s")
        
        return "\n".join(markdown_parts)
    
    async def present_as_html(self, result: BlogResult) -> str:
        """Present blog content as HTML"""
        if not result.content:
            return "<div class='error'>No content available for export.</div>"
        
        content = result.content
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='es'>",
            "<head>",
            "    <meta charset='UTF-8'>",
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"    <title>{content.title}</title>",
        ]
        
        # Add SEO meta tags if available
        if result.seo_data:
            seo = result.seo_data
            if seo.meta_description:
                html_parts.append(f"    <meta name='description' content='{seo.meta_description}'>")
            if seo.keywords:
                html_parts.append(f"    <meta name='keywords' content='{', '.join(seo.keywords)}'>")
            if seo.og_title:
                html_parts.append(f"    <meta property='og:title' content='{seo.og_title}'>")
            if seo.og_description:
                html_parts.append(f"    <meta property='og:description' content='{seo.og_description}'>")
        
        html_parts.extend([
            "    <style>",
            "        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "        h1 { color: #333; border-bottom: 2px solid #333; }",
            "        h2 { color: #666; margin-top: 30px; }",
            "        p { line-height: 1.6; margin-bottom: 15px; }",
            "        .intro { font-size: 1.1em; font-style: italic; }",
            "        .cta { background: #f0f0f0; padding: 15px; border-left: 4px solid #333; margin: 20px 0; }",
            "        .metadata { border-top: 1px solid #ccc; margin-top: 30px; padding-top: 15px; font-size: 0.9em; color: #666; }",
            "    </style>",
            "</head>",
            "<body>",
            f"    <h1>{content.title}</h1>",
        ])
        
        # Introduction
        if content.introduction:
            html_parts.append(f"    <p class='intro'>{content.introduction}</p>")
        
        # Sections
        for section in content.sections:
            title = section.get("title", "")
            section_content = section.get("content", "")
            
            if title:
                html_parts.append(f"    <h2>{title}</h2>")
            if section_content:
                # Convert line breaks to paragraphs
                paragraphs = section_content.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        html_parts.append(f"    <p>{paragraph.strip()}</p>")
        
        # Conclusion
        if content.conclusion:
            html_parts.append("    <h2>Conclusión</h2>")
            html_parts.append(f"    <p>{content.conclusion}</p>")
        
        # Call to Action
        if content.call_to_action:
            html_parts.append(f"    <div class='cta'><strong>¿Qué sigue?</strong><br>{content.call_to_action}</div>")
        
        # Metadata
        if result.metrics:
            html_parts.extend([
                "    <div class='metadata'>",
                "        <h3>Metadatos del Artículo</h3>",
                f"        <p><strong>Palabras:</strong> {content.word_count} | ",
                f"<strong>Tiempo de lectura:</strong> {max(1, content.word_count // 200)} minutos | ",
                f"<strong>Calidad:</strong> {result.metrics.quality_score:.1f}/10</p>",
                f"        <p><strong>Generado con:</strong> {result.metrics.model_used} en {result.metrics.generation_time_ms/1000:.1f} segundos</p>",
                "    </div>"
            ])
        
        html_parts.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    async def present_as_json(self, result: BlogResult) -> str:
        """Present blog result as JSON"""
        # Convert result to dictionary, handling dataclasses
        result_dict = {
            "request_id": result.request_id,
            "status": result.status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "content": None,
            "seo_data": None,
            "metrics": None,
            "error": result.error
        }
        
        if result.content:
            result_dict["content"] = {
                "title": result.content.title,
                "introduction": result.content.introduction,
                "sections": list(result.content.sections),
                "conclusion": result.content.conclusion,
                "call_to_action": result.content.call_to_action,
                "word_count": result.content.word_count
            }
        
        if result.seo_data:
            result_dict["seo_data"] = {
                "meta_title": result.seo_data.meta_title,
                "meta_description": result.seo_data.meta_description,
                "keywords": list(result.seo_data.keywords),
                "og_title": result.seo_data.og_title,
                "og_description": result.seo_data.og_description,
                "schema_markup": result.seo_data.schema_markup
            }
        
        if result.metrics:
            result_dict["metrics"] = {
                "generation_time_ms": result.metrics.generation_time_ms,
                "tokens_used": result.metrics.tokens_used,
                "cost_usd": result.metrics.cost_usd,
                "quality_score": result.metrics.quality_score,
                "model_used": result.metrics.model_used
            }
        
        return json.dumps(result_dict, indent=2, ensure_ascii=False)

class UnifiedBlogPresenter:
    """Unified presenter that combines all presentation formats"""
    
    def __init__(self) -> Any:
        self.api_presenter = APIResponsePresenter()
        self.dashboard_presenter = DashboardPresenter()
        self.export_presenter = ExportPresenter()
    
    async async def present_for_api(self, result: BlogResult) -> Dict[str, Any]:
        """Present for API consumption"""
        return await self.api_presenter.present_blog_result(result)
    
    async def present_for_dashboard(self, result: BlogResult) -> Dict[str, Any]:
        """Present for dashboard display"""
        return await self.dashboard_presenter.present_blog_result(result)
    
    async def present_for_export(self, result: BlogResult, format: str = "markdown") -> str:
        """Present for export in specified format"""
        if format.lower() == "markdown":
            return await self.export_presenter.present_as_markdown(result)
        elif format.lower() == "html":
            return await self.export_presenter.present_as_html(result)
        elif format.lower() == "json":
            return await self.export_presenter.present_as_json(result)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async async def present_batch_for_api(self, results: List[BlogResult]) -> Dict[str, Any]:
        """Present batch results for API"""
        return await self.api_presenter.present_batch_results(results)
    
    async def present_batch_for_dashboard(self, results: List[BlogResult]) -> Dict[str, Any]:
        """Present batch summary for dashboard"""
        return await self.dashboard_presenter.present_batch_summary(results)
    
    async def present_metrics(self, metrics: Dict[str, Any], format: str = "api") -> Dict[str, Any]:
        """Present metrics in specified format"""
        if format == "api":
            return await self.api_presenter.present_metrics(metrics)
        elif format == "dashboard":
            return await self.dashboard_presenter.present_analytics(metrics)
        else:
            raise ValueError(f"Unsupported metrics format: {format}")

# === EXPORTS ===

__all__ = [
    'APIResponsePresenter',
    'DashboardPresenter',
    'ExportPresenter', 
    'UnifiedBlogPresenter'
] 