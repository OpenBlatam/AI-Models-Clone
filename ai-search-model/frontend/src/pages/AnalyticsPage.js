import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Search, 
  FileText, 
  Clock,
  Brain,
  Hash,
  Activity,
  Download,
  RefreshCw,
  Filter,
  Calendar
} from 'lucide-react';

import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const PageContainer = styled.div`
  min-height: 100vh;
  background: ${props => props.theme.colors.background};
  padding-top: 100px;
`;

const ContentContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
`;

const PageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const PageTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const AnalyticsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const AnalyticsCard = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: ${props => props.theme.spacing.xl};
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${props => props.theme.shadows.lg};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const CardIcon = styled.div`
  width: 50px;
  height: 50px;
  background: ${props => props.color}20;
  border-radius: ${props => props.theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color};
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const CardContent = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.6;
`;

const MetricGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const MetricCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const MetricLabel = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  font-weight: 500;
`;

const ChartContainer = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const ChartTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ChartPlaceholder = styled.div`
  height: 300px;
  background: ${props => props.theme.colors.surfaceDark};
  border-radius: ${props => props.theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.textMuted};
  font-size: 1.125rem;
`;

const InsightsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const InsightItem = styled.div`
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surfaceDark};
  border-radius: ${props => props.theme.borderRadius.md};
  border-left: 4px solid ${props => props.theme.colors.primary};
`;

const InsightText = styled.div`
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  line-height: 1.5;
`;

const RecommendationsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
`;

const RecommendationItem = styled.div`
  padding: ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.secondary}20;
  border-radius: ${props => props.theme.borderRadius.md};
  border-left: 4px solid ${props => props.theme.colors.secondary};
`;

const RecommendationText = styled.div`
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  line-height: 1.5;
`;

const FilterSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const FilterTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const FilterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.md};
`;

const FilterGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const FilterLabel = styled.label`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
`;

const FilterSelect = styled.select`
  padding: ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const AnalyticsPage = () => {
  const [filters, setFilters] = useState({
    timeRange: '7d',
    searchType: 'all',
    documentType: 'all'
  });
  const [analyticsData, setAnalyticsData] = useState(null);

  // Queries para obtener datos
  const { data: statistics, isLoading: statsLoading } = useQuery(
    ['statistics'],
    () => apiService.getStatistics(),
    { refetchInterval: 30000 }
  );

  const { data: searchAnalytics, isLoading: searchLoading } = useQuery(
    ['search-analytics', filters],
    () => apiService.getSearchAnalytics(filters),
    { enabled: false } // Se activará cuando implementemos el endpoint
  );

  // Simular datos de analytics para demostración
  useEffect(() => {
    const mockAnalyticsData = {
      searchPatterns: {
        totalSearches: 1250,
        uniqueQueries: 890,
        avgQueryLength: 12.5,
        mostPopularQueries: {
          "inteligencia artificial": 45,
          "machine learning": 38,
          "python": 32,
          "desarrollo web": 28,
          "base de datos": 25
        },
        searchTypeDistribution: {
          "semantic": 65,
          "keyword": 20,
          "hybrid": 15
        }
      },
      temporalPatterns: {
        hourlyDistribution: {
          "9": 45, "10": 52, "11": 48, "12": 35,
          "13": 28, "14": 42, "15": 55, "16": 48,
          "17": 38, "18": 25, "19": 15, "20": 8
        },
        dailyDistribution: {
          "Monday": 180, "Tuesday": 195, "Wednesday": 210,
          "Thursday": 185, "Friday": 165, "Saturday": 45, "Sunday": 25
        }
      },
      performanceAnalysis: {
        avgSearchTimeMs: 125,
        avgResultsPerSearch: 8.5
      },
      insights: [
        "Los usuarios prefieren búsqueda semántica (65% de las consultas)",
        "El pico de uso es entre las 2-4 PM",
        "Las consultas más populares están relacionadas con IA y programación",
        "El rendimiento del sistema es excelente con tiempos promedio de 125ms"
      ],
      recommendations: [
        "Optimizar el modelo de embeddings para consultas técnicas",
        "Implementar sugerencias automáticas para consultas populares",
        "Agregar más contenido sobre machine learning",
        "Considerar implementar búsqueda por voz"
      ]
    };

    setAnalyticsData(mockAnalyticsData);
  }, [filters]);

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleExportAnalytics = () => {
    // Implementar exportación de analytics
    console.log('Exportando analytics...');
  };

  const handleRefreshData = () => {
    // Refrescar datos
    window.location.reload();
  };

  if (statsLoading) {
    return (
      <PageContainer>
        <ContentContainer>
          <LoadingSpinner size="large" message="Cargando analytics..." />
        </ContentContainer>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <ContentContainer>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <PageHeader>
            <PageTitle>Analytics & Insights</PageTitle>
            <HeaderActions>
              <ActionButton onClick={handleRefreshData}>
                <RefreshCw size={16} />
                Actualizar
              </ActionButton>
              <ActionButton onClick={handleExportAnalytics}>
                <Download size={16} />
                Exportar
              </ActionButton>
            </HeaderActions>
          </PageHeader>

          {/* Filtros */}
          <FilterSection>
            <FilterTitle>
              <Filter size={20} />
              Filtros de Analytics
            </FilterTitle>
            <FilterGrid>
              <FilterGroup>
                <FilterLabel>Rango de Tiempo</FilterLabel>
                <FilterSelect
                  value={filters.timeRange}
                  onChange={(e) => handleFilterChange('timeRange', e.target.value)}
                >
                  <option value="1d">Último día</option>
                  <option value="7d">Última semana</option>
                  <option value="30d">Último mes</option>
                  <option value="90d">Últimos 3 meses</option>
                </FilterSelect>
              </FilterGroup>
              <FilterGroup>
                <FilterLabel>Tipo de Búsqueda</FilterLabel>
                <FilterSelect
                  value={filters.searchType}
                  onChange={(e) => handleFilterChange('searchType', e.target.value)}
                >
                  <option value="all">Todos</option>
                  <option value="semantic">Semántica</option>
                  <option value="keyword">Palabras clave</option>
                  <option value="hybrid">Híbrida</option>
                </FilterSelect>
              </FilterGroup>
              <FilterGroup>
                <FilterLabel>Tipo de Documento</FilterLabel>
                <FilterSelect
                  value={filters.documentType}
                  onChange={(e) => handleFilterChange('documentType', e.target.value)}
                >
                  <option value="all">Todos</option>
                  <option value="text">Texto</option>
                  <option value="markdown">Markdown</option>
                  <option value="html">HTML</option>
                  <option value="json">JSON</option>
                </FilterSelect>
              </FilterGroup>
            </FilterGrid>
          </FilterSection>

          {/* Métricas principales */}
          <MetricGrid>
            <MetricCard>
              <MetricValue>{statistics?.total_documents || 0}</MetricValue>
              <MetricLabel>Documentos Totales</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>{analyticsData?.searchPatterns?.totalSearches || 0}</MetricValue>
              <MetricLabel>Búsquedas Totales</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>{analyticsData?.searchPatterns?.uniqueQueries || 0}</MetricValue>
              <MetricLabel>Consultas Únicas</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>{analyticsData?.performanceAnalysis?.avgSearchTimeMs || 0}ms</MetricValue>
              <MetricLabel>Tiempo Promedio</MetricLabel>
            </MetricCard>
          </MetricGrid>

          {/* Grid de analytics */}
          <AnalyticsGrid>
            {/* Patrones de búsqueda */}
            <AnalyticsCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <CardHeader>
                <CardIcon color="#3b82f6">
                  <Search size={24} />
                </CardIcon>
                <CardTitle>Patrones de Búsqueda</CardTitle>
              </CardHeader>
              <CardContent>
                <div style={{ marginBottom: '1rem' }}>
                  <strong>Consultas más populares:</strong>
                  <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                    {analyticsData?.searchPatterns?.mostPopularQueries && 
                      Object.entries(analyticsData.searchPatterns.mostPopularQueries)
                        .slice(0, 5)
                        .map(([query, count]) => (
                          <li key={query}>
                            "{query}" - {count} búsquedas
                          </li>
                        ))
                    }
                  </ul>
                </div>
                <div>
                  <strong>Distribución por tipo:</strong>
                  <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                    {analyticsData?.searchPatterns?.searchTypeDistribution && 
                      Object.entries(analyticsData.searchPatterns.searchTypeDistribution)
                        .map(([type, percentage]) => (
                          <li key={type}>
                            {type}: {percentage}%
                          </li>
                        ))
                    }
                  </ul>
                </div>
              </CardContent>
            </AnalyticsCard>

            {/* Patrones temporales */}
            <AnalyticsCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <CardHeader>
                <CardIcon color="#10b981">
                  <Clock size={24} />
                </CardIcon>
                <CardTitle>Patrones Temporales</CardTitle>
              </CardHeader>
              <CardContent>
                <div style={{ marginBottom: '1rem' }}>
                  <strong>Pico de uso por hora:</strong>
                  <div style={{ marginTop: '0.5rem' }}>
                    {analyticsData?.temporalPatterns?.hourlyDistribution && 
                      Object.entries(analyticsData.temporalPatterns.hourlyDistribution)
                        .sort((a, b) => parseInt(b[1]) - parseInt(a[1]))
                        .slice(0, 3)
                        .map(([hour, count]) => (
                          <div key={hour}>
                            {hour}:00 - {count} búsquedas
                          </div>
                        ))
                    }
                  </div>
                </div>
                <div>
                  <strong>Distribución por día:</strong>
                  <div style={{ marginTop: '0.5rem' }}>
                    {analyticsData?.temporalPatterns?.dailyDistribution && 
                      Object.entries(analyticsData.temporalPatterns.dailyDistribution)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 3)
                        .map(([day, count]) => (
                          <div key={day}>
                            {day}: {count} búsquedas
                          </div>
                        ))
                    }
                  </div>
                </div>
              </CardContent>
            </AnalyticsCard>

            {/* Rendimiento */}
            <AnalyticsCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <CardHeader>
                <CardIcon color="#f59e0b">
                  <Activity size={24} />
                </CardIcon>
                <CardTitle>Rendimiento</CardTitle>
              </CardHeader>
              <CardContent>
                <div style={{ marginBottom: '1rem' }}>
                  <strong>Tiempo promedio de búsqueda:</strong>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981', marginTop: '0.5rem' }}>
                    {analyticsData?.performanceAnalysis?.avgSearchTimeMs || 0}ms
                  </div>
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <strong>Resultados promedio por búsqueda:</strong>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6', marginTop: '0.5rem' }}>
                    {analyticsData?.performanceAnalysis?.avgResultsPerSearch || 0}
                  </div>
                </div>
                <div>
                  <strong>Estado del sistema:</strong>
                  <div style={{ color: '#10b981', fontWeight: 'bold', marginTop: '0.5rem' }}>
                    🟢 Excelente
                  </div>
                </div>
              </CardContent>
            </AnalyticsCard>

            {/* Insights */}
            <AnalyticsCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <CardHeader>
                <CardIcon color="#8b5cf6">
                  <Brain size={24} />
                </CardIcon>
                <CardTitle>Insights Inteligentes</CardTitle>
              </CardHeader>
              <CardContent>
                <InsightsList>
                  {analyticsData?.insights?.map((insight, index) => (
                    <InsightItem key={index}>
                      <InsightText>{insight}</InsightText>
                    </InsightItem>
                  ))}
                </InsightsList>
              </CardContent>
            </AnalyticsCard>

            {/* Recomendaciones */}
            <AnalyticsCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <CardHeader>
                <CardIcon color="#ef4444">
                  <TrendingUp size={24} />
                </CardIcon>
                <CardTitle>Recomendaciones</CardTitle>
              </CardHeader>
              <CardContent>
                <RecommendationsList>
                  {analyticsData?.recommendations?.map((recommendation, index) => (
                    <RecommendationItem key={index}>
                      <RecommendationText>{recommendation}</RecommendationText>
                    </RecommendationItem>
                  ))}
                </RecommendationsList>
              </CardContent>
            </AnalyticsCard>

            {/* Distribución de tipos */}
            <AnalyticsCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              <CardHeader>
                <CardIcon color="#06b6d4">
                  <FileText size={24} />
                </CardIcon>
                <CardTitle>Distribución de Contenido</CardTitle>
              </CardHeader>
              <CardContent>
                <div>
                  <strong>Tipos de documento:</strong>
                  <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                    {statistics?.documents_by_type && 
                      Object.entries(statistics.documents_by_type)
                        .map(([type, count]) => (
                          <li key={type}>
                            {type}: {count} documentos
                          </li>
                        ))
                    }
                  </ul>
                </div>
                <div style={{ marginTop: '1rem' }}>
                  <strong>Estadísticas de contenido:</strong>
                  <div style={{ marginTop: '0.5rem' }}>
                    <div>Promedio de caracteres: {Math.round(statistics?.average_content_length || 0)}</div>
                    <div>Promedio de palabras: {Math.round(statistics?.average_word_count || 0)}</div>
                  </div>
                </div>
              </CardContent>
            </AnalyticsCard>
          </AnalyticsGrid>

          {/* Gráficos */}
          <ChartContainer>
            <ChartTitle>
              <BarChart3 size={24} />
              Visualizaciones de Datos
            </ChartTitle>
            <ChartPlaceholder>
              📊 Gráficos interactivos disponibles próximamente
            </ChartPlaceholder>
          </ChartContainer>
        </motion.div>
      </ContentContainer>
    </PageContainer>
  );
};

export default AnalyticsPage;



























