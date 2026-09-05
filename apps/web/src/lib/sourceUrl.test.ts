import { describe, expect, it } from 'vitest'

import { deriveWorkingName, validateSourceUrl } from '@/lib/sourceUrl'

const PLACE_URL =
  'https://www.google.com/maps/place/Blue+Bottle+Coffee/@37.7823,-122.4074,17z'

describe('validateSourceUrl', () => {
  it('accepts a Google Maps place link', () => {
    expect(validateSourceUrl(PLACE_URL)).toBeNull()
  })

  it('accepts a Google Maps short link', () => {
    expect(validateSourceUrl('https://maps.app.goo.gl/AbCdEfGh')).toBeNull()
  })

  it.each(['', '   ', 'not a url', 'ftp://google.com/maps/place/Cafe'])(
    'rejects malformed input: %s',
    (candidate) => {
      expect(validateSourceUrl(candidate)).not.toBeNull()
    },
  )

  it('rejects a review site other than the supported platform', () => {
    expect(validateSourceUrl('https://www.yelp.com/biz/blue-bottle')).toMatch(
      /Google Maps links only/,
    )
  })

  it('rejects a Google link that is not a Maps place', () => {
    expect(validateSourceUrl('https://www.google.com/search?q=coffee')).toMatch(
      /not a Google Maps place/,
    )
  })
})

describe('deriveWorkingName', () => {
  it('derives a readable name from the place slug', () => {
    expect(deriveWorkingName(PLACE_URL)).toBe('Blue Bottle Coffee')
  })

  it('falls back to a placeholder when no slug is present', () => {
    expect(deriveWorkingName('https://maps.app.goo.gl/AbCdEfGh')).toBe('Untitled Analysis')
  })
})
