import React from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useShipments } from '@/hooks/use-shipments';
import { ShipmentCard } from '@/components/shipment/shipment-card';
import { useRouter } from 'expo-router';
import { Button } from '@/components/ui/button';

export default function ShipmentsScreen() {
  const { data: shipments, isLoading, refetch, isRefetching } = useShipments();
  const router = useRouter();

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <Text>Loading shipments...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.title}>Shipments</Text>
        <Button title="Create" onPress={() => router.push('/quote/create')} size="small" />
      </View>

      <FlatList
        data={shipments}
        keyExtractor={(item) => item.shipment_id}
        renderItem={({ item }) => (
          <ShipmentCard
            shipment={item}
            onPress={() => router.push(`/shipment/${item.shipment_id}`)}
          />
        )}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={refetch} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No shipments found</Text>
            <Button
              title="Create Your First Shipment"
              onPress={() => router.push('/quote/create')}
              style={styles.emptyButton}
            />
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#000',
  },
  listContent: {
    padding: 16,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#8E8E93',
    marginBottom: 16,
  },
  emptyButton: {
    width: '80%',
  },
});


