import React, { Suspense } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { OptimizedSkeleton } from '../../components/feedback/OptimizedSkeleton';

// Lazy load non-critical components
const LazyProfileStats = React.lazy(() => import('../../components/profile/ProfileStats'));
const LazyProfileActions = React.lazy(() => import('../../components/profile/ProfileActions'));
const LazyProfileSettings = React.lazy(() => import('../../components/profile/ProfileSettings'));

interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar: string;
  bio: string;
  followers: number;
  following: number;
  posts: number;
}

const mockUserProfile: UserProfile = {
  id: '1',
  name: 'John Doe',
  email: 'john.doe@example.com',
  avatar: 'https://via.placeholder.com/150',
  bio: 'Software developer passionate about React Native and mobile development.',
  followers: 1234,
  following: 567,
  posts: 89,
};

const ProfileStat: React.FC<{ label: string; value: number }> = React.memo(({ label, value }) => (
  <View style={styles.stat}>
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statLabel}>{label}</Text>
  </View>
));

const ProfileAction: React.FC<{ title: string; onPress: () => void }> = React.memo(({ title, onPress }) => (
  <TouchableOpacity style={styles.action} onPress={onPress}>
    <Text style={styles.actionText}>{title}</Text>
  </TouchableOpacity>
));

const ProfileScreen: React.FC = () => {
  const handleEditProfile = () => {
    console.log('Edit profile pressed');
  };

  const handleSettings = () => {
    console.log('Settings pressed');
  };

  const handleLogout = () => {
    console.log('Logout pressed');
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.name}>{mockUserProfile.name}</Text>
        <Text style={styles.email}>{mockUserProfile.email}</Text>
        <Text style={styles.bio}>{mockUserProfile.bio}</Text>
      </View>

      <View style={styles.stats}>
        <ProfileStat label="Followers" value={mockUserProfile.followers} />
        <ProfileStat label="Following" value={mockUserProfile.following} />
        <ProfileStat label="Posts" value={mockUserProfile.posts} />
      </View>

      <Suspense fallback={<OptimizedSkeleton variant="card" />}>
        <LazyProfileStats />
      </Suspense>

      <View style={styles.actions}>
        <ProfileAction title="Edit Profile" onPress={handleEditProfile} />
        <ProfileAction title="Settings" onPress={handleSettings} />
        <ProfileAction title="Logout" onPress={handleLogout} />
      </View>

      <Suspense fallback={<OptimizedSkeleton variant="list" />}>
        <LazyProfileActions />
      </Suspense>

      <Suspense fallback={<OptimizedSkeleton variant="card" />}>
        <LazyProfileSettings />
      </Suspense>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  email: {
    fontSize: 16,
    color: '#666',
    marginBottom: 10,
  },
  bio: {
    fontSize: 14,
    color: '#333',
    textAlign: 'center',
    lineHeight: 20,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 20,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  actions: {
    padding: 20,
  },
  action: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center',
  },
  actionText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProfileScreen; 