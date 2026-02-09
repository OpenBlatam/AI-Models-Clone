#!/usr/bin/env python3
"""
Deployment Orchestrator
Refactored orchestration logic separated from initialization
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from deployment_exceptions import (
    DeploymentError,
    DeploymentValidationError,
    DeploymentSecurityError,
    DeploymentComplianceError,
    DeploymentApprovalError
)
from deployment_constants import DeploymentStatus


logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """Orchestrates the deployment process"""
    
    def __init__(self, components: Dict[str, Any], config: Any):
        self.components = components
        self.config = config
        self.start_time: Optional[float] = None
        self.commit_hash: Optional[str] = None
        self.trace_id: Optional[str] = None
    
    def _check_approval(self, deployment_id: str) -> bool:
        """Check if deployment is approved"""
        approval_workflow = self.components.get('approval_workflow')
        if not approval_workflow:
            return True  # No approval required
        
        if not approval_workflow.is_approved(deployment_id):
            pending = approval_workflow.get_pending_requests()
            if not pending or not any(req.deployment_id == deployment_id for req in pending):
                raise DeploymentApprovalError(f"Deployment {deployment_id} requires approval")
        return True
    
    def _check_compliance(self) -> bool:
        """Check compliance requirements"""
        compliance_checker = self.components.get('compliance_checker')
        if not compliance_checker:
            return True
        
        try:
            from deployment_compliance import ComplianceStandard
            standards = [ComplianceStandard.SOC2, ComplianceStandard.GDPR]
            compliance_results = compliance_checker.check_all_standards(standards)
            
            if not compliance_checker.is_compliant(standards, min_score=80.0):
                critical_issues = compliance_results.get('severity_counts', {}).get('critical', 0)
                if critical_issues > 0:
                    raise DeploymentComplianceError("Critical compliance issues found")
        except ImportError:
            pass
        
        return True
    
    def _check_security(self) -> bool:
        """Check security requirements"""
        security_scanner = self.components.get('security_scanner')
        if not security_scanner:
            return True
        
        security_results = security_scanner.scan_all()
        
        if security_results.get('total_issues', 0) > 0:
            logger.warning(f"Security scan found {security_results['total_issues']} issues")
            if security_scanner.should_block_deployment(max_critical=0, max_high=2):
                raise DeploymentSecurityError("Security scan found critical/high issues")
        
        return True
    
    def _run_pre_deployment_checks(self) -> bool:
        """Run all pre-deployment checks"""
        # Cost optimization analysis (non-blocking)
        cost_optimizer = self.components.get('cost_optimizer')
        if cost_optimizer:
            logger.info("Running cost optimization analysis...")
            cost_results = cost_optimizer.analyze_all()
            high_priority = cost_optimizer.get_high_priority_recommendations()
            if high_priority:
                logger.info(f"Cost optimization: {len(high_priority)} high priority recommendations")
        
        # Optimizations
        optimizer = self.components.get('optimizer')
        if optimizer:
            logger.info("Running deployment optimizations...")
            recommendations = optimizer.get_optimization_recommendations()
            if recommendations:
                for rec in recommendations:
                    logger.info(f"  - {rec}")
            
            disk_opts = optimizer.optimize_disk_usage()
            if disk_opts.get('cleanup_recommended'):
                logger.info("Performing disk cleanup...")
                optimizer.cleanup_resources()
        
        # Validation
        validator = self.components.get('validator')
        if validator:
            passed, results = validator.validate_all()
            if not passed:
                error_messages = []
                for result in results:
                    if result.severity == 'error':
                        error_messages.append(result.message)
                        logger.error(f"  ERROR: {result.message}")
                
                if error_messages:
                    raise DeploymentValidationError(f"Validation failed: {', '.join(error_messages)}")
        
        # Health checks
        health_checker = self.components.get('health_checker')
        if health_checker:
            logger.info("Running pre-deployment health checks...")
            results = health_checker.run_all_checks()
            
            critical_checks = ['docker', 'project_directory']
            for check_name in critical_checks:
                if check_name in results.get('checks', {}):
                    check_result = results['checks'][check_name]
                    if check_result.get('status') != 'pass':
                        raise DeploymentHealthCheckError(
                            f"Critical check failed: {check_name} - {check_result.get('message')}"
                        )
        
        return True
    
    def _create_backup(self) -> Optional[str]:
        """Create backup before deployment"""
        backup_manager = self.components.get('backup_manager')
        if not backup_manager:
            return None
        
        logger.info("Creating backup before deployment...")
        project_dir = getattr(self.config, 'project_dir', '/opt/blatam-academy')
        backup_path = backup_manager.create_backup(
            project_dir,
            backup_name=f"pre_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if backup_path:
            logger.info(f"Backup created: {backup_path}")
        else:
            logger.warning("Failed to create backup, continuing with deployment")
        
        return backup_path
    
    def _execute_deployment(self) -> Tuple[bool, str]:
        """Execute the actual deployment"""
        strategy = self.components.get('strategy')
        strategy_type = getattr(self.config, 'strategy_type', 'standard')
        
        logger.info(f"Starting deployment using strategy: {strategy_type}")
        
        def execute():
            """Execute deployment with retry logic"""
            if strategy:
                try:
                    return strategy.deploy()
                except Exception as e:
                    logger.error(f"Deployment strategy failed: {e}", exc_info=True)
                    return False, str(e)
            else:
                # Fallback to script-based deployment
                return self._execute_script_deployment()
        
        # Use circuit breaker if available
        circuit_breaker = self.components.get('circuit_breaker')
        if circuit_breaker:
            success, message = circuit_breaker.call(execute, "Deployment")
        else:
            # Use retry handler if available
            retry_handler = self.components.get('retry_handler')
            if retry_handler:
                success, result, attempts = retry_handler.retry(execute, "Deployment")
                if isinstance(result, tuple):
                    success, message = result
                else:
                    message = result if result else "Unknown error"
            else:
                success, message = execute()
        
        return success, message
    
    def _execute_script_deployment(self) -> Tuple[bool, str]:
        """Execute script-based deployment (fallback)"""
        from utils import run_command
        import subprocess
        import os
        
        logger.info("Using script-based deployment (strategy not available)")
        deploy_script = getattr(self.config, 'deploy_script', '/opt/blatam-academy/aws/scripts/auto_deploy.sh')
        project_dir = getattr(self.config, 'project_dir', '/opt/blatam-academy')
        branch = getattr(self.config, 'github_branch', 'main')
        
        env = dict(os.environ, **{
            'GITHUB_BRANCH': branch,
            'PROJECT_DIR': project_dir,
            'PROJECT_NAME': getattr(self.config, 'project_name', 'blatam-academy')
        })
        
        if run_command:
            success, stdout, stderr = run_command(
                ['bash', deploy_script, 'deploy'],
                cwd=project_dir,
                timeout=getattr(self.config, 'deployment_timeout', 1800),
                env=env
            )
            return success, stdout if success else stderr
        else:
            try:
                result = subprocess.run(
                    ['bash', deploy_script, 'deploy'],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=getattr(self.config, 'deployment_timeout', 1800),
                    env=env
                )
                success = result.returncode == 0
                return success, result.stdout if success else result.stderr
            except Exception as e:
                return False, str(e)
    
    def _record_deployment_result(
        self,
        success: bool,
        message: str,
        duration: float,
        branch: str
    ) -> None:
        """Record deployment result in all monitoring systems"""
        # Queue
        deployment_queue = self.components.get('deployment_queue')
        if deployment_queue and deployment_queue.processing:
            deployment_queue.complete(
                deployment_queue.processing.id,
                success,
                message[:200] if message else ''
            )
        
        # Monitor
        monitor = self.components.get('monitor')
        if monitor:
            monitor.record_deployment(success, message[:500], self.commit_hash or '')
        
        # Metrics
        metrics = self.components.get('metrics')
        if metrics and duration:
            strategy_type = getattr(self.config, 'strategy_type', 'standard')
            metrics.record_deployment(
                success,
                duration,
                strategy_type,
                self.commit_hash or '',
                branch
            )
        
        # Scheduler
        scheduler = self.components.get('scheduler')
        if scheduler and success:
            scheduler.record_deployment()
    
    def _handle_rollback(self, branch: str) -> Optional[Dict[str, Any]]:
        """Handle automatic rollback on failure"""
        rollback_manager = self.components.get('rollback_manager')
        if not rollback_manager:
            return None
        
        deployment_result = {
            'success': False,
            'commit_hash': self.commit_hash,
            'branch': branch,
            'message': 'Deployment failed'
        }
        
        if rollback_manager.should_rollback(deployment_result):
            logger.warning("Deployment failed - executing automatic rollback")
            backup_name = f"pre_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            rollback_result = rollback_manager.execute_rollback(
                self.commit_hash or 'unknown',
                backup_name
            )
            return rollback_result
        
        return None
    
    def deploy(self) -> Tuple[bool, str]:
        """Execute complete deployment process"""
        self.start_time = time.time()
        branch = getattr(self.config, 'github_branch', 'main')
        
        # Get commit hash
        try:
            from utils import get_git_commit_hash
            if get_git_commit_hash:
                self.commit_hash = get_git_commit_hash(self.config.project_dir)
        except ImportError:
            pass
        
        deployment_id = self.commit_hash or 'unknown'
        
        try:
            # Start tracing
            tracer = self.components.get('tracer')
            if tracer:
                self.trace_id = tracer.start_trace("deployment", trace_id=f"deploy_{int(self.start_time)}")
                logger.info(f"Started deployment trace: {self.trace_id}")
            
            # Check scheduler
            scheduler = self.components.get('scheduler')
            if scheduler:
                allowed, reason = scheduler.can_deploy_now()
                if not allowed:
                    raise DeploymentError(f"Scheduling restriction: {reason}")
            
            # Check queue
            deployment_queue = self.components.get('deployment_queue')
            if deployment_queue:
                if deployment_queue.processing:
                    request_id = deployment_queue.enqueue(
                        self.commit_hash or '',
                        branch,
                        strategy=getattr(self.config, 'strategy_type', 'standard')
                    )
                    raise DeploymentError(f"Deployment queued with ID: {request_id}")
                
                request = deployment_queue.dequeue()
                if request:
                    self.commit_hash = request.commit_hash
                    branch = request.branch
            
            # Check approval
            self._check_approval(deployment_id)
            
            # Notify deployment started
            notifier = self.components.get('notifier')
            if notifier:
                notifier.notify_deployment_started(self.commit_hash or '', branch)
            
            # Create backup
            backup_path = self._create_backup()
            
            # Publish backup created event
            if backup_path and event_stream:
                from deployment_events import EventType, DeploymentEvent
                event = DeploymentEvent(
                    event_type=EventType.BACKUP_CREATED,
                    deployment_id=deployment_id,
                    data={'backup_path': backup_path}
                )
                event_stream.publish(event)
            
            # Run pre-deployment checks
            self._run_pre_deployment_checks()
            
            # Publish validation event
            if event_stream:
                from deployment_events import EventType, DeploymentEvent
                event = DeploymentEvent(
                    event_type=EventType.VALIDATION_PASSED,
                    deployment_id=deployment_id
                )
                event_stream.publish(event)
            
            # Check compliance
            self._check_compliance()
            
            # Check security
            self._check_security()
            
            # Execute deployment
            success, message = self._execute_deployment()
            
            # Monitor performance
            performance_monitor = self.components.get('performance_monitor')
            if performance_monitor and self.start_time:
                duration = time.time() - self.start_time
                performance_monitor.monitor_deployment(deployment_id, duration)
            
            # Finish tracing
            if tracer and self.trace_id:
                trace_summary = tracer.finish_trace(self.trace_id)
                logger.info(f"Deployment trace completed: {trace_summary.get('duration', 0):.2f}s")
            
            # Record result
            duration = time.time() - self.start_time if self.start_time else None
            self._record_deployment_result(success, message, duration or 0, branch)
            
            # Handle rollback on failure
            if not success:
                rollback_result = self._handle_rollback(branch)
                if rollback_result and rollback_result.get('success'):
                    message = f"Deployment failed, but rollback successful: {message}"
                elif rollback_result:
                    message = f"Deployment failed and rollback failed: {message}"
            
            # Notify result
            if notifier:
                if success:
                    notifier.notify_deployment_success(
                        self.commit_hash or '',
                        branch,
                        duration
                    )
                else:
                    notifier.notify_deployment_failed(
                        message[:200] if message else 'Unknown error',
                        self.commit_hash or '',
                        branch
                    )
            
            return success, message
            
        except (DeploymentApprovalError, DeploymentComplianceError, 
                DeploymentSecurityError, DeploymentValidationError,
                DeploymentHealthCheckError) as e:
            logger.error(f"Deployment blocked: {e}")
            if notifier:
                notifier.notify_deployment_failed(str(e), self.commit_hash or '', branch)
            return False, str(e)
        except Exception as e:
            logger.error(f"Deployment error: {e}", exc_info=True)
            if notifier:
                notifier.notify_deployment_failed(str(e), self.commit_hash or '', branch)
            return False, str(e)
