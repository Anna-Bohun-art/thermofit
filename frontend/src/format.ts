import type { Param } from './api'

/** Significant-digit formatting that avoids 1e-7 noise in the table. */
export function fmt(v: number | null | undefined, digits = 4): string {
  if (v === null || v === undefined || !Number.isFinite(v)) return '–'
  const a = Math.abs(v)
  if (a !== 0 && (a < 1e-3 || a >= 1e6)) return v.toExponential(digits - 1)
  return Number(v.toPrecision(digits)).toString()
}

export function paramRow(p: Param) {
  return {
    name: p.name,
    value: fmt(p.value, 5),
    stderr: fmt(p.stderr),
    ci: p.ci95 ? `${fmt(p.ci95[0], 5)} … ${fmt(p.ci95[1], 5)}` : '–',
    unit: p.unit,
  }
}

/** Kelvin parameters are shown in degC for the user. */
export function displayParam(p: Param): Param {
  if (p.unit === 'K' && p.name.startsWith('T*')) {
    return {
      ...p,
      value: p.value - 273.15,
      ci95: p.ci95 ? [p.ci95[0] - 273.15, p.ci95[1] - 273.15] : null,
      unit: '°C',
    }
  }
  return p
}
