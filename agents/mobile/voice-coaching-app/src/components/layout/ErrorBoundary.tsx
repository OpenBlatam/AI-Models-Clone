import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { COLORS } from '../../constants';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

/**
 * Error boundary component for catching and displaying errors gracefully
 */
export class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('[ErrorBoundary] Caught error:', error, errorInfo);
    }

    handleRetry = () => {
        this.setState({ hasError: false, error: null });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <View
                    style={{
                        flex: 1,
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: COLORS.background,
                        padding: 24,
                    }}
                >
                    <Text style={{ fontSize: 48, marginBottom: 16 }}>😵</Text>
                    <Text
                        style={{
                            fontSize: 20,
                            fontWeight: 'bold',
                            color: COLORS.text.primary,
                            textAlign: 'center',
                            marginBottom: 8,
                        }}
                    >
                        Oops! Something went wrong
                    </Text>
                    <Text
                        style={{
                            fontSize: 14,
                            color: COLORS.text.secondary,
                            textAlign: 'center',
                            marginBottom: 24,
                        }}
                    >
                        {this.state.error?.message || 'An unexpected error occurred'}
                    </Text>
                    <TouchableOpacity
                        onPress={this.handleRetry}
                        style={{
                            backgroundColor: COLORS.primary,
                            paddingVertical: 12,
                            paddingHorizontal: 24,
                            borderRadius: 12,
                        }}
                    >
                        <Text style={{ color: COLORS.white, fontWeight: '600' }}>
                            Try Again
                        </Text>
                    </TouchableOpacity>
                </View>
            );
        }

        return this.props.children;
    }
}
