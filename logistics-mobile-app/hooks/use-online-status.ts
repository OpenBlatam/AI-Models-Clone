import { useNetworkStatus } from './use-network-status';

export function useOnlineStatus() {
  const { isConnected, isInternetReachable } = useNetworkStatus();

  return {
    isOnline: isConnected === true && isInternetReachable === true,
    isOffline: isConnected === false || isInternetReachable === false,
    isConnected,
    isInternetReachable,
  };
}


