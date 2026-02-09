'use client'

import { useRef, useState } from 'react'
import { Upload, X, File as FileIcon } from 'lucide-react'
import { Button } from './ui/button'
import { cn } from '@/lib/utils'

interface FileUploadProps {
  onUpload: (files: File[]) => void
  accept?: string
  multiple?: boolean
  maxSize?: number
  className?: string
}

export function FileUpload({
  onUpload,
  accept,
  multiple = false,
  maxSize,
  className,
}: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const fileArray = Array.from(selectedFiles)
    const validFiles: File[] = []

    for (const file of fileArray) {
      if (maxSize && file.size > maxSize) {
        setError(`El archivo ${file.name} excede el tamaño máximo`)
        continue
      }
      validFiles.push(file)
    }

    if (validFiles.length > 0) {
      setFiles((prev) => (multiple ? [...prev, ...validFiles] : validFiles))
      setError(null)
      onUpload(validFiles)
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          onClick={() => inputRef.current?.click()}
        >
          <Upload className="w-4 h-4 mr-2" />
          Seleccionar archivos
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
        />
      </div>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 bg-gray-50 rounded border"
            >
              <div className="flex items-center gap-2">
                <FileIcon className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{file.name}</span>
                <span className="text-xs text-gray-500">
                  ({(file.size / 1024).toFixed(2)} KB)
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFile(index)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


