import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useMutation } from '@tanstack/react-query';
import { analysisAPI } from '../services/api';

export default function AnalysisScreen() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const questionMutation = useMutation({
    mutationFn: (q: string) => analysisAPI.question(q),
    onSuccess: (response) => {
      setAnswer(response.data.answer);
    },
    onError: () => {
      Alert.alert('오류', 'AI 분석에 실패했습니다');
    },
  });

  const handleAsk = () => {
    if (!question.trim()) {
      Alert.alert('알림', '질문을 입력해주세요');
      return;
    }
    questionMutation.mutate(question);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>AI에게 질문하기</Text>
          <TextInput
            style={styles.textArea}
            placeholder="논문에 대한 질문을 입력하세요..."
            value={question}
            onChangeText={setQuestion}
            multiline
            numberOfLines={4}
          />
          <TouchableOpacity
            style={styles.button}
            onPress={handleAsk}
            disabled={questionMutation.isPending}
          >
            {questionMutation.isPending ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>질문하기</Text>
            )}
          </TouchableOpacity>
        </View>

        {answer && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>답변</Text>
            <Text style={styles.answerText}>{answer}</Text>
          </View>
        )}

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>💡 사용 팁</Text>
          <Text style={styles.infoText}>• 구체적인 질문을 하면 더 정확한 답변을 받을 수 있습니다</Text>
          <Text style={styles.infoText}>• 논문의 특정 부분에 대해 질문해보세요</Text>
          <Text style={styles.infoText}>• 여러 논문을 비교하고 싶다면 웹 버전을 이용하세요</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  content: {
    padding: 16,
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  textArea: {
    backgroundColor: '#f9fafb',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    minHeight: 100,
    textAlignVertical: 'top',
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#0ea5e9',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  answerText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 22,
  },
  infoCard: {
    backgroundColor: '#eff6ff',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#bfdbfe',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e40af',
    marginBottom: 12,
  },
  infoText: {
    fontSize: 13,
    color: '#3b82f6',
    marginBottom: 6,
    lineHeight: 18,
  },
});
