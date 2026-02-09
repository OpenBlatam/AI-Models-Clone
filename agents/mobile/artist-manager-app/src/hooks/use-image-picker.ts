import { useState, useCallback } from 'react';
import * as ImagePicker from 'expo-image-picker';
import { Alert } from 'react-native';

interface ImagePickerOptions {
  allowsEditing?: boolean;
  aspect?: [number, number];
  quality?: number;
  mediaTypes?: ImagePicker.MediaTypeOptions;
}

interface ImageResult {
  uri: string;
  width: number;
  height: number;
  type?: string;
  fileName?: string;
}

/**
 * Hook for picking images from gallery or camera
 */
export function useImagePicker(options: ImagePickerOptions = {}) {
  const [image, setImage] = useState<ImageResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const requestPermissions = useCallback(async () => {
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    const { status: mediaStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (cameraStatus !== 'granted' || mediaStatus !== 'granted') {
      Alert.alert('Permission Required', 'Camera and media library permissions are required');
      return false;
    }

    return true;
  }, []);

  const pickImage = useCallback(
    async (source: 'gallery' | 'camera' = 'gallery') => {
      setIsLoading(true);
      setError(null);

      try {
        const hasPermission = await requestPermissions();
        if (!hasPermission) {
          setIsLoading(false);
          return;
        }

        let result: ImagePicker.ImagePickerResult;

        if (source === 'camera') {
          result = await ImagePicker.launchCameraAsync({
            allowsEditing: options.allowsEditing,
            aspect: options.aspect,
            quality: options.quality ?? 1,
            mediaTypes: options.mediaTypes ?? ImagePicker.MediaTypeOptions.Images,
          });
        } else {
          result = await ImagePicker.launchImageLibraryAsync({
            allowsEditing: options.allowsEditing,
            aspect: options.aspect,
            quality: options.quality ?? 1,
            mediaTypes: options.mediaTypes ?? ImagePicker.MediaTypeOptions.Images,
          });
        }

        if (!result.canceled && result.assets && result.assets.length > 0) {
          const asset = result.assets[0];
          setImage({
            uri: asset.uri,
            width: asset.width,
            height: asset.height,
            type: asset.type,
            fileName: asset.fileName,
          });
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to pick image');
        setError(error);
      } finally {
        setIsLoading(false);
      }
    },
    [options, requestPermissions]
  );

  const clearImage = useCallback(() => {
    setImage(null);
    setError(null);
  }, []);

  return {
    image,
    isLoading,
    error,
    pickImage,
    clearImage,
  };
}


