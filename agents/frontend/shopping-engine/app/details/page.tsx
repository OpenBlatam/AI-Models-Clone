'use client';

import { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import { FileText, Search, Layers } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/Card';
import { Button } from '@/src/components/ui/Button';
import { Input } from '@/src/components/ui/Input';
import { Alert } from '@/src/components/ui/Alert';
import { LoadingPulse } from '@/src/components/ui/LoadingSpinner';
import { ProductDetails } from '@/src/components/features/ProductDetails';
import { useProductDetails } from '@/src/hooks/useProductDetails';
import type { ProductInfo, DetailLevel } from '@/src/types/api';

const detailLevels: { value: DetailLevel; label: string; description: string }[] = [
    { value: 'basic', label: 'Basic', description: 'Key specifications only' },
    { value: 'complete', label: 'Complete', description: 'Full product information' },
    { value: 'technical', label: 'Technical', description: 'Detailed technical specs' },
];

function DetailsPageContent() {
    const { getDetails, result, isLoading, isPolling, error, reset } = useProductDetails();

    const [productName, setProductName] = useState('');
    const [productBrand, setProductBrand] = useState('');
    const [productModel, setProductModel] = useState('');
    const [detailLevel, setDetailLevel] = useState<DetailLevel>('complete');

    const handleSearch = async () => {
        if (!productName.trim()) return;

        const productInfo: ProductInfo = {
            name: productName,
            brand: productBrand || undefined,
            model: productModel || undefined,
        };

        await getDetails({
            product_info: productInfo,
            detail_level: detailLevel,
            direct: true,
        });
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <div className="container mx-auto px-4 py-12">
            {/* Header */}
            <motion.div
                className="max-w-3xl mx-auto text-center mb-12"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/20 text-violet-400 text-sm font-medium mb-4">
                    <FileText className="w-4 h-4" aria-hidden="true" />
                    Product Details
                </div>
                <h1 className="text-3xl md:text-4xl font-bold mb-4">
                    Get Detailed Product Information
                </h1>
                <p className="text-text-muted">
                    Access comprehensive specifications, materials, dimensions,
                    warranty info, and user reviews summary.
                </p>
            </motion.div>

            <div className="max-w-6xl mx-auto">
                {/* Search Form */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mb-8"
                >
                    <Card variant="bordered">
                        <CardHeader>
                            <CardTitle>Product Information</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <Input
                                    label="Product Name"
                                    value={productName}
                                    onChange={(e) => setProductName(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., PlayStation 5"
                                    leftIcon={<Search className="w-4 h-4" />}
                                />
                                <Input
                                    label="Brand (optional)"
                                    value={productBrand}
                                    onChange={(e) => setProductBrand(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., Sony"
                                />
                                <Input
                                    label="Model (optional)"
                                    value={productModel}
                                    onChange={(e) => setProductModel(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., CFI-1215A"
                                />
                            </div>

                            {/* Detail Level Selection */}
                            <div>
                                <label className="block text-sm font-medium text-text mb-3">
                                    <Layers className="w-4 h-4 inline-block mr-2" aria-hidden="true" />
                                    Detail Level
                                </label>
                                <div className="grid grid-cols-3 gap-3">
                                    {detailLevels.map((level) => (
                                        <button
                                            key={level.value}
                                            onClick={() => setDetailLevel(level.value)}
                                            className={`
                        p-4 rounded-xl text-center transition-all duration-200
                        ${detailLevel === level.value
                                                    ? 'bg-primary/20 border-2 border-primary'
                                                    : 'bg-card border-2 border-transparent hover:border-primary/30'
                                                }
                      `}
                                            tabIndex={0}
                                            aria-pressed={detailLevel === level.value}
                                        >
                                            <p className="font-medium text-text">{level.label}</p>
                                            <p className="text-xs text-text-muted mt-1">{level.description}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <Button
                                onClick={handleSearch}
                                disabled={!productName.trim() || isLoading}
                                isLoading={isLoading || isPolling}
                                className="w-full"
                            >
                                {isLoading || isPolling ? 'Fetching Details...' : 'Get Product Details'}
                            </Button>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Error */}
                {error && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="mb-8"
                    >
                        <Alert
                            variant="error"
                            title="Failed to Get Details"
                            description={error}
                            isClosable
                            onClose={reset}
                        />
                    </motion.div>
                )}

                {/* Results */}
                {(isLoading || isPolling) ? (
                    <Card variant="bordered" className="py-20">
                        <CardContent>
                            <LoadingPulse label="Fetching product details..." />
                        </CardContent>
                    </Card>
                ) : result ? (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <ProductDetails details={result} />
                    </motion.div>
                ) : (
                    <Card variant="bordered" className="py-20">
                        <CardContent className="text-center">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-violet-500/20 flex items-center justify-center">
                                <FileText className="w-8 h-8 text-violet-400" aria-hidden="true" />
                            </div>
                            <h3 className="text-lg font-semibold text-text mb-2">
                                Explore Product Details
                            </h3>
                            <p className="text-text-muted text-sm">
                                Enter a product name to get comprehensive specifications and information.
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}

export default function DetailsPage() {
    return (
        <Suspense fallback={<div className="container mx-auto px-4 py-12"><LoadingPulse /></div>}>
            <DetailsPageContent />
        </Suspense>
    );
}
