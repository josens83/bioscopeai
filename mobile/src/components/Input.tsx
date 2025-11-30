import React, { useState } from 'react';
import {
  View,
  TextInput,
  Text,
  StyleSheet,
  TextInputProps,
  TouchableOpacity,
  ViewStyle,
} from 'react-native';
import { useTheme } from '../theme/ThemeContext';
import { borderRadius, spacing, typography } from '../theme';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  hint?: string;
  containerStyle?: ViewStyle;
}

export function Input({
  label,
  error,
  hint,
  containerStyle,
  style,
  ...props
}: InputProps) {
  const { theme } = useTheme();
  const [isFocused, setIsFocused] = useState(false);

  const borderColor = error
    ? theme.colors.error
    : isFocused
    ? theme.colors.primary
    : theme.colors.border;

  return (
    <View style={[styles.container, containerStyle]}>
      {label && (
        <Text style={[styles.label, { color: theme.colors.text }]}>
          {label}
        </Text>
      )}
      <TextInput
        style={[
          styles.input,
          {
            backgroundColor: theme.colors.surface,
            borderColor,
            color: theme.colors.text,
          },
          style,
        ]}
        placeholderTextColor={theme.colors.textTertiary}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        {...props}
      />
      {error && (
        <Text style={[styles.error, { color: theme.colors.error }]}>
          {error}
        </Text>
      )}
      {hint && !error && (
        <Text style={[styles.hint, { color: theme.colors.textTertiary }]}>
          {hint}
        </Text>
      )}
    </View>
  );
}

// Password Input with toggle
interface PasswordInputProps extends Omit<InputProps, 'secureTextEntry'> {}

export function PasswordInput(props: PasswordInputProps) {
  const { theme } = useTheme();
  const [showPassword, setShowPassword] = useState(false);

  return (
    <View>
      <Input
        {...props}
        secureTextEntry={!showPassword}
      />
      <TouchableOpacity
        onPress={() => setShowPassword(!showPassword)}
        style={styles.toggleButton}
        accessibilityLabel={showPassword ? '비밀번호 숨기기' : '비밀번호 보기'}
        accessibilityRole="button"
      >
        <Text style={[styles.toggleText, { color: theme.colors.textTertiary }]}>
          {showPassword ? '숨기기' : '보기'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing[4],
  },
  label: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    marginBottom: spacing[1.5],
  },
  input: {
    padding: spacing[4],
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    fontSize: typography.fontSize.base,
  },
  error: {
    fontSize: typography.fontSize.sm,
    marginTop: spacing[1],
  },
  hint: {
    fontSize: typography.fontSize.sm,
    marginTop: spacing[1],
  },
  toggleButton: {
    position: 'absolute',
    right: spacing[4],
    top: 38,
    padding: spacing[2],
  },
  toggleText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
  },
});
