/**
 * @fileoverview Demo component for biometric authentication system
 * @author Blaze AI Team
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, Alert } from 'react-native';
import { BiometricAuthComponent } from '../security/biometric-auth-component';
import { AccessibleButton } from '../accessibility/accessible-button';

/**
 * BiometricAuthDemo component demonstrates the biometric authentication system
 */
export function BiometricAuthDemo(): JSX.Element {
  const [userId, setUserId] = useState<string>('demo-user-123');
  const [customUserId, setCustomUserId] = useState<string>('');
  const [showAdvancedSettings, setShowAdvancedSettings] = useState<boolean>(false);
  const [lastAuthResult, setLastAuthResult] = useState<string>('');

  /**
   * Handles successful authentication
   */
  const handleAuthenticationSuccess = (sessionId: string): void => {
    setLastAuthResult(`✅ Authentication successful! Session ID: ${sessionId}`);
    Alert.alert('Success', 'Biometric authentication completed successfully!');
  };

  /**
   * Handles authentication failure
   */
  const handleAuthenticationFailure = (error: string): void => {
    setLastAuthResult(`❌ Authentication failed: ${error}`);
    console.error('Authentication failed:', error);
  };

  /**
   * Updates the user ID for testing
   */
  const handleUpdateUserId = (): void => {
    if (!customUserId.trim()) {
      Alert.alert('Error', 'Please enter a user ID');
      return;
    }
    
    setUserId(customUserId.trim());
    setCustomUserId('');
    setLastAuthResult('');
    Alert.alert('Success', `User ID updated to: ${customUserId.trim()}`);
  };

  /**
   * Resets the demo to default state
   */
  const handleResetDemo = (): void => {
    setUserId('demo-user-123');
    setCustomUserId('');
    setLastAuthResult('');
    setShowAdvancedSettings(false);
    Alert.alert('Success', 'Demo reset to default state');
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <Text style={styles.title}>Biometric Authentication Demo</Text>
      <Text style={styles.subtitle}>
        Comprehensive demonstration of the biometric authentication system
      </Text>

      {/* Demo Controls */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Demo Controls</Text>
        
        <View style={styles.controlRow}>
          <Text style={styles.controlLabel}>Current User ID:</Text>
          <Text style={styles.controlValue}>{userId}</Text>
        </View>

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            placeholder="Enter new user ID for testing"
            value={customUserId}
            onChangeText={setCustomUserId}
            autoCapitalize="none"
            autoCorrect={false}
            accessibilityLabel="New User ID Input"
          />
          <AccessibleButton
            accessibilityLabel="Update User ID Button"
            style={styles.button}
            onPress={handleUpdateUserId}
          >
            <Text style={styles.buttonText}>Update User ID</Text>
          </AccessibleButton>
        </View>

        <View style={styles.buttonRow}>
          <AccessibleButton
            accessibilityLabel="Toggle Advanced Settings Button"
            style={[styles.button, styles.secondaryButton]}
            onPress={() => setShowAdvancedSettings(!showAdvancedSettings)}
          >
            <Text style={styles.buttonText}>
              {showAdvancedSettings ? 'Hide' : 'Show'} Advanced Settings
            </Text>
          </AccessibleButton>

          <AccessibleButton
            accessibilityLabel="Reset Demo Button"
            style={[styles.button, styles.dangerButton]}
            onPress={handleResetDemo}
          >
            <Text style={styles.buttonText}>Reset Demo</Text>
          </AccessibleButton>
        </View>
      </View>

      {/* Authentication Result Display */}
      {lastAuthResult && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Last Authentication Result</Text>
          <View style={styles.resultContainer}>
            <Text style={styles.resultText}>{lastAuthResult}</Text>
          </View>
        </View>
      )}

      {/* Biometric Authentication Component */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Biometric Authentication</Text>
        <BiometricAuthComponent
          userId={userId}
          onAuthenticationSuccess={handleAuthenticationSuccess}
          onAuthenticationFailure={handleAuthenticationFailure}
          showAdvancedSettings={showAdvancedSettings}
          style={styles.biometricComponent}
        />
      </View>

      {/* Demo Instructions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Demo Instructions</Text>
        
        <View style={styles.instructionContainer}>
          <Text style={styles.instructionTitle}>1. Setup Phase</Text>
          <Text style={styles.instructionText}>
            • The component will automatically check biometric availability{'\n'}
            • Select your preferred biometric type (fingerprint, facial, etc.){'\n'}
            • Enable biometric authentication for the current user
          </Text>
        </View>

        <View style={styles.instructionContainer}>
          <Text style={styles.instructionTitle}>2. Authentication Phase</Text>
          <Text style={styles.instructionText}>
            • Use the "Authenticate with Biometrics" button{'\n'}
            • Follow the device's biometric prompt{'\n'}
            • Monitor the authentication result above
          </Text>
        </View>

        <View style={styles.instructionContainer}>
          <Text style={styles.instructionTitle}>3. Advanced Features</Text>
          <Text style={styles.instructionText}>
            • Toggle advanced settings to configure security options{'\n'}
            • Use backup codes as an alternative authentication method{'\n'}
            • View usage statistics and security information
          </Text>
        </View>

        <View style={styles.instructionContainer}>
          <Text style={styles.instructionTitle}>4. Testing Scenarios</Text>
          <Text style={styles.instructionText}>
            • Change user ID to test different user contexts{'\n'}
            • Enable/disable biometric authentication{'\n'}
            • Test backup code functionality{'\n'}
            • Monitor session management and security
          </Text>
        </View>
      </View>

      {/* Security Features */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Security Features</Text>
        
        <View style={styles.featureContainer}>
          <Text style={styles.featureTitle}>🔐 Multi-Factor Authentication</Text>
          <Text style={styles.featureText}>
            Supports fingerprint, facial recognition, iris scanning, and voice recognition
          </Text>
        </View>

        <View style={styles.featureContainer}>
          <Text style={styles.featureTitle}>🛡️ Security Levels</Text>
          <Text style={styles.featureText}>
            Automatic security level assessment based on available biometric hardware
          </Text>
        </View>

        <View style={styles.featureContainer}>
          <Text style={styles.featureTitle}>🔑 Backup Codes</Text>
          <Text style={styles.featureText}>
            Secure backup authentication method with auto-regeneration
          </Text>
        </View>

        <View style={styles.featureContainer}>
          <Text style={styles.featureTitle}>📊 Usage Monitoring</Text>
          <Text style={styles.featureText}>
            Track authentication attempts, success rates, and security events
          </Text>
        </View>

        <View style={styles.featureContainer}>
          <Text style={styles.featureTitle}>⏰ Session Management</Text>
          <Text style={styles.featureText}>
            Configurable session timeouts and automatic session invalidation
          </Text>
        </View>

        <View style={styles.featureContainer}>
          <Text style={styles.featureTitle}>🚫 Brute Force Protection</Text>
          <Text style={styles.featureText}>
            Account lockout after multiple failed attempts with configurable thresholds
          </Text>
        </View>
      </View>

      {/* Technical Details */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Technical Implementation</Text>
        
        <View style={styles.techContainer}>
          <Text style={styles.techTitle}>Architecture</Text>
          <Text style={styles.techText}>
            • Singleton pattern for biometric manager{'\n'}
            • React hooks for state management{'\n'}
            • Secure storage with expo-secure-store{'\n'}
            • Zod validation for data integrity{'\n'}
            • Comprehensive error handling
          </Text>
        </View>

        <View style={styles.techContainer}>
          <Text style={styles.techTitle}>Security Measures</Text>
          <Text style={styles.techText}>
            • Encrypted storage of biometric data{'\n'}
            • Secure session management{'\n'}
            • Audit logging of all authentication attempts{'\n'}
            • Configurable security policies{'\n'}
            • GDPR-compliant consent management
          </Text>
        </View>

        <View style={styles.techContainer}>
          <Text style={styles.techTitle}>Platform Support</Text>
          <Text style={styles.techText}>
            • iOS: Touch ID, Face ID, and device passcode{'\n'}
            • Android: Fingerprint, facial recognition, and pattern/PIN{'\n'}
            • Web: Platform-specific biometric APIs{'\n'}
            • Fallback authentication methods
          </Text>
        </View>
      </View>

      <Text style={styles.footerText}>
        This demo showcases the comprehensive biometric authentication system.{'\n'}
        Test different scenarios and explore the security features.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  contentContainer: {
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#000',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
    lineHeight: 22,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
  },
  controlRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  controlLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  controlValue: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  inputContainer: {
    marginBottom: 15,
  },
  textInput: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    marginBottom: 10,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 10,
    marginBottom: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  secondaryButton: {
    backgroundColor: '#8E8E93',
  },
  dangerButton: {
    backgroundColor: '#FF3B30',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  resultContainer: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#34C759',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  resultText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 22,
  },
  biometricComponent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  instructionContainer: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  instructionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF',
    marginBottom: 8,
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  featureContainer: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  techContainer: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  techTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  techText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  footerText: {
    textAlign: 'center',
    marginTop: 20,
    fontSize: 14,
    color: '#888',
    lineHeight: 20,
  },
});


