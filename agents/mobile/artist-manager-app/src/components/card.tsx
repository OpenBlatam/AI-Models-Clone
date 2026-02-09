import { StyleSheet, ViewStyle } from 'react-native';
import { ReactNode } from 'react';
import { AnimatedCard } from './animated-card';

interface CardProps {
  children: ReactNode;
  style?: ViewStyle;
  padding?: number;
  onPress?: () => void;
  delay?: number;
}

export function Card({ children, style, padding = 16, onPress, delay }: CardProps) {
  return (
    <AnimatedCard style={style} padding={padding} onPress={onPress} delay={delay}>
      {children}
    </AnimatedCard>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 12,
    borderWidth: 1,
    marginVertical: 8,
    marginHorizontal: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
});

