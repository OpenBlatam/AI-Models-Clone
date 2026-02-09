#!/usr/bin/env python3
"""
Deployment Approval Workflow
Manages approval workflows for deployments
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum


logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Deployment approval request"""
    request_id: str
    deployment_id: str
    requester: str
    approvers: List[str]
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    approvals: List[Dict[str, Any]] = None
    rejections: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.approvals is None:
            self.approvals = []
        if self.rejections is None:
            self.rejections = []
        if self.metadata is None:
            self.metadata = {}


class ApprovalWorkflow:
    """Manages deployment approval workflows"""
    
    def __init__(self, requests_file: str = '/var/lib/deployment-approvals/requests.json'):
        self.requests_file = Path(requests_file)
        self.requests_file.parent.mkdir(parents=True, exist_ok=True)
        self.requests: Dict[str, ApprovalRequest] = {}
        self._load_requests()
    
    def _load_requests(self):
        """Load approval requests"""
        if self.requests_file.exists():
            try:
                with open(self.requests_file, 'r') as f:
                    data = json.load(f)
                    for req_data in data.get('requests', []):
                        # Convert datetime strings back to datetime
                        if 'created_at' in req_data:
                            req_data['created_at'] = datetime.fromisoformat(req_data['created_at'])
                        if 'expires_at' in req_data and req_data['expires_at']:
                            req_data['expires_at'] = datetime.fromisoformat(req_data['expires_at'])
                        req = ApprovalRequest(**req_data)
                        self.requests[req.request_id] = req
            except Exception as e:
                logger.error(f"Failed to load approval requests: {e}")
    
    def _save_requests(self):
        """Save approval requests"""
        try:
            data = {
                'requests': [asdict(req) for req in self.requests.values()],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.requests_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save approval requests: {e}")
    
    def create_request(
        self,
        deployment_id: str,
        requester: str,
        approvers: List[str],
        expires_in_hours: int = 24
    ) -> ApprovalRequest:
        """Create a new approval request"""
        import uuid
        request_id = str(uuid.uuid4())
        
        expires_at = datetime.now()
        from datetime import timedelta
        expires_at += timedelta(hours=expires_in_hours)
        
        request = ApprovalRequest(
            request_id=request_id,
            deployment_id=deployment_id,
            requester=requester,
            approvers=approvers,
            expires_at=expires_at
        )
        
        self.requests[request_id] = request
        self._save_requests()
        
        logger.info(f"Created approval request {request_id} for deployment {deployment_id}")
        return request
    
    def approve(self, request_id: str, approver: str, comment: Optional[str] = None) -> bool:
        """Approve a deployment request"""
        if request_id not in self.requests:
            logger.error(f"Approval request {request_id} not found")
            return False
        
        request = self.requests[request_id]
        
        # Check if expired
        if request.expires_at and datetime.now() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            self._save_requests()
            logger.warning(f"Approval request {request_id} has expired")
            return False
        
        # Check if already approved/rejected
        if request.status != ApprovalStatus.PENDING:
            logger.warning(f"Approval request {request_id} is not pending")
            return False
        
        # Check if approver is authorized
        if approver not in request.approvers:
            logger.warning(f"Approver {approver} is not authorized for request {request_id}")
            return False
        
        # Add approval
        request.approvals.append({
            'approver': approver,
            'comment': comment,
            'approved_at': datetime.now().isoformat()
        })
        
        # Check if all approvers have approved
        if len(request.approvals) >= len(request.approvers):
            request.status = ApprovalStatus.APPROVED
            logger.info(f"Approval request {request_id} fully approved")
        else:
            logger.info(f"Approval request {request_id} partially approved ({len(request.approvals)}/{len(request.approvers)})")
        
        self._save_requests()
        return True
    
    def reject(self, request_id: str, approver: str, reason: Optional[str] = None) -> bool:
        """Reject a deployment request"""
        if request_id not in self.requests:
            logger.error(f"Approval request {request_id} not found")
            return False
        
        request = self.requests[request_id]
        
        # Check if expired
        if request.expires_at and datetime.now() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            self._save_requests()
            return False
        
        # Check if already approved/rejected
        if request.status != ApprovalStatus.PENDING:
            return False
        
        # Add rejection
        request.rejections.append({
            'approver': approver,
            'reason': reason,
            'rejected_at': datetime.now().isoformat()
        })
        
        request.status = ApprovalStatus.REJECTED
        self._save_requests()
        
        logger.info(f"Approval request {request_id} rejected by {approver}")
        return True
    
    def is_approved(self, deployment_id: str) -> bool:
        """Check if a deployment is approved"""
        for request in self.requests.values():
            if request.deployment_id == deployment_id:
                return request.status == ApprovalStatus.APPROVED
        return False
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get an approval request"""
        return self.requests.get(request_id)
    
    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        return [req for req in self.requests.values() if req.status == ApprovalStatus.PENDING]
