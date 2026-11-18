import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ExplainPanel } from './ExplainPanel'
import type { FitResult } from './api'

const fit = { model: 'two_state', params: [] } as unknown as FitResult
afterEach(() => vi.unstubAllGlobals())

describe('ExplainPanel', () => {
  it('shows answer and sources', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      Response.json({ answer: 'Tm ist der Mittelpunkt.', sources: [{ id: 'm#0', heading: 'Tm', text: 'x' }] })))
    render(<ExplainPanel result={fit} />)
    fireEvent.click(screen.getByRole('button', { name: /Was bedeutet Tm/ }))
    expect((await screen.findByTestId('answer')).textContent).toBe('Tm ist der Mittelpunkt.')
    expect(screen.getByText(/Quelle: Tm/)).toBeTruthy()
  })

  it('shows a readable error on rate limit', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{}', { status: 429 })))
    render(<ExplainPanel result={fit} />)
    fireEvent.click(screen.getByRole('button', { name: /Was bedeutet Tm/ }))
    expect((await screen.findByRole('alert')).textContent).toMatch(/Zu viele Fragen/)
  })
})
