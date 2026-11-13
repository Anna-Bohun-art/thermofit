import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'

// Nach jedem Test die gerenderte Komponente wieder entfernen
afterEach(() => cleanup())

// jsdom kennt ResizeObserver nicht, Recharts' ResponsiveContainer braucht ihn
globalThis.ResizeObserver ??= class {
  observe() {}
  unobserve() {}
  disconnect() {}
}