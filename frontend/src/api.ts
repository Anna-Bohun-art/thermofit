export type Param = {
  name: string
  value: number
  stderr: number | null
  ci95: [number, number] | null
  unit: string
}

export type FitResult = {
  model: string
  params: Param[]
  x: number[]
  y: number[]
  x_fit: number[]
  y_fit: number[]
  residuals: number[]
  r2: number
  rmse: number
  n_points: number
  extras: Record<string, unknown>
}

export type Analysis = 'dsc_two_state' | 'dsc_irreversible'

export type FitOptions = {
  analysis: Analysis
  cpUnit: 'kcal' | 'cal'
  scanRate: number
  fitDcp: boolean
}

export async function runFit(file: File, opts: FitOptions): Promise<FitResult> {
  const form = new FormData()
  form.append('file', file)
  form.append('model', opts.analysis === 'dsc_two_state' ? 'two_state' : 'irreversible')
  form.append('cp_unit', opts.cpUnit)
  form.append('fit_dcp', String(opts.fitDcp))
  if (opts.analysis === 'dsc_irreversible') form.append('scan_rate', String(opts.scanRate))
  const res = await fetch('/api/fit/dsc', { method: 'POST', body: form })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${res.status})`)
  return body as FitResult
}

export type DemoKind = Analysis | 'thesis_zn' | 'thesis_co' | 'thesis_fe_0p5' | 'thesis_fe_1p0' | 'thesis_fe_1p46'

export type Demo = { file: File; synthetic: boolean; source: string | null; scanRate: number | null }

export async function loadDemo(kind: DemoKind): Promise<Demo> {
  const res = await fetch(`/api/demo/${kind}`)
  if (!res.ok) throw new Error('Could not load demo data')
  const body = (await res.json()) as { csv: string; synthetic: boolean; source: string | null; scan_rate: number | null }
  const suffix = body.synthetic ? 'SIMULATED' : 'digitized'
  return { file: new File([body.csv], `${kind}_${suffix}.csv`, { type: 'text/csv' }), synthetic: body.synthetic, source: body.source, scanRate: body.scan_rate }
}
