import { describe, expect, it } from 'vitest'
import type { FitResult, Param } from './api'
import { describeParam, plainSummary } from './glossary'

const p = (name: string, value: number, unit = ''): Param => ({ name, value, stderr: null, ci95: null, unit })
const base = { x: [], y: [], x_fit: [], y_fit: [], residuals: [], r2: 1, rmse: 0, n_points: 0 }

describe('describeParam', () => {
  it('gives plain names and keeps the symbol in brackets', () => {
    expect(describeParam('Tm').label).toBe('Melting temperature (Tm)')
    expect(describeParam('T* (k = 1/min)').label).toContain('(T*)')
    expect(describeParam('Ea').label).toContain('(Ea)')
  })
  it('marks only the baseline parameters as advanced', () => {
    expect(describeParam('baseline offset').advanced).toBe(true)
    expect(describeParam('baseline slope').advanced).toBe(true)
    for (const n of ['Tm', 'ΔH', 'ΔCp', 'T* (k = 1/min)', 'Ea']) expect(describeParam(n).advanced).toBe(false)
  })
  it('falls back to the raw name for unknown parameters', () => {
    expect(describeParam('mystery').label).toBe('mystery')
  })
})

describe('plainSummary', () => {
  it('describes a reversible transition', () => {
    const r: FitResult = { ...base, model: 'two_state', params: [], extras: {} }
    const s = plainSummary(r, [p('Tm', 45.332, '°C'), p('ΔH', 137.11, 'kcal/mol')])
    expect(s).toContain('45.33 °C')
    expect(s).toContain('137 kcal per mole')
    expect(s).toContain('reversible')
  })
  it('describes an irreversible transition including the scan rate', () => {
    const r: FitResult = { ...base, model: 'irreversible', params: [], extras: { scan_rate_K_per_min: 1 } }
    const s = plainSummary(r, [p('T* (k = 1/min)', 43.057, '°C'), p('Ea', 115.91, 'kcal/mol')])
    expect(s).toContain('1 K/min')
    expect(s).toContain('43.06 °C')
    expect(s).toContain('116 kcal per mole')
  })
  it('returns an empty string when the key parameters are missing', () => {
    const r: FitResult = { ...base, model: 'two_state', params: [], extras: {} }
    expect(plainSummary(r, [])).toBe('')
  })
})
