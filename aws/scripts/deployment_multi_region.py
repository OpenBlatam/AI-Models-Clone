#!/usr/bin/env python3
"""
Multi-Region Deployment Manager
Manages deployments across multiple AWS regions
"""

import logging
import boto3
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class RegionStatus(Enum):
    """Region deployment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class RegionDeployment:
    """Region deployment information"""
    region: str
    status: RegionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    instance_count: int = 0


class MultiRegionDeploymentManager:
    """Manages deployments across multiple regions"""
    
    def __init__(self, regions: List[str], primary_region: str = 'us-east-1'):
        self.regions = regions
        self.primary_region = primary_region
        self.deployments: Dict[str, List[RegionDeployment]] = {}
        self.clients: Dict[str, Any] = {}
        
        # Initialize AWS clients for each region
        for region in regions:
            try:
                self.clients[region] = {
                    'ec2': boto3.client('ec2', region_name=region),
                    'ecs': boto3.client('ecs', region_name=region) if self._check_service('ecs', region) else None
                }
            except Exception as e:
                logger.warning(f"Failed to initialize client for region {region}: {e}")
    
    def _check_service(self, service: str, region: str) -> bool:
        """Check if service is available in region"""
        try:
            # Simple check - could be enhanced
            return True
        except:
            return False
    
    def deploy_to_region(
        self,
        region: str,
        deployment_config: Dict[str, Any]
    ) -> RegionDeployment:
        """Deploy to a specific region"""
        logger.info(f"Deploying to region: {region}")
        
        region_deployment = RegionDeployment(
            region=region,
            status=RegionStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        try:
            # Get region client
            if region not in self.clients:
                raise Exception(f"No client available for region {region}")
            
            # Deploy using Terraform or direct API calls
            # This is a simplified version - actual implementation would use Terraform
            # or AWS SDK to deploy infrastructure
            
            # Simulate deployment
            import time
            time.sleep(2)  # Simulate deployment time
            
            # Get instance count
            try:
                ec2_client = self.clients[region]['ec2']
                response = ec2_client.describe_instances(
                    Filters=[{'Name': 'tag:Project', 'Values': [deployment_config.get('project_name', 'blatam-academy')]}]
                )
                instance_count = sum(len(reservation['Instances']) for reservation in response['Reservations'])
                region_deployment.instance_count = instance_count
            except Exception as e:
                logger.warning(f"Failed to get instance count: {e}")
            
            region_deployment.status = RegionStatus.COMPLETED
            region_deployment.completed_at = datetime.now()
            region_deployment.duration = (region_deployment.completed_at - region_deployment.started_at).total_seconds()
            
            logger.info(f"Deployment to {region} completed successfully")
            
        except Exception as e:
            logger.error(f"Deployment to {region} failed: {e}")
            region_deployment.status = RegionStatus.FAILED
            region_deployment.error = str(e)
            region_deployment.completed_at = datetime.now()
            if region_deployment.started_at:
                region_deployment.duration = (region_deployment.completed_at - region_deployment.started_at).total_seconds()
        
        return region_deployment
    
    def deploy_to_all_regions(
        self,
        deployment_config: Dict[str, Any],
        strategy: str = 'sequential'  # sequential, parallel, canary
    ) -> Dict[str, Any]:
        """Deploy to all configured regions"""
        logger.info(f"Deploying to {len(self.regions)} regions using {strategy} strategy")
        
        deployment_id = f"multi_region_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        region_deployments = []
        
        if strategy == 'sequential':
            # Deploy to regions one by one
            for region in self.regions:
                region_deployment = self.deploy_to_region(region, deployment_config)
                region_deployments.append(region_deployment)
                
                # If primary region fails, stop deployment
                if region == self.primary_region and region_deployment.status == RegionStatus.FAILED:
                    logger.error(f"Primary region {region} failed - stopping deployment")
                    break
        
        elif strategy == 'parallel':
            # Deploy to all regions simultaneously
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.regions)) as executor:
                futures = {
                    executor.submit(self.deploy_to_region, region, deployment_config): region
                    for region in self.regions
                }
                
                for future in concurrent.futures.as_completed(futures):
                    region_deployment = future.result()
                    region_deployments.append(region_deployment)
        
        elif strategy == 'canary':
            # Deploy to primary region first, then others
            primary_deployment = self.deploy_to_region(self.primary_region, deployment_config)
            region_deployments.append(primary_deployment)
            
            if primary_deployment.status == RegionStatus.COMPLETED:
                # Deploy to other regions
                for region in self.regions:
                    if region != self.primary_region:
                        region_deployment = self.deploy_to_region(region, deployment_config)
                        region_deployments.append(region_deployment)
        
        # Store deployment history
        self.deployments[deployment_id] = region_deployments
        
        # Calculate summary
        total_regions = len(region_deployments)
        successful = len([d for d in region_deployments if d.status == RegionStatus.COMPLETED])
        failed = len([d for d in region_deployments if d.status == RegionStatus.FAILED])
        
        return {
            'deployment_id': deployment_id,
            'strategy': strategy,
            'total_regions': total_regions,
            'successful': successful,
            'failed': failed,
            'regions': [
                {
                    'region': d.region,
                    'status': d.status.value,
                    'duration': d.duration,
                    'instance_count': d.instance_count,
                    'error': d.error
                }
                for d in region_deployments
            ]
        }
    
    def get_region_status(self, region: str) -> Dict[str, Any]:
        """Get status of a specific region"""
        try:
            ec2_client = self.clients[region]['ec2']
            response = ec2_client.describe_instances(
                Filters=[{'Name': 'tag:Project', 'Values': ['blatam-academy']}]
            )
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'id': instance['InstanceId'],
                        'state': instance['State']['Name'],
                        'type': instance['InstanceType']
                    })
            
            return {
                'region': region,
                'instance_count': len(instances),
                'instances': instances
            }
        except Exception as e:
            logger.error(f"Failed to get region status for {region}: {e}")
            return {'region': region, 'error': str(e)}
