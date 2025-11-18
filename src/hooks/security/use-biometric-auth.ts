import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';

interface BiometricAuthState {
  isSupported: boolean;
  isAvailable: boolean;
  isAuthenticating: boolean;
  error: string | null;
  credentials: any[];
  lastResult: any;
}

export function useBiometricAuth() {
  const [state, setState] = useState<BiometricAuthState>({
    isSupported: false,
    isAvailable: false,
    isAuthenticating: false,
    error: null,
    credentials: [],
    lastResult: null,
  });

  const checkSupport = useCallback(async () => {
    try {
      const support = {
        webauthn: typeof window !== 'undefined' && !!window.PublicKeyCredential,
        fingerprint: false,
        face: false,
        voice: false,
      };

      if (support.webauthn) {
        try {
          const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
          support.fingerprint = available;
          support.face = available;
        } catch (error) {
          console.warn('Platform authenticator check failed:', error);
        }
      }

      const isSupported = Object.values(support).some(Boolean);
      
      setState(prev => ({
        ...prev,
        isSupported,
        isAvailable: isSupported,
        error: null,
      }));

      return support;
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to check biometric support',
      }));
      return null;
    }
  }, []);

  const authenticate = useCallback(async (type: string = 'webauthn') => {
    try {
      setState(prev => ({ ...prev, isAuthenticating: true, error: null }));

      if (type === 'webauthn' && window.PublicKeyCredential) {
        const challenge = new Uint8Array(32);
        crypto.getRandomValues(challenge);

        const credential = await navigator.credentials.get({
          publicKey: {
            challenge,
            timeout: 30000,
            userVerification: 'required',
          },
        });

        if (credential) {
          const result = {
            success: true,
            method: 'webauthn',
            confidence: 0.95,
            timestamp: Date.now(),
          };

          setState(prev => ({
            ...prev,
            lastResult: result,
            isAuthenticating: false,
          }));

          toast.success('Authentication successful');
          return result;
        }
      }

      throw new Error('Authentication failed');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
      setState(prev => ({
        ...prev,
        error: errorMessage,
        isAuthenticating: false,
      }));
      toast.error(`Authentication failed: ${errorMessage}`);
      return null;
    }
  }, []);

  const register = useCallback(async (name: string) => {
    try {
      setState(prev => ({ ...prev, isAuthenticating: true, error: null }));

      if (window.PublicKeyCredential) {
        const challenge = new Uint8Array(32);
        crypto.getRandomValues(challenge);

        const credential = await navigator.credentials.create({
          publicKey: {
            challenge,
            rp: {
              name: 'Blatam Academy',
              id: window.location.hostname,
            },
            user: {
              id: new TextEncoder().encode('user-id'),
              name: 'user@example.com',
              displayName: name,
            },
            pubKeyCredParams: [
              { type: 'public-key', alg: -7 },
              { type: 'public-key', alg: -257 },
            ],
            authenticatorSelection: {
              authenticatorAttachment: 'platform',
              userVerification: 'required',
            },
            timeout: 30000,
            attestation: 'direct',
          },
        });

        if (credential) {
          const newCredential = {
            id: credential.id,
            type: 'webauthn',
            name,
            createdAt: Date.now(),
            isActive: true,
          };

          setState(prev => ({
            ...prev,
            credentials: [...prev.credentials, newCredential],
            isAuthenticating: false,
          }));

          toast.success('Credential registered successfully');
          return newCredential;
        }
      }

      throw new Error('Registration failed');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed';
      setState(prev => ({
        ...prev,
        error: errorMessage,
        isAuthenticating: false,
      }));
      toast.error(`Registration failed: ${errorMessage}`);
      return null;
    }
  }, []);

  useEffect(() => {
    checkSupport();
  }, [checkSupport]);

  return {
    ...state,
    authenticate,
    register,
    checkSupport,
  };
}