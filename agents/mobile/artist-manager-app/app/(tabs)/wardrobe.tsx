import { useQuery } from '@tanstack/react-query';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { wardrobeService } from '@/services/wardrobe-service';
import { LoadingSpinner } from '@/components/loading-spinner';
import { ErrorMessage } from '@/components/error-message';
import { Card } from '@/components/card';
import { Button } from '@/components/button';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { WardrobeItem, Outfit } from '@/types';
import { useRouter } from 'expo-router';

export default function WardrobeScreen() {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;
  const router = useRouter();

  const { data: items, isLoading: itemsLoading, error: itemsError, refetch: refetchItems } = useQuery({
    queryKey: ['wardrobe', 'items'],
    queryFn: () => wardrobeService.getItems(),
  });

  const { data: outfits, isLoading: outfitsLoading, error: outfitsError, refetch: refetchOutfits } =
    useQuery({
      queryKey: ['wardrobe', 'outfits'],
      queryFn: () => wardrobeService.getOutfits(),
    });

  const isLoading = itemsLoading || outfitsLoading;
  const error = itemsError || outfitsError;

  const renderItem = ({ item }: { item: WardrobeItem }) => (
    <Card>
      <Text style={[styles.itemName, { color: colors.text }]}>{item.name}</Text>
      <Text style={[styles.itemDetails, { color: colors.icon }]}>
        {item.category} • {item.color}
      </Text>
      {item.brand && <Text style={[styles.itemBrand, { color: colors.icon }]}>{item.brand}</Text>}
    </Card>
  );

  const renderOutfit = ({ item }: { item: Outfit }) => (
    <Card>
      <Text style={[styles.outfitName, { color: colors.text }]}>{item.name}</Text>
      <Text style={[styles.outfitDetails, { color: colors.icon }]}>
        {item.occasion} • {item.dress_code}
      </Text>
    </Card>
  );

  if (isLoading) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
        <LoadingSpinner fullScreen />
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
        <ErrorMessage message="Failed to load wardrobe" onRetry={() => {
          refetchItems();
          refetchOutfits();
        }} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>Wardrobe</Text>
        <View style={styles.buttonRow}>
          <Button
            title="Add Item"
            onPress={() => router.push('/wardrobe/create-item')}
            variant="primary"
            style={styles.button}
          />
          <Button
            title="Add Outfit"
            onPress={() => router.push('/wardrobe/create-outfit')}
            variant="secondary"
            style={styles.button}
          />
        </View>
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Items ({items?.length ?? 0})</Text>
        {items && items.length > 0 ? (
          <FlatList
            data={items}
            renderItem={renderItem}
            keyExtractor={(item) => item.id}
            scrollEnabled={false}
          />
        ) : (
          <Text style={[styles.emptyText, { color: colors.icon }]}>No items in wardrobe</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          Outfits ({outfits?.length ?? 0})
        </Text>
        {outfits && outfits.length > 0 ? (
          <FlatList
            data={outfits}
            renderItem={renderOutfit}
            keyExtractor={(item) => item.id}
            scrollEnabled={false}
          />
        ) : (
          <Text style={[styles.emptyText, { color: colors.icon }]}>No outfits created</Text>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
  },
  button: {
    flex: 1,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  itemName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  itemDetails: {
    fontSize: 14,
  },
  itemBrand: {
    fontSize: 12,
    marginTop: 2,
  },
  outfitName: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  outfitDetails: {
    fontSize: 14,
  },
  emptyText: {
    fontSize: 14,
    paddingHorizontal: 16,
    fontStyle: 'italic',
  },
});


