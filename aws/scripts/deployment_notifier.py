#!/usr/bin/env python3
"""
Deployment Notifier
Sends notifications about deployment status via various channels
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class DeploymentNotifier:
    """Sends deployment notifications"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.webhook_urls = config.get('webhook_urls', {})
        self.email_config = config.get('email', {})
        self.slack_webhook = config.get('slack_webhook')
        self.discord_webhook = config.get('discord_webhook')
    
    def notify_slack(self, message: str, success: bool = True) -> bool:
        """Send notification to Slack"""
        if not self.slack_webhook:
            return False
        
        try:
            color = "good" if success else "danger"
            payload = {
                "attachments": [{
                    "color": color,
                    "title": "Deployment Notification",
                    "text": message,
                    "footer": "Blatam Academy Auto-Deploy",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    def notify_discord(self, message: str, success: bool = True) -> bool:
        """Send notification to Discord"""
        if not self.discord_webhook:
            return False
        
        try:
            color = 0x00ff00 if success else 0xff0000
            payload = {
                "embeds": [{
                    "title": "Deployment Notification",
                    "description": message,
                    "color": color,
                    "timestamp": datetime.now().isoformat(),
                    "footer": {
                        "text": "Blatam Academy Auto-Deploy"
                    }
                }]
            }
            
            response = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False
    
    def notify_webhook(self, webhook_name: str, data: Dict[str, Any]) -> bool:
        """Send notification to custom webhook"""
        webhook_url = self.webhook_urls.get(webhook_name)
        if not webhook_url:
            return False
        
        try:
            response = requests.post(
                webhook_url,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook notification to {webhook_name}: {e}")
            return False
    
    def notify_deployment_started(self, commit_hash: str = '', branch: str = 'main') -> None:
        """Notify that deployment has started"""
        message = f"🚀 Deployment started\nBranch: {branch}\nCommit: {commit_hash[:7] if commit_hash else 'N/A'}"
        
        self.notify_slack(message, success=True)
        self.notify_discord(message, success=True)
    
    def notify_deployment_success(self, commit_hash: str = '', branch: str = 'main', duration: Optional[float] = None) -> None:
        """Notify that deployment succeeded"""
        duration_str = f" in {duration:.1f}s" if duration else ""
        message = f"✅ Deployment successful{duration_str}\nBranch: {branch}\nCommit: {commit_hash[:7] if commit_hash else 'N/A'}"
        
        self.notify_slack(message, success=True)
        self.notify_discord(message, success=True)
    
    def notify_deployment_failed(self, error: str = '', commit_hash: str = '', branch: str = 'main') -> None:
        """Notify that deployment failed"""
        error_msg = error[:200] if error else "Unknown error"
        message = f"❌ Deployment failed\nBranch: {branch}\nCommit: {commit_hash[:7] if commit_hash else 'N/A'}\nError: {error_msg}"
        
        self.notify_slack(message, success=False)
        self.notify_discord(message, success=False)


def main():
    """Test function"""
    config = {
        'slack_webhook': os.environ.get('SLACK_WEBHOOK_URL'),
        'discord_webhook': os.environ.get('DISCORD_WEBHOOK_URL'),
        'webhook_urls': {}
    }
    
    notifier = DeploymentNotifier(config)
    
    # Test notifications
    notifier.notify_deployment_started('abc123', 'main')
    time.sleep(1)
    notifier.notify_deployment_success('abc123', 'main', 45.2)
    time.sleep(1)
    notifier.notify_deployment_failed('Build failed', 'abc123', 'main')


if __name__ == '__main__':
    import time
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    main()
