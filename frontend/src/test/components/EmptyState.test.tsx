import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  EmptyState,
  EmptyPapers,
  EmptySearchResults,
  EmptyAnalyses,
  EmptyChartData,
  EmptyGeneric,
} from '../../components/ui/EmptyState'
import { DocumentIcon } from '../../components/ui/Icons'

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No items found" />)
    expect(screen.getByText('No items found')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(
      <EmptyState
        title="No items"
        description="Add some items to get started"
      />
    )
    expect(screen.getByText('Add some items to get started')).toBeInTheDocument()
  })

  it('renders with custom icon', () => {
    render(
      <EmptyState
        title="No documents"
        icon={<DocumentIcon data-testid="custom-icon" size={48} />}
      />
    )
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument()
  })

  it('renders primary action button and calls onClick', async () => {
    const handleClick = vi.fn()
    render(
      <EmptyState
        title="No items"
        action={{ label: 'Add Item', onClick: handleClick }}
      />
    )

    const button = screen.getByRole('button', { name: 'Add Item' })
    expect(button).toBeInTheDocument()

    await userEvent.click(button)
    expect(handleClick).toHaveBeenCalled()
  })

  it('renders secondary action button', async () => {
    const handlePrimary = vi.fn()
    const handleSecondary = vi.fn()
    render(
      <EmptyState
        title="No items"
        action={{ label: 'Primary', onClick: handlePrimary }}
        secondaryAction={{ label: 'Secondary', onClick: handleSecondary }}
      />
    )

    expect(screen.getByRole('button', { name: 'Primary' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Secondary' })).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Secondary' }))
    expect(handleSecondary).toHaveBeenCalled()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<EmptyState title="Test" size="sm" />)
    expect(screen.getByText('Test')).toHaveClass('text-base')

    rerender(<EmptyState title="Test" size="md" />)
    expect(screen.getByText('Test')).toHaveClass('text-lg')

    rerender(<EmptyState title="Test" size="lg" />)
    expect(screen.getByText('Test')).toHaveClass('text-xl')
  })
})

describe('EmptyPapers', () => {
  it('renders default empty papers state', () => {
    render(<EmptyPapers />)
    expect(screen.getByText('아직 저장된 논문이 없습니다')).toBeInTheDocument()
  })

  it('renders action button when onAddPaper provided', async () => {
    const handleAdd = vi.fn()
    render(<EmptyPapers onAddPaper={handleAdd} />)

    const button = screen.getByRole('button', { name: '첫 논문 추가하기' })
    await userEvent.click(button)
    expect(handleAdd).toHaveBeenCalled()
  })
})

describe('EmptySearchResults', () => {
  it('renders without query', () => {
    render(<EmptySearchResults />)
    expect(screen.getByText('검색 결과가 없습니다')).toBeInTheDocument()
    expect(screen.getByText('검색 조건에 맞는 결과가 없습니다.')).toBeInTheDocument()
  })

  it('renders with query', () => {
    render(<EmptySearchResults query="cancer" />)
    expect(screen.getByText(/cancer/)).toBeInTheDocument()
  })

  it('renders clear button when onClear provided', async () => {
    const handleClear = vi.fn()
    render(<EmptySearchResults onClear={handleClear} />)

    const button = screen.getByRole('button', { name: '검색 초기화' })
    await userEvent.click(button)
    expect(handleClear).toHaveBeenCalled()
  })
})

describe('EmptyAnalyses', () => {
  it('renders default empty analyses state', () => {
    render(<EmptyAnalyses />)
    expect(screen.getByText('분석 기록이 없습니다')).toBeInTheDocument()
  })

  it('renders action button when onStartAnalysis provided', async () => {
    const handleStart = vi.fn()
    render(<EmptyAnalyses onStartAnalysis={handleStart} />)

    const button = screen.getByRole('button', { name: 'AI 분석 시작하기' })
    await userEvent.click(button)
    expect(handleStart).toHaveBeenCalled()
  })
})

describe('EmptyChartData', () => {
  it('renders chart data empty state', () => {
    render(<EmptyChartData />)
    expect(screen.getByText('표시할 데이터가 없습니다')).toBeInTheDocument()
  })
})

describe('EmptyGeneric', () => {
  it('renders with default message', () => {
    render(<EmptyGeneric />)
    expect(screen.getByText('데이터가 없습니다')).toBeInTheDocument()
  })

  it('renders with custom message', () => {
    render(<EmptyGeneric message="Custom message" />)
    expect(screen.getByText('Custom message')).toBeInTheDocument()
  })
})
