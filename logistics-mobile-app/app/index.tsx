import { Redirect } from 'expo-router';
import { useAuthStore } from '@/store/auth-store';

export default function Index() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    // In a real app, you'd redirect to login
    // For now, we'll just show the dashboard
  }

  return <Redirect href="/(tabs)" />;
}


