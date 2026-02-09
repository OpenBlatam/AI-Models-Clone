import React, { memo } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { ShipmentResponse } from '@/types';
import { Card } from '../ui/card';
import { useTheme } from '@/contexts/theme-context';
import { format } from 'date-fns';

interface ShipmentCardProps {
  shipment: ShipmentResponse;
  onPress: () => void;
}

function ShipmentCardComponent({ shipment, onPress }: ShipmentCardProps) {
  const { theme } = useTheme();

  function getStatusColor(status: string) {
    const statusColors: Record<string, string> = {
      pending: theme.colors.warning,
      quoted: theme.colors.primary,
      booked: theme.colors.secondary,
      in_transit: theme.colors.success,
      in_customs: theme.colors.warning,
      delivered: theme.colors.success,
      delayed: theme.colors.error,
      cancelled: theme.colors.textSecondary,
      exception: theme.colors.error,
    };
    return statusColors[status] || theme.colors.textSecondary;
  }

  return (
    <Card onPress={onPress} variant="elevated" accessibilityRole="button">
      <View style={styles.header}>
        <Text style={[styles.shipmentId, { color: theme.colors.text }]}>{shipment.shipment_reference}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(shipment.status) }]}>
          <Text style={styles.statusText}>{shipment.status.replace('_', ' ').toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.route}>
        <View style={styles.location}>
          <Text style={[styles.locationLabel, { color: theme.colors.textSecondary }]}>From</Text>
          <Text style={[styles.locationText, { color: theme.colors.text }]}>
            {shipment.origin.city}, {shipment.origin.country}
          </Text>
        </View>
        <Text style={[styles.arrow, { color: theme.colors.textSecondary }]}>→</Text>
        <View style={styles.location}>
          <Text style={[styles.locationLabel, { color: theme.colors.textSecondary }]}>To</Text>
          <Text style={[styles.locationText, { color: theme.colors.text }]}>
            {shipment.destination.city}, {shipment.destination.country}
          </Text>
        </View>
      </View>

      <View style={[styles.footer, { borderTopColor: theme.colors.border }]}>
        <Text style={[styles.mode, { color: theme.colors.primary }]}>
          {shipment.transportation_mode.toUpperCase()}
        </Text>
        {shipment.estimated_arrival && (
          <Text style={[styles.date, { color: theme.colors.textSecondary }]}>
            ETA: {format(new Date(shipment.estimated_arrival), 'MMM dd, yyyy')}
          </Text>
        )}
      </View>
    </Card>
  );
}

export const ShipmentCard = memo(ShipmentCardComponent);

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  shipmentId: {
    fontSize: 16,
    fontWeight: '700',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  route: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  location: {
    flex: 1,
  },
  locationLabel: {
    fontSize: 12,
    marginBottom: 4,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  locationText: {
    fontSize: 14,
    fontWeight: '600',
  },
  arrow: {
    fontSize: 20,
    marginHorizontal: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
  },
  mode: {
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  date: {
    fontSize: 12,
  },
});
