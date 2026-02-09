import { ReactNode } from 'react';
import { ScrollView, ScrollViewProps, RefreshControl } from 'react-native';
import { SafeAreaView, Edge } from 'react-native-safe-area-context';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/colors';

interface SafeAreaScrollViewProps extends ScrollViewProps {
  children: ReactNode;
  edges?: Edge[];
  refreshing?: boolean;
  onRefresh?: () => void;
}

export function SafeAreaScrollView({
  children,
  edges = ['top', 'bottom'],
  refreshing = false,
  onRefresh,
  contentContainerStyle,
  ...scrollViewProps
}: SafeAreaScrollViewProps) {
  const { isDark } = useColorScheme();
  const colors = isDark ? Colors.dark : Colors.light;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }} edges={edges}>
      <ScrollView
        {...scrollViewProps}
        style={[{ flex: 1, backgroundColor: colors.background }, scrollViewProps.style]}
        contentContainerStyle={[
          { paddingBottom: 20 },
          contentContainerStyle,
        ]}
        refreshControl={
          onRefresh ? (
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
          ) : undefined
        }
        showsVerticalScrollIndicator={false}
      >
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}


