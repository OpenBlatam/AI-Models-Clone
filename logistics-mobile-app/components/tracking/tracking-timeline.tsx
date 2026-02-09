import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { TrackingEvent } from '@/types';
import { format } from 'date-fns';

interface TrackingTimelineProps {
  events: TrackingEvent[];
}

export function TrackingTimeline({ events }: TrackingTimelineProps) {
  const sortedEvents = [...events].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <View style={styles.container}>
      {sortedEvents.map((event, index) => (
        <View key={index} style={styles.eventContainer}>
          <View style={styles.timeline}>
            <View style={styles.dot} />
            {index < sortedEvents.length - 1 && <View style={styles.line} />}
          </View>
          <View style={styles.eventContent}>
            <Text style={styles.eventType}>{event.event_type}</Text>
            <Text style={styles.description}>{event.description}</Text>
            <Text style={styles.location}>
              {event.location.city}, {event.location.country}
            </Text>
            <Text style={styles.timestamp}>
              {format(new Date(event.timestamp), 'MMM dd, yyyy HH:mm')}
            </Text>
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  eventContainer: {
    flexDirection: 'row',
    marginBottom: 24,
  },
  timeline: {
    alignItems: 'center',
    marginRight: 16,
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#007AFF',
  },
  line: {
    width: 2,
    flex: 1,
    backgroundColor: '#E5E5EA',
    marginTop: 4,
    minHeight: 40,
  },
  eventContent: {
    flex: 1,
  },
  eventType: {
    fontSize: 16,
    fontWeight: '700',
    color: '#000',
    marginBottom: 4,
  },
  description: {
    fontSize: 14,
    color: '#000',
    marginBottom: 4,
  },
  location: {
    fontSize: 12,
    color: '#8E8E93',
    marginBottom: 4,
  },
  timestamp: {
    fontSize: 12,
    color: '#8E8E93',
  },
});


