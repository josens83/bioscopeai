import { useQuery, useMutation } from '@tanstack/react-query'
import { analysisAPI } from '../services/api'

export const useAnalysis = () => {
  const questionMutation = useMutation({
    mutationFn: ({ question, paper_id, k }: { question: string; paper_id?: number; k?: number }) =>
      analysisAPI.question(question, paper_id, k),
  })

  const summarizeMutation = useMutation({
    mutationFn: (paper_id: number) => analysisAPI.summarize(paper_id),
  })

  const compareMutation = useMutation({
    mutationFn: (paper_ids: number[]) => analysisAPI.compare(paper_ids),
  })

  const { data: analyses, isLoading } = useQuery({
    queryKey: ['analyses'],
    queryFn: async () => {
      const response = await analysisAPI.list()
      return response.data
    },
  })

  return {
    questionMutation,
    summarizeMutation,
    compareMutation,
    analyses,
    isLoading,
  }
}
