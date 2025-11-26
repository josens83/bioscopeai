import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Input, PasswordInput, SearchInput, Textarea } from '../../components/ui/Input'

describe('Input', () => {
  it('renders with default props', () => {
    render(<Input placeholder="Enter text" />)
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
  })

  it('renders with label', () => {
    render(<Input label="Email" placeholder="Enter email" />)
    expect(screen.getByText('Email')).toBeInTheDocument()
  })

  it('renders with hint text', () => {
    render(<Input hint="This is a hint" />)
    expect(screen.getByText('This is a hint')).toBeInTheDocument()
  })

  it('renders with error state', () => {
    render(<Input error="This field is required" />)
    expect(screen.getByText('This field is required')).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveClass('border-error-500')
  })

  it('handles value changes', async () => {
    const handleChange = vi.fn()
    render(<Input onChange={handleChange} />)

    await userEvent.type(screen.getByRole('textbox'), 'hello')
    expect(handleChange).toHaveBeenCalled()
  })

  it('supports disabled state', () => {
    render(<Input disabled />)
    expect(screen.getByRole('textbox')).toBeDisabled()
  })

  it('supports required attribute', () => {
    render(<Input required label="Name" />)
    expect(screen.getByRole('textbox')).toBeRequired()
  })

  it('supports different input types', () => {
    render(<Input type="email" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email')
  })
})

describe('PasswordInput', () => {
  it('renders as password type by default', () => {
    render(<PasswordInput placeholder="Enter password" />)
    const input = screen.getByPlaceholderText('Enter password')
    expect(input).toHaveAttribute('type', 'password')
  })

  it('toggles password visibility', async () => {
    render(<PasswordInput placeholder="Enter password" />)
    const input = screen.getByPlaceholderText('Enter password')
    const toggleButton = screen.getByRole('button')

    // Initially password is hidden
    expect(input).toHaveAttribute('type', 'password')
    expect(toggleButton).toHaveAttribute('aria-pressed', 'false')

    // Click to show password
    await userEvent.click(toggleButton)
    expect(input).toHaveAttribute('type', 'text')
    expect(toggleButton).toHaveAttribute('aria-pressed', 'true')

    // Click again to hide password
    await userEvent.click(toggleButton)
    expect(input).toHaveAttribute('type', 'password')
    expect(toggleButton).toHaveAttribute('aria-pressed', 'false')
  })

  it('renders with label', () => {
    render(<PasswordInput label="Password" />)
    expect(screen.getByText('Password')).toBeInTheDocument()
  })
})

describe('SearchInput', () => {
  it('renders with search icon', () => {
    const { container } = render(<SearchInput placeholder="Search..." />)
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
    // Search icon should be present - search for SVG in the container
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('handles value changes', async () => {
    const handleChange = vi.fn()
    render(<SearchInput onChange={handleChange} placeholder="Search..." />)

    await userEvent.type(screen.getByPlaceholderText('Search...'), 'test query')
    expect(handleChange).toHaveBeenCalled()
  })
})

describe('Textarea', () => {
  it('renders with default props', () => {
    render(<Textarea placeholder="Enter description" />)
    expect(screen.getByPlaceholderText('Enter description')).toBeInTheDocument()
  })

  it('renders with label', () => {
    render(<Textarea label="Description" />)
    expect(screen.getByText('Description')).toBeInTheDocument()
  })

  it('supports rows attribute', () => {
    render(<Textarea rows={5} />)
    expect(screen.getByRole('textbox')).toHaveAttribute('rows', '5')
  })

  it('handles value changes', async () => {
    const handleChange = vi.fn()
    render(<Textarea onChange={handleChange} />)

    await userEvent.type(screen.getByRole('textbox'), 'test content')
    expect(handleChange).toHaveBeenCalled()
  })

  it('renders with error state', () => {
    render(<Textarea error="Description is required" />)
    expect(screen.getByText('Description is required')).toBeInTheDocument()
  })
})
