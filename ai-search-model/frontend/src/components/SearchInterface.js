import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Search, Filter, Clock, TrendingUp, Brain, Hash } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

const SearchContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
`;

const SearchHeader = styled.div`
  text-align: center;
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.md};
  background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const Subtitle = styled.p`
  font-size: 1.125rem;
  color: ${props => props.theme.colors.textSecondary};
  max-width: 600px;
  margin: 0 auto;
`;

const SearchForm = styled.form`
  position: relative;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const SearchInput = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.lg} ${props => props.theme.spacing.xl};
  padding-right: 60px;
  font-size: 1.125rem;
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  transition: all 0.3s ease;
  box-shadow: ${props => props.theme.shadows.sm};

  &:focus {
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
    outline: none;
  }

  &::placeholder {
    color: ${props => props.theme.colors.textMuted};
  }
`;

const SearchButton = styled.button`
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  background: ${props => props.theme.colors.primary};
  color: white;
  border-radius: ${props => props.theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
    transform: translateY(-50%) scale(1.05);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: translateY(-50%);
  }
`;

const SearchOptions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.xl};
  flex-wrap: wrap;
  justify-content: center;
`;

const OptionGroup = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  background: ${props => props.theme.colors.surface};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.lg};
  border: 1px solid ${props => props.theme.colors.border};
`;

const OptionLabel = styled.label`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const Select = styled.select`
  background: transparent;
  border: none;
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  outline: none;

  option {
    background: ${props => props.theme.colors.surface};
    color: ${props => props.theme.colors.text};
  }
`;

const NumberInput = styled.input`
  width: 60px;
  background: transparent;
  border: none;
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
  outline: none;

  &::-webkit-outer-spin-button,
  &::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  &[type=number] {
    -moz-appearance: textfield;
  }
`;

const SearchTypeSelector = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.xs};
  background: ${props => props.theme.colors.surfaceDark};
  padding: 4px;
  border-radius: ${props => props.theme.borderRadius.lg};
  border: 1px solid ${props => props.theme.colors.border};
`;

const SearchTypeButton = styled.button`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  background: ${props => props.active ? props.theme.colors.primary : 'transparent'};
  color: ${props => props.active ? 'white' : props.theme.colors.textSecondary};

  &:hover {
    background: ${props => props.active ? props.theme.colors.primaryDark : props.theme.colors.surface};
    color: ${props => props.active ? 'white' : props.theme.colors.text};
  }
`;

const RecentSearches = styled.div`
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const RecentTitle = styled.h3`
  font-size: 1rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const RecentList = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
  flex-wrap: wrap;
`;

const RecentItem = styled.button`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.primary};
    color: white;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const SearchInterface = ({ onSearch, isLoading, recentSearches = [] }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('semantic');
  const [limit, setLimit] = useState(10);
  const [filters, setFilters] = useState({});

  const searchTypes = [
    { value: 'semantic', label: 'Semántica', icon: Brain, description: 'Búsqueda por significado' },
    { value: 'keyword', label: 'Palabras clave', icon: Hash, description: 'Búsqueda por términos exactos' },
    { value: 'hybrid', label: 'Híbrida', icon: TrendingUp, description: 'Combinación de ambos métodos' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Por favor ingresa una consulta de búsqueda');
      return;
    }

    const searchParams = {
      query: query.trim(),
      search_type: searchType,
      limit: limit,
      filters: Object.keys(filters).length > 0 ? filters : undefined
    };

    onSearch(searchParams);
  };

  const handleRecentSearch = (recentQuery) => {
    setQuery(recentQuery);
    const searchParams = {
      query: recentQuery,
      search_type: searchType,
      limit: limit,
      filters: Object.keys(filters).length > 0 ? filters : undefined
    };
    onSearch(searchParams);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <SearchContainer>
      <SearchHeader>
        <Title>Búsqueda Inteligente IA</Title>
        <Subtitle>
          Encuentra la información más relevante en tu base de datos de documentos 
          usando inteligencia artificial avanzada
        </Subtitle>
      </SearchHeader>

      <SearchForm onSubmit={handleSubmit}>
        <SearchInput
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Buscar documentos... (ej: 'inteligencia artificial', 'machine learning')"
          disabled={isLoading}
        />
        <SearchButton type="submit" disabled={isLoading || !query.trim()}>
          <Search size={20} />
        </SearchButton>
      </SearchForm>

      <SearchOptions>
        <OptionGroup>
          <OptionLabel>
            <Filter size={16} />
            Tipo de búsqueda:
          </OptionLabel>
          <SearchTypeSelector>
            {searchTypes.map((type) => {
              const Icon = type.icon;
              return (
                <SearchTypeButton
                  key={type.value}
                  type="button"
                  active={searchType === type.value}
                  onClick={() => setSearchType(type.value)}
                  title={type.description}
                >
                  <Icon size={14} />
                  {type.label}
                </SearchTypeButton>
              );
            })}
          </SearchTypeSelector>
        </OptionGroup>

        <OptionGroup>
          <OptionLabel>Resultados:</OptionLabel>
          <NumberInput
            type="number"
            min="1"
            max="100"
            value={limit}
            onChange={(e) => setLimit(Math.max(1, Math.min(100, parseInt(e.target.value) || 10)))}
          />
        </OptionGroup>
      </SearchOptions>

      {recentSearches.length > 0 && (
        <RecentSearches>
          <RecentTitle>
            <Clock size={16} />
            Búsquedas recientes
          </RecentTitle>
          <RecentList>
            {recentSearches.slice(0, 5).map((search, index) => (
              <RecentItem
                key={index}
                onClick={() => handleRecentSearch(search)}
              >
                {search}
              </RecentItem>
            ))}
          </RecentList>
        </RecentSearches>
      )}
    </SearchContainer>
  );
};

export default SearchInterface;



























