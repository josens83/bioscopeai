import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { subscriptionAPI } from '../services/api'

export const useSubscription = () => {
  const queryClient = useQueryClient()

  const { data: plans, isLoading: plansLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: async () => {
      const response = await subscriptionAPI.getPlans()
      return response.data
    },
  })

  const { data: mySubscription, isLoading: subscriptionLoading } = useQuery({
    queryKey: ['my-subscription'],
    queryFn: async () => {
      try {
        const response = await subscriptionAPI.getMy()
        return response.data
      } catch (error: any) {
        if (error.response?.status === 404) {
          return null
        }
        throw error
      }
    },
  })

  const createMutation = useMutation({
    mutationFn: (tier: string) => subscriptionAPI.create(tier),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-subscription'] })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: (at_period_end: boolean) => subscriptionAPI.cancel(at_period_end),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-subscription'] })
    },
  })

  return {
    plans,
    plansLoading,
    mySubscription,
    subscriptionLoading,
    createMutation,
    cancelMutation,
  }
}
