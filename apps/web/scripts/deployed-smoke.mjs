import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'
import { chromium } from 'playwright'

const frontendUrl = required('FRONTEND_URL').replace(/\/$/, '')
const smokeEmail = required('SMOKE_TEST_EMAIL')
const smokePassword = required('SMOKE_TEST_PASSWORD')
const isolationEmail = required('SMOKE_ISOLATION_EMAIL')
const isolationPassword = required('SMOKE_ISOLATION_PASSWORD')
const apiUrl = `${frontendUrl}/api/v1`
const fixturePath = resolve(import.meta.dirname, '../../api/tests/fixtures/reviews_valid.csv')
const targetName = `ReviewLens smoke ${Date.now()}`
const targetUrl =
  'https://www.google.com/maps/place/Blue+Bottle+Coffee/@37.7823,-122.4074,17z'

function required(name) {
  const value = process.env[name]
  if (!value) throw new Error(`Missing required environment variable: ${name}`)
  return value
}

async function request(path, options = {}) {
  const response = await fetch(`${apiUrl}${path}`, options)
  const text = await response.text()
  let body
  try {
    body = text ? JSON.parse(text) : undefined
  } catch {
    body = text
  }
  return { response, body }
}

async function expectStatus(path, expected, options) {
  const { response, body } = await request(path, options)
  if (response.status !== expected) {
    throw new Error(`${path} returned ${response.status}, expected ${expected}: ${JSON.stringify(body)}`)
  }
  return body
}

async function getToken(email, password) {
  const browser = await chromium.launch({ headless: true })
  try {
    const page = await browser.newPage()
    await page.goto(`${frontendUrl}/sign-in`, { waitUntil: 'networkidle' })
    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password').fill(password)
    await page.getByRole('button', { name: 'Sign in', exact: true }).click()
    await page.waitForURL((url) => url.pathname === '/', { timeout: 30_000 })
    return await page.waitForFunction(
      async () => window.Clerk?.session?.getToken(),
      undefined,
      { timeout: 30_000 },
    ).then((value) => value.jsonValue())
  } finally {
    await browser.close()
  }
}

async function waitForRun(token, runId) {
  const headers = { Authorization: `Bearer ${token}` }
  for (let attempt = 0; attempt < 30; attempt += 1) {
    const run = await expectStatus(`/ingestion-runs/${runId}`, 200, { headers })
    if (['succeeded', 'partial', 'failed'].includes(run.status)) return run
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 1_000))
  }
  throw new Error(`Timed out waiting for ingestion run ${runId}`)
}

async function main() {
  await expectStatus('/health', 200)
  await expectStatus('/ready', 200)
  await expectStatus('/analysis-targets', 401)

  const token = await getToken(smokeEmail, smokePassword)
  if (typeof token !== 'string' || !token) throw new Error('Clerk did not return a session token')
  const headers = { Authorization: `Bearer ${token}` }
  await expectStatus('/me', 200, { headers })

  let targetId
  try {
    const target = await expectStatus('/analysis-targets', 201, {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: targetName, source_url: targetUrl }),
    })
    targetId = target.id

    const isolationToken = await getToken(isolationEmail, isolationPassword)
    await expectStatus(`/analysis-targets/${targetId}`, 404, {
      headers: { Authorization: `Bearer ${isolationToken}` },
    })

    const form = new FormData()
    form.set('file', new Blob([await readFile(fixturePath)]), 'reviews_valid.csv')
    const ingestion = await expectStatus(`/analysis-targets/${targetId}/ingestions/imports`, 202, {
      method: 'POST',
      headers,
      body: form,
    })
    const run = await waitForRun(token, ingestion.id)
    if (!['succeeded', 'partial'].includes(run.status) || run.reviews_ingested < 3) {
      throw new Error(`Smoke ingestion did not persist fixture reviews: ${JSON.stringify(run)}`)
    }

    const summary = await expectStatus(`/analysis-targets/${targetId}/summary`, 200, { headers })
    if (summary.reviews_collected < 3 || summary.average_rating === null) {
      throw new Error(`Smoke summary was incomplete: ${JSON.stringify(summary)}`)
    }

    const grounded = await expectStatus(`/analysis-targets/${targetId}/questions`, 201, {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'What positive feedback appears in these reviews?' }),
    })
    if (grounded.result_kind !== 'grounded' || !grounded.answer || grounded.evidence.length === 0) {
      throw new Error(`Grounded Q&A smoke assertion failed: ${JSON.stringify(grounded)}`)
    }

    const scoped = await expectStatus(`/analysis-targets/${targetId}/questions`, 201, {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'What is the weather today?' }),
    })
    if (scoped.result_kind !== 'out_of_scope') {
      throw new Error(`Scope guard smoke assertion failed: ${JSON.stringify(scoped)}`)
    }
  } finally {
    if (targetId) {
      const { response } = await request(`/analysis-targets/${targetId}`, {
        method: 'DELETE',
        headers,
      })
      if (!response.ok && response.status !== 404) {
        throw new Error(`Could not clean up smoke target ${targetId}: ${response.status}`)
      }
    }
  }

  console.log('Deployed smoke tests passed.')
}

await main()