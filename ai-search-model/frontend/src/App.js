import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';

// Componentes
import Header from './components/Header';
import SearchPage from './pages/SearchPage';
import DocumentPage from './pages/DocumentPage';
import UploadPage from './pages/UploadPage';
import StatsPage from './pages/StatsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import LoadingSpinner from './components/LoadingSpinner';
import ChatbotInterface from './components/ChatbotInterface';

// Tema
const theme = {
  colors: {
    primary: '#3b82f6',
    primaryDark: '#1d4ed8',
    secondary: '#10b981',
    secondaryDark: '#059669',
    accent: '#f59e0b',
    accentDark: '#d97706',
    background: '#f8fafc',
    surface: '#ffffff',
    surfaceDark: '#f1f5f9',
    text: '#1e293b',
    textSecondary: '#64748b',
    textMuted: '#94a3b8',
    border: '#e2e8f0',
    borderDark: '#cbd5e1',
    error: '#ef4444',
    warning: '#f59e0b',
    success: '#10b981',
    info: '#3b82f6'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem'
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem'
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px'
  }
};

// Estilos globales
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
    line-height: 1.6;
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }

  a {
    color: ${props => props.theme.colors.primary};
    text-decoration: none;
    transition: color 0.2s ease;

    &:hover {
      color: ${props => props.theme.colors.primaryDark};
    }
  }

  button {
    cursor: pointer;
    border: none;
    outline: none;
    font-family: inherit;
    transition: all 0.2s ease;
  }

  input, textarea, select {
    font-family: inherit;
    outline: none;
    transition: all 0.2s ease;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 ${props => props.theme.spacing.md};
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  /* Scrollbar personalizado */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.surfaceDark};
  }

  ::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.borderDark};
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${props => props.theme.colors.textMuted};
  }
`;

// Contenedor principal
const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.main`
  flex: 1;
  padding-top: 80px; /* Altura del header */
`;

// Cliente de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    // Verificar estado de la API al cargar
    const checkApiStatus = async () => {
      try {
        const response = await fetch('/health');
        if (response.ok) {
          const data = await response.json();
          setApiStatus(data);
        } else {
          setApiStatus({ status: 'error', message: 'API no disponible' });
        }
      } catch (error) {
        setApiStatus({ status: 'error', message: 'Error de conexión' });
      } finally {
        setIsLoading(false);
      }
    };

    checkApiStatus();
  }, []);

  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <AppContainer>
          <LoadingSpinner size="large" message="Cargando aplicación..." />
        </AppContainer>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <QueryClientProvider client={queryClient}>
        <Router>
          <AppContainer>
            <Header apiStatus={apiStatus} />
            <MainContent>
              <Routes>
                <Route path="/" element={<SearchPage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/document/:id" element={<DocumentPage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/stats" element={<StatsPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
              </Routes>
            </MainContent>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: theme.colors.surface,
                  color: theme.colors.text,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  boxShadow: theme.shadows.lg,
                },
                success: {
                  iconTheme: {
                    primary: theme.colors.success,
                    secondary: theme.colors.surface,
                  },
                },
                error: {
                  iconTheme: {
                    primary: theme.colors.error,
                    secondary: theme.colors.surface,
                  },
                },
              }}
            />
            
            <ChatbotInterface />
          </AppContainer>
        </Router>
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export default App;

