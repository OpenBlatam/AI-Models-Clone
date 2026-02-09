import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { 
  BarChart3, 
  FileText, 
  Database, 
  TrendingUp, 
  Clock, 
  HardDrive,
  Activity,
  AlertCircle
} from 'lucide-react';

import { apiHooks } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const PageContainer = styled.div`
  min-height: 100vh;
  background: ${props => props.theme.colors.background};
  padding-top: 100px;
`;

const ContentContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
`;

const PageTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  text-align: center;
`;

const PageSubtitle = styled.p`
  font-size: 1.125rem;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xxl};
  line-height: 1.6;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const StatCard = styled(motion.div)`
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

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const StatIcon = styled.div`
  width: 50px;
  height: 50px;
  background: ${props => props.color}20;
  border-radius: ${props => props.theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color};
`;

const StatTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const StatValue = styled.div`
  font-size: 2.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const StatDescription = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.5;
`;

const StatList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  margin-top: ${props => props.theme.spacing.lg};
`;

const StatListItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${props => props.theme.spacing.sm};
  background: ${props => props.theme.colors.surfaceDark};
  border-radius: ${props => props.theme.borderRadius.md};
`;

const StatListLabel = styled.span`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const StatListValue = styled.span`
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: ${props => props.theme.colors.surfaceDark};
  border-radius: 4px;
  overflow: hidden;
  margin-top: ${props => props.theme.spacing.sm};
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => props.color};
  width: ${props => props.percentage}%;
  transition: width 0.3s ease;
`;

const ErrorMessage = styled.div`
  background: ${props => props.theme.colors.error}20;
  border: 1px solid ${props => props.theme.colors.error}40;
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  color: ${props => props.theme.colors.error};
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString) => {
  try {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return 'Fecha no disponible';
  }
};

const StatsPage = () => {
  const { data: statistics, isLoading, error } = useQuery(apiHooks.useStatisticsQuery());

  if (isLoading) {
    return (
      <PageContainer>
        <ContentContainer>
          <LoadingSpinner size="large" message="Cargando estadísticas..." />
        </ContentContainer>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <ContentContainer>
          <ErrorMessage>
            <AlertCircle size={48} />
            <div>
              <h3>Error al cargar estadísticas</h3>
              <p>{error.message}</p>
            </div>
          </ErrorMessage>
        </ContentContainer>
      </PageContainer>
    );
  }

  if (!statistics) {
    return (
      <PageContainer>
        <ContentContainer>
          <ErrorMessage>
            <AlertCircle size={48} />
            <div>
              <h3>No hay datos disponibles</h3>
              <p>No se pudieron cargar las estadísticas del sistema</p>
            </div>
          </ErrorMessage>
        </ContentContainer>
      </PageContainer>
    );
  }

  const totalDocuments = statistics.total_documents || 0;
  const documentsByType = statistics.documents_by_type || {};
  const totalEmbeddings = statistics.total_embeddings || 0;
  const avgContentLength = statistics.average_content_length || 0;
  const avgWordCount = statistics.average_word_count || 0;
  const dbSize = statistics.database_size_bytes || 0;
  const embeddingsSize = statistics.embeddings_size_bytes || 0;
  const lastUpdated = statistics.last_updated;

  // Calcular porcentajes para tipos de documento
  const typeEntries = Object.entries(documentsByType);
  const maxTypeCount = Math.max(...typeEntries.map(([, count]) => count), 1);

  return (
    <PageContainer>
      <ContentContainer>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <PageTitle>Estadísticas del Sistema</PageTitle>
          <PageSubtitle>
            Información detallada sobre el rendimiento y uso del sistema de búsqueda IA
          </PageSubtitle>

          <StatsGrid>
            {/* Documentos totales */}
            <StatCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <StatHeader>
                <StatIcon color="#3b82f6">
                  <FileText size={24} />
                </StatIcon>
                <StatTitle>Documentos Indexados</StatTitle>
              </StatHeader>
              <StatValue>{totalDocuments.toLocaleString()}</StatValue>
              <StatDescription>
                Total de documentos disponibles para búsqueda en el sistema
              </StatDescription>
            </StatCard>

            {/* Embeddings */}
            <StatCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <StatHeader>
                <StatIcon color="#10b981">
                  <Database size={24} />
                </StatIcon>
                <StatTitle>Embeddings Generados</StatTitle>
              </StatHeader>
              <StatValue>{totalEmbeddings.toLocaleString()}</StatValue>
              <StatDescription>
                Vectores de IA creados para búsqueda semántica
              </StatDescription>
            </StatCard>

            {/* Tamaño de base de datos */}
            <StatCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <StatHeader>
                <StatIcon color="#f59e0b">
                  <HardDrive size={24} />
                </StatIcon>
                <StatTitle>Tamaño de Base de Datos</StatTitle>
              </StatHeader>
              <StatValue>{formatBytes(dbSize)}</StatValue>
              <StatDescription>
                Espacio utilizado por metadatos y estructura
              </StatDescription>
              <StatList>
                <StatListItem>
                  <StatListLabel>Base de datos</StatListLabel>
                  <StatListValue>{formatBytes(dbSize)}</StatListValue>
                </StatListItem>
                <StatListItem>
                  <StatListLabel>Embeddings</StatListLabel>
                  <StatListValue>{formatBytes(embeddingsSize)}</StatListValue>
                </StatListItem>
              </StatList>
            </StatCard>

            {/* Estadísticas de contenido */}
            <StatCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <StatHeader>
                <StatIcon color="#8b5cf6">
                  <TrendingUp size={24} />
                </StatIcon>
                <StatTitle>Estadísticas de Contenido</StatTitle>
              </StatHeader>
              <StatList>
                <StatListItem>
                  <StatListLabel>Promedio de caracteres</StatListLabel>
                  <StatListValue>{Math.round(avgContentLength).toLocaleString()}</StatListValue>
                </StatListItem>
                <StatListItem>
                  <StatListLabel>Promedio de palabras</StatListLabel>
                  <StatListValue>{Math.round(avgWordCount).toLocaleString()}</StatListValue>
                </StatListItem>
              </StatList>
            </StatCard>

            {/* Tipos de documento */}
            <StatCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <StatHeader>
                <StatIcon color="#ef4444">
                  <BarChart3 size={24} />
                </StatIcon>
                <StatTitle>Distribución por Tipo</StatTitle>
              </StatHeader>
              <StatDescription>
                Documentos organizados por tipo de contenido
              </StatDescription>
              <StatList>
                {typeEntries.map(([type, count]) => (
                  <div key={type}>
                    <StatListItem>
                      <StatListLabel>{type}</StatListLabel>
                      <StatListValue>{count}</StatListValue>
                    </StatListItem>
                    <ProgressBar>
                      <ProgressFill
                        color="#3b82f6"
                        percentage={(count / maxTypeCount) * 100}
                      />
                    </ProgressBar>
                  </div>
                ))}
              </StatList>
            </StatCard>

            {/* Información del sistema */}
            <StatCard
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              <StatHeader>
                <StatIcon color="#06b6d4">
                  <Activity size={24} />
                </StatIcon>
                <StatTitle>Información del Sistema</StatTitle>
              </StatHeader>
              <StatList>
                <StatListItem>
                  <StatListLabel>Última actualización</StatListLabel>
                  <StatListValue>{formatDate(lastUpdated)}</StatListValue>
                </StatListItem>
                <StatListItem>
                  <StatListLabel>Estado</StatListLabel>
                  <StatListValue style={{ color: '#10b981' }}>🟢 Activo</StatListValue>
                </StatListItem>
              </StatList>
            </StatCard>
          </StatsGrid>
        </motion.div>
      </ContentContainer>
    </PageContainer>
  );
};

export default StatsPage;



























