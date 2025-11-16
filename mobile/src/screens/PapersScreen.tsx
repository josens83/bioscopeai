import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { papersAPI } from '../services/api';

export default function PapersScreen() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);

  const { data: papers, isLoading } = useQuery({
    queryKey: ['papers'],
    queryFn: async () => {
      const response = await papersAPI.list();
      return response.data;
    },
  });

  const searchMutation = useMutation({
    mutationFn: (query: string) => papersAPI.search(query),
    onSuccess: (response) => {
      setSearchResults(response.data);
    },
    onError: () => {
      Alert.alert('오류', '검색에 실패했습니다');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => papersAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] });
      Alert.alert('성공', '논문이 삭제되었습니다');
    },
  });

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    searchMutation.mutate(searchQuery);
  };

  const handleDelete = (id: number) => {
    Alert.alert('삭제 확인', '정말 삭제하시겠습니까?', [
      { text: '취소', style: 'cancel' },
      { text: '삭제', onPress: () => deleteMutation.mutate(id), style: 'destructive' },
    ]);
  };

  const renderPaper = ({ item }: any) => (
    <View style={styles.paperCard}>
      <Text style={styles.paperTitle}>{item.title}</Text>
      {item.authors && <Text style={styles.paperAuthors}>{item.authors}</Text>}
      {item.journal && <Text style={styles.paperJournal}>{item.journal}</Text>}
      {item.abstract && (
        <Text style={styles.paperAbstract} numberOfLines={3}>
          {item.abstract}
        </Text>
      )}
      <TouchableOpacity
        style={styles.deleteButton}
        onPress={() => handleDelete(item.id)}
      >
        <Text style={styles.deleteButtonText}>삭제</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="PubMed에서 논문 검색..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          onSubmitEditing={handleSearch}
        />
        <TouchableOpacity
          style={styles.searchButton}
          onPress={handleSearch}
          disabled={searchMutation.isPending}
        >
          {searchMutation.isPending ? (
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.searchButtonText}>검색</Text>
          )}
        </TouchableOpacity>
      </View>

      {isLoading ? (
        <ActivityIndicator style={styles.loader} />
      ) : papers && papers.length > 0 ? (
        <FlatList
          data={papers}
          renderItem={renderPaper}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.list}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>저장된 논문이 없습니다</Text>
          <Text style={styles.emptySubtext}>위에서 검색해보세요</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#f3f4f6',
    padding: 12,
    borderRadius: 8,
  },
  searchButton: {
    backgroundColor: '#0ea5e9',
    padding: 12,
    borderRadius: 8,
    justifyContent: 'center',
    minWidth: 60,
  },
  searchButtonText: {
    color: '#fff',
    fontWeight: '600',
    textAlign: 'center',
  },
  list: {
    padding: 16,
  },
  paperCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  paperTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8,
  },
  paperAuthors: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  paperJournal: {
    fontSize: 13,
    color: '#9ca3af',
    marginBottom: 8,
  },
  paperAbstract: {
    fontSize: 13,
    color: '#6b7280',
    lineHeight: 18,
  },
  deleteButton: {
    marginTop: 12,
    alignSelf: 'flex-end',
  },
  deleteButtonText: {
    color: '#ef4444',
    fontSize: 14,
    fontWeight: '500',
  },
  loader: {
    marginTop: 40,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 4,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9ca3af',
  },
});
