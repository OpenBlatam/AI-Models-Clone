import { useState, useEffect } from 'react';
import * as Updates from 'expo-updates';

interface UpdateInfo {
  isAvailable: boolean;
  isDownloaded: boolean;
  manifest: Updates.Manifest | null;
}

/**
 * Hook for checking Expo OTA updates
 */
export function useUpdateCheck() {
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo>({
    isAvailable: false,
    isDownloaded: false,
    manifest: null,
  });
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const checkForUpdate = async () => {
    if (!__DEV__ && Updates.isEnabled) {
      setIsChecking(true);
      setError(null);

      try {
        const update = await Updates.checkForUpdateAsync();
        setUpdateInfo({
          isAvailable: update.isAvailable,
          isDownloaded: false,
          manifest: update.manifest,
        });
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to check for updates'));
      } finally {
        setIsChecking(false);
      }
    }
  };

  const downloadUpdate = async () => {
    if (!__DEV__ && Updates.isEnabled && updateInfo.isAvailable) {
      setIsChecking(true);
      setError(null);

      try {
        const result = await Updates.fetchUpdateAsync();
        setUpdateInfo((prev) => ({
          ...prev,
          isDownloaded: result.isNew,
        }));
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to download update'));
      } finally {
        setIsChecking(false);
      }
    }
  };

  const reloadApp = async () => {
    if (updateInfo.isDownloaded) {
      await Updates.reloadAsync();
    }
  };

  useEffect(() => {
    checkForUpdate();
  }, []);

  return {
    ...updateInfo,
    isChecking,
    error,
    checkForUpdate,
    downloadUpdate,
    reloadApp,
  };
}


