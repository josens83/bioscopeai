import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Badge, StatusBadge, PlanBadge } from '../../components/ui/Badge'
import { CheckIcon } from '../../components/ui/Icons'

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>Test Badge</Badge>)
    expect(screen.getByText('Test Badge')).toBeInTheDocument()
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Badge variant="default">Default</Badge>)
    expect(screen.getByText('Default')).toHaveClass('bg-surface-100')

    rerender(<Badge variant="brand">Brand</Badge>)
    expect(screen.getByText('Brand')).toHaveClass('bg-brand-100')

    rerender(<Badge variant="success">Success</Badge>)
    expect(screen.getByText('Success')).toHaveClass('bg-success-100')

    rerender(<Badge variant="error">Error</Badge>)
    expect(screen.getByText('Error')).toHaveClass('bg-error-100')

    rerender(<Badge variant="warning">Warning</Badge>)
    expect(screen.getByText('Warning')).toHaveClass('bg-warning-100')
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Badge size="sm">Small</Badge>)
    expect(screen.getByText('Small')).toHaveClass('px-2')

    rerender(<Badge size="md">Medium</Badge>)
    expect(screen.getByText('Medium')).toHaveClass('px-2.5')

    rerender(<Badge size="lg">Large</Badge>)
    expect(screen.getByText('Large')).toHaveClass('px-3')
  })

  it('renders with dot indicator', () => {
    render(<Badge dot>With Dot</Badge>)
    const badge = screen.getByText('With Dot')
    const dot = badge.querySelector('span.rounded-full')
    expect(dot).toBeInTheDocument()
  })

  it('renders with icon', () => {
    render(
      <Badge icon={<CheckIcon data-testid="badge-icon" size={14} />}>
        With Icon
      </Badge>
    )
    expect(screen.getByTestId('badge-icon')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<Badge className="custom-class">Custom</Badge>)
    expect(screen.getByText('Custom')).toHaveClass('custom-class')
  })
})

describe('StatusBadge', () => {
  it('renders active status', () => {
    render(<StatusBadge status="active" />)
    expect(screen.getByText('활성')).toBeInTheDocument()
  })

  it('renders inactive status', () => {
    render(<StatusBadge status="inactive" />)
    expect(screen.getByText('비활성')).toBeInTheDocument()
  })

  it('renders pending status', () => {
    render(<StatusBadge status="pending" />)
    expect(screen.getByText('대기중')).toBeInTheDocument()
  })

  it('renders success status', () => {
    render(<StatusBadge status="success" />)
    expect(screen.getByText('성공')).toBeInTheDocument()
  })

  it('renders error status', () => {
    render(<StatusBadge status="error" />)
    expect(screen.getByText('오류')).toBeInTheDocument()
  })

  it('renders with custom label', () => {
    render(<StatusBadge status="active" label="Online" />)
    expect(screen.getByText('Online')).toBeInTheDocument()
  })
})

describe('PlanBadge', () => {
  it('renders free plan', () => {
    render(<PlanBadge plan="free" />)
    expect(screen.getByText('Free')).toBeInTheDocument()
  })

  it('renders basic plan', () => {
    render(<PlanBadge plan="basic" />)
    expect(screen.getByText('Basic')).toBeInTheDocument()
  })

  it('renders premium plan', () => {
    render(<PlanBadge plan="premium" />)
    expect(screen.getByText('Premium')).toBeInTheDocument()
  })

  it('renders enterprise plan', () => {
    render(<PlanBadge plan="enterprise" />)
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
  })
})
