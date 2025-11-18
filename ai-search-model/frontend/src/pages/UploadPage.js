import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useMutation, useQueryClient } from 'react-query';
import { Upload, FileText, CheckCircle, AlertCircle, X } from 'lucide-react';
import toast from 'react-hot-toast';

import { apiService } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const PageContainer = styled.div`
  min-height: 100vh;
  background: ${props => props.theme.colors.background};
  padding-top: 100px;
`;

const ContentContainer = styled.div`
  max-width: 800px;
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

const UploadSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 2px dashed ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: ${props => props.theme.spacing.xxl};
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: ${props => props.theme.spacing.xl};

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.theme.colors.primary}05;
  }

  &.dragover {
    border-color: ${props => props.theme.colors.primary};
    background: ${props => props.theme.colors.primary}10;
    transform: scale(1.02);
  }
`;

const UploadIcon = styled.div`
  width: 80px;
  height: 80px;
  background: ${props => props.theme.colors.primary}20;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.primary};
`;

const UploadText = styled.div`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const UploadSubtext = styled.div`
  font-size: 1rem;
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const FileInput = styled.input`
  display: none;
`;

const UploadButton = styled.button`
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  margin: 0 auto;

  &:hover {
    background: ${props => props.theme.colors.primaryDark};
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const FormSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const FormTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const FormGroup = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const Input = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  color: ${props => props.theme.colors.text};
  background: ${props => props.theme.colors.surface};
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 200px;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  color: ${props => props.theme.colors.text};
  background: ${props => props.theme.colors.surface};
  resize: vertical;
  font-family: inherit;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  color: ${props => props.theme.colors.text};
  background: ${props => props.theme.colors.surface};
  cursor: pointer;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary}20;
  }

  option {
    background: ${props => props.theme.colors.surface};
    color: ${props => props.theme.colors.text};
  }
`;

const FilePreview = styled.div`
  background: ${props => props.theme.colors.surfaceDark};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const FileIcon = styled.div`
  color: ${props => props.theme.colors.primary};
`;

const FileDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const FileName = styled.div`
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const FileSize = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const RemoveFileButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.colors.error};
  cursor: pointer;
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.colors.error}20;
  }
`;

const UploadPage = () => {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    document_type: 'text',
    metadata: {}
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const queryClient = useQueryClient();

  // Mutation para crear documento
  const createDocumentMutation = useMutation(apiService.createDocument, {
    onSuccess: (data) => {
      toast.success('Documento indexado exitosamente');
      queryClient.invalidateQueries(['statistics']);
      queryClient.invalidateQueries(['documents']);
      resetForm();
    },
    onError: (error) => {
      toast.error(`Error al indexar documento: ${error.message}`);
    }
  });

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      document_type: 'text',
      metadata: {}
    });
    setSelectedFile(null);
  };

  const handleFileSelect = (file) => {
    if (file) {
      setSelectedFile(file);
      
      // Leer contenido del archivo si es texto
      if (file.type.startsWith('text/') || file.type === 'application/json') {
        const reader = new FileReader();
        reader.onload = (e) => {
          setFormData(prev => ({
            ...prev,
            title: file.name,
            content: e.target.result,
            document_type: file.type === 'application/json' ? 'json' : 'text'
          }));
        };
        reader.readAsText(file);
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.content.trim()) {
      toast.error('Por favor completa todos los campos requeridos');
      return;
    }

    createDocumentMutation.mutate(formData);
  };

  const removeFile = () => {
    setSelectedFile(null);
    setFormData(prev => ({
      ...prev,
      title: '',
      content: '',
      document_type: 'text'
    }));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <PageContainer>
      <ContentContainer>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <PageTitle>Subir Documento</PageTitle>
          <PageSubtitle>
            Indexa un nuevo documento en la base de datos para que sea buscable
            usando inteligencia artificial
          </PageSubtitle>

          {/* Sección de subida de archivos */}
          <UploadSection
            className={isDragOver ? 'dragover' : ''}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <UploadIcon>
              <Upload size={40} />
            </UploadIcon>
            <UploadText>
              {selectedFile ? 'Archivo seleccionado' : 'Arrastra un archivo aquí o haz clic para seleccionar'}
            </UploadText>
            <UploadSubtext>
              Soporta archivos de texto, Markdown, HTML y JSON
            </UploadSubtext>
            <FileInput
              id="file-input"
              type="file"
              accept=".txt,.md,.html,.json"
              onChange={handleFileInputChange}
            />
            <UploadButton type="button">
              <Upload size={18} />
              Seleccionar Archivo
            </UploadButton>
          </UploadSection>

          {/* Vista previa del archivo */}
          {selectedFile && (
            <FilePreview>
              <FileInfo>
                <FileIcon>
                  <FileText size={24} />
                </FileIcon>
                <FileDetails>
                  <FileName>{selectedFile.name}</FileName>
                  <FileSize>{formatFileSize(selectedFile.size)}</FileSize>
                </FileDetails>
              </FileInfo>
              <RemoveFileButton onClick={removeFile}>
                <X size={20} />
              </RemoveFileButton>
            </FilePreview>
          )}

          {/* Formulario de documento */}
          <FormSection>
            <FormTitle>Información del Documento</FormTitle>
            <form onSubmit={handleSubmit}>
              <FormGroup>
                <Label htmlFor="title">Título *</Label>
                <Input
                  id="title"
                  name="title"
                  type="text"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Título del documento"
                  required
                />
              </FormGroup>

              <FormGroup>
                <Label htmlFor="document_type">Tipo de Documento</Label>
                <Select
                  id="document_type"
                  name="document_type"
                  value={formData.document_type}
                  onChange={handleInputChange}
                >
                  <option value="text">Texto</option>
                  <option value="markdown">Markdown</option>
                  <option value="html">HTML</option>
                  <option value="json">JSON</option>
                </Select>
              </FormGroup>

              <FormGroup>
                <Label htmlFor="content">Contenido *</Label>
                <TextArea
                  id="content"
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  placeholder="Contenido del documento..."
                  required
                />
              </FormGroup>

              <UploadButton
                type="submit"
                disabled={createDocumentMutation.isLoading}
              >
                {createDocumentMutation.isLoading ? (
                  <>
                    <LoadingSpinner size="small" />
                    Indexando...
                  </>
                ) : (
                  <>
                    <CheckCircle size={18} />
                    Indexar Documento
                  </>
                )}
              </UploadButton>
            </form>
          </FormSection>
        </motion.div>
      </ContentContainer>
    </PageContainer>
  );
};

export default UploadPage;



























