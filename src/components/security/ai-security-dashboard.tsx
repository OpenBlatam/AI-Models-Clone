'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Brain, 
  Cpu, 
  Database, 
  Zap, 
  Target, 
  Activity, 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Play, 
  Pause, 
  Square, 
  Settings, 
  RefreshCw, 
  Download, 
  Upload,
  Eye,
  AlertTriangle,
  CheckCircle,
  Clock,
  Memory,
  HardDrive,
  Network,
  Layers,
  GitBranch,
  Code,
  TestTube,
  Shield,
  Lock
} from 'lucide-react';

interface AIModel {
  id: string;
  name: string;
  type: 'classification' | 'regression' | 'clustering' | 'anomaly_detection' | 'nlp' | 'computer_vision';
  version: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  status: 'training' | 'ready' | 'deployed' | 'retired' | 'error';
  performance: {
    inferenceTime: number;
    memoryUsage: number;
    cpuUsage: number;
    gpuUsage?: number;
  };
  trainingData: {
    size: number;
    lastUpdated: number;
    quality: 'excellent' | 'good' | 'fair' | 'poor';
  };
}

interface AIPrediction {
  id: string;
  modelId: string;
  prediction: any;
  confidence: number;
  riskScore: number;
  explanation: string;
  timestamp: number;
  metadata: any;
}

interface TrainingJob {
  id: string;
  modelId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  startTime: number;
  endTime?: number;
  metrics: Record<string, number>;
  hyperparameters: Record<string, any>;
  dataset: string;
  error?: string;
}

export default function AISecurityDashboard() {
  const [models, setModels] = useState<AIModel[]>([]);
  const [predictions, setPredictions] = useState<AIPrediction[]>([]);
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
  const [selectedJob, setSelectedJob] = useState<TrainingJob | null>(null);

  useEffect(() => {
    fetchAISecurityData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchAISecurityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAISecurityData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Simulate API calls
      const mockModels: AIModel[] = [
        {
          id: 'threat_classifier_v1',
          name: 'Advanced Threat Classifier',
          type: 'classification',
          version: '1.0.0',
          accuracy: 0.95,
          precision: 0.93,
          recall: 0.94,
          f1Score: 0.935,
          status: 'deployed',
          performance: {
            inferenceTime: 15,
            memoryUsage: 512,
            cpuUsage: 25,
            gpuUsage: 15,
          },
          trainingData: {
            size: 1000000,
            lastUpdated: Date.now() - 86400000,
            quality: 'excellent',
          },
        },
        {
          id: 'anomaly_detector_v2',
          name: 'Behavioral Anomaly Detector',
          type: 'anomaly_detection',
          version: '2.1.0',
          accuracy: 0.92,
          precision: 0.89,
          recall: 0.91,
          f1Score: 0.90,
          status: 'deployed',
          performance: {
            inferenceTime: 8,
            memoryUsage: 256,
            cpuUsage: 15,
          },
          trainingData: {
            size: 2500000,
            lastUpdated: Date.now() - 172800000,
            quality: 'excellent',
          },
        },
        {
          id: 'malware_detector_v3',
          name: 'Deep Learning Malware Detector',
          type: 'classification',
          version: '3.0.0',
          accuracy: 0.98,
          precision: 0.97,
          recall: 0.98,
          f1Score: 0.975,
          status: 'training',
          performance: {
            inferenceTime: 25,
            memoryUsage: 1024,
            cpuUsage: 40,
            gpuUsage: 30,
          },
          trainingData: {
            size: 5000000,
            lastUpdated: Date.now() - 259200000,
            quality: 'excellent',
          },
        },
      ];

      const mockPredictions: AIPrediction[] = Array.from({ length: 50 }, (_, i) => ({
        id: `pred_${i}`,
        modelId: mockModels[i % mockModels.length].id,
        prediction: { class: 'malicious', confidence: 0.85 + Math.random() * 0.15 },
        confidence: 0.8 + Math.random() * 0.2,
        riskScore: 0.7 + Math.random() * 0.3,
        explanation: `Model identified ${Math.floor(Math.random() * 10) + 1} suspicious patterns in the input data.`,
        timestamp: Date.now() - Math.random() * 86400000,
        metadata: { priority: 'high', source: 'api' },
      }));

      const mockTrainingJobs: TrainingJob[] = [
        {
          id: 'job_1',
          modelId: 'malware_detector_v3',
          status: 'running',
          progress: 65,
          startTime: Date.now() - 3600000,
          metrics: {
            loss: 0.15,
            accuracy: 0.85,
            precision: 0.83,
            recall: 0.87,
          },
          hyperparameters: {
            learningRate: 0.001,
            batchSize: 32,
            epochs: 100,
          },
          dataset: 'malware_dataset_v3',
        },
        {
          id: 'job_2',
          modelId: 'threat_classifier_v1',
          status: 'completed',
          progress: 100,
          startTime: Date.now() - 7200000,
          endTime: Date.now() - 3600000,
          metrics: {
            loss: 0.08,
            accuracy: 0.95,
            precision: 0.93,
            recall: 0.94,
          },
          hyperparameters: {
            learningRate: 0.0005,
            batchSize: 64,
            epochs: 50,
          },
          dataset: 'threat_dataset_v1',
        },
      ];

      const mockStats = {
        models: {
          total: mockModels.length,
          deployed: mockModels.filter(m => m.status === 'deployed').length,
          training: mockModels.filter(m => m.status === 'training').length,
          averageAccuracy: mockModels.reduce((sum, m) => sum + m.accuracy, 0) / mockModels.length,
        },
        predictions: {
          total: mockPredictions.length,
          last24h: mockPredictions.filter(p => Date.now() - p.timestamp < 86400000).length,
          averageConfidence: mockPredictions.reduce((sum, p) => sum + p.confidence, 0) / mockPredictions.length,
          highRisk: mockPredictions.filter(p => p.riskScore > 0.8).length,
        },
        performance: {
          averageInferenceTime: mockModels.reduce((sum, m) => sum + m.performance.inferenceTime, 0) / mockModels.length,
          totalMemoryUsage: mockModels.reduce((sum, m) => sum + m.performance.memoryUsage, 0),
          totalCpuUsage: mockModels.reduce((sum, m) => sum + m.performance.cpuUsage, 0) / mockModels.length,
        },
      };

      setModels(mockModels);
      setPredictions(mockPredictions);
      setTrainingJobs(mockTrainingJobs);
      setStats(mockStats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch AI security data');
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'classification': return <Target className="h-4 w-4" />;
      case 'anomaly_detection': return <Activity className="h-4 w-4" />;
      case 'regression': return <TrendingUp className="h-4 w-4" />;
      case 'clustering': return <Layers className="h-4 w-4" />;
      case 'nlp': return <Code className="h-4 w-4" />;
      case 'computer_vision': return <Eye className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed': return 'text-green-600 bg-green-100';
      case 'ready': return 'text-blue-600 bg-blue-100';
      case 'training': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'retired': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'fair': return 'text-yellow-600 bg-yellow-100';
      case 'poor': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    return `${minutes}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-600">
        <AlertTriangle className="h-8 w-8 mx-auto mb-4" />
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Security Dashboard</h1>
          <p className="text-gray-600">Advanced AI-powered security with machine learning and deep learning</p>
        </div>
        <div className="flex items-center space-x-4">
          <Button onClick={fetchAISecurityData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
          <Button>
            <Upload className="h-4 w-4 mr-2" />
            Train New Model
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Models</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.models.total}</div>
              <p className="text-xs text-muted-foreground">
                {stats.models.deployed} deployed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Predictions (24h)</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.predictions.last24h}</div>
              <p className="text-xs text-muted-foreground">
                {Math.round(stats.predictions.averageConfidence * 100)}% avg confidence
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.predictions.highRisk}</div>
              <p className="text-xs text-muted-foreground">
                Require immediate attention
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Accuracy</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {Math.round(stats.models.averageAccuracy * 100)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Model performance
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Tabs defaultValue="models" className="space-y-4">
        <TabsList>
          <TabsTrigger value="models">AI Models</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="training">Training Jobs</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        {/* AI Models Tab */}
        <TabsContent value="models" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Security Models</CardTitle>
              <CardDescription>
                Machine learning models for threat detection and security analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {models.map((model) => (
                  <div
                    key={model.id}
                    className={`p-4 border rounded-lg cursor-pointer hover:shadow-md transition-shadow ${
                      selectedModel?.id === model.id ? 'ring-2 ring-blue-500' : ''
                    }`}
                    onClick={() => setSelectedModel(model)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="flex-shrink-0">
                          {getTypeIcon(model.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="font-medium text-gray-900">{model.name}</h3>
                            <Badge className={getStatusColor(model.status)}>
                              {model.status}
                            </Badge>
                            <Badge variant="outline">
                              v{model.version}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-2 capitalize">
                            {model.type.replace('_', ' ')} model
                          </p>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500">Accuracy:</span>
                              <div className="font-medium">{Math.round(model.accuracy * 100)}%</div>
                            </div>
                            <div>
                              <span className="text-gray-500">Precision:</span>
                              <div className="font-medium">{Math.round(model.precision * 100)}%</div>
                            </div>
                            <div>
                              <span className="text-gray-500">Recall:</span>
                              <div className="font-medium">{Math.round(model.recall * 100)}%</div>
                            </div>
                            <div>
                              <span className="text-gray-500">F1 Score:</span>
                              <div className="font-medium">{Math.round(model.f1Score * 100)}%</div>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                            <span>
                              <Database className="h-3 w-3 inline mr-1" />
                              {model.trainingData.size.toLocaleString()} samples
                            </span>
                            <span>
                              <Badge className={getQualityColor(model.trainingData.quality)}>
                                {model.trainingData.quality}
                              </Badge>
                            </span>
                            <span>
                              <Clock className="h-3 w-3 inline mr-1" />
                              {formatTimestamp(model.trainingData.lastUpdated)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button size="sm" variant="outline">
                          <Settings className="h-4 w-4 mr-2" />
                          Configure
                        </Button>
                        {model.status === 'ready' && (
                          <Button size="sm">
                            <Play className="h-4 w-4 mr-2" />
                            Deploy
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Predictions</CardTitle>
              <CardDescription>
                Recent AI model predictions and security analysis results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {predictions.slice(0, 20).map((prediction) => (
                  <div key={prediction.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">
                            {prediction.prediction.class || 'Anomaly Detected'}
                          </h3>
                          <Badge className={
                            prediction.riskScore > 0.8 ? 'text-red-600 bg-red-100' :
                            prediction.riskScore > 0.6 ? 'text-yellow-600 bg-yellow-100' :
                            'text-green-600 bg-green-100'
                          }>
                            Risk: {Math.round(prediction.riskScore * 100)}%
                          </Badge>
                          <Badge variant="outline">
                            Confidence: {Math.round(prediction.confidence * 100)}%
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {prediction.explanation}
                        </p>
                        <div className="text-xs text-gray-500">
                          <Clock className="h-3 w-3 inline mr-1" />
                          {formatTimestamp(prediction.timestamp)}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="h-4 w-4 mr-2" />
                          Details
                        </Button>
                        {prediction.riskScore > 0.8 && (
                          <Button size="sm">
                            <AlertTriangle className="h-4 w-4 mr-2" />
                            Investigate
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Training Jobs Tab */}
        <TabsContent value="training" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Training Jobs</CardTitle>
              <CardDescription>
                AI model training jobs and their current status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {trainingJobs.map((job) => (
                  <div
                    key={job.id}
                    className={`p-4 border rounded-lg cursor-pointer hover:shadow-md transition-shadow ${
                      selectedJob?.id === job.id ? 'ring-2 ring-blue-500' : ''
                    }`}
                    onClick={() => setSelectedJob(job)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">
                            Training Job {job.id}
                          </h3>
                          <Badge className={getStatusColor(job.status)}>
                            {job.status}
                          </Badge>
                          <Badge variant="outline">
                            {job.dataset}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          Model: {job.modelId}
                        </p>
                        {job.status === 'running' && (
                          <div className="mb-2">
                            <div className="flex justify-between text-sm mb-1">
                              <span>Progress</span>
                              <span>{job.progress}%</span>
                            </div>
                            <Progress value={job.progress} className="h-2" />
                          </div>
                        )}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Loss:</span>
                            <div className="font-medium">{job.metrics.loss?.toFixed(4) || 'N/A'}</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Accuracy:</span>
                            <div className="font-medium">{Math.round((job.metrics.accuracy || 0) * 100)}%</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Precision:</span>
                            <div className="font-medium">{Math.round((job.metrics.precision || 0) * 100)}%</div>
                          </div>
                          <div>
                            <span className="text-gray-500">Recall:</span>
                            <div className="font-medium">{Math.round((job.metrics.recall || 0) * 100)}%</div>
                          </div>
                        </div>
                        <div className="text-xs text-gray-500 mt-2">
                          <Clock className="h-3 w-3 inline mr-1" />
                          Started: {formatTimestamp(job.startTime)}
                          {job.endTime && (
                            <>
                              {' • '}
                              Duration: {formatDuration(job.endTime - job.startTime)}
                            </>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {job.status === 'running' && (
                          <Button size="sm" variant="outline">
                            <Pause className="h-4 w-4 mr-2" />
                            Pause
                          </Button>
                        )}
                        {job.status === 'pending' && (
                          <Button size="sm">
                            <Play className="h-4 w-4 mr-2" />
                            Start
                          </Button>
                        )}
                        <Button size="sm" variant="outline">
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Performance</CardTitle>
                <CardDescription>Overall AI system performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>CPU Usage</span>
                      <span>{Math.round(stats?.performance.totalCpuUsage || 0)}%</span>
                    </div>
                    <Progress value={stats?.performance.totalCpuUsage || 0} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Memory Usage</span>
                      <span>{Math.round((stats?.performance.totalMemoryUsage || 0) / 1024)} MB</span>
                    </div>
                    <Progress value={(stats?.performance.totalMemoryUsage || 0) / 2048 * 100} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Avg Inference Time</span>
                      <span>{Math.round(stats?.performance.averageInferenceTime || 0)}ms</span>
                    </div>
                    <Progress value={Math.min(100, (stats?.performance.averageInferenceTime || 0) / 50 * 100)} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Model Performance</CardTitle>
                <CardDescription>Individual model performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {models.slice(0, 3).map((model) => (
                    <div key={model.id} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-sm">{model.name}</h4>
                        <Badge className={getStatusColor(model.status)}>
                          {model.status}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span>Accuracy</span>
                            <span>{Math.round(model.accuracy * 100)}%</span>
                          </div>
                          <Progress value={model.accuracy * 100} className="h-1" />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span>Inference Time</span>
                            <span>{model.performance.inferenceTime}ms</span>
                          </div>
                          <Progress value={Math.min(100, model.performance.inferenceTime / 50 * 100)} className="h-1" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Resource Usage</CardTitle>
                <CardDescription>System resource utilization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Cpu className="h-4 w-4 text-blue-500" />
                      <span className="text-sm">CPU</span>
                    </div>
                    <span className="text-sm font-medium">{Math.round(stats?.performance.totalCpuUsage || 0)}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Memory className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Memory</span>
                    </div>
                    <span className="text-sm font-medium">{Math.round((stats?.performance.totalMemoryUsage || 0) / 1024)} MB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <HardDrive className="h-4 w-4 text-purple-500" />
                      <span className="text-sm">Storage</span>
                    </div>
                    <span className="text-sm font-medium">2.5 GB</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Network className="h-4 w-4 text-orange-500" />
                      <span className="text-sm">Network</span>
                    </div>
                    <span className="text-sm font-medium">125 Mbps</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}