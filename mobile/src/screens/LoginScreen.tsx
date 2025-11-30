import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { authAPI } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { Button, Input, PasswordInput, useTheme, spacing, typography, borderRadius } from '../components';

export default function LoginScreen({ navigation }: any) {
  const { theme } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const setAuth = useAuthStore((state) => state.setAuth);

  const validate = () => {
    const newErrors: typeof errors = {};
    if (!email) {
      newErrors.email = '이메일을 입력해주세요';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = '유효한 이메일을 입력해주세요';
    }
    if (!password) {
      newErrors.password = '비밀번호를 입력해주세요';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async () => {
    if (!validate()) return;

    setLoading(true);
    try {
      const response = await authAPI.login({ email, password });
      const { access_token } = response.data;

      await setAuth(
        { id: 1, email, username: email.split('@')[0] },
        access_token
      );
    } catch (error: any) {
      Alert.alert(
        '로그인 실패',
        error.response?.data?.detail || '로그인에 실패했습니다. 다시 시도해주세요.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <View style={styles.header}>
            <View style={[styles.logoContainer, { backgroundColor: theme.colors.primary }]}>
              <Text style={styles.logoText}>🔬</Text>
            </View>
            <Text style={[styles.title, { color: theme.colors.text }]}>
              BioscopeAI
            </Text>
            <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
              AI 기반 생물의학 논문 분석 플랫폼
            </Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            <Input
              label="이메일"
              placeholder="example@email.com"
              value={email}
              onChangeText={(text) => {
                setEmail(text);
                if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
              }}
              error={errors.email}
              keyboardType="email-address"
              autoCapitalize="none"
              autoComplete="email"
            />

            <PasswordInput
              label="비밀번호"
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
              }}
              error={errors.password}
              autoComplete="password"
            />

            <Button
              onPress={handleLogin}
              isLoading={loading}
              fullWidth
              size="lg"
            >
              로그인
            </Button>
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={[styles.footerText, { color: theme.colors.textSecondary }]}>
              계정이 없으신가요?{' '}
            </Text>
            <Text
              style={[styles.linkText, { color: theme.colors.primary }]}
              onPress={() => navigation.navigate('Register')}
            >
              회원가입
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing[6],
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing[10],
  },
  logoContainer: {
    width: 64,
    height: 64,
    borderRadius: borderRadius.xl,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing[4],
  },
  logoText: {
    fontSize: 32,
  },
  title: {
    fontSize: typography.fontSize['3xl'],
    fontWeight: typography.fontWeight.bold,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.fontSize.base,
    textAlign: 'center',
  },
  form: {
    marginBottom: spacing[8],
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  footerText: {
    fontSize: typography.fontSize.sm,
  },
  linkText: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.semibold,
  },
});
