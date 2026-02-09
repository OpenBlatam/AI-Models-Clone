import { useState, useEffect } from 'react';
import * as Location from 'expo-location';
import { usePermissions } from './use-permissions';

interface LocationData {
  latitude: number;
  longitude: number;
  accuracy?: number;
  altitude?: number | null;
  heading?: number | null;
  speed?: number | null;
}

export function useLocation(options?: Location.LocationOptions) {
  const { granted, requestPermission } = usePermissions('location');
  const [location, setLocation] = useState<LocationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!granted) {
      return;
    }

    async function getCurrentLocation() {
      try {
        setIsLoading(true);
        const currentLocation = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
          ...options,
        });

        setLocation({
          latitude: currentLocation.coords.latitude,
          longitude: currentLocation.coords.longitude,
          accuracy: currentLocation.coords.accuracy || undefined,
          altitude: currentLocation.coords.altitude,
          heading: currentLocation.coords.heading,
          speed: currentLocation.coords.speed,
        });
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get location');
      } finally {
        setIsLoading(false);
      }
    }

    getCurrentLocation();
  }, [granted, options]);

  async function refreshLocation() {
    if (!granted) {
      const hasPermission = await requestPermission();
      if (!hasPermission) {
        setError('Location permission denied');
        return;
      }
    }

    try {
      setIsLoading(true);
      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
        ...options,
      });

      setLocation({
        latitude: currentLocation.coords.latitude,
        longitude: currentLocation.coords.longitude,
        accuracy: currentLocation.coords.accuracy || undefined,
        altitude: currentLocation.coords.altitude,
        heading: currentLocation.coords.heading,
        speed: currentLocation.coords.speed,
      });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get location');
    } finally {
      setIsLoading(false);
    }
  }

  return {
    location,
    error,
    isLoading,
    refreshLocation,
    hasPermission: granted,
  };
}


