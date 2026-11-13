import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

// Nach jedem Test das echte fetch wiederherstellen
afterEach(() => vi.unstubAllGlobals())

describe('App', () => {
  it('shows a readable error when the backend is not reachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 503 })))
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Load simulated demo' }))
    const alert = await screen.findByRole('alert')
    expect(alert.textContent).toBe('Could not load demo data')
  })

  it('shows the error message from the API when the fit fails', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(Response.json({ csv: 'T,Cp\n40,0.1\n', synthetic: true, source: null, scan_rate: null }))
      .mockResolvedValueOnce(Response.json({ detail: 'Need at least 10 data points' }, { status: 422 })))
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: 'Load simulated demo' }))
    const alert = await screen.findByRole('alert')
    expect(alert.textContent).toBe('Need at least 10 data points')
  })
})