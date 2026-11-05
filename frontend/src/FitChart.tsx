import { CartesianGrid, ComposedChart, Line, ResponsiveContainer, Scatter, Tooltip, XAxis, YAxis } from 'recharts'
import type { FitResult } from './api'
import { fmt } from './format'

type Props = { result: FitResult; xLabel: string; yLabel: string }

export function FitChart({ result, xLabel, yLabel }: Props) {
  const points = result.x.map((x, i) => ({ x, y: result.y[i] }))
  const fit = result.x_fit.map((x, i) => ({ x, y: result.y_fit[i] }))
  const resid = result.x.map((x, i) => ({ x, r: result.residuals[i] }))
  const tick = (v: number) => fmt(v, 3)
  return (
    <div>
      <div role="img" aria-label="Data points and fitted curve" style={{ height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart margin={{ top: 8, right: 16, bottom: 24, left: 8 }}>
            <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
            <XAxis type="number" dataKey="x" domain={['dataMin', 'dataMax']} tickFormatter={tick}
              label={{ value: xLabel, position: 'insideBottom', offset: -12, fill: 'var(--muted)' }} stroke="var(--muted)" />
            <YAxis type="number" dataKey="y" domain={['auto', 'auto']} tickFormatter={tick} width={64}
              label={{ value: yLabel, angle: -90, position: 'insideLeft', fill: 'var(--muted)' }} stroke="var(--muted)" />
            <Tooltip formatter={(v) => fmt(Number(v))} labelFormatter={(v) => `${xLabel}: ${fmt(Number(v))}`} />
            <Scatter data={points} dataKey="y" fill="var(--data)" fillOpacity={0.55} isAnimationActive={false} />
            <Line data={fit} dataKey="y" stroke="var(--fit)" strokeWidth={2.5} dot={false} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="legend">
        <span><span className="dot" style={{ background: 'var(--data)' }} />data</span>
        <span><span className="dot" style={{ background: 'var(--fit)' }} />fit</span>
      </div>
      <h3 style={{ margin: '16px 0 4px', fontSize: '1rem' }}>Residuals</h3>
      <div role="img" aria-label="Residuals" style={{ height: 140 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={resid} margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
            <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
            <XAxis type="number" dataKey="x" domain={['dataMin', 'dataMax']} tickFormatter={tick} stroke="var(--muted)" />
            <YAxis type="number" dataKey="r" tickFormatter={tick} width={64} stroke="var(--muted)" />
            <Scatter dataKey="r" fill="var(--accent)" fillOpacity={0.6} isAnimationActive={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
