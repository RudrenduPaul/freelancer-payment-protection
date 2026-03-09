import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders } from '@/test/utils'
import { RiskBadge } from '@/components/shared/risk-badge'
import type { RiskLevel } from '@/lib/types'

const LEVEL_CASES: { level: RiskLevel; expectedLabel: string; expectedColorClass: string }[] = [
  {
    level: 'low',
    expectedLabel: 'Low Risk',
    expectedColorClass: 'bg-emerald-50',
  },
  {
    level: 'medium',
    expectedLabel: 'Medium Risk',
    expectedColorClass: 'bg-amber-50',
  },
  {
    level: 'high',
    expectedLabel: 'High Risk',
    expectedColorClass: 'bg-orange-50',
  },
  {
    level: 'critical',
    expectedLabel: 'Critical',
    expectedColorClass: 'bg-red-50',
  },
]

describe('RiskBadge', () => {
  it.each(LEVEL_CASES)(
    'renders label "$expectedLabel" for level "$level"',
    ({ level, expectedLabel }) => {
      renderWithProviders(<RiskBadge level={level} />)
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    },
  )

  it.each(LEVEL_CASES)(
    'applies correct background color class "$expectedColorClass" for level "$level"',
    ({ level, expectedLabel, expectedColorClass }) => {
      renderWithProviders(<RiskBadge level={level} />)
      const badge = screen.getByText(expectedLabel).closest('span')
      expect(badge).toHaveClass(expectedColorClass)
    },
  )

  it('renders score when provided', () => {
    renderWithProviders(<RiskBadge level="high" score={72} />)
    expect(screen.getByText('72')).toBeInTheDocument()
  })

  it('does not render score when not provided', () => {
    renderWithProviders(<RiskBadge level="low" />)
    // No score parenthetical should be present — check that "(" is absent
    expect(screen.queryByText(/^\(\d+\)$/)).not.toBeInTheDocument()
  })
})
