import { useState, useCallback } from 'react';
import * as ImagePicker from 'expo-image-picker';
import * as MediaLibrary from 'expo-media-library';
import { Platform } from 'react-native';

type PermissionType = 'camera' | 'mediaLibrary' | 'location' | 'notifications';

interface PermissionState {
  status: 'granted' | 'denied' | 'undetermined';
  granted: boolean;
}

/**
 * Hook for managing device permissions
 */
export function usePermissions(permissionTypes: PermissionType[]) {
  const [permissions, setPermissions] = useState<Record<string, PermissionState>>({});
  const [isLoading, setIsLoading] = useState(false);

  const checkPermission = useCallback(async (type: PermissionType) => {
    try {
      if (type === 'camera') {
        const { status } = await ImagePicker.getCameraPermissionsAsync();
        return { status, granted: status === 'granted' };
      }
      if (type === 'mediaLibrary') {
        const { status } = await ImagePicker.getMediaLibraryPermissionsAsync();
        return { status, granted: status === 'granted' };
      }
      return { status: 'undetermined' as const, granted: false };
    } catch (error) {
      console.error(`Error checking ${type} permission:`, error);
      return { status: 'undetermined' as const, granted: false };
    }
  }, []);

  const requestPermission = useCallback(async (type: PermissionType) => {
    try {
      if (type === 'camera') {
        const { status } = await ImagePicker.requestCameraPermissionsAsync();
        return { status, granted: status === 'granted' };
      }
      if (type === 'mediaLibrary') {
        const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
        return { status, granted: status === 'granted' };
      }
      return { status: 'undetermined' as const, granted: false };
    } catch (error) {
      console.error(`Error requesting ${type} permission:`, error);
      return { status: 'undetermined' as const, granted: false };
    }
  }, []);

  const checkPermissions = useCallback(async () => {
    setIsLoading(true);
    try {
      const state: Record<string, PermissionState> = {};
      for (const type of permissionTypes) {
        const result = await checkPermission(type);
        state[type] = result;
      }
      setPermissions(state);
    } catch (error) {
      console.error('Error checking permissions:', error);
    } finally {
      setIsLoading(false);
    }
  }, [permissionTypes, checkPermission]);

  const requestPermissions = useCallback(async () => {
    setIsLoading(true);
    try {
      const state: Record<string, PermissionState> = {};
      for (const type of permissionTypes) {
        const result = await requestPermission(type);
        state[type] = result;
      }
      setPermissions(state);
      return state;
    } catch (error) {
      console.error('Error requesting permissions:', error);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [permissionTypes, requestPermission]);

  return {
    permissions,
    isLoading,
    checkPermissions,
    requestPermissions,
  };
}

