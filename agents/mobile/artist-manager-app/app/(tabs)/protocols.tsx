import { useQuery } from '@tanstack/react-query';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { protocolService } from '@/services/protocol-service';
import { LoadingSpinner } from '@/components/loading-spinner';
import { ErrorMessage } from '@/components/error-message';
import { Card } from '@/components/card';
import { Button } from '@/components/button';
import { Colors } from '@/constants/colors';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Protocol } from '@/types';
import { useRouter } from 'expo-router';

export default function ProtocolsScreen() {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;
  const router = useRouter();

  const { data: protocols, isLoading, error, refetch } = useQuery({
    queryKey: ['protocols'],
    queryFn: () => protocolService.getProtocols(),
  });

  const renderProtocol = ({ item }: { item: Protocol }) => {
    const priorityColor =
      item.priority === 'critical'
        ? colors.error
        : item.priority === 'high'
          ? colors.warning
          : colors.icon;

    return (
      <Card>
        <View style={styles.protocolHeader}>
          <View style={styles.protocolInfo}>
            <Text style={[styles.protocolTitle, { color: colors.text }]}>{item.title}</Text>
            <View style={styles.protocolMeta}>
              <Text style={[styles.protocolCategory, { color: colors.icon }]}>
                {item.category}
              </Text>
              <View style={[styles.priorityBadge, { backgroundColor: priorityColor }]}>
                <Text style={styles.priorityText}>{item.priority}</Text>
              </View>
            </View>
          </View>
        </View>
        {item.description && (
          <Text style={[styles.protocolDescription, { color: colors.text }]}>
            {item.description}
          </Text>
        )}
        {item.rules && item.rules.length > 0 && (
          <View style={styles.rulesContainer}>
            <Text style={[styles.rulesTitle, { color: colors.text }]}>Rules:</Text>
            {item.rules.map((rule, index) => (
              <Text key={index} style={[styles.rule, { color: colors.icon }]}>
                • {rule}
              </Text>
            ))}
          </View>
        )}
      </Card>
    );
  };

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
        <ErrorMessage message="Failed to load protocols" onRetry={() => refetch()} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: colors.background }]} edges={['top']}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: colors.text }]}>Protocols</Text>
        <Button
          title="Add Protocol"
          onPress={() => router.push('/protocols/create')}
          variant="primary"
        />
      </View>

      {protocols && protocols.length > 0 ? (
        <FlatList
          data={protocols}
          renderItem={renderProtocol}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={[styles.emptyText, { color: colors.icon }]}>No protocols defined</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  listContent: {
    paddingBottom: 20,
  },
  protocolHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  protocolInfo: {
    flex: 1,
  },
  protocolTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  protocolMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  protocolCategory: {
    fontSize: 14,
    textTransform: 'capitalize',
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  priorityText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  protocolDescription: {
    fontSize: 14,
    marginTop: 8,
    marginBottom: 8,
  },
  rulesContainer: {
    marginTop: 8,
  },
  rulesTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  rule: {
    fontSize: 14,
    marginLeft: 8,
    marginBottom: 2,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
  },
});


