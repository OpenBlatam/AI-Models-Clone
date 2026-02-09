import { useNetworkStatus } from './use-network-status';

/**
 * Hook that returns a simple boolean for online status
 */
export function useOnlineStatus(): boolean {
  const { isConnected } = useNetworkStatus();
  return isConnected ?? false;
}


