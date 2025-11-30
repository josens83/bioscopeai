import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button, IconButton } from '../../components/ui/Button'
import { PlusIcon } from '../../components/ui/Icons'

describe('Button', () => {
  it('renders with default props', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })

  it('renders with different variants', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-brand-500')

    rerender(<Button variant="secondary">Secondary</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-surface-100')

    rerender(<Button variant="danger">Danger</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-error-500')

    rerender(<Button variant="ghost">Ghost</Button>)
    expect(screen.getByRole('button')).toHaveClass('text-surface-600')

    rerender(<Button variant="outline">Outline</Button>)
    expect(screen.getByRole('button')).toHaveClass('border-2')
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<Button size="sm">Small</Button>)
    expect(screen.getByRole('button')).toHaveClass('px-3')

    rerender(<Button size="md">Medium</Button>)
    expect(screen.getByRole('button')).toHaveClass('px-4')

    rerender(<Button size="lg">Large</Button>)
    expect(screen.getByRole('button')).toHaveClass('px-6')
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('does not trigger click when disabled', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick} disabled>Disabled</Button>)

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).not.toHaveBeenCalled()
  })

  it('shows loading state', () => {
    render(<Button isLoading>Loading</Button>)

    // Button should be disabled when loading
    expect(screen.getByRole('button')).toBeDisabled()
    // Should have spinner
    expect(screen.getByRole('button').querySelector('svg')).toBeInTheDocument()
  })

  it('renders with left icon', () => {
    render(<Button leftIcon={<PlusIcon data-testid="left-icon" size={16} />}>Add Item</Button>)

    expect(screen.getByTestId('left-icon')).toBeInTheDocument()
  })

  it('renders with right icon', () => {
    render(<Button rightIcon={<PlusIcon data-testid="right-icon" size={16} />}>Add Item</Button>)

    expect(screen.getByTestId('right-icon')).toBeInTheDocument()
  })

  it('supports custom className', () => {
    render(<Button className="custom-class">Custom</Button>)

    expect(screen.getByRole('button')).toHaveClass('custom-class')
  })

  it('supports type attribute', () => {
    render(<Button type="submit">Submit</Button>)

    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit')
  })
})

describe('IconButton', () => {
  it('renders with icon', () => {
    render(
      <IconButton icon={<PlusIcon data-testid="icon" size={16} />} label="Add item" />
    )

    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender } = render(
      <IconButton icon={<PlusIcon size={16} />} label="Small" size="sm" />
    )
    expect(screen.getByRole('button')).toHaveClass('p-1.5')

    rerender(
      <IconButton icon={<PlusIcon size={20} />} label="Medium" size="md" />
    )
    expect(screen.getByRole('button')).toHaveClass('p-2')

    rerender(
      <IconButton icon={<PlusIcon size={24} />} label="Large" size="lg" />
    )
    expect(screen.getByRole('button')).toHaveClass('p-2.5')
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    render(
      <IconButton icon={<PlusIcon size={16} />} label="Click" onClick={handleClick} />
    )

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('has accessible label', () => {
    render(
      <IconButton icon={<PlusIcon size={16} />} label="Add item" />
    )

    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Add item')
  })
})
