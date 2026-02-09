'use client';

import { motion } from 'framer-motion';
import { Star, Package, Shield, Ruler, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/Card';
import type { ProductDetailsResult } from '@/src/types/api';

interface ProductDetailsProps {
    details: ProductDetailsResult;
}

export const ProductDetails = ({ details }: ProductDetailsProps) => {
    const { specifications, materials, dimensions, compatibility, warranty, reviews_summary } = details;

    return (
        <div className="space-y-6">
            {/* Main Description */}
            <Card variant="glass">
                <CardContent>
                    <p className="text-text leading-relaxed whitespace-pre-wrap">
                        {details.product_details}
                    </p>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Specifications */}
                {Object.keys(specifications).length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <Card variant="bordered">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Package className="w-5 h-5 text-primary" aria-hidden="true" />
                                    Specifications
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <dl className="space-y-3">
                                    {Object.entries(specifications).map(([key, value]) => (
                                        <div key={key} className="flex justify-between py-2 border-b border-white/5 last:border-0">
                                            <dt className="text-text-muted capitalize">{key.replace(/_/g, ' ')}</dt>
                                            <dd className="text-text font-medium">{value}</dd>
                                        </div>
                                    ))}
                                </dl>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Dimensions */}
                {dimensions && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <Card variant="bordered">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Ruler className="w-5 h-5 text-secondary" aria-hidden="true" />
                                    Dimensions
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 gap-4">
                                    {dimensions.width && (
                                        <div>
                                            <p className="text-text-muted text-sm">Width</p>
                                            <p className="text-text font-medium">{dimensions.width} {dimensions.unit || 'cm'}</p>
                                        </div>
                                    )}
                                    {dimensions.height && (
                                        <div>
                                            <p className="text-text-muted text-sm">Height</p>
                                            <p className="text-text font-medium">{dimensions.height} {dimensions.unit || 'cm'}</p>
                                        </div>
                                    )}
                                    {dimensions.depth && (
                                        <div>
                                            <p className="text-text-muted text-sm">Depth</p>
                                            <p className="text-text font-medium">{dimensions.depth} {dimensions.unit || 'cm'}</p>
                                        </div>
                                    )}
                                    {dimensions.weight && (
                                        <div>
                                            <p className="text-text-muted text-sm">Weight</p>
                                            <p className="text-text font-medium">{dimensions.weight} kg</p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Materials */}
                {materials && materials.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <Card variant="bordered">
                            <CardHeader>
                                <CardTitle>Materials</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-wrap gap-2">
                                    {materials.map((material, i) => (
                                        <span
                                            key={i}
                                            className="px-3 py-1 rounded-full bg-primary/20 text-primary text-sm font-medium"
                                        >
                                            {material}
                                        </span>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Compatibility */}
                {compatibility && compatibility.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <Card variant="bordered">
                            <CardHeader>
                                <CardTitle>Compatibility</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-2">
                                    {compatibility.map((item, i) => (
                                        <li key={i} className="flex items-center gap-2 text-text">
                                            <span className="w-1.5 h-1.5 rounded-full bg-accent-success" aria-hidden="true" />
                                            {item}
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Warranty */}
                {warranty && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                    >
                        <Card variant="bordered">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Shield className="w-5 h-5 text-accent-success" aria-hidden="true" />
                                    Warranty
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="flex justify-between">
                                    <span className="text-text-muted">Duration</span>
                                    <span className="text-text font-medium">{warranty.duration}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-text-muted">Type</span>
                                    <span className="text-text font-medium">{warranty.type}</span>
                                </div>
                                {warranty.coverage && warranty.coverage.length > 0 && (
                                    <div>
                                        <p className="text-text-muted mb-2">Coverage</p>
                                        <ul className="space-y-1">
                                            {warranty.coverage.map((item, i) => (
                                                <li key={i} className="text-sm text-text">• {item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </motion.div>
                )}

                {/* Reviews Summary */}
                {reviews_summary && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        className="lg:col-span-2"
                    >
                        <Card variant="bordered">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Star className="w-5 h-5 text-accent-warning" aria-hidden="true" />
                                    Reviews Summary
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="flex items-center gap-2">
                                        <span className="text-4xl font-bold text-text">
                                            {reviews_summary.average_rating.toFixed(1)}
                                        </span>
                                        <div className="flex">
                                            {[...Array(5)].map((_, i) => (
                                                <Star
                                                    key={i}
                                                    className={`w-5 h-5 ${i < Math.round(reviews_summary.average_rating)
                                                            ? 'text-accent-warning fill-accent-warning'
                                                            : 'text-text-muted'
                                                        }`}
                                                    aria-hidden="true"
                                                />
                                            ))}
                                        </div>
                                    </div>
                                    <span className="text-text-muted">
                                        Based on {reviews_summary.total_reviews.toLocaleString()} reviews
                                    </span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {reviews_summary.pros && reviews_summary.pros.length > 0 && (
                                        <div>
                                            <h4 className="flex items-center gap-2 font-semibold text-accent-success mb-3">
                                                <ThumbsUp className="w-4 h-4" aria-hidden="true" />
                                                Pros
                                            </h4>
                                            <ul className="space-y-2">
                                                {reviews_summary.pros.map((pro, i) => (
                                                    <li key={i} className="text-sm text-text">• {pro}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                    {reviews_summary.cons && reviews_summary.cons.length > 0 && (
                                        <div>
                                            <h4 className="flex items-center gap-2 font-semibold text-accent-error mb-3">
                                                <ThumbsDown className="w-4 h-4" aria-hidden="true" />
                                                Cons
                                            </h4>
                                            <ul className="space-y-2">
                                                {reviews_summary.cons.map((con, i) => (
                                                    <li key={i} className="text-sm text-text">• {con}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default ProductDetails;
