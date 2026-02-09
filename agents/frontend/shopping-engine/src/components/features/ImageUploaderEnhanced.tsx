'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Enhanced Image Uploader with react-dropzone
// ═══════════════════════════════════════════════════════════════════════════════

import { useState, useCallback } from 'react';
import { useDropzone, type FileRejection } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Image as ImageIcon, Link as LinkIcon, X, Camera, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import { Button } from '@/src/components/ui/Button';
import { Input } from '@/src/components/ui/Input';
import { showToast } from '@/src/providers/ToastProvider';

interface ImageUploaderProps {
    onImageSelect: (imageData: string, imageUrl?: string) => void;
    onClear?: () => void;
    isLoading?: boolean;
    maxSizeMB?: number;
    acceptedFormats?: string[];
}

type UploadMode = 'upload' | 'url';

export const ImageUploaderEnhanced = ({
    onImageSelect,
    onClear,
    isLoading = false,
    maxSizeMB = 10,
    acceptedFormats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
}: ImageUploaderProps) => {
    const [mode, setMode] = useState<UploadMode>('upload');
    const [preview, setPreview] = useState<string | null>(null);
    const [url, setUrl] = useState('');
    const [error, setError] = useState<string | null>(null);

    const maxBytes = maxSizeMB * 1024 * 1024;

    const handleFileAccepted = useCallback((file: File) => {
        setError(null);

        const reader = new FileReader();
        reader.onload = (e) => {
            const result = e.target?.result as string;
            setPreview(result);
            // Extract base64 data (remove data:image/xxx;base64, prefix)
            const base64Data = result.split(',')[1];
            onImageSelect(base64Data);
            showToast.success('Image loaded successfully!');
        };
        reader.onerror = () => {
            setError('Failed to read image file');
            showToast.error('Failed to read image file');
        };
        reader.readAsDataURL(file);
    }, [onImageSelect]);

    const handleFileRejection = useCallback((rejections: FileRejection[]) => {
        const rejection = rejections[0];
        const errorCode = rejection?.errors[0]?.code;

        let message = 'File rejected';
        if (errorCode === 'file-too-large') {
            message = `File is too large. Maximum size is ${maxSizeMB}MB`;
        } else if (errorCode === 'file-invalid-type') {
            message = 'Invalid file type. Please upload an image';
        }

        setError(message);
        showToast.error(message);
    }, [maxSizeMB]);

    const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
        onDropAccepted: (files) => handleFileAccepted(files[0]),
        onDropRejected: handleFileRejection,
        accept: acceptedFormats.reduce((acc, format) => ({ ...acc, [format]: [] }), {}),
        maxSize: maxBytes,
        multiple: false,
        disabled: isLoading,
    });

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
            showToast.success('Image URL loaded!');
        } catch {
            setError('Please enter a valid URL');
            showToast.error('Invalid URL format');
        }
    }, [url, onImageSelect]);

    const handleClear = useCallback(() => {
        setPreview(null);
        setUrl('');
        setError(null);
        onClear?.();
    }, [onClear]);

    const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUrl(e.target.value);
    };

    const handleKeyDownUrlSubmit = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleUrlSubmit();
        }
    };

    const dropzoneClassName = clsx(
        'relative flex flex-col items-center justify-center gap-4',
        'h-64 rounded-2xl border-2 border-dashed',
        'cursor-pointer transition-all duration-300',
        {
            'border-primary bg-primary/10': isDragAccept || isDragActive,
            'border-accent-error bg-accent-error/10': isDragReject,
            'border-white/20 hover:border-primary/50 hover:bg-card/50': !isDragActive && !isDragReject,
            'opacity-50 cursor-not-allowed': isLoading,
        }
    );

    return (
        <div className="w-full">
            {/* Mode Toggle */}
            <div className="flex items-center gap-2 mb-4">
                <button
                    type="button"
                    onClick={() => setMode('upload')}
                    className={clsx(
                        'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium',
                        'transition-all duration-200',
                        mode === 'upload'
                            ? 'bg-primary/20 text-primary'
                            : 'text-text-muted hover:text-text hover:bg-card'
                    )}
                    tabIndex={0}
                    aria-pressed={mode === 'upload'}
                >
                    <Upload className="w-4 h-4" aria-hidden="true" />
                    Upload
                </button>
                <button
                    type="button"
                    onClick={() => setMode('url')}
                    className={clsx(
                        'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium',
                        'transition-all duration-200',
                        mode === 'url'
                            ? 'bg-primary/20 text-primary'
                            : 'text-text-muted hover:text-text hover:bg-card'
                    )}
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
                            className={clsx(
                                'absolute top-3 right-3 p-2 rounded-full',
                                'bg-background/80 backdrop-blur-sm hover:bg-background transition-colors'
                            )}
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
                    >
                        <div
                            {...getRootProps({ className: dropzoneClassName })}
                            role="button"
                            aria-label="Drop an image here or click to upload"
                        >
                            <input {...getInputProps()} aria-hidden="true" />
                            <motion.div
                                animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
                                className={clsx(
                                    'p-4 rounded-full',
                                    isDragReject ? 'bg-accent-error/20' : 'bg-primary/20'
                                )}
                            >
                                {isDragReject ? (
                                    <AlertCircle className="w-8 h-8 text-accent-error" aria-hidden="true" />
                                ) : isDragActive ? (
                                    <Camera className="w-8 h-8 text-primary" aria-hidden="true" />
                                ) : (
                                    <ImageIcon className="w-8 h-8 text-primary" aria-hidden="true" />
                                )}
                            </motion.div>
                            <div className="text-center">
                                <p className={clsx(
                                    'font-medium',
                                    isDragReject ? 'text-accent-error' : 'text-text'
                                )}>
                                    {isDragReject
                                        ? 'Invalid file type'
                                        : isDragActive
                                            ? 'Drop your image here'
                                            : 'Drag & drop an image'}
                                </p>
                                <p className="text-sm text-text-muted mt-1">
                                    {isDragReject
                                        ? 'Only images are allowed'
                                        : `or click to browse (max ${maxSizeMB}MB)`}
                                </p>
                            </div>
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
                    className="mt-3 text-sm text-accent-error flex items-center gap-2"
                    role="alert"
                >
                    <AlertCircle className="w-4 h-4" aria-hidden="true" />
                    {error}
                </motion.p>
            )}
        </div>
    );
};

export default ImageUploaderEnhanced;
