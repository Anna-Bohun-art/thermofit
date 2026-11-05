import { useState } from 'react'
import { loadDemo, runFit, type Analysis, type DemoKind, type FitResult } from './api'
import { FitChart } from './FitChart'
import { displayParam, fmt, paramRow } from './format'
import { describeParam, plainSummary } from './glossary'

const LABELS: Record<Analysis, { title: string; x: string; y: string; hint: string }> = {
  dsc_two_state: {
    title: 'DSC – reversible two-state',
    x: 'Temperature (°C)', y: 'Heat absorbed (Cp)',
    hint: 'CSV: temperature in °C, excess heat capacity per mole. Fits Tm, ΔH (optionally ΔCp) and a linear baseline.',
  },
  dsc_irreversible: {
    title: 'DSC – irreversible N → D',
    x: 'Temperature (°C)', y: 'Heat absorbed (Cp)',
    hint: 'CSV as above. Needs the scan rate. Fits ΔH, activation energy Ea and T* (where k = 1/min).',
  },
}

export default function App() {
  const [analysis, setAnalysis] = useState<Analysis>('dsc_two_state')
  const [file, setFile] = useState<File | null>(null)
  const [cpUnit, setCpUnit] = useState<'kcal' | 'cal'>('kcal')
  const [scanRate, setScanRate] = useState(1)
  const [fitDcp, setFitDcp] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<FitResult | null>(null)
  const [banner, setBanner] = useState<{ text: string; kind: 'sim' | 'src' } | null>(null)

  const meta = LABELS[analysis]

  async function fit(f: File, note: { text: string; kind: 'sim' | 'src' } | null, rate = scanRate) {
    setBusy(true); setError(null)
    try {
      setResult(await runFit(f, { analysis, cpUnit, scanRate: rate, fitDcp }))
      setBanner(note)
    } catch (e) {
      setResult(null)
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally { setBusy(false) }
  }

  async function onDemo(kind: DemoKind = analysis) {
    try {
      const d = await loadDemo(kind)
      setFile(d.file)
      if (d.scanRate) setScanRate(d.scanRate)
      await fit(d.file, d.synthetic
        ? { text: 'Simulated demo data – not a measurement.', kind: 'sim' }
        : { text: d.source ?? 'Published data', kind: 'src' }, d.scanRate ?? scanRate)
    } catch (e) { setError(e instanceof Error ? e.message : 'Unknown error') }
  }

  function changeAnalysis(a: Analysis) {
    setAnalysis(a); setFile(null); setResult(null); setError(null)
  }

  return (
    <main className="app">
      <h1>ThermoFit</h1>
      <p className="sub">Protein thermal-stability curve fitting (DSC) with parameter uncertainties.</p>

      <section className="card">
        <div className="row">
          <label>Analysis
            <select value={analysis} onChange={(e) => changeAnalysis(e.target.value as Analysis)}>
              {(Object.keys(LABELS) as Analysis[]).map((k) => <option key={k} value={k}>{LABELS[k].title}</option>)}
            </select>
          </label>
          <label>Cp unit
            <select value={cpUnit} onChange={(e) => setCpUnit(e.target.value as 'kcal' | 'cal')}>
              <option value="kcal">kcal/mol/K</option><option value="cal">cal/mol/K</option>
            </select>
          </label>
          {analysis === 'dsc_irreversible' && (
            <label>Scan rate (K/min)
              <input type="number" min={0.01} step={0.1} value={scanRate}
                onChange={(e) => setScanRate(Number(e.target.value))} />
            </label>
          )}
          {analysis === 'dsc_two_state' && (
            <label className="check"><input type="checkbox" checked={fitDcp} onChange={(e) => setFitDcp(e.target.checked)} />
              fit ΔCp
            </label>
          )}
        </div>
        <p style={{ color: 'var(--muted)', fontSize: '.88rem' }}>{meta.hint}</p>
        <div className="row">
          <label className="filebtn" style={{ cursor: 'pointer' }}>
            {file ? file.name : 'Choose CSV file…'}
            <input type="file" accept=".csv,.txt,text/csv" hidden aria-label="CSV file"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </label>
          <button className="primary" disabled={!file || busy} onClick={() => file && fit(file, file.name.endsWith('_SIMULATED.csv') ? { text: 'Simulated demo data – not a measurement.', kind: 'sim' } : null)}>
            {busy ? 'Fitting…' : 'Fit'}
          </button>
          <button disabled={busy} onClick={() => onDemo()}>Load simulated demo</button>
          {analysis === 'dsc_irreversible' && (<>
            <button disabled={busy} onClick={() => onDemo('thesis_fe_0p5')}>Thesis curve: Fe-AK 0.5 K/min</button>
            <button disabled={busy} onClick={() => onDemo('thesis_fe_1p0')}>Thesis curve: Fe-AK 1 K/min</button>
            <button disabled={busy} onClick={() => onDemo('thesis_fe_1p46')}>Thesis curve: Fe-AK 1.46 K/min</button>
          </>)}
          {analysis === 'dsc_two_state' && (<>
            <button disabled={busy} onClick={() => onDemo('thesis_zn')}>Load thesis curve: Zn-AK</button>
            <button disabled={busy} onClick={() => onDemo('thesis_co')}>Load thesis curve: Co-AK</button>
          </>)}
        </div>
      </section>

      {error && <div className="err" role="alert">{error}</div>}

      {result && (
        <section className="card" aria-live="polite">
          {banner && <div className="warn" style={{ marginBottom: 12 }} data-testid="banner">{banner.text}</div>}
          <FitChart result={result} xLabel={meta.x} yLabel={meta.y} />
          {(() => {
            const shown = result.params.map(displayParam)
            const summary = plainSummary(result, shown)
            const main = shown.filter((q) => !describeParam(q.name).advanced)
            const advanced = shown.filter((q) => describeParam(q.name).advanced)
            const rows = (list: typeof shown) => list.map(paramRow).map((r) => {
              const info = describeParam(r.name)
              return (
                <tr key={r.name}>
                  <td>
                    <div>{info.label}</div>
                    {info.meaning && <div className="meaning">{info.meaning}</div>}
                  </td>
                  <td className="num">{r.value}</td><td className="num">{r.stderr}</td>
                  <td className="num">{r.ci}</td><td>{r.unit}</td>
                </tr>
              )
            })
            const head = (
              <thead><tr><th>Result</th><th>Value</th><th>Uncertainty (±)</th><th>Likely range (95 %)</th><th>Unit</th></tr></thead>
            )
            return (
              <>
                <h3 style={{ margin: '16px 0 4px', fontSize: '1rem' }}>Result</h3>
                {summary && <p className="plain" data-testid="summary">{summary}</p>}
                <table>{head}<tbody>{rows(main)}</tbody></table>
                <div className="stats">
                  <span>Match with the data: R² = {fmt(result.r2, 5)} (1 would be perfect)</span>
                  <span>Typical deviation: {fmt(result.rmse)}</span>
                  <span>Data points: {result.n_points}</span>
                </div>
                {advanced.length > 0 && (
                  <details className="advanced">
                    <summary>Fit details (instrument baseline)</summary>
                    <table>{head}<tbody>{rows(advanced)}</tbody></table>
                  </details>
                )}
              </>
            )
          })()}
        </section>
      )}
    </main>
  )
}
