'use client';

import React from 'react';
import { SkinAnalysis, QualityScores } from '@/lib/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { ExportReport } from './ExportReport';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface AnalysisResultsProps {
  analysis: SkinAnalysis;
  analysisId?: string;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysis, analysisId }) => {
  const { quality_scores, conditions, skin_type, recommendations_priority } = analysis;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getTrendIcon = (score: number) => {
    if (score >= 80) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (score >= 60) return <Minus className="h-4 w-4 text-yellow-600" />;
    return <TrendingDown className="h-4 w-4 text-red-600" />;
  };

  const ScoreCard: React.FC<{ label: string; score: number }> = ({ label, score }) => (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        {getTrendIcon(score)}
      </div>
      <div className="flex items-center space-x-2">
        <div className="flex-1 bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${getScoreBgColor(score)}`}
            style={{ width: `${score}%` }}
          />
        </div>
        <span className={`text-lg font-bold ${getScoreColor(score)}`}>
          {score.toFixed(1)}
        </span>
      </div>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <Card className="animate-fade-in">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Puntuación General</CardTitle>
            {analysisId && (
              <ExportReport analysisId={analysisId} analysisData={analysis} />
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div
              className={`inline-flex items-center justify-center w-32 h-32 rounded-full text-4xl font-bold ${getScoreColor(
                quality_scores.overall_score
              )} ${getScoreBgColor(quality_scores.overall_score)}`}
            >
              {quality_scores.overall_score.toFixed(1)}
            </div>
            <p className="mt-4 text-gray-600">
              Tipo de piel: <span className="font-semibold capitalize">{skin_type}</span>
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Quality Scores */}
      <Card className="animate-fade-in">
        <CardHeader>
          <CardTitle>Métricas de Calidad</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ScoreCard label="Textura" score={quality_scores.texture_score} />
            <ScoreCard label="Hidratación" score={quality_scores.hydration_score} />
            <ScoreCard label="Elasticidad" score={quality_scores.elasticity_score} />
            <ScoreCard label="Pigmentación" score={quality_scores.pigmentation_score} />
            <ScoreCard label="Tamaño de Poros" score={quality_scores.pore_size_score} />
            <ScoreCard label="Arrugas" score={quality_scores.wrinkles_score} />
            <ScoreCard label="Enrojecimiento" score={quality_scores.redness_score} />
            <ScoreCard label="Manchas Oscuras" score={quality_scores.dark_spots_score} />
          </div>
        </CardContent>
      </Card>

      {/* Conditions */}
      {conditions && conditions.length > 0 && (
        <Card className="animate-fade-in">
          <CardHeader>
            <CardTitle>Condiciones Detectadas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {conditions.map((condition, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-gray-900 capitalize">
                        {condition.name}
                      </span>
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          condition.severity === 'severe'
                            ? 'bg-red-100 text-red-800'
                            : condition.severity === 'moderate'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {condition.severity}
                      </span>
                    </div>
                    {condition.description && (
                      <p className="text-sm text-gray-600 mt-1">{condition.description}</p>
                    )}
                  </div>
                  <div className="ml-4">
                    <span className="text-sm font-medium text-gray-700">
                      {(condition.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Priority Recommendations */}
      {recommendations_priority && recommendations_priority.length > 0 && (
        <Card className="animate-fade-in">
          <CardHeader>
            <CardTitle>Áreas Prioritarias</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {recommendations_priority.map((priority, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium"
                >
                  {priority}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

