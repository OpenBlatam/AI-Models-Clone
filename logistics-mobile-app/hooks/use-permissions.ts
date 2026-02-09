import { useState, useEffect } from 'react';
import * as Location from 'expo-location';
import * as Camera from 'expo-camera';
import { Platform } from 'react-native';

type PermissionType = 'location' | 'camera';

interface PermissionStatus {
  granted: boolean;
  canAskAgain: boolean;
  status: string;
}

export function usePermissions(permissionType: PermissionType) {
  const [permissionStatus, setPermissionStatus] = useState<PermissionStatus>({
    granted: false,
    canAskAgain: true,
    status: 'undetermined',
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function checkPermission() {
      try {
        let status;

        if (permissionType === 'location') {
          const { status: locationStatus } = await Location.getForegroundPermissionsAsync();
          status = locationStatus;
        } else if (permissionType === 'camera') {
          const { status: cameraStatus } = await Camera.getCameraPermissionsAsync();
          status = cameraStatus;
        }

        setPermissionStatus({
          granted: status === 'granted',
          canAskAgain: status !== 'denied' || Platform.OS === 'ios',
          status: status || 'undetermined',
        });
      } catch (error) {
        console.error('Error checking permission:', error);
      } finally {
        setIsLoading(false);
      }
    }

    checkPermission();
  }, [permissionType]);

  async function requestPermission() {
    try {
      setIsLoading(true);
      let status;

      if (permissionType === 'location') {
        const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
        status = locationStatus;
      } else if (permissionType === 'camera') {
        const { status: cameraStatus } = await Camera.requestCameraPermissionsAsync();
        status = cameraStatus;
      }

      setPermissionStatus({
        granted: status === 'granted',
        canAskAgain: status !== 'denied' || Platform.OS === 'ios',
        status: status || 'undetermined',
      });

      return status === 'granted';
    } catch (error) {
      console.error('Error requesting permission:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  }

  return {
    ...permissionStatus,
    isLoading,
    requestPermission,
  };
}


