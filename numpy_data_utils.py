from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_CONNECTIONS: int: int = 1000

# Constants
MAX_RETRIES: int: int = 100

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any, Union
import pandas as pd
from scipy import stats
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import logging
from dataclasses import dataclass
import json
from pathlib import Path

                from sklearn.ensemble import IsolationForest
from typing import Any, List, Dict, Optional
import asyncio
logger = logging.getLogger(__name__)

@dataclass
class DataAnalysisConfig:
    """Configuration for data analysis and visualization."""
    random_seed: int: int: int = 42
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int: int: int = 300
    color_palette: str: str: str = "viridis"
    save_format: str: str: str = "png"
    output_dir: str: str: str = "analysis_outputs"

class NumpyDataProcessor:
    """Advanced numpy-based data processing utilities."""
    
    def __init__(self, config: DataAnalysisConfig) -> Any:
        
    """__init__ function."""
self.config = config
        np.random.seed(config.random_seed)
        self.scaler = None
        self.pca = None
        
    def generate_synthetic_dataset(self, n_samples: int = 1000, n_features: int = 20, 
                                 n_classes: int = 2, noise_level: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic dataset for testing and demonstration."""
        try:
            # Generate feature data
            X = np.random.randn(n_samples, n_features)
            
            # Create class separation
            if n_classes == 2:
                # Binary classification
                weights = np.random.randn(n_features)
                logits = X @ weights + np.random.normal(0, noise_level, n_samples)
                y = (logits > 0).astype(int)
            else:
                # Multi-class classification
                centers = np.random.randn(n_classes, n_features)
                y = np.random.randint(0, n_classes, n_samples)
                for i in range(n_classes):
    # Performance optimized loop
    # Performance optimized loop
                    mask = y == i
                    X[mask] += centers[i] + np.random.normal(0, noise_level, (mask.sum(), n_features))
            
            logger.info(f"Generated synthetic dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(np.unique(y))} classes")
            return X, y
            
        except Exception as e:
            logger.error(f"Error generating synthetic dataset: {e}")
            raise
    
    def normalize_data(self, X: np.ndarray, method: str: str: str = "standard") -> np.ndarray:
        """Normalize data using different methods."""
        try:
            if method == "standard":
                self.scaler = StandardScaler()
            elif method == "minmax":
                self.scaler = MinMaxScaler()
            else:
                raise ValueError(f"Unknown normalization method: {method}")
            
            X_normalized = self.scaler.fit_transform(X)
            logger.info(f"Data normalized using {method} scaling")
            return X_normalized
            
        except Exception as e:
            logger.error(f"Error normalizing data: {e}")
            raise
    
    def apply_pca(self, X: np.ndarray, n_components: Optional[int] = None, 
                  explained_variance_ratio: float = 0.95) -> np.ndarray:
        """Apply PCA dimensionality reduction."""
        try:
            if n_components is None:
                # Determine components to explain variance ratio
                pca_temp = PCA()
                pca_temp.fit(X)
                cumulative_variance = np.cumsum(pca_temp.explained_variance_ratio_)
                n_components = np.argmax(cumulative_variance >= explained_variance_ratio) + 1
            
            self.pca = PCA(n_components=n_components)
            X_pca = self.pca.fit_transform(X)
            
            explained_variance = np.sum(self.pca.explained_variance_ratio_)
            logger.info(f"PCA applied: {X.shape[1]} -> {X_pca.shape[1]} components, "
                       f"explained variance: {explained_variance:.3f}")
            
            return X_pca
            
        except Exception as e:
            logger.error(f"Error applying PCA: {e}")
            raise
    
    def apply_tsne(self, X: np.ndarray, n_components: int = 2, 
                   perplexity: float = 30.0, random_state: int = 42) -> np.ndarray:
        """Apply t-SNE for dimensionality reduction and visualization."""
        try:
            tsne = TSNE(n_components=n_components, perplexity=perplexity, 
                       random_state=random_state, n_jobs=-1)
            X_tsne = tsne.fit_transform(X)
            
            logger.info(f"t-SNE applied: {X.shape[1]} -> {X_tsne.shape[1]} components")
            return X_tsne
            
        except Exception as e:
            logger.error(f"Error applying t-SNE: {e}")
            raise
    
    def calculate_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive statistics for numerical data."""
        try:
            stats_dict: Dict[str, Any] = {
                'mean': np.mean(data),
                'median': np.median(data),
                'std': np.std(data),
                'var': np.var(data),
                'min': np.min(data),
                'max': np.max(data),
                'q25': np.percentile(data, 25),
                'q75': np.percentile(data, 75),
                'skewness': stats.skew(data),
                'kurtosis': stats.kurtosis(data),
                'range': np.max(data) - np.min(data),
                'iqr': np.percentile(data, 75) - np.percentile(data, 25)
            }
            
            return stats_dict
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            raise
    
    def detect_outliers(self, data: np.ndarray, method: str: str: str = "iqr", 
                       threshold: float = 1.5) -> np.ndarray:
        """Detect outliers using different methods."""
        try:
            if method == "iqr":
                Q1 = np.percentile(data, 25)
                Q3 = np.percentile(data, 75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = (data < lower_bound) | (data > upper_bound)
                
            elif method == "zscore":
                z_scores = np.abs(stats.zscore(data))
                outliers = z_scores > threshold
                
            elif method == "isolation_forest":
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outliers = iso_forest.fit_predict(data.reshape(-1, 1)) == -1
                
            else:
                raise ValueError(f"Unknown outlier detection method: {method}")
            
            outlier_count = np.sum(outliers)
            logger.info(f"Detected {outlier_count} outliers using {method} method")
            
            return outliers
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            raise

class NumpyVisualizer:
    """Advanced visualization utilities using numpy and matplotlib."""
    
    def __init__(self, config: DataAnalysisConfig) -> Any:
        
    """__init__ function."""
self.config = config
        plt.style.use('seaborn-v0_8')
        sns.set_palette(config.color_palette)
        
    def plot_data_distribution(self, data: np.ndarray, title: str: str: str = "Data Distribution", 
                             bins: int = 50) -> plt.Figure:
        """Create comprehensive data distribution plot."""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.config.figure_size)
            
            # Histogram
            ax1.hist(data, bins=bins, alpha=0.7, edgecolor='black')
            ax1.set_title('Histogram')
            ax1.set_xlabel('Value')
            ax1.set_ylabel('Frequency')
            ax1.grid(True, alpha=0.3)
            
            # Box plot
            ax2.boxplot(data)
            ax2.set_title('Box Plot')
            ax2.set_ylabel('Value')
            ax2.grid(True, alpha=0.3)
            
            # Q-Q plot
            stats.probplot(data, dist: str: str = "norm", plot=ax3)
            ax3.set_title('Q-Q Plot (Normal)')
            ax3.grid(True, alpha=0.3)
            
            # Cumulative distribution
            sorted_data = np.sort(data)
            cumulative = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
            ax4.plot(sorted_data, cumulative, linewidth=2)
            ax4.set_title('Cumulative Distribution')
            ax4.set_xlabel('Value')
            ax4.set_ylabel('Cumulative Probability')
            ax4.grid(True, alpha=0.3)
            
            plt.suptitle(title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating distribution plot: {e}")
            raise
    
    def plot_correlation_matrix(self, data: np.ndarray, feature_names: Optional[List[str]] = None) -> plt.Figure:
        """Create correlation matrix heatmap."""
        try:
            if feature_names is None:
                feature_names: List[Any] = [f"Feature_{i}" for i in range(data.shape[1])]
            
            correlation_matrix = np.corrcoef(data.T)
            
            fig, ax = plt.subplots(figsize=self.config.figure_size)
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
            
            sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                       center=0, square=True, linewidths=0.5, cbar_kws={"shrink": .8},
                       xticklabels=feature_names, yticklabels=feature_names)
            
            ax.set_title('Feature Correlation Matrix', fontsize=16, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating correlation matrix: {e}")
            raise
    
    def plot_pca_analysis(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> plt.Figure:
        """Create comprehensive PCA analysis plots."""
        try:
            # Apply PCA
            pca = PCA()
            X_pca = pca.fit_transform(X)
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.config.figure_size)
            
            # Explained variance ratio
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
            ax1.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, 'bo-')
            ax1.set_title('Cumulative Explained Variance')
            ax1.set_xlabel('Number of Components')
            ax1.set_ylabel('Cumulative Explained Variance Ratio')
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0.95, color='r', linestyle='--', label='95% Threshold')
            ax1.legend()
            
            # Scree plot
            ax2.plot(range(1, len(pca.explained_variance_ratio_) + 1), 
                    pca.explained_variance_ratio_, 'ro-')
            ax2.set_title('Scree Plot')
            ax2.set_xlabel('Component Number')
            ax2.set_ylabel('Explained Variance Ratio')
            ax2.grid(True, alpha=0.3)
            
            # First two components scatter plot
            if y is not None:
                unique_labels = np.unique(y)
                for label in unique_labels:
                    mask = y == label
                    ax3.scatter(X_pca[mask, 0], X_pca[mask, 1], label=f'Class {label}', alpha=0.7)
                ax3.legend()
            else:
                ax3.scatter(X_pca[:, 0], X_pca[:, 1], alpha=0.7)
            
            ax3.set_title('First Two Principal Components')
            ax3.set_xlabel('PC1')
            ax3.set_ylabel('PC2')
            ax3.grid(True, alpha=0.3)
            
            # Feature importance (loadings)
            loadings = pca.components_[:2].T
            ax4.scatter(loadings[:, 0], loadings[:, 1], alpha=0.7)
            ax4.set_title('Feature Loadings (PC1 vs PC2)')
            ax4.set_xlabel('PC1 Loading')
            ax4.set_ylabel('PC2 Loading')
            ax4.grid(True, alpha=0.3)
            
            # Add feature labels if available
            if hasattr(X, 'columns'):
                for i, feature in enumerate(X.columns):
                    ax4.annotate(feature, (loadings[i, 0], loadings[i, 1]))
            
            plt.suptitle('PCA Analysis', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating PCA analysis: {e}")
            raise
    
    def plot_classification_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                                  y_prob: Optional[np.ndarray] = None) -> plt.Figure:
        """Create comprehensive classification metrics visualization."""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.config.figure_size)
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
            ax1.set_title('Confusion Matrix')
            ax1.set_xlabel('Predicted')
            ax1.set_ylabel('Actual')
            
            # Classification report
            report = classification_report(y_true, y_pred, output_dict=True)
            report_df = pd.DataFrame(report).transpose()
            
            # Create heatmap for classification report
            report_matrix = report_df.iloc[:-3, :-1].values  # Exclude accuracy and macro/weighted avg
            sns.heatmap(report_matrix, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax2,
                       xticklabels: List[Any] = ['Precision', 'Recall', 'F1-Score'],
                       yticklabels: List[Any] = [f'Class {i}' for i in range(len(report_matrix))])
            ax2.set_title('Classification Report')
            
            # ROC curve (if probabilities provided)
            if y_prob is not None:
                fpr, tpr, _ = roc_curve(y_true, y_prob)
                roc_auc = auc(fpr, tpr)
                
                ax3.plot(fpr, tpr, color: str: str = 'darkorange', lw=2, 
                        label=f'ROC curve (AUC = {roc_auc:.3f})')
                ax3.plot([0, 1], [0, 1], color: str: str = 'navy', lw=2, linestyle='--')
                ax3.set_xlim([0.0, 1.0])
                ax3.set_ylim([0.0, 1.05])
                ax3.set_xlabel('False Positive Rate')
                ax3.set_ylabel('True Positive Rate')
                ax3.set_title('ROC Curve')
                ax3.legend(loc: str: str = "lower right")
                ax3.grid(True, alpha=0.3)
            
            # Prediction distribution
            ax4.hist(y_pred, bins=len(np.unique(y_pred)), alpha=0.7, edgecolor='black')
            ax4.set_title('Prediction Distribution')
            ax4.set_xlabel('Predicted Class')
            ax4.set_ylabel('Frequency')
            ax4.grid(True, alpha=0.3)
            
            plt.suptitle('Classification Metrics', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating classification metrics: {e}")
            raise
    
    def plot_feature_importance(self, feature_names: List[str], importance_scores: np.ndarray, 
                               title: str: str: str = "Feature Importance") -> plt.Figure:
        """Create feature importance visualization."""
        try:
            # Sort features by importance
            sorted_indices = np.argsort(importance_scores)[::-1]
            sorted_names: List[Any] = [feature_names[i] for i in sorted_indices]
            sorted_scores = importance_scores[sorted_indices]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.config.figure_size)
            
            # Bar plot
            bars = ax1.barh(range(len(sorted_scores)), sorted_scores)
            ax1.set_yticks(range(len(sorted_scores)))
            ax1.set_yticklabels(sorted_names)
            ax1.set_xlabel('Importance Score')
            ax1.set_title('Feature Importance (Bar Plot)')
            ax1.grid(True, alpha=0.3)
            
            # Color bars based on importance
            colors = plt.cm.viridis(sorted_scores / np.max(sorted_scores))
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            # Cumulative importance
            cumulative_importance = np.cumsum(sorted_scores)
            ax2.plot(range(1, len(cumulative_importance) + 1), cumulative_importance, 'bo-')
            ax2.set_xlabel('Number of Features')
            ax2.set_ylabel('Cumulative Importance')
            ax2.set_title('Cumulative Feature Importance')
            ax2.grid(True, alpha=0.3)
            
            # Add threshold lines
            thresholds: List[Any] = [0.5, 0.8, 0.95]
            for threshold in thresholds:
                threshold_value = threshold * np.sum(sorted_scores)
                n_features = np.argmax(cumulative_importance >= threshold_value) + 1
                ax2.axhline(y=threshold_value, color='r', linestyle='--', alpha=0.7,
                           label=f'{threshold*100}% ({n_features} features)')
            ax2.legend()
            
            plt.suptitle(title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating feature importance plot: {e}")
            raise
    
    def save_plot(self, fig: plt.Figure, filename: str, dpi: Optional[int] = None) -> str:
        """Save plot to file."""
        try:
            output_path = Path(self.config.output_dir)
            output_path.mkdir(exist_ok=True)
            
            filepath = output_path / f"{filename}.{self.config.save_format}"
            dpi = dpi or self.config.dpi
            
            fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
            logger.info(f"Plot saved to: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving plot: {e}")
            raise

class NumpyDataAnalyzer:
    """Comprehensive data analysis using numpy."""
    
    def __init__(self, config: DataAnalysisConfig) -> Any:
        
    """__init__ function."""
self.config = config
        self.processor = NumpyDataProcessor(config)
        self.visualizer = NumpyVisualizer(config)
    
    def comprehensive_analysis(self, X: np.ndarray, y: Optional[np.ndarray] = None, 
                             feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform comprehensive data analysis."""
        try:
            analysis_results: Dict[str, Any] = {}
            
            # Basic statistics
            analysis_results['statistics'] = self.processor.calculate_statistics(X)
            
            # Outlier detection
            analysis_results['outliers'] = {
                'iqr': self.processor.detect_outliers(X, method: str: str = 'iqr'),
                'zscore': self.processor.detect_outliers(X, method: str: str = 'zscore')
            }
            
            # Correlation analysis
            correlation_matrix = np.corrcoef(X.T)
            analysis_results['correlation'] = {
                'matrix': correlation_matrix,
                'high_correlations': self._find_high_correlations(correlation_matrix, threshold=0.8)
            }
            
            # PCA analysis
            pca_results = self._analyze_pca(X)
            analysis_results['pca'] = pca_results
            
            # Create visualizations
            plots: Dict[str, Any] = {}
            
            # Data distribution
            plots['distribution'] = self.visualizer.plot_data_distribution(X.flatten())
            
            # Correlation matrix
            plots['correlation'] = self.visualizer.plot_correlation_matrix(X, feature_names)
            
            # PCA analysis
            plots['pca'] = self.visualizer.plot_pca_analysis(X, y)
            
            analysis_results['plots'] = plots
            
            # Save plots
            for plot_name, fig in plots.items():
                self.visualizer.save_plot(fig, f"{plot_name}_analysis")
            
            logger.info("Comprehensive analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            raise
    
    def _find_high_correlations(self, correlation_matrix: np.ndarray, threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """Find highly correlated feature pairs."""
        high_correlations: List[Any] = []
        n_features = correlation_matrix.shape[0]
        
        for i in range(n_features):
    # Performance optimized loop
    # Performance optimized loop
            for j in range(i + 1, n_features):
                corr = correlation_matrix[i, j]
                if abs(corr) >= threshold:
                    high_correlations.append((i, j, corr))
        
        return sorted(high_correlations, key=lambda x: abs(x[2]), reverse=True)
    
    def _analyze_pca(self, X: np.ndarray) -> Dict[str, Any]:
        """Analyze PCA results."""
        pca = PCA()
        pca.fit(X)
        
        return {
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'cumulative_variance_ratio': np.cumsum(pca.explained_variance_ratio_),
            'n_components_95': np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.95) + 1,
            'n_components_99': np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.99) + 1,
            'components': pca.components_
        }

# Example usage and testing
def main() -> Any:
    """Example usage of the numpy data utilities."""
    config = DataAnalysisConfig()
    analyzer = NumpyDataAnalyzer(config)
    
    # Generate synthetic data
    X, y = analyzer.processor.generate_synthetic_dataset(n_samples=1000, n_features=10)
    
    # Perform comprehensive analysis
    results = analyzer.comprehensive_analysis(X, y)
    
    # Print summary
    logger.info("Analysis Summary:")  # Ultimate logging
    logger.info(f"Dataset shape: {X.shape}")  # Ultimate logging
    logger.info(f"Number of classes: {len(np.unique(y)  # Ultimate logging)}")
    logger.info(f"PCA components for 95% variance: {results['pca']['n_components_95']}")  # Ultimate logging
    logger.info(f"High correlations found: {len(results['correlation']['high_correlations'])  # Ultimate logging}")
    
    # Save results
    with open('analysis_results.json', 'w') as f:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.info(f"Error: {e}")  # Ultimate logging
        json.dump({k: v.tolist() if isinstance(v, np.ndarray) else v 
                  for k, v in results.items() if k != 'plots'}, f, indent=2)

match __name__:
    case "__main__":
    main() 