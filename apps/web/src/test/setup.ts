import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// Tests never talk to Clerk; the token getter is all the app needs from it.
vi.mock('@clerk/clerk-react', () => ({
  useAuth: () => ({
    isLoaded: true,
    isSignedIn: true,
    getToken: async () => 'test-token',
  }),
  useUser: () => ({ user: { fullName: 'Test User' } }),
  useClerk: () => ({ signOut: vi.fn() }),
  SignedIn: ({ children }: { children: React.ReactNode }) => children,
  SignedOut: () => null,
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

// jsdom does not implement these, and Radix primitives rely on them.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }),
})

window.HTMLElement.prototype.scrollIntoView = vi.fn()
window.HTMLElement.prototype.hasPointerCapture = vi.fn()
window.HTMLElement.prototype.releasePointerCapture = vi.fn()

// Radix positioning depends on ResizeObserver, which jsdom does not provide.
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// Without IntersectionObserver, floating-ui falls back to an animation-frame
// loop that never settles and leaves tests hanging.
global.IntersectionObserver = class {
  readonly root = null
  readonly rootMargin = ''
  readonly thresholds: readonly number[] = []
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords(): IntersectionObserverEntry[] {
    return []
  }
} as unknown as typeof IntersectionObserver

// jsdom has no PointerEvent, and Radix menus open on pointerdown.
class PointerEventPolyfill extends MouseEvent {
  readonly pointerId: number
  readonly pointerType: string
  readonly isPrimary: boolean

  constructor(type: string, params: PointerEventInit = {}) {
    super(type, params)
    this.pointerId = params.pointerId ?? 1
    this.pointerType = params.pointerType ?? 'mouse'
    this.isPrimary = params.isPrimary ?? true
  }
}

if (!('PointerEvent' in window)) {
  const polyfill = PointerEventPolyfill as unknown as typeof PointerEvent
  ;(globalThis as { PointerEvent: typeof PointerEvent }).PointerEvent = polyfill
}
