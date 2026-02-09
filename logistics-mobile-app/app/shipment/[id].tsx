import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams } from 'expo-router';
import { useShipment } from '@/hooks/use-shipments';
import { TrackingTimeline } from '@/components/tracking/tracking-timeline';
import { Card } from '@/components/ui/card';
import { format } from 'date-fns';

export default function ShipmentDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data: shipment, isLoading } = useShipment(id);

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <Text>Loading...</Text>
      </SafeAreaView>
    );
  }

  if (!shipment) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <Text>Shipment not found</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.content}>
        <Card>
          <Text style={styles.label}>Shipment Reference</Text>
          <Text style={styles.value}>{shipment.shipment_reference}</Text>

          <Text style={styles.label}>Status</Text>
          <Text style={styles.value}>{shipment.status.toUpperCase()}</Text>

          <Text style={styles.label}>Transportation Mode</Text>
          <Text style={styles.value}>{shipment.transportation_mode.toUpperCase()}</Text>

          {shipment.tracking_number && (
            <>
              <Text style={styles.label}>Tracking Number</Text>
              <Text style={styles.value}>{shipment.tracking_number}</Text>
            </>
          )}
        </Card>

        <Card>
          <Text style={styles.sectionTitle}>Route</Text>
          <View style={styles.route}>
            <View>
              <Text style={styles.locationLabel}>Origin</Text>
              <Text style={styles.locationText}>
                {shipment.origin.city}, {shipment.origin.country}
              </Text>
            </View>
            <Text style={styles.arrow}>→</Text>
            <View>
              <Text style={styles.locationLabel}>Destination</Text>
              <Text style={styles.locationText}>
                {shipment.destination.city}, {shipment.destination.country}
              </Text>
            </View>
          </View>
        </Card>

        <Card>
          <Text style={styles.sectionTitle}>Cargo Details</Text>
          <Text style={styles.label}>Description</Text>
          <Text style={styles.value}>{shipment.cargo.description}</Text>

          <Text style={styles.label}>Weight</Text>
          <Text style={styles.value}>{shipment.cargo.weight_kg} kg</Text>

          <Text style={styles.label}>Quantity</Text>
          <Text style={styles.value}>{shipment.cargo.quantity} {shipment.cargo.unit_type}</Text>

          {shipment.cargo.value_usd && (
            <>
              <Text style={styles.label}>Value</Text>
              <Text style={styles.value}>${shipment.cargo.value_usd.toLocaleString()}</Text>
            </>
          )}
        </Card>

        {shipment.estimated_arrival && (
          <Card>
            <Text style={styles.label}>Estimated Arrival</Text>
            <Text style={styles.value}>
              {format(new Date(shipment.estimated_arrival), 'MMM dd, yyyy')}
            </Text>
          </Card>
        )}

        {shipment.tracking_events.length > 0 && (
          <View style={styles.timelineContainer}>
            <Text style={styles.sectionTitle}>Tracking History</Text>
            <TrackingTimeline events={shipment.tracking_events} />
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F2F2F7',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
  },
  label: {
    fontSize: 12,
    color: '#8E8E93',
    marginTop: 12,
    marginBottom: 4,
  },
  value: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 16,
    color: '#000',
  },
  route: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  locationLabel: {
    fontSize: 12,
    color: '#8E8E93',
    marginBottom: 4,
  },
  locationText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#000',
  },
  arrow: {
    fontSize: 24,
    color: '#8E8E93',
  },
  timelineContainer: {
    marginTop: 16,
  },
});


