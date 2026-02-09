'use client';

import { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, Search, Store } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/Card';
import { Button } from '@/src/components/ui/Button';
import { Input } from '@/src/components/ui/Input';
import { Alert } from '@/src/components/ui/Alert';
import { LoadingPulse } from '@/src/components/ui/LoadingSpinner';
import { PriceComparison } from '@/src/components/features/PriceComparison';
import { useComparePrices } from '@/src/hooks/useComparePrices';
import type { ProductInfo } from '@/src/types/api';

const popularVendors = [
    'Amazon', 'Mercado Libre', 'Liverpool', 'Elektra',
    'Best Buy', 'Walmart', 'Costco', 'Sam\'s Club'
];

function ComparePageContent() {
    const { comparePrices, result, isLoading, isPolling, error, reset } = useComparePrices();

    const [productName, setProductName] = useState('');
    const [productBrand, setProductBrand] = useState('');
    const [selectedVendors, setSelectedVendors] = useState<string[]>([]);

    const handleToggleVendor = (vendor: string) => {
        setSelectedVendors((prev) =>
            prev.includes(vendor)
                ? prev.filter((v) => v !== vendor)
                : [...prev, vendor]
        );
    };

    const handleSearch = async () => {
        if (!productName.trim()) return;

        const productInfo: ProductInfo = {
            name: productName,
            brand: productBrand || undefined,
        };

        await comparePrices({
            product_info: productInfo,
            vendors: selectedVendors.length > 0 ? selectedVendors : undefined,
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
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/20 text-green-400 text-sm font-medium mb-4">
                    <DollarSign className="w-4 h-4" aria-hidden="true" />
                    Price Comparison
                </div>
                <h1 className="text-3xl md:text-4xl font-bold mb-4">
                    Compare Prices Across Vendors
                </h1>
                <p className="text-text-muted">
                    Find the best deals by comparing prices from multiple stores
                    and marketplaces in one place.
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
                            <CardTitle>Product to Compare</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <Input
                                    label="Product Name"
                                    value={productName}
                                    onChange={(e) => setProductName(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., Sony WH-1000XM5"
                                    leftIcon={<Search className="w-4 h-4" />}
                                />
                                <Input
                                    label="Brand (optional)"
                                    value={productBrand}
                                    onChange={(e) => setProductBrand(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="e.g., Sony"
                                />
                            </div>

                            {/* Vendor Selection */}
                            <div>
                                <label className="block text-sm font-medium text-text mb-3">
                                    <Store className="w-4 h-4 inline-block mr-2" aria-hidden="true" />
                                    Filter by Vendors (optional)
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {popularVendors.map((vendor) => (
                                        <button
                                            key={vendor}
                                            onClick={() => handleToggleVendor(vendor)}
                                            className={`
                        px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                        ${selectedVendors.includes(vendor)
                                                    ? 'bg-primary text-white'
                                                    : 'bg-card text-text-muted hover:text-text hover:bg-card-hover'
                                                }
                      `}
                                            tabIndex={0}
                                            aria-pressed={selectedVendors.includes(vendor)}
                                        >
                                            {vendor}
                                        </button>
                                    ))}
                                </div>
                                {selectedVendors.length > 0 && (
                                    <button
                                        onClick={() => setSelectedVendors([])}
                                        className="text-sm text-text-muted hover:text-text mt-2"
                                        tabIndex={0}
                                    >
                                        Clear selection
                                    </button>
                                )}
                            </div>

                            <Button
                                onClick={handleSearch}
                                disabled={!productName.trim() || isLoading}
                                isLoading={isLoading || isPolling}
                                className="w-full"
                            >
                                {isLoading || isPolling ? 'Comparing Prices...' : 'Compare Prices'}
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
                            title="Comparison Failed"
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
                            <LoadingPulse label="Comparing prices across vendors..." />
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
                                    {result.price_comparison}
                                </p>
                            </CardContent>
                        </Card>

                        {/* Price Comparison Table */}
                        {result.prices && result.prices.length > 0 && (
                            <PriceComparison
                                prices={result.prices}
                                bestDeal={result.best_deal}
                                priceRange={result.price_range}
                            />
                        )}
                    </motion.div>
                ) : (
                    <Card variant="bordered" className="py-20">
                        <CardContent className="text-center">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-500/20 flex items-center justify-center">
                                <DollarSign className="w-8 h-8 text-green-400" aria-hidden="true" />
                            </div>
                            <h3 className="text-lg font-semibold text-text mb-2">
                                Compare Product Prices
                            </h3>
                            <p className="text-text-muted text-sm">
                                Enter a product name to compare prices across multiple vendors.
                            </p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}

export default function ComparePage() {
    return (
        <Suspense fallback={<div className="container mx-auto px-4 py-12"><LoadingPulse /></div>}>
            <ComparePageContent />
        </Suspense>
    );
}
