import React from 'react'
import { render, type RenderOptions, type RenderResult } from '@testing-library/react'

/**
 * Minimal provider shell for unit tests.
 * Extend this if you add context providers (e.g. auth, theme) to the app.
 */
function Providers({ children }: { children: React.ReactNode }) {
  return React.createElement(React.Fragment, null, children)
}

export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
): RenderResult {
  return render(ui, { wrapper: Providers, ...options })
}
