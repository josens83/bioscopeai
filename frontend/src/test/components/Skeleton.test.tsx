import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  Skeleton,
  SkeletonText,
  SkeletonAvatar,
  SkeletonCard,
  SkeletonStatCard,
  SkeletonListItem,
  SkeletonPaperCard,
} from '../../components/ui/Skeleton'

describe('Skeleton', () => {
  it('renders with default props', () => {
    render(<Skeleton data-testid="skeleton" />)
    const skeleton = screen.getByTestId('skeleton')
    expect(skeleton).toBeInTheDocument()
    expect(skeleton).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders with shimmer variant by default', () => {
    render(<Skeleton data-testid="skeleton" />)
    expect(screen.getByTestId('skeleton')).toHaveClass('skeleton-shimmer')
  })

  it('renders with default variant', () => {
    render(<Skeleton data-testid="skeleton" variant="default" />)
    expect(screen.getByTestId('skeleton')).toHaveClass('skeleton')
  })

  it('applies width and height as numbers', () => {
    render(<Skeleton data-testid="skeleton" width={100} height={50} />)
    const skeleton = screen.getByTestId('skeleton')
    expect(skeleton).toHaveStyle({ width: '100px', height: '50px' })
  })

  it('applies width and height as strings', () => {
    render(<Skeleton data-testid="skeleton" width="50%" height="2rem" />)
    const skeleton = screen.getByTestId('skeleton')
    expect(skeleton).toHaveStyle({ width: '50%', height: '2rem' })
  })

  it('renders with different rounded values', () => {
    const { rerender } = render(<Skeleton data-testid="skeleton" rounded="none" />)
    expect(screen.getByTestId('skeleton')).toHaveClass('rounded-none')

    rerender(<Skeleton data-testid="skeleton" rounded="sm" />)
    expect(screen.getByTestId('skeleton')).toHaveClass('rounded-sm')

    rerender(<Skeleton data-testid="skeleton" rounded="lg" />)
    expect(screen.getByTestId('skeleton')).toHaveClass('rounded-lg')

    rerender(<Skeleton data-testid="skeleton" rounded="full" />)
    expect(screen.getByTestId('skeleton')).toHaveClass('rounded-full')
  })

  it('applies custom className', () => {
    render(<Skeleton data-testid="skeleton" className="custom-class" />)
    expect(screen.getByTestId('skeleton')).toHaveClass('custom-class')
  })
})

describe('SkeletonText', () => {
  it('renders default number of lines', () => {
    const { container } = render(<SkeletonText />)
    const wrapper = container.querySelector('.space-y-2')
    expect(wrapper?.children).toHaveLength(3)
  })

  it('renders specified number of lines', () => {
    const { container } = render(<SkeletonText lines={5} />)
    const wrapper = container.querySelector('.space-y-2')
    expect(wrapper?.children).toHaveLength(5)
  })
})

describe('SkeletonAvatar', () => {
  it('renders with default size', () => {
    render(<SkeletonAvatar />)
    const avatar = document.querySelector('[aria-hidden="true"]')
    expect(avatar).toHaveStyle({ width: '40px', height: '40px' })
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<SkeletonAvatar size="sm" />)
    let avatar = document.querySelector('[aria-hidden="true"]')
    expect(avatar).toHaveStyle({ width: '32px', height: '32px' })

    rerender(<SkeletonAvatar size="lg" />)
    avatar = document.querySelector('[aria-hidden="true"]')
    expect(avatar).toHaveStyle({ width: '48px', height: '48px' })

    rerender(<SkeletonAvatar size="xl" />)
    avatar = document.querySelector('[aria-hidden="true"]')
    expect(avatar).toHaveStyle({ width: '64px', height: '64px' })
  })
})

describe('SkeletonCard', () => {
  it('renders card skeleton structure', () => {
    render(<SkeletonCard />)
    const card = document.querySelector('[aria-hidden="true"]')
    expect(card).toBeInTheDocument()
    expect(card).toHaveClass('card')
  })
})

describe('SkeletonStatCard', () => {
  it('renders stat card skeleton structure', () => {
    render(<SkeletonStatCard />)
    const card = document.querySelector('[aria-hidden="true"]')
    expect(card).toBeInTheDocument()
    expect(card).toHaveClass('card')
  })
})

describe('SkeletonListItem', () => {
  it('renders list item skeleton structure', () => {
    render(<SkeletonListItem />)
    const listItem = document.querySelector('[aria-hidden="true"]')
    expect(listItem).toBeInTheDocument()
  })
})

describe('SkeletonPaperCard', () => {
  it('renders paper card skeleton structure', () => {
    render(<SkeletonPaperCard />)
    const card = document.querySelector('[aria-hidden="true"]')
    expect(card).toBeInTheDocument()
    expect(card).toHaveClass('card')
  })
})
