'use client';

import { useState, useCallback, useRef, type DragEvent, type ChangeEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Image as ImageIcon, Link as LinkIcon, X, Camera } from 'lucide-react';
import { Button } from '@/src/components/ui/Button';
import { Input } from '@/src/components/ui/Input';

interface ImageUploaderProps {
    onImageSelect: (imageData: string, imageUrl?: string) => void;
    onClear?: () => void;
    isLoading?: boolean;
    maxSizeMB?: number;
}

type UploadMode = 'upload' | 'url';

export const ImageUploader = ({
    onImageSelect,
    onClear,
    isLoading = false,
    maxSizeMB = 10,
}: ImageUploaderProps) => {
    const [mode, setMode] = useState<UploadMode>('upload');
    const [preview, setPreview] = useState<string | null>(null);
    const [url, setUrl] = useState('');
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = useCallback((file: File) => {
        setError(null);

        // Validate file type
        if (!file.type.startsWith('image/')) {
            setError('Please select an image file');
            return;
        }

        // Validate file size
        const maxBytes = maxSizeMB * 1024 * 1024;
        if (file.size > maxBytes) {
            setError(`Image must be smaller than ${maxSizeMB}MB`);
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const result = e.target?.result as string;
            setPreview(result);
            // Extract base64 data (remove data:image/xxx;base64, prefix)
            const base64Data = result.split(',')[1];
            onImageSelect(base64Data);
        };
        reader.onerror = () => {
            setError('Failed to read image file');
        };
        reader.readAsDataURL(file);
    }, [maxSizeMB, onImageSelect]);

    const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    }, [handleFileSelect]);

    const handleInputChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFileSelect(files[0]);
        }
    }, [handleFileSelect]);

    const handleUrlSubmit = useCallback(() => {
        if (!url.trim()) {
            setError('Please enter an image URL');
            return;
        }

        try {
            new URL(url);
            setPreview(url);
            onImageSelect('', url);
            setError(null);
        } catch {
            setError('Please enter a valid URL');
        }
    }, [url, onImageSelect]);

    const handleClear = useCallback(() => {
        setPreview(null);
        setUrl('');
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
        onClear?.();
    }, [onClear]);

    const handleClickUpload = () => {
        fileInputRef.current?.click();
    };

    const handleUrlChange = (e: ChangeEvent<HTMLInputElement>) => {
        setUrl(e.target.value);
    };

    const handleKeyDownUrlSubmit = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleUrlSubmit();
        }
    };

    return (
        <div className="w-full">
            {/* Mode Toggle */}
            <div className="flex items-center gap-2 mb-4">
                <button
                    type="button"
                    onClick={() => setMode('upload')}
                    className={`
            flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
            transition-all duration-200
            ${mode === 'upload'
                            ? 'bg-primary/20 text-primary'
                            : 'text-text-muted hover:text-text hover:bg-card'
                        }
          `}
                    tabIndex={0}
                    aria-pressed={mode === 'upload'}
                >
                    <Upload className="w-4 h-4" aria-hidden="true" />
                    Upload
                </button>
                <button
                    type="button"
                    onClick={() => setMode('url')}
                    className={`
            flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
            transition-all duration-200
            ${mode === 'url'
                            ? 'bg-primary/20 text-primary'
                            : 'text-text-muted hover:text-text hover:bg-card'
                        }
          `}
                    tabIndex={0}
                    aria-pressed={mode === 'url'}
                >
                    <LinkIcon className="w-4 h-4" aria-hidden="true" />
                    URL
                </button>
            </div>

            {/* Upload Area or URL Input */}
            <AnimatePresence mode="wait">
                {preview ? (
                    <motion.div
                        key="preview"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="relative rounded-2xl overflow-hidden border border-primary/30"
                    >
                        <img
                            src={preview}
                            alt="Selected product"
                            className="w-full h-64 object-contain bg-card"
                        />
                        <button
                            type="button"
                            onClick={handleClear}
                            className="absolute top-3 right-3 p-2 rounded-full bg-background/80 backdrop-blur-sm hover:bg-background transition-colors"
                            aria-label="Clear image"
                            tabIndex={0}
                        >
                            <X className="w-5 h-5 text-text" aria-hidden="true" />
                        </button>
                    </motion.div>
                ) : mode === 'upload' ? (
                    <motion.div
                        key="upload"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={handleClickUpload}
                        onKeyDown={(e) => e.key === 'Enter' && handleClickUpload()}
                        className={`
              relative flex flex-col items-center justify-center gap-4
              h-64 rounded-2xl border-2 border-dashed
              cursor-pointer transition-all duration-300
              ${isDragging
                                ? 'border-primary bg-primary/10'
                                : 'border-white/20 hover:border-primary/50 hover:bg-card/50'
                            }
            `}
                        role="button"
                        tabIndex={0}
                        aria-label="Drop an image here or click to upload"
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleInputChange}
                            className="hidden"
                            aria-hidden="true"
                        />
                        <motion.div
                            animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
                            className="p-4 rounded-full bg-primary/20"
                        >
                            {isDragging ? (
                                <Camera className="w-8 h-8 text-primary" aria-hidden="true" />
                            ) : (
                                <ImageIcon className="w-8 h-8 text-primary" aria-hidden="true" />
                            )}
                        </motion.div>
                        <div className="text-center">
                            <p className="text-text font-medium">
                                {isDragging ? 'Drop your image here' : 'Drag & drop an image'}
                            </p>
                            <p className="text-sm text-text-muted mt-1">
                                or click to browse (max {maxSizeMB}MB)
                            </p>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="url"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="space-y-4"
                    >
                        <Input
                            type="url"
                            value={url}
                            onChange={handleUrlChange}
                            onKeyDown={handleKeyDownUrlSubmit}
                            placeholder="https://example.com/product-image.jpg"
                            leftIcon={<LinkIcon className="w-4 h-4" />}
                            error={error || undefined}
                        />
                        <Button
                            onClick={handleUrlSubmit}
                            disabled={!url.trim()}
                            isLoading={isLoading}
                            className="w-full"
                        >
                            Load Image
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Error Display */}
            {error && mode === 'upload' && (
                <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-3 text-sm text-accent-error"
                    role="alert"
                >
                    {error}
                </motion.p>
            )}
        </div>
    );
};

export default ImageUploader;
