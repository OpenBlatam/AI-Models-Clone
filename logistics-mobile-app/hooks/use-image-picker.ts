import { useState } from 'react';
import * as ImagePicker from 'expo-image-picker';
import { usePermissions } from './use-permissions';

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

export function useImagePicker(options?: ImagePickerOptions) {
  const { granted, requestPermission } = usePermissions('camera');
  const [image, setImage] = useState<ImageResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function pickImage(source: 'camera' | 'library') {
    try {
      setIsLoading(true);
      setError(null);

      if (source === 'camera' && !granted) {
        const hasPermission = await requestPermission();
        if (!hasPermission) {
          setError('Camera permission denied');
          return;
        }
      }

      let result: ImagePicker.ImagePickerResult;

      if (source === 'camera') {
        result = await ImagePicker.launchCameraAsync({
          allowsEditing: options?.allowsEditing ?? true,
          aspect: options?.aspect,
          quality: options?.quality ?? 0.8,
          mediaTypes: options?.mediaTypes ?? ImagePicker.MediaTypeOptions.Images,
        });
      } else {
        result = await ImagePicker.launchImageLibraryAsync({
          allowsEditing: options?.allowsEditing ?? true,
          aspect: options?.aspect,
          quality: options?.quality ?? 0.8,
          mediaTypes: options?.mediaTypes ?? ImagePicker.MediaTypeOptions.Images,
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
      setError(err instanceof Error ? err.message : 'Failed to pick image');
    } finally {
      setIsLoading(false);
    }
  }

  function clearImage() {
    setImage(null);
    setError(null);
  }

  return {
    image,
    isLoading,
    error,
    pickImage,
    clearImage,
    hasPermission: granted,
  };
}


