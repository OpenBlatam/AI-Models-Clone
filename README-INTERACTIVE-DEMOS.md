# 🎨 Interactive Gradio Demos for Model Inference & Visualization

## 📋 Overview

This repository contains comprehensive interactive demos built with Gradio that showcase AI model inference, data visualization, and performance monitoring capabilities. The demos provide an intuitive web interface for exploring different AI models and visualizing results in real-time.

## 🚀 Features

### 🤖 **Model Inference Demo**
- **Multiple Model Types**: Classification, regression, autoencoder, and GAN models
- **Dynamic Parameters**: Adjust input size, batch size, and noise levels in real-time
- **Real-time Results**: Instant inference results with confidence scores
- **Performance Tracking**: Monitor processing time and memory usage
- **Interactive Charts**: Visualize performance metrics over time

### 📊 **Data Visualization Demo**
- **Multiple Chart Types**: Scatter plots, line charts, histograms, heatmaps, 3D scatter plots
- **Dynamic Data Sources**: Switch between classification, regression, and time series data
- **Customizable Appearance**: Adjust color schemes, opacity, and themes
- **Real-time Updates**: Charts update automatically when parameters change
- **Data Statistics**: Comprehensive data analysis and summary statistics

### 📈 **Performance Monitoring Demo**
- **Real-time Metrics**: Monitor CPU, GPU, memory, and network usage
- **System Alerts**: Automatic detection of performance issues
- **Stress Testing**: Simulate high-load scenarios
- **Performance Charts**: Visual representation of system metrics
- **Configurable Monitoring**: Adjust update intervals and tracked metrics

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (optional, for GPU acceleration)

### Install Dependencies
```bash
# Install core requirements
pip install -r requirements-interactive-demos.txt

# Or install manually
pip install gradio>=4.0.0 torch>=2.0.0 numpy pandas matplotlib seaborn plotly
```

### Optional GPU Support
```bash
# For CUDA support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For GPU monitoring
pip install nvidia-ml-py3
```

## 🚀 Quick Start

### 1. Simple Demo (Recommended for Testing)
```bash
python simple_interactive_demo.py
```

### 2. Full Interactive Demos
```bash
python interactive_gradio_demos.py
```

### 3. Access the Interface
- Open your browser and navigate to: `http://localhost:7860`
- The interface will automatically open in your default browser
- For external access, use the provided share link

## 📱 Usage Guide

### 🤖 Model Inference Tab

1. **Select Model Type**
   - Choose from available models (classifier, regressor, autoencoder, GAN)
   - Each model has different capabilities and input requirements

2. **Adjust Parameters**
   - **Input Size**: Number of input features (1-100)
   - **Batch Size**: Number of samples to process (1-128)
   - **Noise Level**: Add noise to input data (0.0-1.0)

3. **Run Inference**
   - Click "🚀 Run Inference" to execute the model
   - View results in real-time
   - Monitor performance metrics

4. **Analyze Results**
   - Check confidence scores and predictions
   - Review processing time and memory usage
   - Explore performance trends over time

### 📊 Data Visualization Tab

1. **Choose Chart Type**
   - **Scatter**: 2D scatter plots with color coding
   - **Line**: Time series and sequential data
   - **Histogram**: Data distribution analysis
   - **Bar**: Categorical data representation
   - **Heatmap**: Correlation matrices
   - **3D Scatter**: Three-dimensional data visualization

2. **Select Data Source**
   - **Classification**: Multi-class labeled data
   - **Regression**: Continuous target variables
   - **Autoencoder**: Unsupervised learning data
   - **Time Series**: Sequential temporal data

3. **Customize Appearance**
   - **Color Schemes**: Viridis, plasma, inferno, magma, cividis
   - **Opacity**: Adjust transparency (0.1-1.0)
   - **Themes**: Plotly white, dark, and custom themes

4. **Interactive Features**
   - Hover over data points for details
   - Zoom and pan across charts
   - Export charts and data statistics

### 📈 Performance Monitoring Tab

1. **Enable Monitoring**
   - Toggle real-time performance tracking
   - Set update intervals (1-10 seconds)
   - Choose metrics to track

2. **Monitor System Resources**
   - **CPU Usage**: Real-time processor utilization
   - **Memory Usage**: RAM consumption tracking
   - **GPU Usage**: Graphics processor monitoring
   - **Network I/O**: Network activity monitoring

3. **Performance Analysis**
   - View performance trends over time
   - Identify bottlenecks and optimization opportunities
   - Set up alerts for critical thresholds

4. **Stress Testing**
   - Simulate high-load scenarios
   - Test system stability under pressure
   - Monitor performance degradation

## 🔧 Customization

### Adding New Models

```python
def _create_custom_model(self) -> nn.Module:
    """Create a custom model for demo."""
    model = nn.Sequential(
        nn.Linear(input_size, hidden_size),
        nn.ReLU(),
        nn.Linear(hidden_size, output_size),
        nn.Softmax(dim=1)
    )
    return model

# Add to models dictionary
self.models["custom_model"] = self._create_custom_model()
```

### Adding New Visualization Types

```python
def create_custom_chart(self, data, parameters):
    """Create custom visualization."""
    if chart_type == "custom":
        fig = px.custom_chart(
            data=data,
            **parameters
        )
    return fig
```

### Custom Performance Metrics

```python
def track_custom_metric(self, metric_name, value):
    """Track custom performance metric."""
    if metric_name not in self.performance_metrics:
        self.performance_metrics[metric_name] = []
    self.performance_metrics[metric_name].append(value)
```

## 🎯 Advanced Features

### Real-time Updates
- Automatic chart updates when parameters change
- Live performance monitoring with configurable intervals
- Dynamic model switching without page refresh

### Interactive Elements
- Hover tooltips with detailed information
- Zoom and pan capabilities in charts
- Responsive design for mobile and desktop

### Performance Optimization
- Efficient data handling with NumPy and PyTorch
- GPU acceleration when available
- Memory management and garbage collection

### Error Handling
- Comprehensive error catching and reporting
- Graceful degradation when models fail
- User-friendly error messages

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in the launch configuration
   interface.launch(server_port=7861)
   ```

2. **GPU Not Detected**
   ```bash
   # Check CUDA installation
   python -c "import torch; print(torch.cuda.is_available())"
   
   # Install CUDA version of PyTorch
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Memory Issues**
   - Reduce batch size in model inference
   - Close other applications using GPU memory
   - Use CPU-only mode if GPU memory is limited

4. **Slow Performance**
   - Enable GPU acceleration
   - Reduce monitoring update frequency
   - Optimize data processing pipelines

### Performance Tips

- Use GPU acceleration when available
- Optimize batch sizes for your hardware
- Monitor memory usage during inference
- Use efficient data structures (NumPy arrays)

## 🔮 Future Enhancements

### Planned Features
- **Model Training Interface**: Interactive model training with real-time progress
- **Advanced Analytics**: Statistical analysis and hypothesis testing
- **Export Capabilities**: Save models, charts, and results
- **Collaborative Features**: Share demos and results with team members
- **API Integration**: Connect to external AI services and models

### Customization Options
- **Theme Engine**: Custom color schemes and layouts
- **Plugin System**: Extensible demo functionality
- **Multi-language Support**: Internationalization for global users
- **Accessibility Features**: Screen reader support and keyboard navigation

## 📚 API Reference

### Core Classes

#### `InteractiveGradioDemos`
Main class for comprehensive interactive demos.

**Methods:**
- `create_model_inference_demo()`: Model inference interface
- `create_visualization_demo()`: Data visualization interface
- `create_performance_monitoring_demo()`: Performance monitoring interface

#### `SimpleInteractiveDemo`
Streamlined demo for quick testing and demonstration.

**Methods:**
- `run_model_inference()`: Execute model inference
- `create_visualization()`: Generate interactive charts
- `create_interface()`: Build Gradio interface

### Configuration

#### `DemoConfig`
Configuration class for demo settings.

**Attributes:**
- `model_type`: Type of model to use
- `batch_size`: Batch size for inference
- `max_length`: Maximum input length
- `theme`: Visualization theme
- `colors`: Color palette for charts

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd interactive-gradio-demos

# Install development dependencies
pip install -r requirements-interactive-demos.txt

# Run tests
python -m pytest tests/

# Format code
black .
flake8 .
```

### Adding New Demos
1. Create new demo class inheriting from base classes
2. Implement required methods and interfaces
3. Add comprehensive error handling
4. Include unit tests and documentation
5. Update main interface to include new demo

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Include docstrings for all methods
- Write comprehensive unit tests
- Use meaningful variable and function names

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Gradio Team**: For the excellent web interface framework
- **PyTorch Team**: For the powerful deep learning framework
- **Plotly Team**: For interactive visualization capabilities
- **Open Source Community**: For contributions and feedback

## 📞 Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions for help and ideas
- **Examples**: Review example implementations in the codebase

### Community
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community support and ideas
- **Contributions**: Pull requests and code improvements
- **Documentation**: Help improve documentation and examples

---

**Happy Demo-ing! 🎉**

For more information, visit the project repository or contact the development team.
