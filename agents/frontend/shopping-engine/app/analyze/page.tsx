'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ScanSearch, ShoppingCart, Sparkles, ArrowRight, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/Card';
import { Button } from '@/src/components/ui/Button';
import { Alert } from '@/src/components/ui/Alert';
import { LoadingPulse } from '@/src/components/ui/LoadingSpinner';
import { ImageUploader } from '@/src/components/features/ImageUploader';
import { useAnalyzeProduct } from '@/src/hooks/useAnalyzeProduct';
import type { ProductInfo } from '@/src/types/api';
import Link from 'next/link';

export default function AnalyzePage() {
    const { analyze, result, isLoading, isPolling, error, reset } = useAnalyzeProduct();
    const [additionalContext, setAdditionalContext] = useState('');
    const [imageReady, setImageReady] = useState(false);
    const [currentImageData, setCurrentImageData] = useState<string>('');
    const [currentImageUrl, setCurrentImageUrl] = useState<string>('');

    const handleImageSelect = (imageData: string, imageUrl?: string) => {
        setCurrentImageData(imageData);
        setCurrentImageUrl(imageUrl || '');
        setImageReady(true);
    };

    const handleClear = () => {
        setImageReady(false);
        setCurrentImageData('');
        setCurrentImageUrl('');
        reset();
    };

    const handleAnalyze = async () => {
        await analyze({
            image_data: currentImageData || undefined,
            image_url: currentImageUrl || undefined,
            additional_context: additionalContext || undefined,
            direct: true,
        });
    };

    const handleContextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setAdditionalContext(e.target.value);
    };

    // Extract product info for linking to other pages
    const productInfo: ProductInfo | null = result?.product_info || null;

    return (
        <div className="container mx-auto px-4 py-12">
            {/* Header */}
            <motion.div
                className="max-w-3xl mx-auto text-center mb-12"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/20 text-primary text-sm font-medium mb-4">
                    <ScanSearch className="w-4 h-4" aria-hidden="true" />
                    AI Product Analysis
                </div>
                <h1 className="text-3xl md:text-4xl font-bold mb-4">
                    Analyze Any Product
                </h1>
                <p className="text-text-muted">
                    Upload a product image or paste an image URL to get instant AI-powered analysis,
                    including product identification, features, and estimated pricing.
                </p>
            </motion.div>

            <div className="max-w-4xl mx-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Upload Section */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <Card variant="bordered">
                            <CardHeader>
                                <CardTitle>Upload Product Image</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <ImageUploader
                                    onImageSelect={handleImageSelect}
                                    onClear={handleClear}
                                    isLoading={isLoading}
                                />

                                {/* Additional Context */}
                                <div>
                                    <label
                                        htmlFor="context"
                                        className="block text-sm font-medium text-text mb-2"
                                    >
                                        Additional Context (optional)
                                    </label>
                                    <textarea
                                        id="context"
                                        value={additionalContext}
                                        onChange={handleContextChange}
                                        placeholder="E.g., 'I think this is a vintage watch from the 1970s'"
                                        className="w-full px-4 py-3 rounded-xl bg-card border border-white/10 text-text placeholder:text-text-muted/50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary/50 transition-all duration-200 resize-none"
                                        rows={3}
                                    />
                                </div>

                                <Button
                                    onClick={handleAnalyze}
                                    disabled={!imageReady || isLoading}
                                    isLoading={isLoading || isPolling}
                                    className="w-full"
                                    rightIcon={!isLoading && <ArrowRight className="w-5 h-5" />}
                                >
                                    {isLoading || isPolling ? 'Analyzing...' : 'Analyze Product'}
                                </Button>

                                {error && (
                                    <Alert
                                        variant="error"
                                        title="Analysis Failed"
                                        description={error}
                                        isClosable
                                        onClose={reset}
                                    />
                                )}
                            </CardContent>
                        </Card>
                    </motion.div>

                    {/* Results Section */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <AnimatePresence mode="wait">
                            {isLoading || isPolling ? (
                                <motion.div
                                    key="loading"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                >
                                    <Card variant="bordered" className="h-full flex items-center justify-center min-h-[400px]">
                                        <CardContent>
                                            <LoadingPulse label="Analyzing your product..." />
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            ) : result ? (
                                <motion.div
                                    key="result"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                >
                                    <Card variant="glass">
                                        <CardHeader>
                                            <CardTitle className="flex items-center gap-2">
                                                <ScanSearch className="w-5 h-5 text-primary" />
                                                Analysis Results
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-6">
                                            {/* Main Analysis */}
                                            <div>
                                                <p className="text-text whitespace-pre-wrap leading-relaxed">
                                                    {result.analysis}
                                                </p>
                                            </div>

                                            {/* Product Info */}
                                            {productInfo && (
                                                <div className="space-y-3 p-4 rounded-xl bg-card">
                                                    {productInfo.name && (
                                                        <div>
                                                            <span className="text-text-muted text-sm">Product Name</span>
                                                            <p className="text-text font-semibold">{productInfo.name}</p>
                                                        </div>
                                                    )}
                                                    {productInfo.brand && (
                                                        <div>
                                                            <span className="text-text-muted text-sm">Brand</span>
                                                            <p className="text-text font-medium">{productInfo.brand}</p>
                                                        </div>
                                                    )}
                                                    {productInfo.category && (
                                                        <div>
                                                            <span className="text-text-muted text-sm">Category</span>
                                                            <p className="text-text">{productInfo.category}</p>
                                                        </div>
                                                    )}
                                                    {productInfo.estimated_price && (
                                                        <div>
                                                            <span className="text-text-muted text-sm">Est. Price</span>
                                                            <p className="text-lg font-bold text-accent-success">
                                                                ${productInfo.estimated_price.toLocaleString()} {productInfo.currency || 'MXN'}
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                            )}

                                            {/* Confidence */}
                                            {result.confidence && (
                                                <div className="flex items-center gap-2">
                                                    <span className="text-text-muted text-sm">Confidence:</span>
                                                    <div className="flex-1 h-2 bg-card rounded-full overflow-hidden">
                                                        <motion.div
                                                            className="h-full bg-gradient-to-r from-primary to-secondary"
                                                            initial={{ width: 0 }}
                                                            animate={{ width: `${result.confidence * 100}%` }}
                                                            transition={{ duration: 0.5, delay: 0.2 }}
                                                        />
                                                    </div>
                                                    <span className="text-sm font-medium text-text">
                                                        {Math.round(result.confidence * 100)}%
                                                    </span>
                                                </div>
                                            )}

                                            {/* Actions */}
                                            <div className="flex flex-col gap-3 pt-4 border-t border-white/10">
                                                <p className="text-sm text-text-muted">Continue with:</p>
                                                <div className="grid grid-cols-2 gap-3">
                                                    <Link href={`/purchase?product=${encodeURIComponent(JSON.stringify(productInfo))}`}>
                                                        <Button variant="secondary" className="w-full" leftIcon={<ShoppingCart className="w-4 h-4" />}>
                                                            Find Where to Buy
                                                        </Button>
                                                    </Link>
                                                    <Link href={`/recommendations?product=${encodeURIComponent(JSON.stringify(productInfo))}`}>
                                                        <Button variant="secondary" className="w-full" leftIcon={<Sparkles className="w-4 h-4" />}>
                                                            Get Recommendations
                                                        </Button>
                                                    </Link>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="empty"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                >
                                    <Card variant="bordered" className="h-full flex items-center justify-center min-h-[400px]">
                                        <CardContent className="text-center">
                                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 flex items-center justify-center">
                                                <ScanSearch className="w-8 h-8 text-primary" aria-hidden="true" />
                                            </div>
                                            <h3 className="text-lg font-semibold text-text mb-2">
                                                Ready to Analyze
                                            </h3>
                                            <p className="text-text-muted text-sm">
                                                Upload a product image to get started with AI-powered analysis.
                                            </p>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
