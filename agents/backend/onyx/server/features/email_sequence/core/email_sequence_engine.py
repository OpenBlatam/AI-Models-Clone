"""
Email Sequence Engine

This module contains the main engine for managing email sequences,
integrating LangChain for intelligent automation and personalization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from ..models.sequence import EmailSequence, SequenceStep, SequenceStatus, StepType
from ..models.template import EmailTemplate, TemplateStatus
from ..models.subscriber import Subscriber, SubscriberStatus
from ..models.campaign import EmailCampaign, CampaignMetrics
from ..services.langchain_service import LangChainEmailService
from ..services.delivery_service import EmailDeliveryService
from ..services.analytics_service import EmailAnalyticsService

logger = logging.getLogger(__name__)


class EmailSequenceEngine:
    """
    Main engine for managing email sequences with LangChain integration.
    """
    
    def __init__(
        self,
        langchain_service: LangChainEmailService,
        delivery_service: EmailDeliveryService,
        analytics_service: EmailAnalyticsService
    ):
        """
        Initialize the email sequence engine.
        
        Args:
            langchain_service: LangChain service for AI-powered features
            delivery_service: Email delivery service
            analytics_service: Analytics service for tracking
        """
        self.langchain_service = langchain_service
        self.delivery_service = delivery_service
        self.analytics_service = analytics_service
        
        # Active sequences and campaigns
        self.active_sequences: Dict[UUID, EmailSequence] = {}
        self.active_campaigns: Dict[UUID, EmailCampaign] = {}
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info("Email Sequence Engine initialized")
    
    async def start(self):
        """Start the email sequence engine"""
        try:
            # Start background tasks
            await self._start_background_tasks()
            logger.info("Email Sequence Engine started successfully")
        except Exception as e:
            logger.error(f"Error starting Email Sequence Engine: {e}")
            raise
    
    async def stop(self):
        """Stop the email sequence engine"""
        try:
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Close services
            await self.langchain_service.close()
            await self.delivery_service.close()
            await self.analytics_service.close()
            
            logger.info("Email Sequence Engine stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Email Sequence Engine: {e}")
            raise
    
    async def create_sequence(
        self,
        name: str,
        target_audience: str,
        goals: List[str],
        tone: str = "professional",
        length: int = 5,
        templates: List[EmailTemplate] = None
    ) -> EmailSequence:
        """
        Create a new email sequence using LangChain.
        
        Args:
            name: Sequence name
            target_audience: Target audience description
            goals: Sequence goals
            tone: Email tone
            length: Number of emails
            templates: Optional templates to use
            
        Returns:
            Created email sequence
        """
        try:
            # Generate sequence using LangChain
            sequence = await self.langchain_service.generate_email_sequence(
                sequence_name=name,
                target_audience=target_audience,
                goals=goals,
                tone=tone,
                length=length
            )
            
            # Apply templates if provided
            if templates:
                await self._apply_templates_to_sequence(sequence, templates)
            
            logger.info(f"Created email sequence: {sequence.name}")
            return sequence
            
        except Exception as e:
            logger.error(f"Error creating email sequence: {e}")
            raise
    
    async def activate_sequence(self, sequence_id: UUID) -> bool:
        """
        Activate an email sequence.
        
        Args:
            sequence_id: ID of the sequence to activate
            
        Returns:
            True if activated successfully
        """
        try:
            sequence = self.active_sequences.get(sequence_id)
            if not sequence:
                raise ValueError(f"Sequence {sequence_id} not found")
            
            if sequence.status != SequenceStatus.DRAFT:
                raise ValueError(f"Sequence {sequence_id} is not in draft status")
            
            # Activate sequence
            sequence.activate()
            self.active_sequences[sequence_id] = sequence
            
            # Start sequence processing
            await self._start_sequence_processing(sequence)
            
            logger.info(f"Activated email sequence: {sequence.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating sequence {sequence_id}: {e}")
            raise
    
    async def add_subscribers_to_sequence(
        self,
        sequence_id: UUID,
        subscribers: List[Subscriber]
    ) -> bool:
        """
        Add subscribers to an active sequence.
        
        Args:
            sequence_id: ID of the sequence
            subscribers: List of subscribers to add
            
        Returns:
            True if added successfully
        """
        try:
            sequence = self.active_sequences.get(sequence_id)
            if not sequence:
                raise ValueError(f"Sequence {sequence_id} not found")
            
            if sequence.status != SequenceStatus.ACTIVE:
                raise ValueError(f"Sequence {sequence_id} is not active")
            
            # Filter active subscribers
            active_subscribers = [
                sub for sub in subscribers 
                if sub.status == SubscriberStatus.ACTIVE
            ]
            
            # Add subscribers to sequence
            for subscriber in active_subscribers:
                await self._add_subscriber_to_sequence(sequence, subscriber)
            
            # Update sequence statistics
            sequence.total_subscribers += len(active_subscribers)
            sequence.active_subscribers += len(active_subscribers)
            
            logger.info(f"Added {len(active_subscribers)} subscribers to sequence {sequence.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding subscribers to sequence {sequence_id}: {e}")
            raise
    
    async def send_sequence_email(
        self,
        sequence_id: UUID,
        step_order: int,
        subscribers: List[Subscriber]
    ) -> Dict[str, Any]:
        """
        Send a specific email from a sequence.
        
        Args:
            sequence_id: ID of the sequence
            step_order: Order of the step to send
            subscribers: List of subscribers to send to
            
        Returns:
            Delivery results
        """
        try:
            sequence = self.active_sequences.get(sequence_id)
            if not sequence:
                raise ValueError(f"Sequence {sequence_id} not found")
            
            step = sequence.get_step_by_order(step_order)
            if not step:
                raise ValueError(f"Step {step_order} not found in sequence")
            
            if step.step_type != StepType.EMAIL:
                raise ValueError(f"Step {step_order} is not an email step")
            
            # Personalize and send emails
            results = []
            for subscriber in subscribers:
                try:
                    # Personalize content using LangChain
                    personalized_content = await self.langchain_service.personalize_email_content(
                        template=self._create_template_from_step(step),
                        subscriber=subscriber
                    )
                    
                    # Generate optimized subject line
                    subject_line = await self.langchain_service.generate_subject_line(
                        email_content=personalized_content['html_content'],
                        subscriber_data=subscriber.to_dict(),
                        tone=sequence.personalization_variables.get('tone', 'professional')
                    )
                    
                    # Send email
                    delivery_result = await self.delivery_service.send_email(
                        to_email=subscriber.email,
                        subject=subject_line,
                        html_content=personalized_content['html_content'],
                        text_content=personalized_content['text_content']
                    )
                    
                    # Record metrics
                    subscriber.record_email_sent()
                    await self.analytics_service.record_email_sent(
                        sequence_id=sequence_id,
                        step_order=step_order,
                        subscriber_id=subscriber.id,
                        delivery_result=delivery_result
                    )
                    
                    results.append({
                        'subscriber_id': subscriber.id,
                        'email': subscriber.email,
                        'status': 'sent',
                        'delivery_result': delivery_result
                    })
                    
                except Exception as e:
                    logger.error(f"Error sending email to {subscriber.email}: {e}")
                    results.append({
                        'subscriber_id': subscriber.id,
                        'email': subscriber.email,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            logger.info(f"Sent step {step_order} of sequence {sequence.name} to {len(subscribers)} subscribers")
            return {
                'sequence_id': sequence_id,
                'step_order': step_order,
                'total_subscribers': len(subscribers),
                'successful_sends': len([r for r in results if r['status'] == 'sent']),
                'failed_sends': len([r for r in results if r['status'] == 'failed']),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error sending sequence email: {e}")
            raise
    
    async def process_sequence_step(
        self,
        sequence_id: UUID,
        step_order: int
    ) -> Dict[str, Any]:
        """
        Process a specific step in a sequence.
        
        Args:
            sequence_id: ID of the sequence
            step_order: Order of the step to process
            
        Returns:
            Processing results
        """
        try:
            sequence = self.active_sequences.get(sequence_id)
            if not sequence:
                raise ValueError(f"Sequence {sequence_id} not found")
            
            step = sequence.get_step_by_order(step_order)
            if not step:
                raise ValueError(f"Step {step_order} not found in sequence")
            
            # Process based on step type
            if step.step_type == StepType.EMAIL:
                return await self._process_email_step(sequence, step)
            elif step.step_type == StepType.DELAY:
                return await self._process_delay_step(sequence, step)
            elif step.step_type == StepType.CONDITION:
                return await self._process_condition_step(sequence, step)
            elif step.step_type == StepType.ACTION:
                return await self._process_action_step(sequence, step)
            elif step.step_type == StepType.WEBHOOK:
                return await self._process_webhook_step(sequence, step)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
                
        except Exception as e:
            logger.error(f"Error processing sequence step: {e}")
            raise
    
    async def get_sequence_analytics(
        self,
        sequence_id: UUID
    ) -> Dict[str, Any]:
        """
        Get analytics for a sequence.
        
        Args:
            sequence_id: ID of the sequence
            
        Returns:
            Analytics data
        """
        try:
            sequence = self.active_sequences.get(sequence_id)
            if not sequence:
                raise ValueError(f"Sequence {sequence_id} not found")
            
            # Get analytics from analytics service
            analytics = await self.analytics_service.get_sequence_analytics(sequence_id)
            
            # Add sequence metadata
            analytics.update({
                'sequence_name': sequence.name,
                'sequence_status': sequence.status,
                'total_steps': len(sequence.steps),
                'total_subscribers': sequence.total_subscribers,
                'active_subscribers': sequence.active_subscribers,
                'completed_subscribers': sequence.completed_subscribers
            })
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting sequence analytics: {e}")
            raise
    
    async def _start_background_tasks(self):
        """Start background tasks for sequence processing"""
        # Task for processing scheduled sequences
        task1 = asyncio.create_task(self._process_scheduled_sequences())
        self.background_tasks.append(task1)
        
        # Task for processing delayed steps
        task2 = asyncio.create_task(self._process_delayed_steps())
        self.background_tasks.append(task2)
        
        # Task for analytics processing
        task3 = asyncio.create_task(self._process_analytics())
        self.background_tasks.append(task3)
    
    async def _start_sequence_processing(self, sequence: EmailSequence):
        """Start processing for a sequence"""
        # Add sequence to active sequences
        self.active_sequences[sequence.id] = sequence
        
        # Process first step if immediate trigger exists
        for trigger in sequence.triggers:
            if trigger.trigger_type == "immediate":
                await self.process_sequence_step(sequence.id, 1)
                break
    
    async def _add_subscriber_to_sequence(
        self,
        sequence: EmailSequence,
        subscriber: Subscriber
    ):
        """Add a subscriber to a sequence"""
        # This would typically involve database operations
        # For now, we'll just log the action
        logger.info(f"Added subscriber {subscriber.email} to sequence {sequence.name}")
    
    def _create_template_from_step(self, step: SequenceStep) -> EmailTemplate:
        """Create a template from a sequence step"""
        from ..models.template import EmailTemplate, TemplateType
        
        return EmailTemplate(
            name=f"Step {step.order}",
            template_type=TemplateType.CUSTOM,
            subject=step.subject or "Email from sequence",
            html_content=step.content or "<p>Email content</p>",
            status=TemplateStatus.ACTIVE
        )
    
    async def _process_email_step(
        self,
        sequence: EmailSequence,
        step: SequenceStep
    ) -> Dict[str, Any]:
        """Process an email step"""
        # This would get subscribers ready for this step
        # and trigger email sending
        return {
            'step_type': 'email',
            'step_order': step.order,
            'status': 'processed',
            'message': f'Email step {step.order} processed'
        }
    
    async def _process_delay_step(
        self,
        sequence: EmailSequence,
        step: SequenceStep
    ) -> Dict[str, Any]:
        """Process a delay step"""
        delay_hours = step.delay_hours or 0
        delay_days = step.delay_days or 0
        
        total_delay = timedelta(days=delay_days, hours=delay_hours)
        
        return {
            'step_type': 'delay',
            'step_order': step.order,
            'status': 'processed',
            'delay': total_delay,
            'message': f'Delay step {step.order} processed - waiting {total_delay}'
        }
    
    async def _process_condition_step(
        self,
        sequence: EmailSequence,
        step: SequenceStep
    ) -> Dict[str, Any]:
        """Process a condition step"""
        return {
            'step_type': 'condition',
            'step_order': step.order,
            'status': 'processed',
            'message': f'Condition step {step.order} processed'
        }
    
    async def _process_action_step(
        self,
        sequence: EmailSequence,
        step: SequenceStep
    ) -> Dict[str, Any]:
        """Process an action step"""
        return {
            'step_type': 'action',
            'step_order': step.order,
            'status': 'processed',
            'message': f'Action step {step.order} processed'
        }
    
    async def _process_webhook_step(
        self,
        sequence: EmailSequence,
        step: SequenceStep
    ) -> Dict[str, Any]:
        """Process a webhook step"""
        return {
            'step_type': 'webhook',
            'step_order': step.order,
            'status': 'processed',
            'message': f'Webhook step {step.order} processed'
        }
    
    async def _apply_templates_to_sequence(
        self,
        sequence: EmailSequence,
        templates: List[EmailTemplate]
    ):
        """Apply templates to sequence steps"""
        for i, template in enumerate(templates):
            if i < len(sequence.steps):
                step = sequence.steps[i]
                step.template_id = template.id
                step.subject = template.subject
                step.content = template.html_content
    
    async def _process_scheduled_sequences(self):
        """Background task for processing scheduled sequences"""
        while True:
            try:
                # Process scheduled sequences
                # This would check for sequences that need to be triggered
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduled sequences processing: {e}")
    
    async def _process_delayed_steps(self):
        """Background task for processing delayed steps"""
        while True:
            try:
                # Process delayed steps
                # This would check for steps that have completed their delay
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in delayed steps processing: {e}")
    
    async def _process_analytics(self):
        """Background task for processing analytics"""
        while True:
            try:
                # Process analytics data
                # This would aggregate and process analytics data
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in analytics processing: {e}") 