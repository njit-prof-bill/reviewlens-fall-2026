import { describe, expect, it } from 'vitest'

import {
  deriveWorkingName,
  detectSourcePlatform,
  validateSourceUrl,
} from '@/lib/sourceUrl'

const PLACE_URL =
  'https://www.google.com/maps/place/Blue+Bottle+Coffee/@37.7823,-122.4074,17z'

describe('validateSourceUrl', () => {
  it('accepts a Google Maps place link', () => {
    expect(validateSourceUrl(PLACE_URL)).toBeNull()
  })

  it('accepts a Google Maps short link', () => {
    expect(validateSourceUrl('https://maps.app.goo.gl/AbCdEfGh')).toBeNull()
  })

  it.each([
    'https://www.amazon.com/dp/B012345678',
    'https://amazon.com/Example-Product/dp/B012345678?th=1',
    'https://www.amazon.com/gp/product/B012345678/',
  ])('accepts an Amazon product link: %s', (url) => {
    expect(validateSourceUrl(url)).toBeNull()
  })

  it.each([
    'https://amazon.com/s?k=headphones',
    'https://amazon.co.uk/dp/B012345678',
    'https://amazon.com.evil.example/dp/B012345678',
  ])('rejects unsupported Amazon links: %s', (url) => {
    expect(validateSourceUrl(url)).not.toBeNull()
  })

  it.each(['', '   ', 'not a url', 'ftp://google.com/maps/place/Cafe'])(
    'rejects malformed input: %s',
    (candidate) => {
      expect(validateSourceUrl(candidate)).not.toBeNull()
    },
  )

  it('rejects a review site other than the supported platform', () => {
    expect(validateSourceUrl('https://www.yelp.com/biz/blue-bottle')).toMatch(
      /Google Maps place links and Amazon.com product links/,
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

  it('derives an Amazon working name from its ASIN', () => {
    expect(deriveWorkingName('https://www.amazon.com/Example/dp/B012345678')).toBe(
      'Amazon Product B012345678',
    )
  })
})

describe('detectSourcePlatform', () => {
  it('detects Google Maps and Amazon product URLs', () => {
    expect(detectSourcePlatform(PLACE_URL)).toBe('google_maps')
    expect(detectSourcePlatform('https://www.amazon.com/dp/B012345678')).toBe('amazon')
  })

  it('does not detect invalid URLs', () => {
    expect(detectSourcePlatform('https://amazon.com/s?k=headphones')).toBeNull()
    expect(detectSourcePlatform('https://www.yelp.com/biz/x')).toBeNull()
  })
})
