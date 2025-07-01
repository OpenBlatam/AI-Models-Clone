"""
Instagram Captions API v8.0 - Simple Gradio Demo

Interactive demo for the CPU-optimized AI caption generator.
Real transformers running efficiently on any hardware.
"""

import gradio as gr
import requests
import json
import time
from typing import Tuple, Dict, Any


class SimpleAIDemo:
    """Simple demo interface for AI caption generation."""
    
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
        self.session_stats = {
            "total_requests": 0,
            "avg_quality": 0,
            "avg_time": 0,
            "style_counts": {}
        }
    
    def generate_caption(self, content: str, style: str, hashtag_count: int) -> Tuple[str, str, str, str]:
        """
        Generate caption using the AI API.
        
        Returns:
            Tuple of (caption, hashtags, analysis, status)
        """
        if not content.strip():
            return "❌ Please provide a content description", "", "", "No input provided"
        
        # Prepare request
        payload = {
            "content_description": content,
            "style": style.lower(),
            "hashtag_count": hashtag_count,
            "client_id": "gradio-demo"
        }
        
        start_time = time.time()
        
        try:
            # Make API request
            response = requests.post(
                f"{self.api_url}/api/v8/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Update session stats
                self._update_stats(result, time.time() - start_time, style)
                
                # Format response
                caption = result["caption"]
                hashtags = " ".join(result["hashtags"])
                
                # Create analysis
                analysis = self._format_analysis(result)
                
                # Status info
                status = self._format_status(result, time.time() - start_time)
                
                return caption, hashtags, analysis, status
            
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    error_msg += f" - {error_detail}"
                except:
                    pass
                
                return f"❌ {error_msg}", "", "", f"Request failed: {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "❌ Request timeout (30s)", "", "", "API took too long to respond"
        
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to API", "", "", "Make sure API is running on localhost:8080"
        
        except Exception as e:
            return f"❌ Error: {str(e)}", "", "", f"Exception: {type(e).__name__}"
    
    def _update_stats(self, result: Dict, processing_time: float, style: str):
        """Update session statistics."""
        self.session_stats["total_requests"] += 1
        total = self.session_stats["total_requests"]
        
        # Update averages
        self.session_stats["avg_quality"] = (
            (self.session_stats["avg_quality"] * (total - 1) + result["quality_score"]) / total
        )
        self.session_stats["avg_time"] = (
            (self.session_stats["avg_time"] * (total - 1) + processing_time) / total
        )
        
        # Track style usage
        if style not in self.session_stats["style_counts"]:
            self.session_stats["style_counts"][style] = 0
        self.session_stats["style_counts"][style] += 1
    
    def _format_analysis(self, result: Dict) -> str:
        """Format analysis results."""
        analysis_lines = [
            f"📊 AI Analysis Results:",
            f"├── Quality Score: {result['quality_score']:.1f}/100",
            f"├── Style: {result['style'].title()}",
            f"├── Processing Time: {result['processing_time_seconds']:.3f}s",
            f"└── Model: {result['model_info'].get('model_used', 'Unknown')}"
        ]
        
        if "tokens_generated" in result["model_info"]:
            analysis_lines.append(f"    ├── Tokens Generated: {result['model_info']['tokens_generated']}")
        
        analysis_lines.append(f"    └── AI Version: {result['model_info'].get('ai_version', 'v8.0')}")
        
        return "\n".join(analysis_lines)
    
    def _format_status(self, result: Dict, total_time: float) -> str:
        """Format status information."""
        status_lines = [
            f"🔍 Request Status:",
            f"├── Request ID: {result['request_id']}",
            f"├── Timestamp: {result['timestamp']}",
            f"├── API Version: {result['api_version']}",
            f"├── Total Time: {total_time:.3f}s",
            f"└── API Processing: {result['processing_time_seconds']:.3f}s"
        ]
        
        return "\n".join(status_lines)
    
    def check_api_health(self) -> str:
        """Check API health status."""
        try:
            response = requests.get(f"{self.api_url}/ai/health", timeout=10)
            
            if response.status_code == 200:
                health = response.json()
                
                status_emoji = "🟢" if health["status"] == "healthy" else "🟡"
                models_count = len(health["ai_status"]["available_models"])
                total_gens = health["ai_status"]["performance_stats"]["total_generations"]
                
                health_lines = [
                    f"{status_emoji} API Status: {health['status'].title()}",
                    f"├── Models Loaded: {models_count}",
                    f"├── Total Generations: {total_gens}",
                    f"├── Test Generation: {'✅' if health['test_generation'] else '❌'}",
                    f"└── Capabilities: Real Transformers ✅, CPU Optimized ✅"
                ]
                
                return "\n".join(health_lines)
            
            else:
                return f"🔴 API Health Check Failed: {response.status_code}"
        
        except Exception as e:
            return f"🔴 Cannot reach API: {str(e)}"
    
    def get_session_stats(self) -> str:
        """Get current session statistics."""
        if self.session_stats["total_requests"] == 0:
            return "📊 No requests made in this session yet"
        
        stats_lines = [
            f"📊 Session Statistics:",
            f"├── Total Requests: {self.session_stats['total_requests']}",
            f"├── Average Quality: {self.session_stats['avg_quality']:.1f}/100",
            f"├── Average Time: {self.session_stats['avg_time']:.3f}s",
            f"└── Style Usage:"
        ]
        
        for style, count in self.session_stats["style_counts"].items():
            percentage = (count / self.session_stats["total_requests"]) * 100
            stats_lines.append(f"    ├── {style.title()}: {count} ({percentage:.1f}%)")
        
        return "\n".join(stats_lines)
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        
        # Custom CSS
        custom_css = """
        .gradio-container {
            max-width: 1100px !important;
        }
        .output-text {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .metric-display {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        """
        
        with gr.Blocks(
            title="Instagram AI Captions v8.0",
            theme=gr.themes.Soft(primary_hue="blue"),
            css=custom_css
        ) as demo:
            
            # Header
            gr.Markdown("""
            # 🧠 Instagram Captions AI v8.0 - Real Transformers Demo
            
            Experience **real AI-powered caption generation** using **actual transformer models**:
            - 🤖 **DistilGPT-2 & GPT-2**: Real neural language models
            - 🎯 **6 Smart Styles**: Casual, Professional, Playful, Inspirational, Educational, Promotional
            - ⚡ **CPU Optimized**: Works perfectly on any computer
            - 📊 **Quality Prediction**: AI-powered quality scoring
            - 🏷️ **Smart Hashtags**: Intelligently generated hashtags
            
            ---
            """)
            
            with gr.Row():
                # Input Column
                with gr.Column(scale=2):
                    gr.Markdown("## 📝 Content Input")
                    
                    content_input = gr.Textbox(
                        label="📷 Content Description",
                        placeholder="Describe your content in detail (e.g., 'Beautiful sunset at the beach with golden reflections on the water')",
                        lines=4,
                        max_lines=6
                    )
                    
                    with gr.Row():
                        style_input = gr.Dropdown(
                            choices=["Casual", "Professional", "Playful", "Inspirational", "Educational", "Promotional"],
                            value="Casual",
                            label="🎨 Caption Style",
                            info="Choose the tone and style for your caption"
                        )
                        
                        hashtag_input = gr.Slider(
                            minimum=5,
                            maximum=30,
                            value=15,
                            step=1,
                            label="🏷️ Hashtag Count",
                            info="Number of hashtags to generate"
                        )
                    
                    generate_btn = gr.Button(
                        "🚀 Generate AI Caption",
                        variant="primary",
                        size="lg"
                    )
                
                # Output Column
                with gr.Column(scale=3):
                    gr.Markdown("## 🎯 AI Generation Results")
                    
                    caption_output = gr.Textbox(
                        label="✨ Generated Caption",
                        lines=5,
                        max_lines=8,
                        info="AI-generated caption using real transformers"
                    )
                    
                    hashtags_output = gr.Textbox(
                        label="🏷️ Smart Hashtags",
                        lines=3,
                        info="AI-selected hashtags for maximum engagement"
                    )
            
            # Analysis Row
            with gr.Row():
                with gr.Column():
                    analysis_output = gr.Code(
                        label="📊 AI Analysis",
                        language="yaml",
                        info="Detailed AI performance metrics"
                    )
                
                with gr.Column():
                    status_output = gr.Code(
                        label="🔍 Request Status",
                        language="yaml",
                        info="Technical details and timing"
                    )
            
            # Tools Row
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 🏥 API Health")
                    health_btn = gr.Button("Check API Status", variant="secondary")
                    health_output = gr.Code(label="Health Status", language="yaml")
                
                with gr.Column():
                    gr.Markdown("### 📊 Session Stats")
                    stats_btn = gr.Button("View Statistics", variant="secondary")
                    stats_output = gr.Code(label="Session Statistics", language="yaml")
            
            # Examples
            gr.Markdown("## 💡 Try These Examples:")
            gr.Examples(
                examples=[
                    ["Beautiful sunset at the beach with golden reflections on the water", "Inspirational", 15],
                    ["Professional headshot for LinkedIn profile", "Professional", 12],
                    ["Delicious homemade pasta with fresh herbs and parmesan", "Casual", 18],
                    ["Team building workshop at the office", "Professional", 10],
                    ["Cute golden retriever puppy playing in the park", "Playful", 20],
                    ["Morning workout routine at the gym", "Inspirational", 16],
                    ["New product launch announcement", "Promotional", 14]
                ],
                inputs=[content_input, style_input, hashtag_input],
                label="Click any example to try it!"
            )
            
            # Event handlers
            generate_btn.click(
                fn=self.generate_caption,
                inputs=[content_input, style_input, hashtag_input],
                outputs=[caption_output, hashtags_output, analysis_output, status_output]
            )
            
            health_btn.click(
                fn=self.check_api_health,
                outputs=health_output
            )
            
            stats_btn.click(
                fn=self.get_session_stats,
                outputs=stats_output
            )
            
            # Footer
            gr.Markdown("""
            ---
            ### 🔬 Technical Notes:
            - **Real AI Models**: Using actual DistilGPT-2 and GPT-2 transformer models
            - **CPU Optimized**: Efficient performance on any hardware
            - **Quality Scoring**: Advanced algorithms predict caption effectiveness  
            - **Smart Hashtags**: AI-powered hashtag selection based on content and style
            - **Processing Time**: Includes model inference and analysis (typically 1-3 seconds)
            
            🚀 **API Server**: Make sure the API is running on `localhost:8080`
            """)
        
        return demo


def main():
    """Launch the simple AI demo."""
    print("🚀 Starting Instagram Captions AI v8.0 - Simple Demo")
    print("="*60)
    
    # Check if API is reachable
    demo_app = SimpleAIDemo()
    print("🔍 Checking API connection...")
    health_status = demo_app.check_api_health()
    print(f"📡 API Status: {health_status.split('API Status: ')[1].split('├')[0] if 'API Status:' in health_status else 'Unknown'}")
    
    print("="*60)
    print("🌐 Demo Features:")
    print("   • Real transformer models (DistilGPT-2, GPT-2)")
    print("   • 6 intelligent caption styles") 
    print("   • AI-powered hashtag generation")
    print("   • Quality prediction and analysis")
    print("   • Session statistics tracking")
    print("="*60)
    
    # Create and launch interface
    interface = demo_app.create_interface()
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public access
        inbrowser=True,
        show_error=True,
        favicon_path=None
    )


if __name__ == "__main__":
    main() 