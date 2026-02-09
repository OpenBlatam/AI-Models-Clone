import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';

// Componentes
import SearchInterface from '../components/SearchInterface';
import SearchResults from '../components/SearchResults';
import LoadingSpinner from '../components/LoadingSpinner';

// Servicios
import { apiService, apiHooks } from '../services/api';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, 
    ${props => props.theme.colors.background} 0%, 
    ${props => props.theme.colors.surfaceDark} 100%);
`;

const ContentContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
`;

const WelcomeSection = styled(motion.div)`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xxl};
  padding: ${props => props.theme.spacing.xxl} 0;
`;

const WelcomeTitle = styled.h1`
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: ${props => props.theme.spacing.lg};
  background: linear-gradient(135deg, 
    ${props => props.theme.colors.primary}, 
    ${props => props.theme.colors.secondary});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const WelcomeSubtitle = styled.p`
  font-size: 1.25rem;
  color: ${props => props.theme.colors.textSecondary};
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
`;

const StatsSection = styled(motion.div)`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const StatCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  text-align: center;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${props => props.theme.shadows.lg};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const StatNumber = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const StatLabel = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  font-weight: 500;
`;

const SearchSection = styled.div`
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const ResultsSection = styled.div`
  min-height: 400px;
`;

const RecentSearchesSection = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const RecentSearchesList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.sm};
`;

const RecentSearchItem = styled.button`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surfaceDark};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    background: ${props => props.theme.colors.primary};
    color: white;
    border-color: ${props => props.theme.colors.primary};
    transform: translateY(-1px);
  }
`;

const SearchPage = () => {
  const [searchParams, setSearchParams] = useState(null);
  const [recentSearches, setRecentSearches] = useState([]);
  const queryClient = useQueryClient();

  // Queries
  const { data: statistics, isLoading: statsLoading } = useQuery(apiHooks.useStatisticsQuery());
  const { data: health, isLoading: healthLoading } = useQuery(apiHooks.useHealthQuery());

  // Búsqueda
  const { 
    data: searchResults, 
    isLoading: searchLoading, 
    error: searchError,
    refetch: refetchSearch
  } = useQuery({
    ...apiHooks.useSearchQuery(searchParams?.query, {
      search_type: searchParams?.search_type,
      limit: searchParams?.limit,
      filters: searchParams?.filters
    }),
    enabled: !!searchParams,
  });

  // Cargar búsquedas recientes del localStorage
  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (error) {
        console.error('Error al cargar búsquedas recientes:', error);
      }
    }
  }, []);

  // Guardar búsquedas recientes
  const saveRecentSearch = useCallback((query) => {
    if (!query || query.trim().length === 0) return;
    
    const trimmedQuery = query.trim();
    const updated = [trimmedQuery, ...recentSearches.filter(q => q !== trimmedQuery)].slice(0, 10);
    
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
  }, [recentSearches]);

  // Manejar búsqueda
  const handleSearch = useCallback(async (params) => {
    try {
      setSearchParams(params);
      saveRecentSearch(params.query);
      
      // Mostrar toast de búsqueda iniciada
      toast.loading('Buscando documentos...', { id: 'search' });
      
    } catch (error) {
      console.error('Error en búsqueda:', error);
      toast.error('Error al realizar la búsqueda');
    }
  }, [saveRecentSearch]);

  // Manejar click en resultado
  const handleResultClick = useCallback((result) => {
    // Aquí podrías navegar a una página de detalle del documento
    console.log('Documento seleccionado:', result);
    toast.success(`Documento seleccionado: ${result.title}`);
  }, []);

  // Manejar búsqueda reciente
  const handleRecentSearch = useCallback((query) => {
    const params = {
      query,
      search_type: 'semantic',
      limit: 10
    };
    handleSearch(params);
  }, [handleSearch]);

  // Efecto para manejar resultados de búsqueda
  useEffect(() => {
    if (searchResults) {
      toast.success(
        `${searchResults.total_results} resultado${searchResults.total_results !== 1 ? 's' : ''} encontrado${searchResults.total_results !== 1 ? 's' : ''}`,
        { id: 'search' }
      );
    }
  }, [searchResults]);

  // Efecto para manejar errores de búsqueda
  useEffect(() => {
    if (searchError) {
      toast.error(`Error en búsqueda: ${searchError.message}`, { id: 'search' });
    }
  }, [searchError]);

  // Verificar estado del sistema
  const isSystemHealthy = health?.status === 'healthy';
  const systemStatus = isSystemHealthy ? '🟢 Operativo' : '🔴 Con problemas';

  return (
    <PageContainer>
      <ContentContainer>
        {/* Sección de bienvenida */}
        <WelcomeSection
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <WelcomeTitle>Búsqueda Inteligente IA</WelcomeTitle>
          <WelcomeSubtitle>
            Encuentra la información más relevante en tu base de datos de documentos 
            usando inteligencia artificial avanzada. Búsqueda semántica, por palabras clave o híbrida.
          </WelcomeSubtitle>
        </WelcomeSection>

        {/* Estadísticas del sistema */}
        {statistics && (
          <StatsSection
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <StatCard>
              <StatNumber>{statistics.total_documents || 0}</StatNumber>
              <StatLabel>Documentos Indexados</StatLabel>
            </StatCard>
            <StatCard>
              <StatNumber>{statistics.documents_by_type ? Object.keys(statistics.documents_by_type).length : 0}</StatNumber>
              <StatLabel>Tipos de Documento</StatLabel>
            </StatCard>
            <StatCard>
              <StatNumber>{systemStatus}</StatNumber>
              <StatLabel>Estado del Sistema</StatLabel>
            </StatCard>
            <StatCard>
              <StatNumber>{statistics.average_content_length ? Math.round(statistics.average_content_length) : 0}</StatNumber>
              <StatLabel>Promedio de Caracteres</StatLabel>
            </StatCard>
          </StatsSection>
        )}

        {/* Búsquedas recientes */}
        {recentSearches.length > 0 && (
          <RecentSearchesSection
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <SectionTitle>🔍 Búsquedas Recientes</SectionTitle>
            <RecentSearchesList>
              {recentSearches.map((search, index) => (
                <RecentSearchItem
                  key={index}
                  onClick={() => handleRecentSearch(search)}
                >
                  {search}
                </RecentSearchItem>
              ))}
            </RecentSearchesList>
          </RecentSearchesSection>
        )}

        {/* Interfaz de búsqueda */}
        <SearchSection>
          <SearchInterface
            onSearch={handleSearch}
            isLoading={searchLoading}
            recentSearches={recentSearches}
          />
        </SearchSection>

        {/* Resultados de búsqueda */}
        <ResultsSection>
          {searchLoading ? (
            <LoadingSpinner size="large" message="Buscando documentos..." />
          ) : (
            <SearchResults
              results={searchResults?.results || []}
              isLoading={searchLoading}
              searchTime={searchResults?.search_time || 0}
              searchType={searchParams?.search_type || 'semantic'}
              totalResults={searchResults?.total_results || 0}
              onResultClick={handleResultClick}
            />
          )}
        </ResultsSection>
      </ContentContainer>
    </PageContainer>
  );
};

export default SearchPage;



























