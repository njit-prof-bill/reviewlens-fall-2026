/**
 * Client-side mirror of the backend's source rules. The server remains
 * authoritative; this exists only to give immediate feedback.
 */

const GOOGLE_HOST = /^(www\.|maps\.)?google(\.[a-z]{2,3}){1,2}$/
const GOOGLE_SHORT_HOSTS = ['maps.app.goo.gl', 'goo.gl', 'g.co']
const AMAZON_HOSTS = ['amazon.com', 'www.amazon.com']
const AMAZON_ASIN = /\/(?:dp|gp\/product)\/([A-Z0-9]{10})(?:[/?]|$)/i
const AMAZON_SLUG_ASIN = /\/[^/]+\/dp\/([A-Z0-9]{10})(?:[/?]|$)/i
const PLACE_SEGMENT = /\/place\/([^/@]+)/

export type SourcePlatform = 'google_maps' | 'amazon'

export function detectSourcePlatform(raw: string): SourcePlatform | null {
  if (validateSourceUrl(raw)) return null
  const parsed = new URL(raw.trim())
  const host = parsed.hostname.toLowerCase()
  if (AMAZON_HOSTS.includes(host)) return 'amazon'
  return 'google_maps'
}

export function validateSourceUrl(raw: string): string | null {
  const candidate = raw.trim()
  if (!candidate) return 'Paste a Google Maps place or Amazon.com product link to get started.'

  let parsed: URL
  try {
    parsed = new URL(candidate)
  } catch {
    return 'That does not look like a valid web address.'
  }

  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    return 'The review source must be a http:// or https:// web address.'
  }

  const host = parsed.hostname.toLowerCase()
  if (GOOGLE_SHORT_HOSTS.includes(host)) return null

  if (AMAZON_HOSTS.includes(host)) {
    if (!(AMAZON_ASIN.test(parsed.pathname) || AMAZON_SLUG_ASIN.test(parsed.pathname))) {
      return 'Paste an Amazon.com product link that contains a product ASIN.'
    }
    return null
  }

  if (!GOOGLE_HOST.test(host)) {
    return 'ReviewLens supports Google Maps place links and Amazon.com product links.'
  }

  if (!parsed.pathname.startsWith('/maps')) {
    return 'That Google link is not a Google Maps place. Open the business on Google Maps and copy the link.'
  }

  return null
}

/** Working name derived from the place slug or product ASIN. */
export function deriveWorkingName(raw: string): string {
  try {
    const parsed = new URL(raw.trim())
    if (AMAZON_HOSTS.includes(parsed.hostname.toLowerCase())) {
      const match = AMAZON_ASIN.exec(parsed.pathname) ?? AMAZON_SLUG_ASIN.exec(parsed.pathname)
      if (match) return `Amazon Product ${match[1].toUpperCase()}`
    }
    const match = PLACE_SEGMENT.exec(parsed.pathname)
    if (match) {
      const slug = decodeURIComponent(match[1]).replace(/\+/g, ' ').trim()
      if (slug) return slug.slice(0, 200)
    }
  } catch {
    // Fall through to the placeholder name.
  }
  return 'Untitled Analysis'
}
