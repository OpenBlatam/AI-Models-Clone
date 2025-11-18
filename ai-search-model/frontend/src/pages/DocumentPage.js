import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { 
  ArrowLeft, 
  FileText, 
  Calendar, 
  Tag, 
  Hash,
  ExternalLink,
  Copy,
  Check
} from 'lucide-react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

import { apiHooks } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const PageContainer = styled.div`
  min-height: 100vh;
  background: ${props => props.theme.colors.background};
  padding-top: 100px;
`;

const ContentContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: ${props => props.theme.spacing.xl};
`;

const BackButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  color: ${props => props.theme.colors.text};
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  margin-bottom: ${props => props.theme.spacing.xl};

  &:hover {
    background: ${props => props.theme.colors.primary};
    color: white;
    border-color: ${props => props.theme.colors.primary};
    transform: translateX(-2px);
  }
`;

const DocumentHeader = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const DocumentTitle = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  line-height: 1.3;
`;

const DocumentMetadata = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${props => props.theme.spacing.lg};
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const MetadataItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  background: ${props => props.theme.colors.surfaceDark};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const DocumentActions = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.sm};
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

const DocumentContent = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const ContentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};
  padding-bottom: ${props => props.theme.spacing.md};
  border-bottom: 1px solid ${props => props.theme.colors.border};
`;

const ContentTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const ContentStats = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.lg};
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const ContentBody = styled.div`
  line-height: 1.7;
  color: ${props => props.theme.colors.text};

  h1, h2, h3, h4, h5, h6 {
    color: ${props => props.theme.colors.text};
    margin-top: ${props => props.theme.spacing.xl};
    margin-bottom: ${props => props.theme.spacing.md};
  }

  p {
    margin-bottom: ${props => props.theme.spacing.md};
  }

  code {
    background: ${props => props.theme.colors.surfaceDark};
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.875em;
  }

  pre {
    background: ${props => props.theme.colors.surfaceDark};
    padding: ${props => props.theme.spacing.md};
    border-radius: ${props => props.theme.borderRadius.md};
    overflow-x: auto;
    margin: ${props => props.theme.spacing.md} 0;
  }

  blockquote {
    border-left: 4px solid ${props => props.theme.colors.primary};
    padding-left: ${props => props.theme.spacing.md};
    margin: ${props => props.theme.spacing.md} 0;
    color: ${props => props.theme.colors.textSecondary};
  }

  ul, ol {
    margin: ${props => props.theme.spacing.md} 0;
    padding-left: ${props => props.theme.spacing.xl};
  }

  li {
    margin-bottom: ${props => props.theme.spacing.sm};
  }
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

const formatDate = (dateString) => {
  try {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return 'Fecha no disponible';
  }
};

const DocumentPage = () => {
  const { id } = useParams();
  const [copied, setCopied] = React.useState(false);

  const { data: document, isLoading, error } = useQuery({
    ...apiHooks.useDocumentQuery(id),
    enabled: !!id,
  });

  const handleCopyContent = async () => {
    if (document?.content) {
      try {
        await navigator.clipboard.writeText(document.content);
        setCopied(true);
        toast.success('Contenido copiado al portapapeles');
        setTimeout(() => setCopied(false), 2000);
      } catch (error) {
        toast.error('Error al copiar contenido');
      }
    }
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast.success('Enlace copiado al portapapeles');
    } catch (error) {
      toast.error('Error al copiar enlace');
    }
  };

  if (isLoading) {
    return (
      <PageContainer>
        <ContentContainer>
          <LoadingSpinner size="large" message="Cargando documento..." />
        </ContentContainer>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <ContentContainer>
          <ErrorMessage>
            <FileText size={48} />
            <div>
              <h3>Error al cargar documento</h3>
              <p>{error.message}</p>
            </div>
          </ErrorMessage>
        </ContentContainer>
      </PageContainer>
    );
  }

  if (!document) {
    return (
      <PageContainer>
        <ContentContainer>
          <ErrorMessage>
            <FileText size={48} />
            <div>
              <h3>Documento no encontrado</h3>
              <p>El documento solicitado no existe o ha sido eliminado</p>
            </div>
          </ErrorMessage>
        </ContentContainer>
      </PageContainer>
    );
  }

  const wordCount = document.content?.split(/\s+/).length || 0;
  const charCount = document.content?.length || 0;

  return (
    <PageContainer>
      <ContentContainer>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <BackButton to="/">
            <ArrowLeft size={18} />
            Volver a búsqueda
          </BackButton>

          <DocumentHeader>
            <DocumentTitle>{document.title}</DocumentTitle>
            
            <DocumentMetadata>
              <MetadataItem>
                <FileText size={16} />
                {document.document_type || 'text'}
              </MetadataItem>
              
              {document.metadata?.category && (
                <MetadataItem>
                  <Tag size={16} />
                  {document.metadata.category}
                </MetadataItem>
              )}
              
              {document.metadata?.tags && document.metadata.tags.length > 0 && (
                <MetadataItem>
                  <Hash size={16} />
                  {document.metadata.tags.slice(0, 3).join(', ')}
                </MetadataItem>
              )}
              
              {document.created_at && (
                <MetadataItem>
                  <Calendar size={16} />
                  {formatDate(document.created_at)}
                </MetadataItem>
              )}
            </DocumentMetadata>

            <DocumentActions>
              <ActionButton onClick={handleCopyContent}>
                {copied ? <Check size={16} /> : <Copy size={16} />}
                {copied ? 'Copiado' : 'Copiar contenido'}
              </ActionButton>
              
              <ActionButton onClick={handleCopyLink}>
                <ExternalLink size={16} />
                Copiar enlace
              </ActionButton>
            </DocumentActions>
          </DocumentHeader>

          <DocumentContent>
            <ContentHeader>
              <ContentTitle>Contenido del Documento</ContentTitle>
              <ContentStats>
                <span>{wordCount.toLocaleString()} palabras</span>
                <span>{charCount.toLocaleString()} caracteres</span>
              </ContentStats>
            </ContentHeader>

            <ContentBody>
              {document.document_type === 'markdown' ? (
                <ReactMarkdown>{document.content}</ReactMarkdown>
              ) : (
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  {document.content}
                </div>
              )}
            </ContentBody>
          </DocumentContent>
        </motion.div>
      </ContentContainer>
    </PageContainer>
  );
};

export default DocumentPage;



























