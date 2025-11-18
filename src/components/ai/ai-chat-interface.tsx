/**
 * @fileoverview Comprehensive AI chat interface component
 * @author Blaze AI Team
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAI } from '../../hooks/ai/use-ai';
import { AccessibleButton } from '../accessibility/accessible-button';
import {
  AITextRequest,
  AIVisionRequest,
  AIAudioRequest,
  AIMultimodalRequest,
  AIResponseUnion,
  AIModel,
} from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: number;
  modelId?: string;
  requestType?: string;
  isError?: boolean;
  metadata?: Record<string, unknown>;
}

interface AIRequestForm {
  prompt: string;
  modelId: string;
  requestType: 'text' | 'vision' | 'audio' | 'multimodal';
  images: string[];
  audioData: string;
  text: string;
  maxTokens?: number;
  temperature?: number;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * Comprehensive AI chat interface component
 * Provides a user-friendly way to interact with the AI system
 */
export function AIChatInterface(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const ai = useAI();
  const scrollViewRef = useRef<ScrollView>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [form, setForm] = useState<AIRequestForm>({
    prompt: '',
    modelId: 'gpt-4',
    requestType: 'text',
    images: [],
    audioData: '',
    text: '',
  });
  const [isTyping, setIsTyping] = useState(false);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Initialize AI manager on component mount
  useEffect(() => {
    if (!ai.isInitialized) {
      ai.initialize();
    }
  }, [ai]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollViewRef.current && messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSendMessage = useCallback(async () => {
    if (!form.prompt.trim() || ai.isLoading) return;

    try {
      setIsTyping(true);

      // Add user message
      const userMessage: ChatMessage = {
        id: `user_${Date.now()}`,
        type: 'user',
        content: form.prompt,
        timestamp: Date.now(),
        requestType: form.requestType,
      };

      setMessages(prev => [...prev, userMessage]);

      // Create AI request based on type
      const request = createAIRequest(form);

      // Process request
      const response = await ai.processRequest(request);

      // Add AI response
      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        type: 'ai',
        content: response.content,
        timestamp: Date.now(),
        modelId: response.modelId,
        metadata: {
          responseType: response.type,
          usage: response.usage,
        },
      };

      setMessages(prev => [...prev, aiMessage]);

      // Clear form
      setForm(prev => ({ ...prev, prompt: '' }));
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        type: 'ai',
        content: error instanceof Error ? error.message : 'An error occurred',
        timestamp: Date.now(),
        isError: true,
      };

      setMessages(prev => [...prev, errorMessage]);
      Alert.alert('Error', 'Failed to process AI request');
    } finally {
      setIsTyping(false);
    }
  }, [form, ai, ai.isLoading]);

  const handleModelChange = useCallback((modelId: string) => {
    setForm(prev => ({ ...prev, modelId }));
  }, []);

  const handleRequestTypeChange = useCallback((requestType: AIRequestForm['requestType']) => {
    setForm(prev => ({ ...prev, requestType }));
  }, []);

  const handleAddImage = useCallback(() => {
    // In a real app, this would open image picker
    Alert.alert('Image Upload', 'Image upload functionality would be implemented here');
  }, []);

  const handleAddAudio = useCallback(() => {
    // In a real app, this would open audio picker
    Alert.alert('Audio Upload', 'Audio upload functionality would be implemented here');
  }, []);

  const handleClearChat = useCallback(() => {
    Alert.alert(
      'Clear Chat',
      'Are you sure you want to clear all messages?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => setMessages([]),
        },
      ]
    );
  }, []);

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  const createAIRequest = (formData: AIRequestForm) => {
    const baseRequest = {
      id: `request_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      modelId: formData.modelId,
      timestamp: Date.now(),
      userId: 'current_user', // In real app, get from auth context
      priority: 'medium' as const,
    };

    switch (formData.requestType) {
      case 'text':
        return {
          ...baseRequest,
          type: 'text' as const,
          prompt: formData.prompt,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AITextRequest;

      case 'vision':
        return {
          ...baseRequest,
          type: 'vision' as const,
          prompt: formData.prompt,
          images: formData.images,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AIVisionRequest;

      case 'audio':
        return {
          ...baseRequest,
          type: 'audio' as const,
          prompt: formData.prompt,
          audioData: formData.audioData,
          format: 'mp3' as const,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AIAudioRequest;

      case 'multimodal':
        return {
          ...baseRequest,
          type: 'multimodal' as const,
          prompt: formData.prompt,
          text: formData.text,
          images: formData.images,
          audio: formData.audioData,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AIMultimodalRequest;

      default:
        throw new Error(`Unsupported request type: ${formData.requestType}`);
    }
  };

  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getModelDisplayName = (modelId: string): string => {
    const model = ai.models.find(m => m.id === modelId);
    return model?.name || modelId;
  };

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderMessage = (message: ChatMessage): JSX.Element => {
    const isUser = message.type === 'user';
    const messageStyle = isUser ? styles.userMessage : styles.aiMessage;
    const textStyle = isUser ? styles.userMessageText : styles.aiMessageText;

    return (
      <View key={message.id} style={[styles.messageContainer, messageStyle]}>
        <View style={styles.messageHeader}>
          <Text style={styles.messageSender}>
            {isUser ? 'You' : 'AI Assistant'}
          </Text>
          <Text style={styles.messageTimestamp}>
            {formatTimestamp(message.timestamp)}
          </Text>
        </View>

        <Text style={textStyle}>{message.content}</Text>

        {message.modelId && (
          <Text style={styles.modelInfo}>
            Model: {getModelDisplayName(message.modelId)}
          </Text>
        )}

        {message.requestType && (
          <Text style={styles.requestTypeInfo}>
            Type: {message.requestType}
          </Text>
        )}

        {message.metadata?.usage && (
          <View style={styles.usageInfo}>
            <Text style={styles.usageText}>
              Tokens: {message.metadata.usage.totalTokens}
            </Text>
          </View>
        )}
      </View>
    );
  };

  const renderRequestTypeSelector = (): JSX.Element => (
    <View style={styles.requestTypeContainer}>
      <Text style={styles.sectionTitle}>Request Type</Text>
      <View style={styles.requestTypeButtons}>
        {(['text', 'vision', 'audio', 'multimodal'] as const).map(type => (
          <TouchableOpacity
            key={type}
            style={[
              styles.requestTypeButton,
              form.requestType === type && styles.requestTypeButtonActive,
            ]}
            onPress={() => handleRequestTypeChange(type)}
          >
            <Text
              style={[
                styles.requestTypeButtonText,
                form.requestType === type && styles.requestTypeButtonTextActive,
              ]}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderModelSelector = (): JSX.Element => (
    <View style={styles.modelSelectorContainer}>
      <Text style={styles.sectionTitle}>AI Model</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.modelButtons}>
          {ai.models.map(model => (
            <TouchableOpacity
              key={model.id}
              style={[
                styles.modelButton,
                form.modelId === model.id && styles.modelButtonActive,
              ]}
              onPress={() => handleModelChange(model.id)}
            >
              <Text
                style={[
                  styles.modelButtonText,
                  form.modelId === model.id && styles.modelButtonTextActive,
                ]}
              >
                {model.name}
              </Text>
              <Text style={styles.modelButtonDescription}>
                {model.description}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );

  const renderInputForm = (): JSX.Element => (
    <View style={styles.inputFormContainer}>
      <View style={styles.inputRow}>
        <TextInput
          style={styles.textInput}
          placeholder="Enter your prompt..."
          value={form.prompt}
          onChangeText={(text) => setForm(prev => ({ ...prev, prompt: text }))}
          multiline
          maxLength={1000}
          editable={!ai.isLoading}
        />
      </View>

      {form.requestType === 'multimodal' && (
        <View style={styles.multimodalInputs}>
          <TextInput
            style={styles.textInput}
            placeholder="Additional text content..."
            value={form.text}
            onChangeText={(text) => setForm(prev => ({ ...prev, text }))}
            multiline
            maxLength={500}
          />
        </View>
      )}

      {(form.requestType === 'vision' || form.requestType === 'multimodal') && (
        <View style={styles.mediaInputs}>
          <AccessibleButton
            accessibilityLabel="Add image"
            onPress={handleAddImage}
            style={styles.mediaButton}
          >
            <Text style={styles.mediaButtonText}>📷 Add Image</Text>
          </AccessibleButton>
        </View>
      )}

      {(form.requestType === 'audio' || form.requestType === 'multimodal') && (
        <View style={styles.mediaInputs}>
          <AccessibleButton
            accessibilityLabel="Add audio"
            onPress={handleAddAudio}
            style={styles.mediaButton}
          >
            <Text style={styles.mediaButtonText}>🎵 Add Audio</Text>
          </AccessibleButton>
        </View>
      )}

      <View style={styles.sendButtonContainer}>
        <AccessibleButton
          accessibilityLabel="Send message"
          onPress={handleSendMessage}
          disabled={!form.prompt.trim() || ai.isLoading}
          style={[
            styles.sendButton,
            (!form.prompt.trim() || ai.isLoading) && styles.sendButtonDisabled,
          ]}
        >
          {ai.isLoading ? (
            <ActivityIndicator color="#ffffff" size="small" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </AccessibleButton>
      </View>
    </View>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Blaze AI Chat</Text>
          <View style={styles.headerActions}>
            <AccessibleButton
              accessibilityLabel="Clear chat"
              onPress={handleClearChat}
              style={styles.clearButton}
            >
              <Text style={styles.clearButtonText}>Clear</Text>
            </AccessibleButton>
          </View>
        </View>

        {/* Request Type and Model Selectors */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.selectorsContainer}>
            {renderRequestTypeSelector()}
            {renderModelSelector()}
          </View>
        </ScrollView>

        {/* Messages */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        >
          {messages.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>
                Start a conversation with AI
              </Text>
              <Text style={styles.emptyStateSubtext}>
                Choose a model and request type, then enter your prompt
              </Text>
            </View>
          ) : (
            messages.map(renderMessage)
          )}

          {isTyping && (
            <View style={styles.typingIndicator}>
              <Text style={styles.typingText}>AI is thinking...</Text>
              <ActivityIndicator size="small" color="#666" />
            </View>
          )}
        </ScrollView>

        {/* Input Form */}
        {renderInputForm()}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  headerActions: {
    flexDirection: 'row',
  },
  clearButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#ff6b6b',
    borderRadius: 6,
  },
  clearButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  selectorsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  requestTypeContainer: {
    marginRight: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  requestTypeButtons: {
    flexDirection: 'row',
  },
  requestTypeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    marginRight: 8,
  },
  requestTypeButtonActive: {
    backgroundColor: '#007AFF',
  },
  requestTypeButtonText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  requestTypeButtonTextActive: {
    color: '#ffffff',
  },
  modelSelectorContainer: {
    flex: 1,
  },
  modelButtons: {
    flexDirection: 'row',
  },
  modelButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    marginRight: 12,
    minWidth: 120,
  },
  modelButtonActive: {
    backgroundColor: '#007AFF',
  },
  modelButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  modelButtonTextActive: {
    color: '#ffffff',
  },
  modelButtonDescription: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center',
    marginTop: 2,
  },
  messagesContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  messagesContent: {
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  messageContainer: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
    maxWidth: '85%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  messageSender: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
  },
  messageTimestamp: {
    fontSize: 10,
    color: '#ffffff',
    opacity: 0.8,
  },
  userMessageText: {
    fontSize: 16,
    color: '#ffffff',
    lineHeight: 22,
  },
  aiMessageText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 22,
  },
  modelInfo: {
    fontSize: 11,
    color: '#666',
    marginTop: 6,
    fontStyle: 'italic',
  },
  requestTypeInfo: {
    fontSize: 11,
    color: '#666',
    marginTop: 2,
    fontStyle: 'italic',
  },
  usageInfo: {
    marginTop: 6,
    paddingTop: 6,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  usageText: {
    fontSize: 10,
    color: '#999',
  },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
  },
  typingText: {
    fontSize: 14,
    color: '#666',
    marginRight: 8,
  },
  inputFormContainer: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  inputRow: {
    marginBottom: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 48,
    backgroundColor: '#ffffff',
  },
  multimodalInputs: {
    marginBottom: 12,
  },
  mediaInputs: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  mediaButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    marginRight: 12,
  },
  mediaButtonText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  sendButtonContainer: {
    alignItems: 'flex-end',
  },
  sendButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
  sendButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

// ============================================================================
// EXPORTS
// ============================================================================

export default AIChatInterface;
 * @fileoverview Comprehensive AI chat interface component
 * @author Blaze AI Team
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAI } from '../../hooks/ai/use-ai';
import { AccessibleButton } from '../accessibility/accessible-button';
import {
  AITextRequest,
  AIVisionRequest,
  AIAudioRequest,
  AIMultimodalRequest,
  AIResponseUnion,
  AIModel,
} from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: number;
  modelId?: string;
  requestType?: string;
  isError?: boolean;
  metadata?: Record<string, unknown>;
}

interface AIRequestForm {
  prompt: string;
  modelId: string;
  requestType: 'text' | 'vision' | 'audio' | 'multimodal';
  images: string[];
  audioData: string;
  text: string;
  maxTokens?: number;
  temperature?: number;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * Comprehensive AI chat interface component
 * Provides a user-friendly way to interact with the AI system
 */
export function AIChatInterface(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const ai = useAI();
  const scrollViewRef = useRef<ScrollView>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [form, setForm] = useState<AIRequestForm>({
    prompt: '',
    modelId: 'gpt-4',
    requestType: 'text',
    images: [],
    audioData: '',
    text: '',
  });
  const [isTyping, setIsTyping] = useState(false);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Initialize AI manager on component mount
  useEffect(() => {
    if (!ai.isInitialized) {
      ai.initialize();
    }
  }, [ai]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollViewRef.current && messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleSendMessage = useCallback(async () => {
    if (!form.prompt.trim() || ai.isLoading) return;

    try {
      setIsTyping(true);

      // Add user message
      const userMessage: ChatMessage = {
        id: `user_${Date.now()}`,
        type: 'user',
        content: form.prompt,
        timestamp: Date.now(),
        requestType: form.requestType,
      };

      setMessages(prev => [...prev, userMessage]);

      // Create AI request based on type
      const request = createAIRequest(form);

      // Process request
      const response = await ai.processRequest(request);

      // Add AI response
      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        type: 'ai',
        content: response.content,
        timestamp: Date.now(),
        modelId: response.modelId,
        metadata: {
          responseType: response.type,
          usage: response.usage,
        },
      };

      setMessages(prev => [...prev, aiMessage]);

      // Clear form
      setForm(prev => ({ ...prev, prompt: '' }));
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        type: 'ai',
        content: error instanceof Error ? error.message : 'An error occurred',
        timestamp: Date.now(),
        isError: true,
      };

      setMessages(prev => [...prev, errorMessage]);
      Alert.alert('Error', 'Failed to process AI request');
    } finally {
      setIsTyping(false);
    }
  }, [form, ai, ai.isLoading]);

  const handleModelChange = useCallback((modelId: string) => {
    setForm(prev => ({ ...prev, modelId }));
  }, []);

  const handleRequestTypeChange = useCallback((requestType: AIRequestForm['requestType']) => {
    setForm(prev => ({ ...prev, requestType }));
  }, []);

  const handleAddImage = useCallback(() => {
    // In a real app, this would open image picker
    Alert.alert('Image Upload', 'Image upload functionality would be implemented here');
  }, []);

  const handleAddAudio = useCallback(() => {
    // In a real app, this would open audio picker
    Alert.alert('Audio Upload', 'Audio upload functionality would be implemented here');
  }, []);

  const handleClearChat = useCallback(() => {
    Alert.alert(
      'Clear Chat',
      'Are you sure you want to clear all messages?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => setMessages([]),
        },
      ]
    );
  }, []);

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  const createAIRequest = (formData: AIRequestForm) => {
    const baseRequest = {
      id: `request_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      modelId: formData.modelId,
      timestamp: Date.now(),
      userId: 'current_user', // In real app, get from auth context
      priority: 'medium' as const,
    };

    switch (formData.requestType) {
      case 'text':
        return {
          ...baseRequest,
          type: 'text' as const,
          prompt: formData.prompt,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AITextRequest;

      case 'vision':
        return {
          ...baseRequest,
          type: 'vision' as const,
          prompt: formData.prompt,
          images: formData.images,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AIVisionRequest;

      case 'audio':
        return {
          ...baseRequest,
          type: 'audio' as const,
          prompt: formData.prompt,
          audioData: formData.audioData,
          format: 'mp3' as const,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AIAudioRequest;

      case 'multimodal':
        return {
          ...baseRequest,
          type: 'multimodal' as const,
          prompt: formData.prompt,
          text: formData.text,
          images: formData.images,
          audio: formData.audioData,
          maxTokens: formData.maxTokens,
          temperature: formData.temperature,
        } as AIMultimodalRequest;

      default:
        throw new Error(`Unsupported request type: ${formData.requestType}`);
    }
  };

  const formatTimestamp = (timestamp: number): string => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getModelDisplayName = (modelId: string): string => {
    const model = ai.models.find(m => m.id === modelId);
    return model?.name || modelId;
  };

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderMessage = (message: ChatMessage): JSX.Element => {
    const isUser = message.type === 'user';
    const messageStyle = isUser ? styles.userMessage : styles.aiMessage;
    const textStyle = isUser ? styles.userMessageText : styles.aiMessageText;

    return (
      <View key={message.id} style={[styles.messageContainer, messageStyle]}>
        <View style={styles.messageHeader}>
          <Text style={styles.messageSender}>
            {isUser ? 'You' : 'AI Assistant'}
          </Text>
          <Text style={styles.messageTimestamp}>
            {formatTimestamp(message.timestamp)}
          </Text>
        </View>

        <Text style={textStyle}>{message.content}</Text>

        {message.modelId && (
          <Text style={styles.modelInfo}>
            Model: {getModelDisplayName(message.modelId)}
          </Text>
        )}

        {message.requestType && (
          <Text style={styles.requestTypeInfo}>
            Type: {message.requestType}
          </Text>
        )}

        {message.metadata?.usage && (
          <View style={styles.usageInfo}>
            <Text style={styles.usageText}>
              Tokens: {message.metadata.usage.totalTokens}
            </Text>
          </View>
        )}
      </View>
    );
  };

  const renderRequestTypeSelector = (): JSX.Element => (
    <View style={styles.requestTypeContainer}>
      <Text style={styles.sectionTitle}>Request Type</Text>
      <View style={styles.requestTypeButtons}>
        {(['text', 'vision', 'audio', 'multimodal'] as const).map(type => (
          <TouchableOpacity
            key={type}
            style={[
              styles.requestTypeButton,
              form.requestType === type && styles.requestTypeButtonActive,
            ]}
            onPress={() => handleRequestTypeChange(type)}
          >
            <Text
              style={[
                styles.requestTypeButtonText,
                form.requestType === type && styles.requestTypeButtonTextActive,
              ]}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderModelSelector = (): JSX.Element => (
    <View style={styles.modelSelectorContainer}>
      <Text style={styles.sectionTitle}>AI Model</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.modelButtons}>
          {ai.models.map(model => (
            <TouchableOpacity
              key={model.id}
              style={[
                styles.modelButton,
                form.modelId === model.id && styles.modelButtonActive,
              ]}
              onPress={() => handleModelChange(model.id)}
            >
              <Text
                style={[
                  styles.modelButtonText,
                  form.modelId === model.id && styles.modelButtonTextActive,
                ]}
              >
                {model.name}
              </Text>
              <Text style={styles.modelButtonDescription}>
                {model.description}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  );

  const renderInputForm = (): JSX.Element => (
    <View style={styles.inputFormContainer}>
      <View style={styles.inputRow}>
        <TextInput
          style={styles.textInput}
          placeholder="Enter your prompt..."
          value={form.prompt}
          onChangeText={(text) => setForm(prev => ({ ...prev, prompt: text }))}
          multiline
          maxLength={1000}
          editable={!ai.isLoading}
        />
      </View>

      {form.requestType === 'multimodal' && (
        <View style={styles.multimodalInputs}>
          <TextInput
            style={styles.textInput}
            placeholder="Additional text content..."
            value={form.text}
            onChangeText={(text) => setForm(prev => ({ ...prev, text }))}
            multiline
            maxLength={500}
          />
        </View>
      )}

      {(form.requestType === 'vision' || form.requestType === 'multimodal') && (
        <View style={styles.mediaInputs}>
          <AccessibleButton
            accessibilityLabel="Add image"
            onPress={handleAddImage}
            style={styles.mediaButton}
          >
            <Text style={styles.mediaButtonText}>📷 Add Image</Text>
          </AccessibleButton>
        </View>
      )}

      {(form.requestType === 'audio' || form.requestType === 'multimodal') && (
        <View style={styles.mediaInputs}>
          <AccessibleButton
            accessibilityLabel="Add audio"
            onPress={handleAddAudio}
            style={styles.mediaButton}
          >
            <Text style={styles.mediaButtonText}>🎵 Add Audio</Text>
          </AccessibleButton>
        </View>
      )}

      <View style={styles.sendButtonContainer}>
        <AccessibleButton
          accessibilityLabel="Send message"
          onPress={handleSendMessage}
          disabled={!form.prompt.trim() || ai.isLoading}
          style={[
            styles.sendButton,
            (!form.prompt.trim() || ai.isLoading) && styles.sendButtonDisabled,
          ]}
        >
          {ai.isLoading ? (
            <ActivityIndicator color="#ffffff" size="small" />
          ) : (
            <Text style={styles.sendButtonText}>Send</Text>
          )}
        </AccessibleButton>
      </View>
    </View>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Blaze AI Chat</Text>
          <View style={styles.headerActions}>
            <AccessibleButton
              accessibilityLabel="Clear chat"
              onPress={handleClearChat}
              style={styles.clearButton}
            >
              <Text style={styles.clearButtonText}>Clear</Text>
            </AccessibleButton>
          </View>
        </View>

        {/* Request Type and Model Selectors */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View style={styles.selectorsContainer}>
            {renderRequestTypeSelector()}
            {renderModelSelector()}
          </View>
        </ScrollView>

        {/* Messages */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        >
          {messages.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>
                Start a conversation with AI
              </Text>
              <Text style={styles.emptyStateSubtext}>
                Choose a model and request type, then enter your prompt
              </Text>
            </View>
          ) : (
            messages.map(renderMessage)
          )}

          {isTyping && (
            <View style={styles.typingIndicator}>
              <Text style={styles.typingText}>AI is thinking...</Text>
              <ActivityIndicator size="small" color="#666" />
            </View>
          )}
        </ScrollView>

        {/* Input Form */}
        {renderInputForm()}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  headerActions: {
    flexDirection: 'row',
  },
  clearButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#ff6b6b',
    borderRadius: 6,
  },
  clearButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
  },
  selectorsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  requestTypeContainer: {
    marginRight: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  requestTypeButtons: {
    flexDirection: 'row',
  },
  requestTypeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    marginRight: 8,
  },
  requestTypeButtonActive: {
    backgroundColor: '#007AFF',
  },
  requestTypeButtonText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  requestTypeButtonTextActive: {
    color: '#ffffff',
  },
  modelSelectorContainer: {
    flex: 1,
  },
  modelButtons: {
    flexDirection: 'row',
  },
  modelButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    marginRight: 12,
    minWidth: 120,
  },
  modelButtonActive: {
    backgroundColor: '#007AFF',
  },
  modelButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  modelButtonTextActive: {
    color: '#ffffff',
  },
  modelButtonDescription: {
    fontSize: 11,
    color: '#666',
    textAlign: 'center',
    marginTop: 2,
  },
  messagesContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  messagesContent: {
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
  messageContainer: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
    maxWidth: '85%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  messageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  messageSender: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
  },
  messageTimestamp: {
    fontSize: 10,
    color: '#ffffff',
    opacity: 0.8,
  },
  userMessageText: {
    fontSize: 16,
    color: '#ffffff',
    lineHeight: 22,
  },
  aiMessageText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 22,
  },
  modelInfo: {
    fontSize: 11,
    color: '#666',
    marginTop: 6,
    fontStyle: 'italic',
  },
  requestTypeInfo: {
    fontSize: 11,
    color: '#666',
    marginTop: 2,
    fontStyle: 'italic',
  },
  usageInfo: {
    marginTop: 6,
    paddingTop: 6,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  usageText: {
    fontSize: 10,
    color: '#999',
  },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
  },
  typingText: {
    fontSize: 14,
    color: '#666',
    marginRight: 8,
  },
  inputFormContainer: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  inputRow: {
    marginBottom: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 48,
    backgroundColor: '#ffffff',
  },
  multimodalInputs: {
    marginBottom: 12,
  },
  mediaInputs: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  mediaButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    marginRight: 12,
  },
  mediaButtonText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  sendButtonContainer: {
    alignItems: 'flex-end',
  },
  sendButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
  sendButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

// ============================================================================
// EXPORTS
// ============================================================================

export default AIChatInterface;


