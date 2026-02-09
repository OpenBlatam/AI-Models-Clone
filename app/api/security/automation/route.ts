/**
 * Security Automation API Routes
 * Manage security automation rules and executions
 */

import { NextRequest, NextResponse } from 'next/server';
import { securityAutomationManager } from '@/lib/security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type');
    const ruleId = searchParams.get('ruleId');

    if (ruleId) {
      const rule = securityAutomationManager.getRule(ruleId);
      if (!rule) {
        return NextResponse.json(
          { error: 'Rule not found' },
          { status: 404 }
        );
      }
      return NextResponse.json({ rule });
    }

    let rules = securityAutomationManager.getAllRules();
    let executions = securityAutomationManager.getAllExecutions();

    if (type === 'enabled') {
      rules = securityAutomationManager.getEnabledRules();
    }

    if (type === 'templates') {
      const templates = securityAutomationManager.getAllTemplates();
      return NextResponse.json({ templates });
    }

    if (type === 'executions') {
      const limit = parseInt(searchParams.get('limit') || '50');
      executions = executions.slice(0, limit);
      return NextResponse.json({ executions });
    }

    if (type === 'stats') {
      const stats = securityAutomationManager.getAutomationStats();
      return NextResponse.json({ stats });
    }

    return NextResponse.json({
      rules,
      executions: executions.slice(0, 20), // Return recent executions
      stats: securityAutomationManager.getAutomationStats(),
    });
  } catch (error) {
    console.error('Failed to get automation data:', error);
    return NextResponse.json(
      { error: 'Failed to get automation data' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, rule, templateId, overrides, context } = body;

    switch (action) {
      case 'add-rule':
        securityAutomationManager.addRule(rule);
        return NextResponse.json({ message: 'Rule added successfully' });

      case 'update-rule':
        const updated = securityAutomationManager.updateRule(rule.id, rule);
        if (!updated) {
          return NextResponse.json(
            { error: 'Rule not found' },
            { status: 404 }
          );
        }
        return NextResponse.json({ message: 'Rule updated successfully' });

      case 'remove-rule':
        const removed = securityAutomationManager.removeRule(rule.id);
        if (!removed) {
          return NextResponse.json(
            { error: 'Rule not found' },
            { status: 404 }
          );
        }
        return NextResponse.json({ message: 'Rule removed successfully' });

      case 'create-from-template':
        if (!templateId) {
          return NextResponse.json(
            { error: 'Template ID is required' },
            { status: 400 }
          );
        }

        const newRule = securityAutomationManager.createRuleFromTemplate(
          templateId,
          overrides || {}
        );

        if (!newRule) {
          return NextResponse.json(
            { error: 'Template not found' },
            { status: 404 }
          );
        }

        return NextResponse.json({ rule: newRule });

      case 'trigger-rule':
        if (!rule.id) {
          return NextResponse.json(
            { error: 'Rule ID is required' },
            { status: 400 }
          );
        }

        const execution = await securityAutomationManager.triggerRule(
          rule.id,
          context || {}
        );

        if (!execution) {
          return NextResponse.json(
            { error: 'Rule not found or disabled' },
            { status: 404 }
          );
        }

        return NextResponse.json({ execution });

      case 'get-execution':
        if (!rule.id) {
          return NextResponse.json(
            { error: 'Execution ID is required' },
            { status: 400 }
          );
        }

        const executionResult = securityAutomationManager.getExecution(rule.id);
        if (!executionResult) {
          return NextResponse.json(
            { error: 'Execution not found' },
            { status: 404 }
          );
        }

        return NextResponse.json({ execution: executionResult });

      case 'get-executions-by-rule':
        if (!rule.id) {
          return NextResponse.json(
            { error: 'Rule ID is required' },
            { status: 400 }
          );
        }

        const ruleExecutions = securityAutomationManager.getExecutionsByRule(rule.id);
        return NextResponse.json({ executions: ruleExecutions });

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Failed to process automation request:', error);
    return NextResponse.json(
      { error: 'Failed to process automation request' },
      { status: 500 }
    );
  }
}
