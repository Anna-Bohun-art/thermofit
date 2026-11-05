import { describe, expect, it } from 'vitest'
import { displayParam, fmt } from './format'

describe('fmt', () => {
  it('rounds to significant digits', () => expect(fmt(134.80012)).toBe('134.8'))
  it('uses exponent for tiny values', () => expect(fmt(0.00001234)).toBe('1.234e-5'))
  it('shows a dash for missing values', () => {
    expect(fmt(null)).toBe('–')
    expect(fmt(NaN)).toBe('–')
  })
})

describe('displayParam', () => {
  it('converts T* from K to degC', () => {
    const p = displayParam({ name: 'T* (k = 1/min)', value: 325.15, stderr: 0.1, ci95: [325, 325.3], unit: 'K' })
    expect(p.value).toBeCloseTo(52, 6)
    expect(p.unit).toBe('°C')
  })
  it('leaves other parameters untouched', () => {
    const p = { name: 'ΔH', value: 100, stderr: 1, ci95: null, unit: 'kcal/mol' }
    expect(displayParam(p)).toEqual(p)
  })
})
