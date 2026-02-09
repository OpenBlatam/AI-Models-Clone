'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { ShoppingCart, Search, MapPin } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/Card';
import { Button } from '@/src/components/ui/Button';
import { Input } from '@/src/components/ui/Input';
import { Alert } from '@/src/components/ui/Alert';
import { LoadingPulse } from '@/src/components/ui/LoadingSpinner';
import { PurchaseOptions } from '@/src/components/features/PurchaseOptions';
import { usePurchaseOptions } from '@/src/hooks/usePurchaseOptions';
import type { ProductInfo } from '@/src/types/api';

function PurchasePageContent() {
    const searchParams = useSearchParams();
    const { findOptions, result, isLoading, isPolling, error, reset } = usePurchaseOptions();

    const [productName, setProductName] = useState('');
    const [productBrand, setProductBrand] = useState('');
    const [productCategory, setProductCategory] = useState('');
    const [country, setCountry] = useState('México');

    // Load product info from URL params if available
    useEffect(() => {
        const productParam = searchParams.get('product');
        if (productParam) {
            try {
                const productInfo: ProductInfo = JSON.parse(productParam);
                setProductName(productInfo.name || '');
                setProductBrand(productInfo.brand || '');
                setProductCategory(productInfo.category || '');
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
            category: productCategory || undefined,
        };

        await findOptions({
            product_info: productInfo,
            country,
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
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/20 text-blue-400 text-sm font-medium mb-4">
                    <ShoppingCart className="w-4 h-4" aria-hidden="true" />
                    Purchase Options
                </div>
                <h1 className="text-3xl md:text-4xl font-bold mb-4">
                    Find Where to Buy
                </h1>
                <p className="text-text-muted">
                    Discover the best places to purchase your product with price estimates,
                    availability, and vendor recommendations.
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
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <Input
                                    label="Product Name"
                                    value={productName}
                                    onChange={(e) => setProductName(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., iPhone 15 Pro"
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
                                    label="Category (optional)"
                                    value={productCategory}
                                    onChange={(e) => setProductCategory(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., Electronics"
                                />
                                <Input
                                    label="Country"
                                    value={country}
                                    onChange={(e) => setCountry(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., México"
                                    leftIcon={<MapPin className="w-4 h-4" />}
                                />
                            </div>
                            <Button
                                onClick={handleSearch}
                                disabled={!productName.trim() || isLoading}
                                isLoading={isLoading || isPolling}
                                className="w-full mt-4"
                            >
                                {isLoading || isPolling ? 'Searching...' : 'Find Purchase Options'}
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
                            <LoadingPulse label="Finding purchase options..." />
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
                                    {result.purchase_options}
                                </p>
                            </CardContent>
                        </Card>

                        {/* Options List */}
                        {result.options && result.options.length > 0 && (
                            <PurchaseOptions
                                options={result.options}
                                recommendedVendor={result.recommended_option?.vendor}
                            />
                        )}
                    </motion.div>
                ) : (
                    <Card variant="bordered" className="py-20">
                        <CardContent className="text-center">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-500/20 flex items-center justify-center">
                                <ShoppingCart className="w-8 h-8 text-blue-400" aria-hidden="true" />
                            </div>
                            <h3 className="text-lg font-semibold text-text mb-2">
                                Search for a Product
                            </h3>
                            <p className="text-text-muted text-sm">
                                Enter a product name to find the best places to buy it.
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}

export default function PurchasePage() {
    return (
        <Suspense fallback={<div className="container mx-auto px-4 py-12"><LoadingPulse /></div>}>
            <PurchasePageContent />
        </Suspense>
    );
}
