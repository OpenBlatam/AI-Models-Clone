#!/usr/bin/env python3
"""
Deployment Metrics Collector
Collects and analyzes deployment metrics
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


logger = logging.getLogger(__name__)


class DeploymentMetrics:
    """Collects and analyzes deployment metrics"""
    
    def __init__(self, metrics_file: str = '/var/lib/deployment-metrics/metrics.json'):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'deployments': [],
            'performance': {
                'avg_deployment_time': 0,
                'min_deployment_time': 0,
                'max_deployment_time': 0,
                'total_deployments': 0
            },
            'reliability': {
                'success_rate': 0,
                'failure_rate': 0,
                'rollback_rate': 0
            },
            'trends': {
                'deployments_per_day': {},
                'success_rate_by_day': {}
            }
        }
    
    def _save_metrics(self) -> None:
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def record_deployment(
        self,
        success: bool,
        duration: float,
        strategy: str = 'standard',
        commit_hash: str = '',
        branch: str = 'main'
    ) -> None:
        """Record a deployment metric"""
        deployment = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'duration': duration,
            'strategy': strategy,
            'commit_hash': commit_hash[:7] if commit_hash else '',
            'branch': branch
        }
        
        self.metrics['deployments'].append(deployment)
        
        # Keep only last 1000 deployments
        if len(self.metrics['deployments']) > 1000:
            self.metrics['deployments'] = self.metrics['deployments'][-1000:]
        
        # Update performance metrics
        self._update_performance_metrics()
        
        # Update reliability metrics
        self._update_reliability_metrics()
        
        # Update trends
        self._update_trends()
        
        self._save_metrics()
    
    def _update_performance_metrics(self) -> None:
        """Update performance metrics"""
        deployments = self.metrics['deployments']
        if not deployments:
            return
        
        durations = [d['duration'] for d in deployments if 'duration' in d and d['duration']]
        
        if durations:
            perf = self.metrics['performance']
            perf['total_deployments'] = len(deployments)
            perf['avg_deployment_time'] = sum(durations) / len(durations)
            perf['min_deployment_time'] = min(durations)
            perf['max_deployment_time'] = max(durations)
    
    def _update_reliability_metrics(self) -> None:
        """Update reliability metrics"""
        deployments = self.metrics['deployments']
        if not deployments:
            return
        
        total = len(deployments)
        successful = sum(1 for d in deployments if d.get('success', False))
        failed = total - successful
        
        # Count rollbacks (deployments followed by another deployment quickly)
        rollbacks = 0
        for i in range(1, len(deployments)):
            prev = deployments[i-1]
            curr = deployments[i]
            if not prev.get('success', False) and curr.get('success', False):
                prev_time = datetime.fromisoformat(prev['timestamp'])
                curr_time = datetime.fromisoformat(curr['timestamp'])
                if (curr_time - prev_time).total_seconds() < 300:  # Within 5 minutes
                    rollbacks += 1
        
        rel = self.metrics['reliability']
        rel['success_rate'] = (successful / total * 100) if total > 0 else 0
        rel['failure_rate'] = (failed / total * 100) if total > 0 else 0
        rel['rollback_rate'] = (rollbacks / total * 100) if total > 0 else 0
    
    def _update_trends(self) -> None:
        """Update trend metrics"""
        deployments = self.metrics['deployments']
        if not deployments:
            return
        
        # Group by day
        deployments_by_day = defaultdict(list)
        for deployment in deployments[-30:]:  # Last 30 days
            timestamp = datetime.fromisoformat(deployment['timestamp'])
            day_key = timestamp.strftime('%Y-%m-%d')
            deployments_by_day[day_key].append(deployment)
        
        # Calculate deployments per day
        trends = self.metrics['trends']
        trends['deployments_per_day'] = {
            day: len(deploys) for day, deploys in deployments_by_day.items()
        }
        
        # Calculate success rate by day
        trends['success_rate_by_day'] = {}
        for day, deploys in deployments_by_day.items():
            if deploys:
                successful = sum(1 for d in deploys if d.get('success', False))
                trends['success_rate_by_day'][day] = (successful / len(deploys) * 100)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        recent_deployments = self.metrics['deployments'][-10:]
        
        return {
            'performance': self.metrics['performance'],
            'reliability': self.metrics['reliability'],
            'recent_deployments': recent_deployments,
            'trends': self.metrics['trends'],
            'summary': {
                'total_deployments': len(self.metrics['deployments']),
                'last_7_days': self._get_deployments_in_period(7),
                'last_30_days': self._get_deployments_in_period(30),
                'avg_deployment_time_minutes': self.metrics['performance']['avg_deployment_time'] / 60
            }
        }
    
    def _get_deployments_in_period(self, days: int) -> Dict[str, Any]:
        """Get deployment stats for a period"""
        cutoff = datetime.now() - timedelta(days=days)
        period_deployments = [
            d for d in self.metrics['deployments']
            if datetime.fromisoformat(d['timestamp']) >= cutoff
        ]
        
        if not period_deployments:
            return {'count': 0, 'successful': 0, 'failed': 0}
        
        successful = sum(1 for d in period_deployments if d.get('success', False))
        
        return {
            'count': len(period_deployments),
            'successful': successful,
            'failed': len(period_deployments) - successful,
            'success_rate': (successful / len(period_deployments) * 100) if period_deployments else 0
        }
    
    def get_strategy_comparison(self) -> Dict[str, Any]:
        """Compare performance of different deployment strategies"""
        deployments = self.metrics['deployments']
        strategies = defaultdict(lambda: {'count': 0, 'successful': 0, 'durations': []})
        
        for deployment in deployments:
            strategy = deployment.get('strategy', 'standard')
            strategies[strategy]['count'] += 1
            if deployment.get('success', False):
                strategies[strategy]['successful'] += 1
            if 'duration' in deployment and deployment['duration']:
                strategies[strategy]['durations'].append(deployment['duration'])
        
        comparison = {}
        for strategy, stats in strategies.items():
            comparison[strategy] = {
                'count': stats['count'],
                'success_rate': (stats['successful'] / stats['count'] * 100) if stats['count'] > 0 else 0,
                'avg_duration': (sum(stats['durations']) / len(stats['durations'])) if stats['durations'] else 0
            }
        
        return comparison
