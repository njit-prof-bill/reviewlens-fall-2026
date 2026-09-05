/**
 * Client-side mirror of the backend's source rules. The server remains
 * authoritative; this exists only to give immediate feedback.
 */

const GOOGLE_HOST = /^(www\.|maps\.)?google(\.[a-z]{2,3}){1,2}$/
const GOOGLE_SHORT_HOSTS = ['maps.app.goo.gl', 'goo.gl', 'g.co']
const PLACE_SEGMENT = /\/place\/([^/@]+)/

export function validateSourceUrl(raw: string): string | null {
  const candidate = raw.trim()
  if (!candidate) return 'Paste a Google Maps link to get started.'

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

  if (!GOOGLE_HOST.test(host)) {
    return 'ReviewLens currently supports Google Maps links only.'
  }

  if (!parsed.pathname.startsWith('/maps')) {
    return 'That Google link is not a Google Maps place. Open the business on Google Maps and copy the link.'
  }

  return null
}

/** Working name derived from the place slug, which the user can rename later. */
export function deriveWorkingName(raw: string): string {
  try {
    const match = PLACE_SEGMENT.exec(new URL(raw.trim()).pathname)
    if (match) {
      const slug = decodeURIComponent(match[1]).replace(/\+/g, ' ').trim()
      if (slug) return slug.slice(0, 200)
    }
  } catch {
    // Fall through to the placeholder name.
  }
  return 'Untitled Analysis'
}
