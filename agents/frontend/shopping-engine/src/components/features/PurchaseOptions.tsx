'use client';

import { motion } from 'framer-motion';
import { Star, ExternalLink } from 'lucide-react';
import { Card, CardContent } from '@/src/components/ui/Card';
import type { PurchaseOption } from '@/src/types/api';

interface PurchaseOptionsProps {
    options: PurchaseOption[];
    recommendedVendor?: string;
    onSelect?: (option: PurchaseOption) => void;
}

const availabilityColors: Record<string, string> = {
    in_stock: 'text-accent-success',
    limited: 'text-accent-warning',
    out_of_stock: 'text-accent-error',
};

const availabilityLabels: Record<string, string> = {
    in_stock: 'In Stock',
    limited: 'Limited',
    out_of_stock: 'Out of Stock',
};

export const PurchaseOptions = ({
    options,
    recommendedVendor,
    onSelect,
}: PurchaseOptionsProps) => {
    if (options.length === 0) {
        return (
            <Card variant="bordered" className="text-center py-12">
                <CardContent>
                    <p className="text-text-muted">No purchase options found</p>
                </CardContent>
            </Card>
        );
    }

    const handleSelectOption = (option: PurchaseOption) => {
        onSelect?.(option);
    };

    const handleKeyDownSelectOption = (e: React.KeyboardEvent, option: PurchaseOption) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleSelectOption(option);
        }
    };

    return (
        <div className="space-y-4">
            {options.map((option, index) => {
                const isRecommended = option.vendor === recommendedVendor;

                return (
                    <motion.div
                        key={`${option.vendor}-${index}`}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <Card
                            variant={isRecommended ? 'bordered' : 'default'}
                            isHoverable
                            isClickable
                            onClick={() => handleSelectOption(option)}
                            onKeyDown={(e) => handleKeyDownSelectOption(e, option)}
                            className={`
                relative
                ${isRecommended ? 'ring-2 ring-primary/50' : ''}
              `}
                        >
                            {isRecommended && (
                                <div className="absolute -top-3 left-4 px-3 py-1 rounded-full bg-gradient-to-r from-primary to-secondary text-xs font-semibold text-white">
                                    Recommended
                                </div>
                            )}
                            <CardContent className="flex flex-col md:flex-row md:items-center gap-4">
                                {/* Vendor Info */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <h3 className="text-lg font-semibold text-text truncate">
                                            {option.vendor}
                                        </h3>
                                        <a
                                            href={option.vendor_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            onClick={(e) => e.stopPropagation()}
                                            className="p-1 rounded hover:bg-white/10 transition-colors"
                                            aria-label={`Visit ${option.vendor}`}
                                            tabIndex={0}
                                        >
                                            <ExternalLink className="w-4 h-4 text-text-muted" aria-hidden="true" />
                                        </a>
                                    </div>
                                    <div className="flex items-center gap-4 mt-2 text-sm">
                                        <span className={availabilityColors[option.availability]}>
                                            {availabilityLabels[option.availability]}
                                        </span>
                                        <span className="text-text-muted capitalize">
                                            {option.condition}
                                        </span>
                                        {option.rating && (
                                            <span className="flex items-center gap-1 text-text-muted">
                                                <Star className="w-4 h-4 text-accent-warning fill-accent-warning" aria-hidden="true" />
                                                {option.rating.toFixed(1)}
                                                {option.reviews_count && (
                                                    <span className="text-xs">({option.reviews_count})</span>
                                                )}
                                            </span>
                                        )}
                                    </div>
                                    {option.delivery_estimate && (
                                        <p className="text-sm text-text-muted mt-1">
                                            Delivery: {option.delivery_estimate}
                                        </p>
                                    )}
                                    {option.special_offer && (
                                        <p className="text-sm text-accent-success mt-1">
                                            🎁 {option.special_offer}
                                        </p>
                                    )}
                                </div>

                                {/* Price */}
                                <div className="text-right">
                                    <p className="text-2xl font-bold text-text">
                                        {option.currency} ${option.price.toLocaleString()}
                                    </p>
                                    {option.shipping_cost !== undefined && (
                                        <p className="text-sm text-text-muted">
                                            {option.shipping_cost === 0
                                                ? 'Free shipping'
                                                : `+ $${option.shipping_cost.toLocaleString()} shipping`
                                            }
                                        </p>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                );
            })}
        </div>
    );
};

export default PurchaseOptions;
