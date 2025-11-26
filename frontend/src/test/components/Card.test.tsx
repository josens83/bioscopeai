import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Card, CardHeader, CardContent, CardFooter, StatCard } from '../../components/ui/Card'
import { DocumentIcon } from '../../components/ui/Icons'

describe('Card', () => {
  it('renders children', () => {
    render(
      <Card>
        <div data-testid="content">Card content</div>
      </Card>
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('renders with default variant', () => {
    render(<Card data-testid="card">Content</Card>)
    expect(screen.getByTestId('card')).toHaveClass('bg-white')
  })

  it('renders with elevated variant', () => {
    render(<Card variant="elevated" data-testid="card">Content</Card>)
    expect(screen.getByTestId('card')).toHaveClass('shadow-md')
  })

  it('renders with outlined variant', () => {
    render(<Card variant="outlined" data-testid="card">Content</Card>)
    expect(screen.getByTestId('card')).toHaveClass('border-2')
  })

  it('renders with ghost variant', () => {
    render(<Card variant="ghost" data-testid="card">Content</Card>)
    expect(screen.getByTestId('card')).toHaveClass('bg-surface-50')
  })

  it('supports custom className', () => {
    render(<Card className="custom-class" data-testid="card">Content</Card>)
    expect(screen.getByTestId('card')).toHaveClass('custom-class')
  })

  it('supports onClick handler', () => {
    const handleClick = vi.fn()
    render(<Card onClick={handleClick} data-testid="card">Content</Card>)

    fireEvent.click(screen.getByTestId('card'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})

describe('CardHeader', () => {
  it('renders title', () => {
    render(<CardHeader title="Card Title" />)
    expect(screen.getByText('Card Title')).toBeInTheDocument()
  })

  it('renders title and subtitle', () => {
    render(<CardHeader title="Card Title" subtitle="Card subtitle" />)
    expect(screen.getByText('Card Title')).toBeInTheDocument()
    expect(screen.getByText('Card subtitle')).toBeInTheDocument()
  })

  it('renders with action', () => {
    render(
      <CardHeader
        title="Card Title"
        action={<button data-testid="action">Action</button>}
      />
    )
    expect(screen.getByTestId('action')).toBeInTheDocument()
  })
})

describe('CardContent', () => {
  it('renders children', () => {
    render(
      <CardContent>
        <p data-testid="content">Content text</p>
      </CardContent>
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('supports custom className', () => {
    render(<CardContent className="custom-class" data-testid="content">Content</CardContent>)
    expect(screen.getByTestId('content')).toHaveClass('custom-class')
  })
})

describe('CardFooter', () => {
  it('renders children', () => {
    render(
      <CardFooter>
        <button data-testid="footer-btn">Submit</button>
      </CardFooter>
    )
    expect(screen.getByTestId('footer-btn')).toBeInTheDocument()
  })
})

describe('StatCard', () => {
  it('renders title and value', () => {
    render(<StatCard title="Total Papers" value={42} />)
    expect(screen.getByText('Total Papers')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders with icon', () => {
    render(<StatCard title="Papers" value={10} icon={<DocumentIcon data-testid="icon" size={24} />} />)
    expect(screen.getByText('Papers')).toBeInTheDocument()
    expect(screen.getByTestId('icon')).toBeInTheDocument()
  })

  it('renders with description', () => {
    render(<StatCard title="Papers" value={10} description="Last 30 days" />)
    expect(screen.getByText('Last 30 days')).toBeInTheDocument()
  })

  it('renders with positive change', () => {
    render(<StatCard title="Papers" value={10} change={{ value: 12, type: 'increase' }} />)
    expect(screen.getByText('+12%')).toBeInTheDocument()
  })

  it('renders with negative change', () => {
    render(<StatCard title="Papers" value={10} change={{ value: 5, type: 'decrease' }} />)
    expect(screen.getByText('5%')).toBeInTheDocument()
  })

  it('renders string value', () => {
    render(<StatCard title="Plan" value="Pro" />)
    expect(screen.getByText('Pro')).toBeInTheDocument()
  })
})
