/**
 * @fileoverview Comprehensive biometric authentication component
 * @author Blaze AI Team
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Switch,
  ScrollView,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { useBiometricAuth } from '../../hooks/security/use-biometric-auth';
import { BiometricType, BiometricSecurityLevel } from '../../lib/security/biometric-auth';
import { AccessibleButton } from '../accessibility/accessible-button';

/**
 * Props for the BiometricAuthComponent
 */
interface BiometricAuthComponentProps {
  userId: string;
  onAuthenticationSuccess?: (sessionId: string) => void;
  onAuthenticationFailure?: (error: string) => void;
  showAdvancedSettings?: boolean;
  style?: any;
}

/**
 * Comprehensive biometric authentication component
 * Provides setup, configuration, and authentication capabilities
 */
export function BiometricAuthComponent({
  userId,
  onAuthenticationSuccess,
  onAuthenticationFailure,
  showAdvancedSettings = false,
  style,
}: BiometricAuthComponentProps): JSX.Element {
  const {
    isAvailable,
    isEnabled,
    isLoading,
    biometricTypes,
    securityLevel,
    config,
    biometricData,
    checkAvailability,
    enableBiometric,
    disableBiometric,
    authenticate,
    verifyBackupCode,
    updateConfig,
    refreshBiometricData,
  } = useBiometricAuth();

  const [selectedBiometricType, setSelectedBiometricType] = useState<BiometricType>(BiometricType.NONE);
  const [backupCode, setBackupCode] = useState<string>('');
  const [showBackupCodeInput, setShowBackupCodeInput] = useState<boolean>(false);
  const [isAuthenticating, setIsAuthenticating] = useState<boolean>(false);

  useEffect(() => {
    if (biometricTypes.length > 0 && biometricTypes[0] !== BiometricType.NONE) {
      setSelectedBiometricType(biometricTypes[0]);
    }
  }, [biometricTypes]);

  useEffect(() => {
    if (userId) {
      refreshBiometricData(userId);
    }
  }, [userId, refreshBiometricData]);

  /**
   * Handles biometric authentication
   */
  const handleAuthenticate = async (): Promise<void> => {
    if (!userId) {
      Alert.alert('Error', 'User ID is required');
      return;
    }

    try {
      setIsAuthenticating(true);
      const result = await authenticate(userId);

      if (result.success) {
        Alert.alert('Success', 'Biometric authentication successful!');
        onAuthenticationSuccess?.(result.sessionId || '');
      } else {
        Alert.alert('Authentication Failed', result.error || 'Unknown error');
        onAuthenticationFailure?.(result.error || 'Unknown error');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      Alert.alert('Error', errorMessage);
      onAuthenticationFailure?.(errorMessage);
    } finally {
      setIsAuthenticating(false);
    }
  };

  /**
   * Handles enabling biometric authentication
   */
  const handleEnableBiometric = async (): Promise<void> => {
    if (!userId) {
      Alert.alert('Error', 'User ID is required');
      return;
    }

    if (selectedBiometricType === BiometricType.NONE) {
      Alert.alert('Error', 'Please select a biometric type');
      return;
    }

    try {
      await enableBiometric(userId, selectedBiometricType);
      Alert.alert('Success', 'Biometric authentication enabled successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to enable biometric authentication';
      Alert.alert('Error', errorMessage);
    }
  };

  /**
   * Handles disabling biometric authentication
   */
  const handleDisableBiometric = async (): Promise<void> => {
    if (!userId) {
      Alert.alert('Error', 'User ID is required');
      return;
    }

    Alert.alert(
      'Disable Biometric Authentication',
      'Are you sure you want to disable biometric authentication? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Disable',
          style: 'destructive',
          onPress: async () => {
            try {
              await disableBiometric(userId);
              Alert.alert('Success', 'Biometric authentication disabled successfully!');
            } catch (error) {
              const errorMessage = error instanceof Error ? error.message : 'Failed to disable biometric authentication';
              Alert.alert('Error', errorMessage);
            }
          },
        },
      ]
    );
  };

  /**
   * Handles backup code verification
   */
  const handleVerifyBackupCode = async (): Promise<void> => {
    if (!backupCode.trim()) {
      Alert.alert('Error', 'Please enter a backup code');
      return;
    }

    try {
      const isValid = await verifyBackupCode(userId, backupCode);
      
      if (isValid) {
        Alert.alert('Success', 'Backup code verified successfully!');
        setBackupCode('');
        setShowBackupCodeInput(false);
        onAuthenticationSuccess?.('backup-code-auth');
      } else {
        Alert.alert('Error', 'Invalid backup code');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to verify backup code');
    }
  };

  /**
   * Handles configuration updates
   */
  const handleConfigUpdate = async (key: keyof typeof config, value: any): Promise<void> => {
    if (!config) return;

    try {
      await updateConfig({ [key]: value });
      Alert.alert('Success', 'Configuration updated successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update configuration';
      Alert.alert('Error', errorMessage);
    }
  };

  /**
   * Gets the display name for a biometric type
   */
  const getBiometricTypeDisplayName = (type: BiometricType): string => {
    switch (type) {
      case BiometricType.FINGERPRINT:
        return 'Fingerprint';
      case BiometricType.FACIAL:
        return 'Facial Recognition';
      case BiometricType.IRIS:
        return 'Iris Scan';
      case BiometricType.VOICE:
        return 'Voice Recognition';
      default:
        return 'None';
    }
  };

  /**
   * Gets the display name for a security level
   */
  const getSecurityLevelDisplayName = (level: BiometricSecurityLevel): string => {
    switch (level) {
      case BiometricSecurityLevel.LOW:
        return 'Low';
      case BiometricSecurityLevel.MEDIUM:
        return 'Medium';
      case BiometricSecurityLevel.HIGH:
        return 'High';
      case BiometricSecurityLevel.MAXIMUM:
        return 'Maximum';
      default:
        return 'Unknown';
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, style]}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Checking biometric availability...</Text>
      </View>
    );
  }

  if (!isAvailable) {
    return (
      <View style={[styles.container, style]}>
        <Text style={styles.title}>Biometric Authentication</Text>
        <Text style={styles.errorText}>
          Biometric authentication is not available on this device.
        </Text>
        <AccessibleButton
          accessibilityLabel="Check Biometric Availability Button"
          style={styles.button}
          onPress={checkAvailability}
        >
          <Text style={styles.buttonText}>Check Again</Text>
        </AccessibleButton>
      </View>
    );
  }

  return (
    <ScrollView style={[styles.container, style]} contentContainerStyle={styles.contentContainer}>
      <Text style={styles.title}>Biometric Authentication</Text>
      
      {/* Status Information */}
      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Status:</Text>
        <Text style={[styles.statusValue, { color: isEnabled ? '#34C759' : '#FF3B30' }]}>
          {isEnabled ? 'Enabled' : 'Disabled'}
        </Text>
      </View>

      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Available Types:</Text>
        <Text style={styles.statusValue}>
          {biometricTypes.map(type => getBiometricTypeDisplayName(type)).join(', ')}
        </Text>
      </View>

      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Security Level:</Text>
        <Text style={styles.statusValue}>
          {getSecurityLevelDisplayName(securityLevel)}
        </Text>
      </View>

      {/* Biometric Type Selection */}
      {!isEnabled && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select Biometric Type</Text>
          {biometricTypes
            .filter(type => type !== BiometricType.NONE)
            .map(type => (
              <TouchableOpacity
                key={type}
                style={[
                  styles.biometricTypeOption,
                  selectedBiometricType === type && styles.selectedBiometricType,
                ]}
                onPress={() => setSelectedBiometricType(type)}
                accessibilityLabel={`Select ${getBiometricTypeDisplayName(type)} Button`}
              >
                <Text style={[
                  styles.biometricTypeText,
                  selectedBiometricType === type && styles.selectedBiometricTypeText,
                ]}>
                  {getBiometricTypeDisplayName(type)}
                </Text>
              </TouchableOpacity>
            ))}
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actions</Text>
        
        {!isEnabled ? (
          <AccessibleButton
            accessibilityLabel="Enable Biometric Authentication Button"
            style={styles.button}
            onPress={handleEnableBiometric}
          >
            <Text style={styles.buttonText}>Enable Biometric Authentication</Text>
          </AccessibleButton>
        ) : (
          <>
            <AccessibleButton
              accessibilityLabel="Authenticate with Biometrics Button"
              style={[styles.button, styles.primaryButton]}
              onPress={handleAuthenticate}
              disabled={isAuthenticating}
            >
              {isAuthenticating ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text style={styles.buttonText}>Authenticate with Biometrics</Text>
              )}
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Use Backup Code Button"
              style={styles.button}
              onPress={() => setShowBackupCodeInput(!showBackupCodeInput)}
            >
              <Text style={styles.buttonText}>Use Backup Code</Text>
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Disable Biometric Authentication Button"
              style={[styles.button, styles.dangerButton]}
              onPress={handleDisableBiometric}
            >
              <Text style={styles.buttonText}>Disable Biometric Authentication</Text>
            </AccessibleButton>
          </>
        )}
      </View>

      {/* Backup Code Input */}
      {showBackupCodeInput && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Backup Code Authentication</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter backup code"
            value={backupCode}
            onChangeText={setBackupCode}
            autoCapitalize="none"
            autoCorrect={false}
            accessibilityLabel="Backup Code Input"
          />
          <View style={styles.buttonRow}>
            <AccessibleButton
              accessibilityLabel="Verify Backup Code Button"
              style={[styles.button, styles.smallButton]}
              onPress={handleVerifyBackupCode}
            >
              <Text style={styles.buttonText}>Verify</Text>
            </AccessibleButton>
            <AccessibleButton
              accessibilityLabel="Cancel Backup Code Button"
              style={[styles.button, styles.smallButton, styles.secondaryButton]}
              onPress={() => {
                setShowBackupCodeInput(false);
                setBackupCode('');
              }}
            >
              <Text style={styles.buttonText}>Cancel</Text>
            </AccessibleButton>
          </View>
        </View>
      )}

      {/* Advanced Settings */}
      {showAdvancedSettings && config && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Advanced Settings</Text>
          
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Allow Device Credentials</Text>
            <Switch
              value={config.allowDeviceCredentials}
              onValueChange={(value) => handleConfigUpdate('allowDeviceCredentials', value)}
              accessibilityLabel="Toggle Allow Device Credentials"
            />
          </View>

          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Allow Backup Authentication</Text>
            <Switch
              value={config.allowBackupAuthentication}
              onValueChange={(value) => handleConfigUpdate('allowBackupAuthentication', value)}
              accessibilityLabel="Toggle Allow Backup Authentication"
            />
          </View>

          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Require Strong Biometrics</Text>
            <Switch
              value={config.requireStrongBiometrics}
              onValueChange={(value) => handleConfigUpdate('requireStrongBiometrics', value)}
              accessibilityLabel="Toggle Require Strong Biometrics"
            />
          </View>
        </View>
      )}

      {/* Usage Statistics */}
      {biometricData && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Usage Statistics</Text>
          <View style={styles.statsContainer}>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Total Uses:</Text>
              <Text style={styles.statValue}>{biometricData.usageCount}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Last Used:</Text>
              <Text style={styles.statValue}>
                {new Date(biometricData.lastUsed).toLocaleDateString()}
              </Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Backup Codes:</Text>
              <Text style={styles.statValue}>{biometricData.backupCodes.length}</Text>
            </View>
          </View>
        </View>
      )}
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
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#000',
  },
  loadingText: {
    textAlign: 'center',
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    textAlign: 'center',
    marginBottom: 20,
    fontSize: 16,
    color: '#FF3B30',
  },
  statusContainer: {
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
  statusLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  statusValue: {
    fontSize: 16,
    fontWeight: '500',
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
  },
  biometricTypeOption: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#E5E5EA',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  selectedBiometricType: {
    borderColor: '#007AFF',
    backgroundColor: '#F0F8FF',
  },
  biometricTypeText: {
    fontSize: 16,
    textAlign: 'center',
    color: '#333',
  },
  selectedBiometricTypeText: {
    color: '#007AFF',
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 15,
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
  primaryButton: {
    backgroundColor: '#34C759',
  },
  dangerButton: {
    backgroundColor: '#FF3B30',
  },
  secondaryButton: {
    backgroundColor: '#8E8E93',
  },
  smallButton: {
    flex: 1,
    marginHorizontal: 5,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    marginBottom: 15,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
  },
  statsContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  statLabel: {
    fontSize: 16,
    color: '#666',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
});
 * @fileoverview Comprehensive biometric authentication component
 * @author Blaze AI Team
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Switch,
  ScrollView,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { useBiometricAuth } from '../../hooks/security/use-biometric-auth';
import { BiometricType, BiometricSecurityLevel } from '../../lib/security/biometric-auth';
import { AccessibleButton } from '../accessibility/accessible-button';

/**
 * Props for the BiometricAuthComponent
 */
interface BiometricAuthComponentProps {
  userId: string;
  onAuthenticationSuccess?: (sessionId: string) => void;
  onAuthenticationFailure?: (error: string) => void;
  showAdvancedSettings?: boolean;
  style?: any;
}

/**
 * Comprehensive biometric authentication component
 * Provides setup, configuration, and authentication capabilities
 */
export function BiometricAuthComponent({
  userId,
  onAuthenticationSuccess,
  onAuthenticationFailure,
  showAdvancedSettings = false,
  style,
}: BiometricAuthComponentProps): JSX.Element {
  const {
    isAvailable,
    isEnabled,
    isLoading,
    biometricTypes,
    securityLevel,
    config,
    biometricData,
    checkAvailability,
    enableBiometric,
    disableBiometric,
    authenticate,
    verifyBackupCode,
    updateConfig,
    refreshBiometricData,
  } = useBiometricAuth();

  const [selectedBiometricType, setSelectedBiometricType] = useState<BiometricType>(BiometricType.NONE);
  const [backupCode, setBackupCode] = useState<string>('');
  const [showBackupCodeInput, setShowBackupCodeInput] = useState<boolean>(false);
  const [isAuthenticating, setIsAuthenticating] = useState<boolean>(false);

  useEffect(() => {
    if (biometricTypes.length > 0 && biometricTypes[0] !== BiometricType.NONE) {
      setSelectedBiometricType(biometricTypes[0]);
    }
  }, [biometricTypes]);

  useEffect(() => {
    if (userId) {
      refreshBiometricData(userId);
    }
  }, [userId, refreshBiometricData]);

  /**
   * Handles biometric authentication
   */
  const handleAuthenticate = async (): Promise<void> => {
    if (!userId) {
      Alert.alert('Error', 'User ID is required');
      return;
    }

    try {
      setIsAuthenticating(true);
      const result = await authenticate(userId);

      if (result.success) {
        Alert.alert('Success', 'Biometric authentication successful!');
        onAuthenticationSuccess?.(result.sessionId || '');
      } else {
        Alert.alert('Authentication Failed', result.error || 'Unknown error');
        onAuthenticationFailure?.(result.error || 'Unknown error');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      Alert.alert('Error', errorMessage);
      onAuthenticationFailure?.(errorMessage);
    } finally {
      setIsAuthenticating(false);
    }
  };

  /**
   * Handles enabling biometric authentication
   */
  const handleEnableBiometric = async (): Promise<void> => {
    if (!userId) {
      Alert.alert('Error', 'User ID is required');
      return;
    }

    if (selectedBiometricType === BiometricType.NONE) {
      Alert.alert('Error', 'Please select a biometric type');
      return;
    }

    try {
      await enableBiometric(userId, selectedBiometricType);
      Alert.alert('Success', 'Biometric authentication enabled successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to enable biometric authentication';
      Alert.alert('Error', errorMessage);
    }
  };

  /**
   * Handles disabling biometric authentication
   */
  const handleDisableBiometric = async (): Promise<void> => {
    if (!userId) {
      Alert.alert('Error', 'User ID is required');
      return;
    }

    Alert.alert(
      'Disable Biometric Authentication',
      'Are you sure you want to disable biometric authentication? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Disable',
          style: 'destructive',
          onPress: async () => {
            try {
              await disableBiometric(userId);
              Alert.alert('Success', 'Biometric authentication disabled successfully!');
            } catch (error) {
              const errorMessage = error instanceof Error ? error.message : 'Failed to disable biometric authentication';
              Alert.alert('Error', errorMessage);
            }
          },
        },
      ]
    );
  };

  /**
   * Handles backup code verification
   */
  const handleVerifyBackupCode = async (): Promise<void> => {
    if (!backupCode.trim()) {
      Alert.alert('Error', 'Please enter a backup code');
      return;
    }

    try {
      const isValid = await verifyBackupCode(userId, backupCode);
      
      if (isValid) {
        Alert.alert('Success', 'Backup code verified successfully!');
        setBackupCode('');
        setShowBackupCodeInput(false);
        onAuthenticationSuccess?.('backup-code-auth');
      } else {
        Alert.alert('Error', 'Invalid backup code');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to verify backup code');
    }
  };

  /**
   * Handles configuration updates
   */
  const handleConfigUpdate = async (key: keyof typeof config, value: any): Promise<void> => {
    if (!config) return;

    try {
      await updateConfig({ [key]: value });
      Alert.alert('Success', 'Configuration updated successfully!');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update configuration';
      Alert.alert('Error', errorMessage);
    }
  };

  /**
   * Gets the display name for a biometric type
   */
  const getBiometricTypeDisplayName = (type: BiometricType): string => {
    switch (type) {
      case BiometricType.FINGERPRINT:
        return 'Fingerprint';
      case BiometricType.FACIAL:
        return 'Facial Recognition';
      case BiometricType.IRIS:
        return 'Iris Scan';
      case BiometricType.VOICE:
        return 'Voice Recognition';
      default:
        return 'None';
    }
  };

  /**
   * Gets the display name for a security level
   */
  const getSecurityLevelDisplayName = (level: BiometricSecurityLevel): string => {
    switch (level) {
      case BiometricSecurityLevel.LOW:
        return 'Low';
      case BiometricSecurityLevel.MEDIUM:
        return 'Medium';
      case BiometricSecurityLevel.HIGH:
        return 'High';
      case BiometricSecurityLevel.MAXIMUM:
        return 'Maximum';
      default:
        return 'Unknown';
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, style]}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Checking biometric availability...</Text>
      </View>
    );
  }

  if (!isAvailable) {
    return (
      <View style={[styles.container, style]}>
        <Text style={styles.title}>Biometric Authentication</Text>
        <Text style={styles.errorText}>
          Biometric authentication is not available on this device.
        </Text>
        <AccessibleButton
          accessibilityLabel="Check Biometric Availability Button"
          style={styles.button}
          onPress={checkAvailability}
        >
          <Text style={styles.buttonText}>Check Again</Text>
        </AccessibleButton>
      </View>
    );
  }

  return (
    <ScrollView style={[styles.container, style]} contentContainerStyle={styles.contentContainer}>
      <Text style={styles.title}>Biometric Authentication</Text>
      
      {/* Status Information */}
      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Status:</Text>
        <Text style={[styles.statusValue, { color: isEnabled ? '#34C759' : '#FF3B30' }]}>
          {isEnabled ? 'Enabled' : 'Disabled'}
        </Text>
      </View>

      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Available Types:</Text>
        <Text style={styles.statusValue}>
          {biometricTypes.map(type => getBiometricTypeDisplayName(type)).join(', ')}
        </Text>
      </View>

      <View style={styles.statusContainer}>
        <Text style={styles.statusLabel}>Security Level:</Text>
        <Text style={styles.statusValue}>
          {getSecurityLevelDisplayName(securityLevel)}
        </Text>
      </View>

      {/* Biometric Type Selection */}
      {!isEnabled && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select Biometric Type</Text>
          {biometricTypes
            .filter(type => type !== BiometricType.NONE)
            .map(type => (
              <TouchableOpacity
                key={type}
                style={[
                  styles.biometricTypeOption,
                  selectedBiometricType === type && styles.selectedBiometricType,
                ]}
                onPress={() => setSelectedBiometricType(type)}
                accessibilityLabel={`Select ${getBiometricTypeDisplayName(type)} Button`}
              >
                <Text style={[
                  styles.biometricTypeText,
                  selectedBiometricType === type && styles.selectedBiometricTypeText,
                ]}>
                  {getBiometricTypeDisplayName(type)}
                </Text>
              </TouchableOpacity>
            ))}
        </View>
      )}

      {/* Action Buttons */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Actions</Text>
        
        {!isEnabled ? (
          <AccessibleButton
            accessibilityLabel="Enable Biometric Authentication Button"
            style={styles.button}
            onPress={handleEnableBiometric}
          >
            <Text style={styles.buttonText}>Enable Biometric Authentication</Text>
          </AccessibleButton>
        ) : (
          <>
            <AccessibleButton
              accessibilityLabel="Authenticate with Biometrics Button"
              style={[styles.button, styles.primaryButton]}
              onPress={handleAuthenticate}
              disabled={isAuthenticating}
            >
              {isAuthenticating ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text style={styles.buttonText}>Authenticate with Biometrics</Text>
              )}
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Use Backup Code Button"
              style={styles.button}
              onPress={() => setShowBackupCodeInput(!showBackupCodeInput)}
            >
              <Text style={styles.buttonText}>Use Backup Code</Text>
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Disable Biometric Authentication Button"
              style={[styles.button, styles.dangerButton]}
              onPress={handleDisableBiometric}
            >
              <Text style={styles.buttonText}>Disable Biometric Authentication</Text>
            </AccessibleButton>
          </>
        )}
      </View>

      {/* Backup Code Input */}
      {showBackupCodeInput && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Backup Code Authentication</Text>
          <TextInput
            style={styles.input}
            placeholder="Enter backup code"
            value={backupCode}
            onChangeText={setBackupCode}
            autoCapitalize="none"
            autoCorrect={false}
            accessibilityLabel="Backup Code Input"
          />
          <View style={styles.buttonRow}>
            <AccessibleButton
              accessibilityLabel="Verify Backup Code Button"
              style={[styles.button, styles.smallButton]}
              onPress={handleVerifyBackupCode}
            >
              <Text style={styles.buttonText}>Verify</Text>
            </AccessibleButton>
            <AccessibleButton
              accessibilityLabel="Cancel Backup Code Button"
              style={[styles.button, styles.smallButton, styles.secondaryButton]}
              onPress={() => {
                setShowBackupCodeInput(false);
                setBackupCode('');
              }}
            >
              <Text style={styles.buttonText}>Cancel</Text>
            </AccessibleButton>
          </View>
        </View>
      )}

      {/* Advanced Settings */}
      {showAdvancedSettings && config && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Advanced Settings</Text>
          
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Allow Device Credentials</Text>
            <Switch
              value={config.allowDeviceCredentials}
              onValueChange={(value) => handleConfigUpdate('allowDeviceCredentials', value)}
              accessibilityLabel="Toggle Allow Device Credentials"
            />
          </View>

          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Allow Backup Authentication</Text>
            <Switch
              value={config.allowBackupAuthentication}
              onValueChange={(value) => handleConfigUpdate('allowBackupAuthentication', value)}
              accessibilityLabel="Toggle Allow Backup Authentication"
            />
          </View>

          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Require Strong Biometrics</Text>
            <Switch
              value={config.requireStrongBiometrics}
              onValueChange={(value) => handleConfigUpdate('requireStrongBiometrics', value)}
              accessibilityLabel="Toggle Require Strong Biometrics"
            />
          </View>
        </View>
      )}

      {/* Usage Statistics */}
      {biometricData && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Usage Statistics</Text>
          <View style={styles.statsContainer}>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Total Uses:</Text>
              <Text style={styles.statValue}>{biometricData.usageCount}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Last Used:</Text>
              <Text style={styles.statValue}>
                {new Date(biometricData.lastUsed).toLocaleDateString()}
              </Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Backup Codes:</Text>
              <Text style={styles.statValue}>{biometricData.backupCodes.length}</Text>
            </View>
          </View>
        </View>
      )}
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
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#000',
  },
  loadingText: {
    textAlign: 'center',
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    textAlign: 'center',
    marginBottom: 20,
    fontSize: 16,
    color: '#FF3B30',
  },
  statusContainer: {
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
  statusLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  statusValue: {
    fontSize: 16,
    fontWeight: '500',
  },
  section: {
    marginBottom: 25,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
    color: '#333',
  },
  biometricTypeOption: {
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#E5E5EA',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  selectedBiometricType: {
    borderColor: '#007AFF',
    backgroundColor: '#F0F8FF',
  },
  biometricTypeText: {
    fontSize: 16,
    textAlign: 'center',
    color: '#333',
  },
  selectedBiometricTypeText: {
    color: '#007AFF',
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 15,
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
  primaryButton: {
    backgroundColor: '#34C759',
  },
  dangerButton: {
    backgroundColor: '#FF3B30',
  },
  secondaryButton: {
    backgroundColor: '#8E8E93',
  },
  smallButton: {
    flex: 1,
    marginHorizontal: 5,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    marginBottom: 15,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  settingLabel: {
    fontSize: 16,
    color: '#333',
  },
  statsContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  statLabel: {
    fontSize: 16,
    color: '#666',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
});


