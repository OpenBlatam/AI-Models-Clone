'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

interface ImageUploadProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  maxSize?: number;
  currentFile?: File | null;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  onFileSelect,
  accept = 'image/*',
  maxSize = 10 * 1024 * 1024, // 10MB
  currentFile,
}) => {
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        if (file.size > maxSize) {
          setError(`El archivo es demasiado grande. Máximo ${maxSize / 1024 / 1024}MB`);
          return;
        }
        setError(null);
        setPreview(URL.createObjectURL(file));
        onFileSelect(file);
      }
    },
    [onFileSelect, maxSize]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: accept ? { [accept]: [] } : undefined,
    maxFiles: 1,
    maxSize,
  });

  const removeFile = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setPreview(null);
    setError(null);
    onFileSelect(null as any);
  };

  return (
    <div className="w-full">
      {!preview ? (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200
            ${
              isDragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }
            ${error ? 'border-red-500 bg-red-50' : ''}
          `}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          {isDragActive ? (
            <p className="text-primary-600 font-medium">
              Suelta la imagen aquí...
            </p>
          ) : (
            <>
              <p className="text-gray-600 mb-2">
                Arrastra una imagen aquí o haz clic para seleccionar
              </p>
              <p className="text-sm text-gray-500">
                Formatos: JPG, PNG, WEBP (máx. {maxSize / 1024 / 1024}MB)
              </p>
            </>
          )}
        </div>
      ) : (
        <Card className="relative">
          <div className="relative">
            <img
              src={preview}
              alt="Preview"
              className="w-full h-auto rounded-lg max-h-96 object-contain"
            />
            <button
              onClick={removeFile}
              className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-2 hover:bg-red-600 transition-colors"
              aria-label="Eliminar imagen"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center text-sm text-gray-600">
              <ImageIcon className="h-4 w-4 mr-2" />
              {currentFile?.name || 'Imagen seleccionada'}
            </div>
            <Button variant="outline" size="sm" onClick={removeFile}>
              Cambiar imagen
            </Button>
          </div>
        </Card>
      )}
      {error && (
        <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

