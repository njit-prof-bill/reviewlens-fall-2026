import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { registerSW } from 'virtual:pwa-register'
import './index.css'
import App from './App.tsx'
import { appDisplayName } from './lib/branding'

const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!clerkPublishableKey) {
  throw new Error(
    'Missing VITE_CLERK_PUBLISHABLE_KEY. Set it in apps/web/.env.local (local) or Cloudflare Pages environment variables (prod).',
  )
}

if (import.meta.env.PROD) {
  registerSW({ immediate: true })
}

document.title = appDisplayName
const mobileTitleMeta = document.querySelector('meta[name="apple-mobile-web-app-title"]')
if (mobileTitleMeta) {
  mobileTitleMeta.setAttribute('content', appDisplayName)
}

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000, refetchOnWindowFocus: false } },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ClerkProvider>
  </StrictMode>,
)
