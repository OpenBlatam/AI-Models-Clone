#!/usr/bin/env python3
"""
Resource Tagger
Manages resource tagging for cost allocation and organization
"""

import logging
import boto3
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class ResourceTag:
    """Resource tag definition"""
    key: str
    value: str
    propagate_at_launch: bool = True


class ResourceTagger:
    """Manages resource tagging"""
    
    def __init__(self, default_tags: Optional[Dict[str, str]] = None):
        self.default_tags = default_tags or {}
        self.ec2_client = None
        
        try:
            self.ec2_client = boto3.client('ec2')
        except Exception as e:
            logger.warning(f"Failed to initialize EC2 client: {e}")
    
    def get_default_tags(self, deployment_id: str, environment: str = 'production') -> Dict[str, str]:
        """Get default tags for resources"""
        tags = {
            'Project': 'blatam-academy',
            'Environment': environment,
            'DeploymentID': deployment_id,
            'ManagedBy': 'deployment-system',
            'CreatedAt': datetime.now().isoformat()
        }
        
        # Merge with custom default tags
        tags.update(self.default_tags)
        
        return tags
    
    def tag_resources(
        self,
        resource_ids: List[str],
        resource_type: str,
        tags: Dict[str, str]
    ) -> bool:
        """Tag AWS resources"""
        if not self.ec2_client:
            logger.warning("EC2 client not available, skipping tagging")
            return False
        
        try:
            # Convert tags to AWS format
            aws_tags = [{'Key': k, 'Value': v} for k, v in tags.items()]
            
            if resource_type == 'instance':
                self.ec2_client.create_tags(
                    Resources=resource_ids,
                    Tags=aws_tags
                )
            elif resource_type == 'volume':
                self.ec2_client.create_tags(
                    Resources=resource_ids,
                    Tags=aws_tags
                )
            
            logger.info(f"Tagged {len(resource_ids)} {resource_type}(s) with {len(tags)} tags")
            return True
            
        except Exception as e:
            logger.error(f"Failed to tag resources: {e}")
            return False
    
    def get_resource_tags(self, resource_id: str) -> Dict[str, str]:
        """Get tags for a resource"""
        if not self.ec2_client:
            return {}
        
        try:
            response = self.ec2_client.describe_tags(
                Filters=[
                    {'Name': 'resource-id', 'Values': [resource_id]}
                ]
            )
            
            tags = {}
            for tag in response.get('Tags', []):
                tags[tag['Key']] = tag['Value']
            
            return tags
        except Exception as e:
            logger.error(f"Failed to get resource tags: {e}")
            return {}
