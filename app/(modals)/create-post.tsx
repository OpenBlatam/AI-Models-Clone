import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function CreatePostModal() {
  const router = useRouter();
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleClose = useCallback(() => {
    if (content.trim()) {
      Alert.alert(
        'Discard Post',
        'Are you sure you want to discard this post?',
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Discard', 
            style: 'destructive',
            onPress: () => router.back()
          },
        ]
      );
    } else {
      router.back();
    }
  }, [content, router]);

  const handleSubmit = useCallback(async () => {
    if (!content.trim()) return;

    setIsSubmitting(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      Alert.alert('Success', 'Post created successfully!');
      router.back();
    } catch (error) {
      Alert.alert('Error', 'Failed to create post. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [content, router]);

  const handleAddImage = useCallback(() => {
    // Image picker logic would go here
    Alert.alert('Image Picker', 'Image picker functionality would be implemented here');
  }, []);

  const handleAddLocation = useCallback(() => {
    // Location picker logic would go here
    Alert.alert('Location Picker', 'Location picker functionality would be implemented here');
  }, []);

  const isSubmitDisabled = !content.trim() || isSubmitting;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.header}>
        <TouchableOpacity onPress={handleClose}>
          <Text style={styles.cancelButton}>Cancel</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Create Post</Text>
        <TouchableOpacity
          onPress={handleSubmit}
          disabled={isSubmitDisabled}
        >
          <Text
            style={[
              styles.postButton,
              { color: isSubmitDisabled ? '#C7C7CC' : '#007AFF' },
            ]}
          >
            {isSubmitting ? 'Posting...' : 'Post'}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} keyboardShouldPersistTaps="handled">
        <TextInput
          style={styles.textInput}
          placeholder="What's on your mind?"
          placeholderTextColor="#8E8E93"
          value={content}
          onChangeText={setContent}
          multiline
          autoFocus
          textAlignVertical="top"
          maxLength={1000}
        />

        <View style={styles.actionsContainer}>
          <TouchableOpacity style={styles.actionButton} onPress={handleAddImage}>
            <Ionicons name="image-outline" size={24} color="#007AFF" />
            <Text style={styles.actionText}>Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton} onPress={handleAddLocation}>
            <Ionicons name="location-outline" size={24} color="#007AFF" />
            <Text style={styles.actionText}>Location</Text>
          </TouchableOpacity>
        </View>

        {content.length > 0 && (
          <View style={styles.characterCount}>
            <Text style={styles.characterCountText}>
              {content.length}/1000
            </Text>
          </View>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
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
  cancelButton: {
    fontSize: 16,
    color: '#007AFF',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#000000',
  },
  postButton: {
    fontSize: 16,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  textInput: {
    fontSize: 16,
    lineHeight: 24,
    minHeight: 120,
    color: '#000000',
    marginBottom: 16,
  },
  actionsContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 24,
  },
  actionText: {
    marginLeft: 8,
    fontSize: 16,
    color: '#007AFF',
  },
  characterCount: {
    alignItems: 'flex-end',
  },
  characterCountText: {
    fontSize: 12,
    color: '#8E8E93',
  },
}); 