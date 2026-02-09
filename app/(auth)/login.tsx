import React, { useCallback } from 'react';
import { View, Text, StyleSheet, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { OptimizedInput } from '../../components/OptimizedInput';
import { OptimizedButton } from '../../components/OptimizedButton';
import { useOptimizedForm } from '../../hooks/useOptimizedForm';
import { useApi } from '../../hooks/useApi';

export default function LoginScreen() {
  const router = useRouter();
  const loginMutation = useApi.useLogin();

  const form = useOptimizedForm({
    initialValues: {
      email: '',
      password: '',
    },
    validationRules: {
      email: {
        required: true,
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      },
      password: {
        required: true,
        minLength: 6,
      },
    },
    onSubmit: async (values) => {
      try {
        await loginMutation.mutateAsync(values);
        router.replace('/(tabs)');
      } catch (error) {
        Alert.alert('Login Failed', 'Invalid email or password');
      }
    },
  });

  const handleForgotPassword = useCallback(() => {
    router.push('/(auth)/forgot-password');
  }, [router]);

  const handleRegister = useCallback(() => {
    router.push('/(auth)/register');
  }, [router]);

  const handleSocialLogin = useCallback((provider: string) => {
    Alert.alert('Coming Soon', `${provider} login will be available soon`);
  }, []);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Welcome Back</Text>
          <Text style={styles.subtitle}>Sign in to your account</Text>
        </View>

        <View style={styles.form}>
          <OptimizedInput
            label="Email"
            value={form.values.email}
            onChangeText={(value) => form.setFieldValue('email', value)}
            onBlur={() => form.setFieldTouched('email')}
            error={form.touched.email ? form.errors.email : undefined}
            leftIcon="mail"
            placeholder="Enter your email"
            keyboardType="email-address"
            autoCapitalize="none"
            autoComplete="email"
            isRequired
          />

          <OptimizedInput
            label="Password"
            value={form.values.password}
            onChangeText={(value) => form.setFieldValue('password', value)}
            onBlur={() => form.setFieldTouched('password')}
            error={form.touched.password ? form.errors.password : undefined}
            leftIcon="lock-closed"
            placeholder="Enter your password"
            isPassword
            isRequired
          />

          <OptimizedButton
            title="Sign In"
            onPress={form.handleSubmit}
            isLoading={form.isSubmitting || loginMutation.isLoading}
            isDisabled={!form.isValid || form.isSubmitting}
            style={styles.submitButton}
          />

          <OptimizedButton
            title="Forgot Password?"
            onPress={handleForgotPassword}
            variant="ghost"
            size="small"
            style={styles.forgotButton}
          />
        </View>

        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>or</Text>
          <View style={styles.dividerLine} />
        </View>

        <View style={styles.socialButtons}>
          <OptimizedButton
            title="Continue with Google"
            onPress={() => handleSocialLogin('Google')}
            variant="outline"
            leftIcon="🔍"
            style={styles.socialButton}
          />

          <OptimizedButton
            title="Continue with Apple"
            onPress={() => handleSocialLogin('Apple')}
            variant="outline"
            leftIcon="🍎"
            style={styles.socialButton}
          />
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Don't have an account? </Text>
          <OptimizedButton
            title="Sign Up"
            onPress={handleRegister}
            variant="ghost"
            size="small"
          />
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 60,
    paddingBottom: 40,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#000000',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
  form: {
    marginBottom: 32,
  },
  submitButton: {
    marginTop: 24,
  },
  forgotButton: {
    marginTop: 16,
    alignSelf: 'center',
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 32,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#E5E5EA',
  },
  dividerText: {
    marginHorizontal: 16,
    fontSize: 14,
    color: '#8E8E93',
  },
  socialButtons: {
    marginBottom: 32,
  },
  socialButton: {
    marginBottom: 12,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 'auto',
  },
  footerText: {
    fontSize: 14,
    color: '#8E8E93',
  },
}); 