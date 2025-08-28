import React, { useCallback, useState, useMemo } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'post' | 'user' | 'topic';
}

const mockSearchResults: SearchResult[] = [
  {
    id: '1',
    title: 'React Native Performance',
    description: 'Tips for optimizing React Native apps',
    type: 'post',
  },
  {
    id: '2',
    title: 'John Doe',
    description: 'Mobile Developer',
    type: 'user',
  },
  {
    id: '3',
    title: 'Mobile Development',
    description: 'Latest trends in mobile app development',
    type: 'topic',
  },
];

const SearchResultItem: React.FC<{ 
  item: SearchResult; 
  onPress: () => void;
}> = React.memo(({ item, onPress }) => (
  <TouchableOpacity style={styles.resultItem} onPress={onPress}>
    <View style={styles.resultIcon}>
      <Ionicons 
        name={
          item.type === 'post' ? 'document-text' :
          item.type === 'user' ? 'person' : 'hash'
        } 
        size={20} 
        color="#007AFF" 
      />
    </View>
    <View style={styles.resultContent}>
      <Text style={styles.resultTitle}>{item.title}</Text>
      <Text style={styles.resultDescription}>{item.description}</Text>
    </View>
    <Ionicons name="chevron-forward" size={16} color="#C7C7CC" />
  </TouchableOpacity>
));

export default function SearchScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

  const filteredResults = useMemo(() => {
    if (!searchQuery.trim()) return [];
    return mockSearchResults.filter(item =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [searchQuery]);

  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      setIsSearching(true);
      // Simulate API call with delay
      await new Promise(resolve => setTimeout(resolve, 500));
      setSearchResults(filteredResults);
      setIsSearching(false);
    } else {
      setSearchResults([]);
    }
  }, [filteredResults]);

  const handleResultPress = useCallback((result: SearchResult) => {
    if (result.type === 'post') {
      router.push(`/posts/${result.id}`);
    } else if (result.type === 'user') {
      router.push(`/profile/${result.id}`);
    } else {
      router.push(`/topics/${result.id}`);
    }
  }, [router]);

  const renderItem = useCallback(({ item }: { item: SearchResult }) => (
    <SearchResultItem
      item={item}
      onPress={() => handleResultPress(item)}
    />
  ), [handleResultPress]);

  const keyExtractor = useCallback((item: SearchResult) => item.id, []);

  const ListEmptyComponent = useCallback(() => (
    <View style={styles.emptyContainer}>
      <Ionicons name="search" size={48} color="#C7C7CC" />
      <Text style={styles.emptyText}>
        {searchQuery.trim() ? 'No results found' : 'Search for posts, users, or topics'}
      </Text>
    </View>
  ), [searchQuery]);

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <Ionicons name="search" size={20} color="#8E8E93" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search..."
            placeholderTextColor="#8E8E93"
            value={searchQuery}
            onChangeText={handleSearch}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="search"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity
              onPress={() => setSearchQuery('')}
              style={styles.clearButton}
            >
              <Ionicons name="close-circle" size={20} color="#8E8E93" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {isSearching ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Searching...</Text>
        </View>
      ) : (
        <FlatList
          data={searchResults}
          keyExtractor={keyExtractor}
          renderItem={renderItem}
          ListEmptyComponent={ListEmptyComponent}
          removeClippedSubviews={true}
          maxToRenderPerBatch={10}
          windowSize={10}
          initialNumToRender={5}
          updateCellsBatchingPeriod={50}
          contentContainerStyle={styles.listContent}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  searchInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F2F2F7',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  searchInput: {
    flex: 1,
    marginLeft: 8,
    fontSize: 16,
    color: '#000000',
  },
  clearButton: {
    padding: 4,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#8E8E93',
  },
  listContent: {
    flexGrow: 1,
  },
  resultItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F2F2F7',
  },
  resultIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  resultContent: {
    flex: 1,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000000',
    marginBottom: 2,
  },
  resultDescription: {
    fontSize: 14,
    color: '#8E8E93',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
}); 