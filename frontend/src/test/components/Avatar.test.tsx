import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Avatar, AvatarGroup } from '../../components/ui/Avatar'

describe('Avatar', () => {
  it('renders with name initials', () => {
    render(<Avatar name="John Doe" />)
    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('renders single name initials', () => {
    render(<Avatar name="John" />)
    expect(screen.getByText('JO')).toBeInTheDocument()
  })

  it('renders fallback when provided', () => {
    render(<Avatar name="John Doe" fallback="X" />)
    expect(screen.getByText('X')).toBeInTheDocument()
  })

  it('renders image when src provided', () => {
    render(<Avatar src="https://example.com/avatar.jpg" alt="Test Avatar" />)
    const img = screen.getByRole('img')
    expect(img).toHaveAttribute('src', 'https://example.com/avatar.jpg')
    expect(img).toHaveAttribute('alt', 'Test Avatar')
  })

  it('shows initials on image error', () => {
    render(<Avatar src="invalid-url.jpg" name="John Doe" />)
    const img = screen.getByRole('img')
    fireEvent.error(img)
    expect(screen.getByText('JD')).toBeInTheDocument()
  })

  it('renders with different sizes', () => {
    const { rerender, container } = render(<Avatar name="Test" size="xs" />)
    expect(container.firstChild).toHaveClass('w-6', 'h-6')

    rerender(<Avatar name="Test" size="sm" />)
    expect(container.firstChild).toHaveClass('w-8', 'h-8')

    rerender(<Avatar name="Test" size="md" />)
    expect(container.firstChild).toHaveClass('w-10', 'h-10')

    rerender(<Avatar name="Test" size="lg" />)
    expect(container.firstChild).toHaveClass('w-12', 'h-12')

    rerender(<Avatar name="Test" size="xl" />)
    expect(container.firstChild).toHaveClass('w-16', 'h-16')

    rerender(<Avatar name="Test" size="2xl" />)
    expect(container.firstChild).toHaveClass('w-20', 'h-20')
  })

  it('renders status indicator when showStatus is true', () => {
    const { container } = render(<Avatar name="Test" showStatus status="online" />)
    const statusDot = container.querySelector('.bg-success-500')
    expect(statusDot).toBeInTheDocument()
  })

  it('renders different status colors', () => {
    const { container, rerender } = render(
      <Avatar name="Test" showStatus status="online" />
    )
    expect(container.querySelector('.bg-success-500')).toBeInTheDocument()

    rerender(<Avatar name="Test" showStatus status="offline" />)
    expect(container.querySelector('.bg-surface-400')).toBeInTheDocument()

    rerender(<Avatar name="Test" showStatus status="busy" />)
    expect(container.querySelector('.bg-error-500')).toBeInTheDocument()

    rerender(<Avatar name="Test" showStatus status="away" />)
    expect(container.querySelector('.bg-warning-500')).toBeInTheDocument()
  })

  it('renders placeholder icon when no name or image', () => {
    render(<Avatar />)
    const svg = document.querySelector('svg')
    expect(svg).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<Avatar name="Test" className="custom-class" />)
    expect(container.firstChild).toHaveClass('custom-class')
  })
})

describe('AvatarGroup', () => {
  const avatars = [
    { name: 'John Doe' },
    { name: 'Jane Smith' },
    { name: 'Bob Wilson' },
    { name: 'Alice Brown' },
    { name: 'Charlie Davis' },
  ]

  it('renders avatars up to max limit', () => {
    render(<AvatarGroup avatars={avatars} max={3} />)
    expect(screen.getByText('JD')).toBeInTheDocument()
    expect(screen.getByText('JS')).toBeInTheDocument()
    expect(screen.getByText('BW')).toBeInTheDocument()
    expect(screen.queryByText('AB')).not.toBeInTheDocument()
  })

  it('shows remaining count', () => {
    render(<AvatarGroup avatars={avatars} max={3} />)
    expect(screen.getByText('+2')).toBeInTheDocument()
  })

  it('renders all avatars when less than max', () => {
    const fewAvatars = [{ name: 'John' }, { name: 'Jane' }]
    render(<AvatarGroup avatars={fewAvatars} max={4} />)
    expect(screen.getByText('JO')).toBeInTheDocument()
    expect(screen.getByText('JA')).toBeInTheDocument()
    expect(screen.queryByText('+')).not.toBeInTheDocument()
  })

  it('uses default max of 4', () => {
    render(<AvatarGroup avatars={avatars} />)
    expect(screen.getByText('+1')).toBeInTheDocument()
  })
})
