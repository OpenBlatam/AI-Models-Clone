'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Sparkles, Search, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/Card';
import { Button } from '@/src/components/ui/Button';
import { Input } from '@/src/components/ui/Input';
import { Alert } from '@/src/components/ui/Alert';
import { LoadingPulse } from '@/src/components/ui/LoadingSpinner';
import { Recommendations } from '@/src/components/features/Recommendations';
import { useRecommendations } from '@/src/hooks/useRecommendations';
import type { ProductInfo, RecommendationType } from '@/src/types/api';

const recommendationTypes: { value: RecommendationType; label: string; description: string }[] = [
    { value: 'alternatives', label: 'Alternatives', description: 'Similar products from different brands' },
    { value: 'upgrades', label: 'Upgrades', description: 'Premium options with better features' },
    { value: 'accessories', label: 'Accessories', description: 'Compatible add-ons and extras' },
    { value: 'bundle', label: 'Bundles', description: 'Save more with combined offers' },
];

function RecommendationsPageContent() {
    const searchParams = useSearchParams();
    const { getRecommendations, result, isLoading, isPolling, error, reset } = useRecommendations();

    const [productName, setProductName] = useState('');
    const [productBrand, setProductBrand] = useState('');
    const [budget, setBudget] = useState('');
    const [recommendationType, setRecommendationType] = useState<RecommendationType>('alternatives');

    // Load product info from URL params if available
    useEffect(() => {
        const productParam = searchParams.get('product');
        if (productParam) {
            try {
                const productInfo: ProductInfo = JSON.parse(productParam);
                setProductName(productInfo.name || '');
                setProductBrand(productInfo.brand || '');
            } catch {
                // Invalid JSON, ignore
            }
        }
    }, [searchParams]);

    const handleSearch = async () => {
        if (!productName.trim()) return;

        const productInfo: ProductInfo = {
            name: productName,
            brand: productBrand || undefined,
        };

        await getRecommendations({
            product_info: productInfo,
            recommendation_type: recommendationType,
            budget: budget ? parseFloat(budget) : undefined,
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
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/20 text-amber-400 text-sm font-medium mb-4">
                    <Sparkles className="w-4 h-4" aria-hidden="true" />
                    Smart Recommendations
                </div>
                <h1 className="text-3xl md:text-4xl font-bold mb-4">
                    Get Product Recommendations
                </h1>
                <p className="text-text-muted">
                    Discover alternatives, upgrades, and accessories tailored to your needs
                    with AI-powered recommendations.
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
                            <CardTitle>What product are you looking for?</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <Input
                                    label="Product Name"
                                    value={productName}
                                    onChange={(e) => setProductName(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., MacBook Pro"
                                    leftIcon={<Search className="w-4 h-4" />}
                                />
                                <Input
                                    label="Brand (optional)"
                                    value={productBrand}
                                    onChange={(e) => setProductBrand(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., Apple"
                                />
                                <Input
                                    label="Budget (optional)"
                                    type="number"
                                    value={budget}
                                    onChange={(e) => setBudget(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., 25000"
                                    leftIcon={<DollarSign className="w-4 h-4" />}
                                />
                            </div>

                            {/* Recommendation Type Selection */}
                            <div>
                                <label className="block text-sm font-medium text-text mb-3">
                                    Recommendation Type
                                </label>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    {recommendationTypes.map((type) => (
                                        <button
                                            key={type.value}
                                            onClick={() => setRecommendationType(type.value)}
                                            className={`
                        p-4 rounded-xl text-left transition-all duration-200
                        ${recommendationType === type.value
                                                    ? 'bg-primary/20 border-2 border-primary'
                                                    : 'bg-card border-2 border-transparent hover:border-primary/30'
                                                }
                      `}
                                            tabIndex={0}
                                            aria-pressed={recommendationType === type.value}
                                        >
                                            <p className="font-medium text-text">{type.label}</p>
                                            <p className="text-xs text-text-muted mt-1">{type.description}</p>
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
                                {isLoading || isPolling ? 'Finding Recommendations...' : 'Get Recommendations'}
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
                            title="Search Failed"
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
                            <LoadingPulse label="Finding recommendations..." />
                        </CardContent>
                    </Card>
                ) : result ? (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-6"
                    >
                        {/* Summary */}
                        <Card variant="glass">
                            <CardContent>
                                <p className="text-text leading-relaxed whitespace-pre-wrap">
                                    {result.recommendations}
                                </p>
                            </CardContent>
                        </Card>

                        {/* Recommendations Grid */}
                        {result.items && result.items.length > 0 && (
                            <Recommendations
                                recommendations={result.items}
                                type={result.recommendation_type}
                            />
                        )}
                    </motion.div>
                ) : (
                    <Card variant="bordered" className="py-20">
                        <CardContent className="text-center">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-500/20 flex items-center justify-center">
                                <Sparkles className="w-8 h-8 text-amber-400" aria-hidden="true" />
                            </div>
                            <h3 className="text-lg font-semibold text-text mb-2">
                                Get Personalized Recommendations
                            </h3>
                            <p className="text-text-muted text-sm">
                                Enter a product to discover alternatives, upgrades, and accessories.
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}

export default function RecommendationsPage() {
    return (
        <Suspense fallback={<div className="container mx-auto px-4 py-12"><LoadingPulse /></div>}>
            <RecommendationsPageContent />
        </Suspense>
    );
}
