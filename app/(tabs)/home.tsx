import React, { useCallback } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { OptimizedList } from '../../components/OptimizedList';
import { OptimizedImage } from '../../components/OptimizedImage';
import { useApi } from '../../hooks/useApi';
import { useAppStore } from '../../lib/store';

interface Post {
  id: string;
  content: string;
  author: {
    id: string;
    name: string;
    avatar?: string;
  };
  imageUrl?: string;
  timestamp: string;
  likes: number;
  comments: number;
}

const PostCard: React.FC<{ post: Post; onPress: () => void }> = React.memo(({ post, onPress }) => (
  <TouchableOpacity style={styles.postCard} onPress={onPress}>
    <View style={styles.postHeader}>
      <OptimizedImage
        uri={post.author.avatar || 'https://via.placeholder.com/40'}
        width={40}
        height={40}
        borderRadius={20}
      />
      <View style={styles.postInfo}>
        <Text style={styles.authorName}>{post.author.name}</Text>
        <Text style={styles.timestamp}>{post.timestamp}</Text>
      </View>
    </View>
    <Text style={styles.postContent}>{post.content}</Text>
    {post.imageUrl && (
      <OptimizedImage
        uri={post.imageUrl}
        width="100%"
        height={200}
        borderRadius={8}
        style={styles.postImage}
      />
    )}
    <View style={styles.postActions}>
      <TouchableOpacity style={styles.actionButton}>
        <Ionicons name="heart-outline" size={20} color="#8E8E93" />
        <Text style={styles.actionText}>{post.likes}</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.actionButton}>
        <Ionicons name="chatbubble-outline" size={20} color="#8E8E93" />
        <Text style={styles.actionText}>{post.comments}</Text>
      </TouchableOpacity>
    </View>
  </TouchableOpacity>
));

export default function HomeScreen() {
  const router = useRouter();
  const { user } = useAppStore();
  const { data: postsResponse, isLoading, isError, refetch } = useApi.usePosts();

  const posts = postsResponse?.data || [];

  const handlePostPress = useCallback((postId: string) => {
    router.push(`/posts/${postId}`);
  }, [router]);

  const handleCreatePost = useCallback(() => {
    router.push('/(modals)/create-post');
  }, [router]);

  const renderPost = useCallback((post: Post) => (
    <PostCard
      post={post}
      onPress={() => handlePostPress(post.id)}
    />
  ), [handlePostPress]);

  const keyExtractor = useCallback((post: Post) => post.id, []);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Home</Text>
        <TouchableOpacity
          style={styles.createButton}
          onPress={handleCreatePost}
        >
          <Ionicons name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <OptimizedList
        data={posts}
        renderItem={renderPost}
        keyExtractor={keyExtractor}
        isLoading={isLoading}
        isError={isError}
        errorMessage="Failed to load posts"
        emptyMessage="No posts yet"
        estimatedItemSize={200}
        onRefresh={refetch}
        refreshing={isLoading}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000000',
  },
  createButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  postCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: 16,
    marginVertical: 8,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  postHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  postInfo: {
    marginLeft: 12,
    flex: 1,
  },
  authorName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#000000',
  },
  timestamp: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 2,
  },
  postContent: {
    fontSize: 16,
    lineHeight: 24,
    color: '#000000',
    marginBottom: 12,
  },
  postImage: {
    marginBottom: 12,
  },
  postActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 24,
  },
  actionText: {
    marginLeft: 4,
    fontSize: 14,
    color: '#8E8E93',
  },
}); 