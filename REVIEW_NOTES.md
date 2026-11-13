# Review notes (Claude, 13.11.2026) – hints only, no code changed

Based on the local copy (commit 53a5d74). Decide yourself whether to commit this file, add it to `.gitignore`, or keep it only locally.

## What is already good
- Backend and frontend tested, E2E in Playwright (5 tests, including a bad upload that shows a readable error), CI runs backend tests, `tsc -b`, Vitest, build and Playwright, Docker and Vercel/Render deployment, honest data note in the README.
- Errors are shown with `role="alert"`, results with `aria-live="polite"`, and the file input has an `aria-label`. This is better than I first thought (I only counted `aria-` strings from a quick search).

## Gaps, in the order I would do them
1. **No `test` script in `frontend/package.json`.** Scripts are `dev`, `build`, `lint`, `preview`. CI calls `npx vitest run` directly. Add `test` (Vitest) and `test:e2e` (Playwright) so that anyone can run `npm test`, and so the README commands match.
2. **Component tests are missing.** Unit tests cover only `format.ts` and `glossary.ts`. `@testing-library/react` and a DOM environment (jsdom or happy-dom) are not installed. First test: `FitChart` renders without data and with data. Second: `App` shows the error `div` when the API call fails (mock `fetch` or `api.ts`).
3. **TypeScript strictness.** `tsconfig.app.json` has no `"strict": true`. Newer TypeScript versions may turn it on by default; I could not check this because `node_modules` is from Windows. Run `npx tsc -p tsconfig.app.json --showConfig` and look for `strict`. Either way, setting it explicitly makes the intention visible to a reader. Then run `npx tsc -b` and fix what appears.
4. **`catch (e)` blocks in `App.tsx` (lines ~38 and ~52)** repeat `e instanceof Error ? e.message : 'Unknown error'`. One small helper would remove the duplication.
5. **Loading state:** look at what the user sees while the backend (Render free tier) wakes up. A cold start can take a while; a visible message avoids "is it broken?".
6. **README:** add a short "Limits" section (not for clinical use, demo data digitized from a figure, no validation of the fitting for GxP use).
