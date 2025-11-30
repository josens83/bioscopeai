import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { borderRadius, spacing, shadows } from '../theme';

type CardVariant = 'default' | 'elevated' | 'outlined';

interface CardProps {
  children: React.ReactNode;
  variant?: CardVariant;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  style?: ViewStyle;
}

export function Card({
  children,
  variant = 'default',
  padding = 'md',
  style,
}: CardProps) {
  const { theme } = useTheme();

  const getPadding = () => {
    switch (padding) {
      case 'none': return 0;
      case 'sm': return spacing[4];
      case 'lg': return spacing[8];
      default: return spacing[6];
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'elevated':
        return {
          ...shadows.md,
        };
      case 'outlined':
        return {
          borderWidth: 1,
          borderColor: theme.colors.border,
        };
      default:
        return {
          ...shadows.sm,
        };
    }
  };

  return (
    <View
      style={[
        styles.card,
        {
          backgroundColor: theme.colors.surface,
          padding: getPadding(),
        },
        getVariantStyles(),
        style,
      ]}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: borderRadius.xl,
  },
});
