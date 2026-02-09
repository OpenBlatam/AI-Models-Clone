import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, FileText, Star, TrendingUp, Hash, Brain } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ResultsContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.xl};
  padding: ${props => props.theme.spacing.lg};
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  border: 1px solid ${props => props.theme.colors.border};
`;

const ResultsInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const ResultsCount = styled.span`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const SearchTime = styled.span`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const SearchType = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.primary}20;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.primary};
`;

const ResultsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
`;

const ResultCard = styled(motion.div)`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    box-shadow: ${props => props.theme.shadows.lg};
    transform: translateY(-2px);
  }
`;

const ResultHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const ResultTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
  line-height: 1.4;
  flex: 1;
`;

const ResultScore = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.secondary}20;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.secondary};
`;

const ResultSnippet = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.6;
  margin-bottom: ${props => props.theme.spacing.md};
  
  p {
    margin: 0;
  }
  
  strong {
    color: ${props => props.theme.colors.primary};
    font-weight: 600;
  }
`;

const ResultMetadata = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.sm};
  align-items: center;
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textMuted};
`;

const MetadataItem = styled.span`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  background: ${props => props.theme.colors.surfaceDark};
  border-radius: ${props => props.theme.borderRadius.sm};
`;

const ScoreBreakdown = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  margin-top: ${props => props.theme.spacing.sm};
`;

const ScoreItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textMuted};
`;

const NoResults = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
`;

const NoResultsIcon = styled.div`
  font-size: 4rem;
  margin-bottom: ${props => props.theme.spacing.lg};
  opacity: 0.5;
`;

const NoResultsTitle = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: ${props => props.theme.spacing.md};
  color: ${props => props.theme.colors.text};
`;

const NoResultsText = styled.p`
  font-size: 1rem;
  line-height: 1.6;
  max-width: 500px;
  margin: 0 auto;
`;

const LoadingResults = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: ${props => props.theme.spacing.xxl};
`;

const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 3px solid ${props => props.theme.colors.border};
  border-top: 3px solid ${props => props.theme.colors.primary};
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const SearchResults = ({ 
  results = [], 
  isLoading = false, 
  searchTime = 0, 
  searchType = 'semantic',
  totalResults = 0,
  onResultClick 
}) => {
  const getSearchTypeIcon = (type) => {
    switch (type) {
      case 'semantic':
        return Brain;
      case 'keyword':
        return Hash;
      case 'hybrid':
        return TrendingUp;
      default:
        return Brain;
    }
  };

  const getSearchTypeLabel = (type) => {
    switch (type) {
      case 'semantic':
        return 'Semántica';
      case 'keyword':
        return 'Palabras clave';
      case 'hybrid':
        return 'Híbrida';
      default:
        return 'Semántica';
    }
  };

  const formatSearchTime = (time) => {
    if (time < 1000) {
      return `${time.toFixed(0)}ms`;
    }
    return `${(time / 1000).toFixed(2)}s`;
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Fecha no disponible';
    }
  };

  if (isLoading) {
    return (
      <ResultsContainer>
        <LoadingResults>
          <LoadingSpinner />
        </LoadingResults>
      </ResultsContainer>
    );
  }

  if (results.length === 0) {
    return (
      <ResultsContainer>
        <NoResults>
          <NoResultsIcon>🔍</NoResultsIcon>
          <NoResultsTitle>No se encontraron resultados</NoResultsTitle>
          <NoResultsText>
            Intenta con términos diferentes o cambia el tipo de búsqueda. 
            También puedes verificar la ortografía de tu consulta.
          </NoResultsText>
        </NoResults>
      </ResultsContainer>
    );
  }

  const SearchTypeIcon = getSearchTypeIcon(searchType);

  return (
    <ResultsContainer>
      <ResultsHeader>
        <ResultsInfo>
          <ResultsCount>
            {totalResults} resultado{totalResults !== 1 ? 's' : ''} encontrado{totalResults !== 1 ? 's' : ''}
          </ResultsCount>
          <SearchTime>
            <Clock size={16} />
            {formatSearchTime(searchTime)}
          </SearchTime>
        </ResultsInfo>
        <SearchType>
          <SearchTypeIcon size={16} />
          {getSearchTypeLabel(searchType)}
        </SearchType>
      </ResultsHeader>

      <ResultsList>
        <AnimatePresence>
          {results.map((result, index) => (
            <ResultCard
              key={result.document_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => onResultClick && onResultClick(result)}
            >
              <ResultHeader>
                <ResultTitle>{result.title}</ResultTitle>
                <ResultScore>
                  <Star size={16} />
                  {(result.score * 100).toFixed(1)}%
                </ResultScore>
              </ResultHeader>

              <ResultSnippet>
                <ReactMarkdown>
                  {result.snippet || result.content?.substring(0, 200) + '...'}
                </ReactMarkdown>
              </ResultSnippet>

              <ResultMetadata>
                <MetadataItem>
                  <FileText size={14} />
                  {result.metadata?.document_type || 'text'}
                </MetadataItem>
                {result.metadata?.category && (
                  <MetadataItem>
                    📁 {result.metadata.category}
                  </MetadataItem>
                )}
                {result.metadata?.tags && result.metadata.tags.length > 0 && (
                  <MetadataItem>
                    🏷️ {result.metadata.tags.slice(0, 3).join(', ')}
                  </MetadataItem>
                )}
                {result.created_at && (
                  <MetadataItem>
                    📅 {formatDate(result.created_at)}
                  </MetadataItem>
                )}
              </ResultMetadata>

              {(result.semantic_score !== undefined || result.keyword_score !== undefined) && (
                <ScoreBreakdown>
                  {result.semantic_score !== undefined && (
                    <ScoreItem>
                      <Brain size={12} />
                      Semántica: {(result.semantic_score * 100).toFixed(1)}%
                    </ScoreItem>
                  )}
                  {result.keyword_score !== undefined && (
                    <ScoreItem>
                      <Hash size={12} />
                      Keywords: {(result.keyword_score * 100).toFixed(1)}%
                    </ScoreItem>
                  )}
                </ScoreBreakdown>
              )}
            </ResultCard>
          ))}
        </AnimatePresence>
      </ResultsList>
    </ResultsContainer>
  );
};

export default SearchResults;



























