import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useShipmentTracking } from '@/hooks/use-tracking';
import { TrackingTimeline } from '@/components/tracking/tracking-timeline';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function TrackingScreen() {
  const [trackingId, setTrackingId] = useState('');
  const [searchId, setSearchId] = useState<string | null>(null);
  const { data: tracking, isLoading } = useShipmentTracking(searchId);

  function handleSearch() {
    if (trackingId.trim()) {
      setSearchId(trackingId.trim());
    }
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.content}>
        <Text style={styles.title}>Track Shipment</Text>

        <View style={styles.searchContainer}>
          <Input
            placeholder="Enter shipment ID or tracking number"
            value={trackingId}
            onChangeText={setTrackingId}
            style={styles.searchInput}
          />
          <Button title="Track" onPress={handleSearch} style={styles.searchButton} />
        </View>

        {isLoading && <Text style={styles.loadingText}>Loading tracking information...</Text>}

        {tracking && (
          <View style={styles.trackingContainer}>
            <Card>
              <Text style={styles.statusLabel}>Current Status</Text>
              <Text style={styles.statusValue}>{tracking.current_status.toUpperCase()}</Text>
              {tracking.current_location && (
                <Text style={styles.location}>
                  {tracking.current_location.city}, {tracking.current_location.country}
                </Text>
              )}
              {tracking.estimated_arrival && (
                <Text style={styles.eta}>
                  ETA: {new Date(tracking.estimated_arrival).toLocaleDateString()}
                </Text>
              )}
            </Card>

            <Text style={styles.timelineTitle}>Tracking History</Text>
            <TrackingTimeline events={tracking.tracking_events} />
          </View>
        )}

        {!tracking && !isLoading && searchId && (
          <View style={styles.noResults}>
            <Text style={styles.noResultsText}>No tracking information found</Text>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 24,
    color: '#000',
  },
  searchContainer: {
    marginBottom: 24,
  },
  searchInput: {
    marginBottom: 12,
  },
  searchButton: {
    width: '100%',
  },
  loadingText: {
    textAlign: 'center',
    color: '#8E8E93',
    marginTop: 24,
  },
  trackingContainer: {
    marginTop: 16,
  },
  statusLabel: {
    fontSize: 12,
    color: '#8E8E93',
    marginBottom: 4,
  },
  statusValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#000',
    marginBottom: 8,
  },
  location: {
    fontSize: 14,
    color: '#000',
    marginBottom: 4,
  },
  eta: {
    fontSize: 14,
    color: '#8E8E93',
  },
  timelineTitle: {
    fontSize: 20,
    fontWeight: '700',
    marginTop: 24,
    marginBottom: 16,
    color: '#000',
  },
  noResults: {
    alignItems: 'center',
    marginTop: 48,
  },
  noResultsText: {
    fontSize: 16,
    color: '#8E8E93',
  },
});


