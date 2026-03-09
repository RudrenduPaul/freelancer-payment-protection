import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders } from '@/test/utils'
import { StatusBadge } from '@/components/shared/status-badge'
import type { InvoiceStatus } from '@/lib/types'

const STATUS_CASES: { status: InvoiceStatus; expectedLabel: string }[] = [
  { status: 'draft', expectedLabel: 'Draft' },
  { status: 'sent', expectedLabel: 'Sent' },
  { status: 'overdue', expectedLabel: 'Overdue' },
  { status: 'disputed', expectedLabel: 'Disputed' },
  { status: 'paid', expectedLabel: 'Paid' },
  { status: 'written_off', expectedLabel: 'Written Off' },
]

describe('StatusBadge', () => {
  it.each(STATUS_CASES)(
    'renders "$expectedLabel" for status "$status"',
    ({ status, expectedLabel }) => {
      renderWithProviders(<StatusBadge status={status} />)
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    },
  )

  it('applies a custom className to the badge element', () => {
    renderWithProviders(<StatusBadge status="paid" className="test-custom-class" />)
    const badge = screen.getByText('Paid')
    expect(badge).toHaveClass('test-custom-class')
  })

  it('renders overdue badge with correct red color class', () => {
    renderWithProviders(<StatusBadge status="overdue" />)
    const badge = screen.getByText('Overdue')
    expect(badge).toHaveClass('bg-red-50')
  })

  it('renders paid badge with correct emerald color class', () => {
    renderWithProviders(<StatusBadge status="paid" />)
    const badge = screen.getByText('Paid')
    expect(badge).toHaveClass('bg-emerald-50')
  })
})
