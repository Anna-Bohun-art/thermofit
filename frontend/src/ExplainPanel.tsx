import { useState } from 'react'
import { explainFit, type Explanation, type FitResult } from './api'

const EXAMPLES = [
  'Was bedeutet Tm in meinem Fit?',
  'Wie verlässlich ist dieser Fit?',
  'Warum ist der Fit hier ein irreversibles bzw. reversibles Modell?',
]

export function ExplainPanel({ result }: { result: FitResult }) {
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [answer, setAnswer] = useState<Explanation | null>(null)

  async function ask(q: string) {
    if (q.trim().length < 3) return
    setQuestion(q); setBusy(true); setError(null)
    try {
      setAnswer(await explainFit(result, q.trim()))
    } catch (e) {
      setAnswer(null)
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally { setBusy(false) }
  }

  return (
    <section className="card" aria-label="Fit erklären">
      <h3 style={{ margin: '0 0 8px', fontSize: '1rem' }}>Fit erklären</h3>
      <div className="row">
        {EXAMPLES.map((q) => <button key={q} disabled={busy} onClick={() => ask(q)}>{q}</button>)}
      </div>
      <form className="row" onSubmit={(e) => { e.preventDefault(); ask(question) }}>
        <input type="text" value={question} maxLength={300} placeholder="Eigene Frage …"
          aria-label="Frage zum Fit" onChange={(e) => setQuestion(e.target.value)} style={{ flex: 1 }} />
        <button className="primary" disabled={busy || question.trim().length < 3}>{busy ? 'Denke nach …' : 'Fragen'}</button>
      </form>
      {busy && <p style={{ color: 'var(--muted)', fontSize: '.88rem' }}>Falls das Backend schlief, dauert die erste Antwort bis zu einer Minute („Backend wacht auf …“).</p>}
      {error && <div className="err" role="alert">{error}</div>}
      {answer && (
        <div aria-live="polite">
          <p className="plain" data-testid="answer">{answer.answer}</p>
          {answer.sources.map((s) => (
            <details key={s.id} className="advanced">
              <summary>Quelle: {s.heading} <code>{s.id}</code></summary>
              <p>{s.text}</p>
            </details>
          ))}
        </div>
      )}
    </section>
  )
}
