#!/usr/bin/env python3
"""
Refactored Gradio Interface for Enhanced SEO Engine
Leverages advanced architecture with improved UX and real-time monitoring
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import gradio as gr
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from refactored_seo_engine import (
    RefactoredSEOEngine, RefactoredSEOConfig, SEOEngineFactory,
    CacheStrategy, ProcessingMode
)

# ============================================================================
# GLOBAL STATE MANAGEMENT
# ============================================================================

class GlobalState:
    """Global state manager for the Gradio interface."""
    
    def __init__(self):
        self.engine: Optional[RefactoredSEOEngine] = None
        self.config: Optional[RefactoredSEOConfig] = None
        self.metrics_history: List[Dict[str, Any]] = []
        self.processing_queue: List[Dict[str, Any]] = []
        self.last_update = time.time()
    
    async def initialize_engine(self, config: RefactoredSEOConfig) -> None:
        """Initialize the SEO engine with configuration."""
        if self.engine:
            await self.engine.cleanup()
        
        self.config = config
        self.engine = RefactoredSEOEngine(config)
        
        # Start background metrics collection
        asyncio.create_task(self._collect_metrics_background())
    
    async def _collect_metrics_background(self) -> None:
        """Collect metrics in the background."""
        while self.engine:
            try:
                metrics = await self.engine.get_metrics()
                metrics['timestamp'] = time.time()
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics (last 100 entries)
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Metrics collection error: {e}")
                await asyncio.sleep(10)
    
    def add_to_queue(self, text: str, user_id: str) -> str:
        """Add text to processing queue."""
        queue_id = f"{user_id}_{int(time.time())}"
        self.processing_queue.append({
            'id': queue_id,
            'text': text,
            'user_id': user_id,
            'timestamp': time.time(),
            'status': 'pending'
        })
        return queue_id
    
    def get_queue_status(self, queue_id: str) -> Optional[Dict[str, Any]]:
        """Get status of queued item."""
        for item in self.processing_queue:
            if item['id'] == queue_id:
                return item
        return None

# Initialize global state
global_state = GlobalState()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_metrics(metrics: Dict[str, Any]) -> str:
    """Format metrics into human-readable string."""
    if not metrics:
        return "No metrics available"
    
    output = []
    
    # System metrics
    if 'system' in metrics:
        sys_info = metrics['system']
        output.append("🖥️ **System Information:**")
        output.append(f"   • CPU Cores: {sys_info.get('cpu_count', 'N/A')}")
        output.append(f"   • Memory Usage: {sys_info.get('memory_usage', {}).get('percent', 'N/A')}%")
        output.append(f"   • GPU Available: {'✅' if sys_info.get('gpu_available') else '❌'}")
        output.append(f"   • GPU Count: {sys_info.get('gpu_count', 0)}")
    
    # Processing metrics
    if 'counters' in metrics:
        counters = metrics['counters']
        output.append("\n📊 **Processing Metrics:**")
        output.append(f"   • Texts Processed: {counters.get('texts_processed', 0)}")
        output.append(f"   • Cache Hits: {counters.get('cache_hits', 0)}")
        output.append(f"   • Cache Misses: {counters.get('cache_misses', 0)}")
        output.append(f"   • Analysis Errors: {counters.get('analysis_errors', 0)}")
    
    # Cache metrics
    if 'cache' in metrics:
        cache_stats = metrics['cache']
        output.append("\n💾 **Cache Metrics:**")
        output.append(f"   • Hits: {cache_stats.get('hits', 0)}")
        output.append(f"   • Misses: {cache_stats.get('misses', 0)}")
        output.append(f"   • Evictions: {cache_stats.get('evictions', 0)}")
        output.append(f"   • Hit Rate: {cache_stats.get('hits', 0) / max(cache_stats.get('hits', 0) + cache_stats.get('misses', 0), 1) * 100:.1f}%")
    
    # Timing metrics
    if 'timers' in metrics and 'seo_analysis' in metrics['timers']:
        timing = metrics['timers']['seo_analysis']
        output.append("\n⏱️ **Performance Metrics:**")
        output.append(f"   • Average Processing Time: {timing.get('mean', 0):.3f}s")
        output.append(f"   • 95th Percentile: {timing.get('p95', 0):.3f}s")
        output.append(f"   • 99th Percentile: {timing.get('p99', 0):.3f}s")
    
    return "\n".join(output)

def create_performance_chart(metrics_history: List[Dict[str, Any]]) -> go.Figure:
    """Create performance chart from metrics history."""
    if not metrics_history:
        return go.Figure().add_annotation(
            text="No metrics data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Extract data
    timestamps = [m.get('timestamp', 0) for m in metrics_history]
    cache_hits = [m.get('counters', {}).get('cache_hits', 0) for m in metrics_history]
    cache_misses = [m.get('counters', {}).get('cache_misses', 0) for m in metrics_history]
    texts_processed = [m.get('counters', {}).get('texts_processed', 0) for m in metrics_history]
    
    # Convert timestamps to datetime
    datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Cache Performance', 'Processing Volume', 'Cache Hit Rate', 'System Load'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Cache Performance
    fig.add_trace(
        go.Scatter(x=datetimes, y=cache_hits, name="Cache Hits", line=dict(color='green')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=datetimes, y=cache_misses, name="Cache Misses", line=dict(color='red')),
        row=1, col=1
    )
    
    # Processing Volume
    fig.add_trace(
        go.Bar(x=datetimes, y=texts_processed, name="Texts Processed", marker_color='blue'),
        row=1, col=2
    )
    
    # Cache Hit Rate
    hit_rates = []
    for i in range(len(cache_hits)):
        total = cache_hits[i] + cache_misses[i]
        rate = (cache_hits[i] / total * 100) if total > 0 else 0
        hit_rates.append(rate)
    
    fig.add_trace(
        go.Scatter(x=datetimes, y=hit_rates, name="Hit Rate %", line=dict(color='purple')),
        row=2, col=1
    )
    
    # System Load (simulated)
    system_load = [np.random.normal(50, 10) for _ in range(len(datetimes))]
    fig.add_trace(
        go.Scatter(x=datetimes, y=system_load, name="System Load %", line=dict(color='orange')),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text="Real-time Performance Metrics"
    )
    
    return fig

def create_seo_score_distribution(metrics_history: List[Dict[str, Any]]) -> go.Figure:
    """Create SEO score distribution chart."""
    if not metrics_history:
        return go.Figure().add_annotation(
            text="No SEO analysis data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Extract SEO scores (this would come from actual analysis results)
    # For now, generate sample data
    seo_scores = np.random.normal(75, 15, 100)
    seo_scores = np.clip(seo_scores, 0, 100)
    
    fig = px.histogram(
        x=seo_scores,
        nbins=20,
        title="SEO Score Distribution",
        labels={'x': 'SEO Score', 'y': 'Frequency'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_layout(
        xaxis_title="SEO Score",
        yaxis_title="Frequency",
        showlegend=False
    )
    
    return fig

def create_keyword_analysis_chart() -> go.Figure:
    """Create keyword analysis chart."""
    # Sample keyword data
    keywords = ['seo', 'optimization', 'content', 'marketing', 'digital', 'strategy', 'analysis', 'performance']
    frequencies = [45, 38, 32, 28, 25, 22, 18, 15]
    
    fig = go.Figure(data=[
        go.Bar(x=keywords, y=frequencies, marker_color='lightcoral')
    ])
    
    fig.update_layout(
        title="Top Keywords Frequency",
        xaxis_title="Keywords",
        yaxis_title="Frequency",
        showlegend=False
    )
    
    return fig

# ============================================================================
# CORE PROCESSING FUNCTIONS
# ============================================================================

async def analyze_single_text(text: str, progress: gr.Progress) -> str:
    """Analyze single text with progress updates."""
    if not global_state.engine:
        return "❌ Engine not initialized. Please configure and initialize the engine first."
    
    if not text.strip():
        return "❌ Please provide text to analyze."
    
    try:
        progress(0.1, desc="Validating input...")
        
        # Add to processing queue
        queue_id = global_state.add_to_queue(text, "user_1")
        
        progress(0.3, desc="Performing SEO analysis...")
        
        # Perform analysis
        result = await global_state.engine.analyze_text(text)
        
        progress(0.8, desc="Formatting results...")
        
        # Update queue status
        for item in global_state.processing_queue:
            if item['id'] == queue_id:
                item['status'] = 'completed'
                item['result'] = result
                break
        
        progress(1.0, desc="Analysis complete!")
        
        # Format result
        formatted_result = {
            'text_preview': text[:100] + "..." if len(text) > 100 else text,
            'seo_score': result.get('seo_score', 0),
            'word_count': result.get('word_count', 0),
            'character_count': result.get('character_count', 0),
            'sentence_count': result.get('sentence_count', 0),
            'readability_score': result.get('readability_score', 0),
            'unique_keywords': result.get('unique_keywords', 0),
            'structure_score': result.get('structure_score', 0),
            'processing_time': result.get('processing_time', 0),
            'timestamp': datetime.fromtimestamp(result.get('timestamp', time.time())).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        # Update queue status
        for item in global_state.processing_queue:
            if item['id'] == queue_id:
                item['status'] = 'failed'
                item['error'] = str(e)
                break
        
        return f"❌ Analysis failed: {str(e)}"

async def analyze_multiple_texts(texts_input: str, progress: gr.Progress) -> str:
    """Analyze multiple texts in batch."""
    if not global_state.engine:
        return "❌ Engine not initialized. Please configure and initialize the engine first."
    
    if not texts_input.strip():
        return "❌ Please provide texts to analyze."
    
    try:
        # Parse input (one text per line)
        texts = [line.strip() for line in texts_input.split('\n') if line.strip()]
        
        if not texts:
            return "❌ No valid texts found in input."
        
        progress(0.1, desc=f"Processing {len(texts)} texts...")
        
        # Process in batches
        batch_size = global_state.config.performance.batch_size if global_state.config else 8
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            progress(0.3 + (i / len(texts)) * 0.5, desc=f"Processing batch {i//batch_size + 1}...")
            
            batch_results = await global_state.engine.analyze_texts_batch(batch)
            results.extend(batch_results)
        
        progress(0.9, desc="Generating summary...")
        
        # Generate summary
        successful_results = [r for r in results if 'error' not in r]
        failed_results = [r for r in results if 'error' in r]
        
        summary = {
            'total_texts': len(texts),
            'successful_analyses': len(successful_results),
            'failed_analyses': len(failed_results),
            'average_seo_score': np.mean([r.get('seo_score', 0) for r in successful_results]) if successful_results else 0,
            'average_processing_time': np.mean([r.get('processing_time', 0) for r in successful_results]) if successful_results else 0,
            'results': results
        }
        
        progress(1.0, desc="Batch analysis complete!")
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        return f"❌ Batch analysis failed: {str(e)}"

async def get_system_metrics() -> str:
    """Get current system metrics."""
    if not global_state.engine:
        return "❌ Engine not initialized."
    
    try:
        metrics = await global_state.engine.get_metrics()
        return format_metrics(metrics)
    except Exception as e:
        return f"❌ Failed to get metrics: {str(e)}"

async def get_performance_chart() -> go.Figure:
    """Get performance chart."""
    return create_performance_chart(global_state.metrics_history)

async def get_seo_score_distribution() -> go.Figure:
    """Get SEO score distribution chart."""
    return create_seo_score_distribution(global_state.metrics_history)

async def get_keyword_analysis() -> go.Figure:
    """Get keyword analysis chart."""
    return create_keyword_analysis_chart()

async def initialize_engine(
    model_name: str,
    batch_size: int,
    cache_strategy: str,
    cache_size: int,
    enable_caching: bool,
    enable_async: bool,
    log_level: str
) -> str:
    """Initialize the SEO engine with custom configuration."""
    try:
        # Create configuration
        config = RefactoredSEOConfig(
            model_name=model_name,
            performance=global_state.config.performance if global_state.config else None,
            cache=global_state.config.cache if global_state.config else None,
            monitoring=global_state.config.monitoring if global_state.config else None,
            enable_caching=enable_caching,
            enable_async=enable_async
        )
        
        # Update specific settings
        if config.performance:
            config.performance.batch_size = batch_size
        
        if config.cache:
            config.cache.strategy = CacheStrategy(cache_strategy.lower())
            config.cache.max_size = cache_size
        
        if config.monitoring:
            config.monitoring.log_level = log_level.upper()
        
        # Initialize engine
        await global_state.initialize_engine(config)
        
        return f"✅ Engine initialized successfully!\n\nConfiguration:\n{json.dumps(config.__dict__, indent=2, default=str)}"
        
    except Exception as e:
        return f"❌ Engine initialization failed: {str(e)}"

async def cleanup_resources() -> str:
    """Cleanup system resources."""
    try:
        if global_state.engine:
            await global_state.engine.cleanup()
            global_state.engine = None
            global_state.config = None
        
        # Clear metrics history
        global_state.metrics_history.clear()
        global_state.processing_queue.clear()
        
        return "✅ Resources cleaned up successfully!"
        
    except Exception as e:
        return f"❌ Cleanup failed: {str(e)}"

def get_queue_status(queue_id: str) -> str:
    """Get status of queued processing item."""
    if not queue_id.strip():
        return "❌ Please provide a queue ID."
    
    status = global_state.get_queue_status(queue_id)
    if not status:
        return f"❌ Queue item '{queue_id}' not found."
    
    if status['status'] == 'completed':
        result = status.get('result', {})
        return f"✅ Completed\n\nSEO Score: {result.get('seo_score', 'N/A')}\nProcessing Time: {result.get('processing_time', 'N/A'):.3f}s"
    elif status['status'] == 'failed':
        return f"❌ Failed\n\nError: {status.get('error', 'Unknown error')}"
    else:
        return f"⏳ {status['status'].title()}\n\nQueued at: {datetime.fromtimestamp(status['timestamp']).strftime('%H:%M:%S')}"

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_interface() -> gr.Blocks:
    """Create the Gradio interface."""
    
    with gr.Blocks(
        title="🚀 Refactored Enhanced SEO Engine",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        """
    ) as interface:
        
        gr.Markdown("# 🚀 Refactored Enhanced SEO Engine")
        gr.Markdown("Advanced SEO analysis with improved architecture, real-time monitoring, and enterprise-grade features")
        
        with gr.Tabs():
            
            # ========================================================================
            # SEO ANALYSIS TAB
            # ========================================================================
            
            with gr.Tab("📊 SEO Analysis"):
                
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### Single Text Analysis")
                        
                        text_input = gr.Textbox(
                            label="Input Text",
                            placeholder="Enter text for SEO analysis...",
                            lines=8,
                            max_lines=20
                        )
                        
                        with gr.Row():
                            analyze_btn = gr.Button("🔍 Analyze Text", variant="primary")
                            analyze_async_btn = gr.Button("⚡ Async Analysis", variant="secondary")
                        
                        text_output = gr.JSON(label="Analysis Results")
                        
                        gr.Markdown("### Batch Analysis")
                        
                        batch_input = gr.Textbox(
                            label="Multiple Texts (one per line)",
                            placeholder="Enter multiple texts, one per line...",
                            lines=6
                        )
                        
                        batch_btn = gr.Button("📦 Analyze Batch", variant="primary")
                        batch_output = gr.JSON(label="Batch Results")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Quick Stats")
                        quick_stats = gr.Markdown("No data available")
                        
                        gr.Markdown("### Processing Queue")
                        queue_id_input = gr.Textbox(label="Queue ID", placeholder="Enter queue ID to check status")
                        check_queue_btn = gr.Button("🔍 Check Status")
                        queue_status = gr.Markdown("No queue ID provided")
                
                # Event handlers
                analyze_btn.click(
                    analyze_single_text,
                    inputs=[text_input],
                    outputs=[text_output],
                    show_progress=True
                )
                
                analyze_async_btn.click(
                    analyze_single_text,
                    inputs=[text_input],
                    outputs=[text_output],
                    show_progress=True
                )
                
                batch_btn.click(
                    analyze_multiple_texts,
                    inputs=[batch_input],
                    outputs=[batch_output],
                    show_progress=True
                )
                
                check_queue_btn.click(
                    get_queue_status,
                    inputs=[queue_id_input],
                    outputs=[queue_status]
                )
            
            # ========================================================================
            # MONITORING TAB
            # ========================================================================
            
            with gr.Tab("📈 Monitoring"):
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### System Metrics")
                        refresh_metrics_btn = gr.Button("🔄 Refresh Metrics")
                        metrics_display = gr.Markdown("Click refresh to load metrics")
                        
                        gr.Markdown("### Performance Chart")
                        update_chart_btn = gr.Button("📊 Update Chart")
                        performance_chart = gr.Plotly(label="Performance Metrics")
                    
                    with gr.Column():
                        gr.Markdown("### SEO Score Distribution")
                        seo_distribution_chart = gr.Plotly(label="SEO Score Distribution")
                        
                        gr.Markdown("### Keyword Analysis")
                        keyword_chart = gr.Plotly(label="Keyword Analysis")
                
                # Event handlers
                refresh_metrics_btn.click(
                    get_system_metrics,
                    outputs=[metrics_display]
                )
                
                update_chart_btn.click(
                    get_performance_chart,
                    outputs=[performance_chart]
                )
                
                # Auto-load charts
                interface.load(
                    get_performance_chart,
                    outputs=[performance_chart]
                )
                
                interface.load(
                    get_seo_score_distribution,
                    outputs=[seo_distribution_chart]
                )
                
                interface.load(
                    get_keyword_analysis,
                    outputs=[keyword_chart]
                )
            
            # ========================================================================
            # CONFIGURATION TAB
            # ========================================================================
            
            with gr.Tab("⚙️ Configuration"):
                
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### Engine Configuration")
                        
                        with gr.Row():
                            model_name = gr.Dropdown(
                                label="Model Name",
                                choices=[
                                    "microsoft/DialoGPT-medium",
                                    "microsoft/DialoGPT-large",
                                    "gpt2",
                                    "gpt2-medium"
                                ],
                                value="microsoft/DialoGPT-medium"
                            )
                            
                            batch_size = gr.Slider(
                                label="Batch Size",
                                minimum=1,
                                maximum=32,
                                value=8,
                                step=1
                            )
                        
                        with gr.Row():
                            cache_strategy = gr.Dropdown(
                                label="Cache Strategy",
                                choices=["LRU", "LFU", "TTL", "HYBRID"],
                                value="LRU"
                            )
                            
                            cache_size = gr.Slider(
                                label="Cache Size",
                                minimum=100,
                                maximum=10000,
                                value=1000,
                                step=100
                            )
                        
                        with gr.Row():
                            enable_caching = gr.Checkbox(label="Enable Caching", value=True)
                            enable_async = gr.Checkbox(label="Enable Async Processing", value=True)
                        
                        log_level = gr.Dropdown(
                            label="Log Level",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                            value="INFO"
                        )
                        
                        init_btn = gr.Button("🚀 Initialize Engine", variant="primary")
                        init_status = gr.Markdown("Engine not initialized")
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### System Information")
                        system_info = gr.Markdown("Click initialize to load system info")
                        
                        gr.Markdown("### Resource Management")
                        cleanup_btn = gr.Button("🧹 Cleanup Resources", variant="secondary")
                        cleanup_status = gr.Markdown("Ready")
                
                # Event handlers
                init_btn.click(
                    initialize_engine,
                    inputs=[
                        model_name, batch_size, cache_strategy, cache_size,
                        enable_caching, enable_async, log_level
                    ],
                    outputs=[init_status]
                )
                
                cleanup_btn.click(
                    cleanup_resources,
                    outputs=[cleanup_status]
                )
        
        # Auto-refresh metrics
        interface.load(
            get_system_metrics,
            outputs=[metrics_display]
        )
    
    return interface

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Launch the Gradio interface."""
    interface = create_interface()
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
