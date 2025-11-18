'use client';

import React, { useState } from 'react';
import { ImageUpload } from '@/components/analysis/ImageUpload';
import { AnalysisResults } from '@/components/analysis/AnalysisResults';
import { RecommendationsDisplay } from '@/components/recommendations/RecommendationsDisplay';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Tabs } from '@/components/ui/Tabs';
import { Badge } from '@/components/ui/Badge';
import { Alert } from '@/components/ui/Alert';
import { apiClient } from '@/lib/api/client';
import { AnalysisResponse, RecommendationsResponse } from '@/lib/types/api';
import toast from 'react-hot-toast';
import { Sparkles, Upload, FileImage, Video } from 'lucide-react';
import { useAuth } from '@/lib/contexts/AuthContext';

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationsResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGettingRecommendations, setIsGettingRecommendations] = useState(false);
  const [activeTab, setActiveTab] = useState<'analysis' | 'recommendations'>('analysis');
  const [uploadType, setUploadType] = useState<'image' | 'video'>('image');

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast.error('Por favor selecciona una imagen primero');
      return;
    }

    setIsAnalyzing(true);
    try {
      const result = await apiClient.analyzeImage(selectedFile, true);
      setAnalysis(result);
      setActiveTab('analysis');
      toast.success('Análisis completado exitosamente');
    } catch (error: any) {
      toast.error(error.message || 'Error al analizar la imagen');
      console.error('Analysis error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGetRecommendations = async () => {
    if (!selectedFile) {
      toast.error('Por favor selecciona una imagen primero');
      return;
    }

    setIsGettingRecommendations(true);
    try {
      const result = await apiClient.getRecommendations(selectedFile, true);
      setRecommendations(result);
      setAnalysis(result); // Recommendations include analysis
      setActiveTab('recommendations');
      toast.success('Recomendaciones generadas exitosamente');
    } catch (error: any) {
      toast.error(error.message || 'Error al obtener recomendaciones');
      console.error('Recommendations error:', error);
    } finally {
      setIsGettingRecommendations(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Análisis de Piel con IA
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Sube una imagen o video de tu piel para obtener un análisis detallado y recomendaciones personalizadas
              </p>
            </div>
            {!isAuthenticated && (
              <Badge variant="info" size="lg">
                <Sparkles className="h-4 w-4 mr-1" />
                Inicia sesión para guardar tu historial
              </Badge>
            )}
          </div>

          {!isAuthenticated && (
            <Alert variant="info" className="mb-6">
              <strong>Tip:</strong> Crea una cuenta para guardar tu historial de análisis y hacer seguimiento de tu progreso.
            </Alert>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload and Actions */}
          <div className="space-y-6">
            <Card>
              <div className="mb-4">
                <Tabs
                  tabs={[
                    {
                      id: 'image',
                      label: 'Imagen',
                      icon: <FileImage className="h-4 w-4" />,
                      content: (
                        <div className="mt-4">
                          <ImageUpload
                            onFileSelect={setSelectedFile}
                            currentFile={selectedFile}
                            accept="image/*"
                          />
                        </div>
                      ),
                    },
                    {
                      id: 'video',
                      label: 'Video',
                      icon: <Video className="h-4 w-4" />,
                      content: (
                        <div className="mt-4">
                          <ImageUpload
                            onFileSelect={setSelectedFile}
                            currentFile={selectedFile}
                            accept="video/*"
                          />
                          <Alert variant="info" className="mt-4">
                            Los videos se analizan extrayendo frames clave para mayor precisión.
                          </Alert>
                        </div>
                      ),
                    },
                  ]}
                  onTabChange={(tabId) => {
                    setUploadType(tabId as 'image' | 'video');
                    setSelectedFile(null);
                    setAnalysis(null);
                    setRecommendations(null);
                  }}
                />
              </div>
            </Card>

            {selectedFile && (
              <Card>
                <h3 className="text-xl font-semibold mb-4 dark:text-white">Acciones</h3>
                <div className="space-y-3">
                  <Button
                    onClick={uploadType === 'image' ? handleAnalyze : async () => {
                      if (!selectedFile) return;
                      setIsAnalyzing(true);
                      try {
                        const result = await apiClient.analyzeVideo(selectedFile, 30);
                        setAnalysis(result);
                        setActiveTab('analysis');
                        toast.success('Análisis de video completado');
                      } catch (error: any) {
                        toast.error(error.message || 'Error al analizar el video');
                      } finally {
                        setIsAnalyzing(false);
                      }
                    }}
                    isLoading={isAnalyzing}
                    className="w-full"
                    size="lg"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    {uploadType === 'image' ? 'Analizar Imagen' : 'Analizar Video'}
                  </Button>
                  {uploadType === 'image' && (
                    <Button
                      onClick={handleGetRecommendations}
                      isLoading={isGettingRecommendations}
                      variant="secondary"
                      className="w-full"
                      size="lg"
                    >
                      <Sparkles className="h-4 w-4 mr-2" />
                      Obtener Recomendaciones Completas
                    </Button>
                  )}
                </div>
              </Card>
            )}
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {(analysis || recommendations) && (
              <div className="mb-4">
                <div className="flex space-x-2 border-b border-gray-200">
                  <button
                    onClick={() => setActiveTab('analysis')}
                    className={`px-4 py-2 font-medium transition-colors ${
                      activeTab === 'analysis'
                        ? 'text-primary-600 border-b-2 border-primary-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Análisis
                  </button>
                  {recommendations && (
                    <button
                      onClick={() => setActiveTab('recommendations')}
                      className={`px-4 py-2 font-medium transition-colors ${
                        activeTab === 'recommendations'
                          ? 'text-primary-600 border-b-2 border-primary-600'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Recomendaciones
                    </button>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'analysis' && analysis && (
              <AnalysisResults
                analysis={analysis.analysis}
                analysisId={analysis.analysis.analysis_id}
              />
            )}

            {activeTab === 'recommendations' && recommendations && (
              <RecommendationsDisplay
                recommendations={recommendations.recommendations}
              />
            )}

            {!analysis && !recommendations && (
              <Card className="p-12 text-center dark:bg-gray-800">
                <Sparkles className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Comienza tu análisis
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Sube una {uploadType === 'image' ? 'imagen' : 'video'} de tu piel para comenzar el análisis
                </p>
                <div className="mt-6 grid grid-cols-2 gap-4 max-w-md mx-auto">
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <FileImage className="h-8 w-8 text-primary-600 dark:text-primary-400 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Imágenes</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">JPG, PNG, WEBP</p>
                  </div>
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <Video className="h-8 w-8 text-primary-600 dark:text-primary-400 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Videos</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">MP4, MOV, AVI</p>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

