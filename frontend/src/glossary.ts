import type { FitResult, Param } from './api'
import { fmt } from './format'

export type ParamInfo = { label: string; meaning: string; advanced: boolean }

/** Plain-language names for the fitted parameters (the technical symbol stays in brackets). */
export function describeParam(name: string): ParamInfo {
  if (name === 'Tm')
    return {
      label: 'Melting temperature (Tm)',
      meaning: 'The temperature at which half of the protein is unfolded. Higher means more stable.',
      advanced: false,
    }
  if (name.startsWith('ΔH'))
    return {
      label: 'Energy needed to unfold (ΔH)',
      meaning: 'Heat absorbed when one mole of protein unfolds. A larger value means a more tightly folded protein.',
      advanced: false,
    }
  if (name === 'ΔCp')
    return {
      label: 'Heat-capacity change (ΔCp)',
      meaning: 'How much the heat capacity changes on unfolding. It sets how stability changes with temperature.',
      advanced: false,
    }
  if (name.startsWith('T*'))
    return {
      label: 'Temperature of fast unfolding (T*)',
      meaning: 'The temperature at which the protein unfolds at a rate of once per minute.',
      advanced: false,
    }
  if (name === 'Ea')
    return {
      label: 'Energy barrier to unfolding (Ea)',
      meaning: 'How strongly the unfolding speed depends on temperature. A larger barrier means a sharper onset.',
      advanced: false,
    }
  if (name === 'baseline offset')
    return { label: 'Baseline level', meaning: 'Instrument background that is subtracted (constant part).', advanced: true }
  if (name === 'baseline slope')
    return { label: 'Baseline tilt', meaning: 'Instrument background that is subtracted (sloping part).', advanced: true }
  return { label: name, meaning: '', advanced: false }
}

/** One or two sentences that say what the result means, for readers who are not protein scientists. */
export function plainSummary(result: FitResult, shown: Param[]): string {
  const get = (test: (n: string) => boolean) => shown.find((p) => test(p.name))
  if (result.model === 'two_state') {
    const tm = get((n) => n === 'Tm')
    const dh = get((n) => n === 'ΔH')
    if (tm && dh)
      return `Heated up, this protein is half unfolded at ${fmt(tm.value, 4)} °C. Unfolding it takes about ${fmt(dh.value, 3)} kcal per mole, and the process is reversible: the protein can fold back when it cools.`
  }
  if (result.model === 'irreversible') {
    const ts = get((n) => n.startsWith('T*'))
    const ea = get((n) => n === 'Ea')
    const v = result.extras['scan_rate_K_per_min']
    if (ts && ea)
      return `This protein unfolds for good (it cannot fold back). Heated at ${typeof v === 'number' ? fmt(v, 3) : 'the given'} K/min, it unfolds at a rate of once per minute at ${fmt(ts.value, 4)} °C. The energy barrier to unfolding is about ${fmt(ea.value, 3)} kcal per mole.`
  }
  return ''
}
