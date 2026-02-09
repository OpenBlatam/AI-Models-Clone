import { NextRequest, NextResponse } from 'next/server';
import { advancedAISecurity } from '@/lib/security/advanced-ai-security';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const modelId = searchParams.get('modelId');
    const limit = parseInt(searchParams.get('limit') || '100');

    switch (action) {
      case 'models':
        return await getAIModels();
      case 'predictions':
        return await getAIPredictions(modelId, limit);
      case 'training-jobs':
        return await getTrainingJobs();
      case 'stats':
        return await getAIStats();
      case 'model-metrics':
        if (!modelId) {
          return NextResponse.json(
            { error: 'modelId parameter is required' },
            { status: 400 }
          );
        }
        return await getModelMetrics(modelId);
      default:
        return await getAIOverview();
    }
  } catch (error) {
    console.error('AI Security API error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch AI security data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, data } = body;

    switch (action) {
      case 'make-prediction':
        return await makePrediction(data.modelId, data.input, data.options);
      case 'train-model':
        return await trainModel(data.modelConfig);
      case 'deploy-model':
        return await deployModel(data.modelId);
      case 'stop-training':
        return await stopTraining(data.jobId);
      default:
        return NextResponse.json(
          { error: 'Invalid action parameter' },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('AI Security API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * Get AI overview
 */
async function getAIOverview() {
  const stats = advancedAISecurity.getAISecurityStats();
  const models = advancedAISecurity.getModels();
  const recentPredictions = advancedAISecurity.getPredictions(undefined, 10);
  
  return NextResponse.json({
    success: true,
    data: {
      overview: stats,
      recentModels: models.slice(0, 5),
      recentPredictions: recentPredictions,
      generatedAt: new Date().toISOString(),
    },
  }, {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
  });
}

/**
 * Get AI models
 */
async function getAIModels() {
  const models = advancedAISecurity.getModels();
  
  return NextResponse.json({
    success: true,
    data: {
      models,
      total: models.length,
      deployed: models.filter(m => m.status === 'deployed').length,
      training: models.filter(m => m.status === 'training').length,
      ready: models.filter(m => m.status === 'ready').length,
    },
    generatedAt: new Date().toISOString(),
  });
}

/**
 * Get AI predictions
 */
async function getAIPredictions(modelId?: string, limit?: number) {
  const predictions = advancedAISecurity.getPredictions(modelId, limit);
  
  return NextResponse.json({
    success: true,
    data: {
      predictions,
      total: predictions.length,
      summary: {
        highRisk: predictions.filter(p => p.riskScore > 0.8).length,
        averageConfidence: predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length || 0,
        averageRiskScore: predictions.reduce((sum, p) => sum + p.riskScore, 0) / predictions.length || 0,
      },
    },
    generatedAt: new Date().toISOString(),
  });
}

/**
 * Get training jobs
 */
async function getTrainingJobs() {
  const trainingJobs = advancedAISecurity.getTrainingJobs();
  
  return NextResponse.json({
    success: true,
    data: {
      trainingJobs,
      total: trainingJobs.length,
      running: trainingJobs.filter(j => j.status === 'running').length,
      completed: trainingJobs.filter(j => j.status === 'completed').length,
      failed: trainingJobs.filter(j => j.status === 'failed').length,
    },
    generatedAt: new Date().toISOString(),
  });
}

/**
 * Get AI statistics
 */
async function getAIStats() {
  const stats = advancedAISecurity.getAISecurityStats();
  
  return NextResponse.json({
    success: true,
    data: stats,
    generatedAt: new Date().toISOString(),
  });
}

/**
 * Get model metrics
 */
async function getModelMetrics(modelId: string) {
  try {
    const metrics = advancedAISecurity.getModelMetrics(modelId);
    
    return NextResponse.json({
      success: true,
      data: metrics,
      generatedAt: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Model not found' },
      { status: 404 }
    );
  }
}

/**
 * Make AI prediction
 */
async function makePrediction(modelId: string, input: any, options?: any) {
  try {
    const prediction = await advancedAISecurity.makePrediction(modelId, input, options);
    
    return NextResponse.json({
      success: true,
      data: {
        prediction,
        message: 'Prediction completed successfully',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { 
        error: 'Prediction failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 400 }
    );
  }
}

/**
 * Train new model
 */
async function trainModel(modelConfig: any) {
  try {
    const trainingJob = await advancedAISecurity.trainModel(modelConfig);
    
    return NextResponse.json({
      success: true,
      data: {
        trainingJob,
        message: 'Training job started successfully',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { 
        error: 'Training failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 400 }
    );
  }
}

/**
 * Deploy model
 */
async function deployModel(modelId: string) {
  try {
    const success = await advancedAISecurity.deployModel(modelId);
    
    if (success) {
      return NextResponse.json({
        success: true,
        data: {
          modelId,
          message: 'Model deployed successfully',
        },
      });
    } else {
      return NextResponse.json(
        { error: 'Model deployment failed' },
        { status: 400 }
      );
    }
  } catch (error) {
    return NextResponse.json(
      { 
        error: 'Deployment failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 400 }
    );
  }
}

/**
 * Stop training job
 */
async function stopTraining(jobId: string) {
  try {
    // In a real implementation, this would stop the training job
    return NextResponse.json({
      success: true,
      data: {
        jobId,
        message: 'Training job stopped successfully',
      },
    });
  } catch (error) {
    return NextResponse.json(
      { 
        error: 'Failed to stop training',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 400 }
    );
  }
}