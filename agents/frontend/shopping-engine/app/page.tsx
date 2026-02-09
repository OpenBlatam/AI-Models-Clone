'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import {
    ScanSearch,
    ShoppingCart,
    Sparkles,
    DollarSign,
    FileText,
    ArrowRight,
    Zap,
    Globe,
    Shield
} from 'lucide-react';
import { Button } from '@/src/components/ui/Button';
import { Card, CardContent } from '@/src/components/ui/Card';

interface FeatureCard {
    icon: React.ReactNode;
    title: string;
    description: string;
    href: string;
    color: string;
}

const features: FeatureCard[] = [
    {
        icon: <ScanSearch className="w-6 h-6" />,
        title: 'Product Analysis',
        description: 'Upload any product image and get instant AI-powered identification with brand, model, and features.',
        href: '/analyze',
        color: 'from-purple-500 to-pink-500',
    },
    {
        icon: <ShoppingCart className="w-6 h-6" />,
        title: 'Purchase Options',
        description: 'Find the best places to buy with price estimates, availability, and store recommendations.',
        href: '/purchase',
        color: 'from-blue-500 to-cyan-500',
    },
    {
        icon: <Sparkles className="w-6 h-6" />,
        title: 'Smart Recommendations',
        description: 'Get personalized alternatives, upgrades, and accessories tailored to your needs.',
        href: '/recommendations',
        color: 'from-amber-500 to-orange-500',
    },
    {
        icon: <DollarSign className="w-6 h-6" />,
        title: 'Price Comparison',
        description: 'Compare prices across multiple vendors to ensure you get the best deal available.',
        href: '/compare',
        color: 'from-green-500 to-emerald-500',
    },
    {
        icon: <FileText className="w-6 h-6" />,
        title: 'Product Details',
        description: 'Access comprehensive specifications, reviews, warranty info, and compatibility data.',
        href: '/details',
        color: 'from-indigo-500 to-violet-500',
    },
];

const stats = [
    { icon: <Zap className="w-5 h-5" />, value: '24/7', label: 'AI Assistance' },
    { icon: <Globe className="w-5 h-5" />, value: '100+', label: 'Vendors' },
    { icon: <Shield className="w-5 h-5" />, value: '99.9%', label: 'Accuracy' },
];

export default function HomePage() {
    return (
        <div className="relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 -z-10">
                <div className="absolute top-0 -left-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl" />
                <div className="absolute top-40 -right-40 w-80 h-80 bg-secondary/20 rounded-full blur-3xl" />
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-80 h-80 bg-primary/10 rounded-full blur-3xl" />
            </div>

            {/* Hero Section */}
            <section className="container mx-auto px-4 py-20 lg:py-32">
                <div className="max-w-4xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/20 text-primary text-sm font-medium mb-6">
                            <Sparkles className="w-4 h-4" aria-hidden="true" />
                            AI-Powered Shopping Intelligence
                        </span>
                    </motion.div>

                    <motion.h1
                        className="text-4xl md:text-6xl lg:text-7xl font-extrabold mb-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                    >
                        Shop Smarter with{' '}
                        <span className="gradient-text">AI Analysis</span>
                    </motion.h1>

                    <motion.p
                        className="text-lg md:text-xl text-text-muted max-w-2xl mx-auto mb-10"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                    >
                        Upload any product image and instantly get identification, price comparisons,
                        recommendations, and the best places to buy — all powered by advanced AI.
                    </motion.p>

                    <motion.div
                        className="flex flex-col sm:flex-row items-center justify-center gap-4"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                    >
                        <Link href="/analyze">
                            <Button size="lg" rightIcon={<ArrowRight className="w-5 h-5" />}>
                                Analyze a Product
                            </Button>
                        </Link>
                        <Link href="/compare">
                            <Button variant="secondary" size="lg">
                                Compare Prices
                            </Button>
                        </Link>
                    </motion.div>

                    {/* Stats */}
                    <motion.div
                        className="flex items-center justify-center gap-8 mt-16"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.6, delay: 0.5 }}
                    >
                        {stats.map((stat, i) => (
                            <div key={i} className="text-center">
                                <div className="flex items-center justify-center gap-2 text-primary mb-1">
                                    {stat.icon}
                                    <span className="text-2xl font-bold">{stat.value}</span>
                                </div>
                                <p className="text-sm text-text-muted">{stat.label}</p>
                            </div>
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* Features Section */}
            <section className="container mx-auto px-4 py-20">
                <motion.div
                    className="text-center mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">
                        Everything You Need to Shop Smart
                    </h2>
                    <p className="text-text-muted max-w-2xl mx-auto">
                        Our AI-powered platform provides comprehensive shopping analysis
                        to help you make informed purchasing decisions.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <Link href={feature.href}>
                                <Card isHoverable isClickable className="h-full">
                                    <CardContent className="flex flex-col h-full">
                                        <div className={`
                      w-12 h-12 rounded-xl mb-4 flex items-center justify-center
                      bg-gradient-to-br ${feature.color} text-white
                    `}>
                                            {feature.icon}
                                        </div>
                                        <h3 className="text-xl font-semibold text-text mb-2">
                                            {feature.title}
                                        </h3>
                                        <p className="text-text-muted flex-1">
                                            {feature.description}
                                        </p>
                                        <div className="flex items-center gap-2 mt-4 text-primary font-medium">
                                            Learn more
                                            <ArrowRight className="w-4 h-4" aria-hidden="true" />
                                        </div>
                                    </CardContent>
                                </Card>
                            </Link>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="container mx-auto px-4 py-20">
                <motion.div
                    className="relative rounded-3xl overflow-hidden"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary opacity-90" />
                    <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />

                    <div className="relative z-10 px-8 py-16 md:py-20 text-center">
                        <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                            Ready to Transform Your Shopping?
                        </h2>
                        <p className="text-white/80 max-w-xl mx-auto mb-8">
                            Start analyzing products now and discover the power of AI-assisted shopping.
                        </p>
                        <Link href="/analyze">
                            <Button
                                variant="secondary"
                                size="lg"
                                className="bg-white text-primary hover:bg-white/90"
                            >
                                Get Started Free
                            </Button>
                        </Link>
                    </div>
                </motion.div>
            </section>
        </div>
    );
}
