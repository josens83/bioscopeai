import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from '../App'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

describe('App', () => {
  it('renders without crashing', () => {
    // App already includes its own Router, ThemeProvider, and ToastProvider
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    )
    expect(document.body).toBeTruthy()
  })
})
