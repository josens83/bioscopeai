import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { papersAPI } from '../services/api'

export const usePapers = () => {
  const queryClient = useQueryClient()

  const { data: papers, isLoading } = useQuery({
    queryKey: ['papers'],
    queryFn: async () => {
      const response = await papersAPI.list()
      return response.data
    },
  })

  const searchMutation = useMutation({
    mutationFn: (query: string) => papersAPI.search(query),
  })

  const uploadMutation = useMutation({
    mutationFn: ({ file, title, authors }: { file: File; title?: string; authors?: string }) =>
      papersAPI.upload(file, title, authors),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] })
    },
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => papersAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => papersAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['papers'] })
    },
  })

  return {
    papers,
    isLoading,
    searchMutation,
    uploadMutation,
    createMutation,
    deleteMutation,
  }
}
