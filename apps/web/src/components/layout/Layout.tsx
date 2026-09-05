import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import { useTheme } from '@/lib/theme'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { AnalysisSidebar } from './AnalysisSidebar'
import { Header } from './Header'

export interface LayoutProps {
  children?: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // Initialize theme infrastructure based on system preference
  useTheme()

  const toggleSidebar = () => {
    setIsSidebarOpen((current) => !current)
  }

  const closeSidebar = () => {
    setIsSidebarOpen(false)
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background text-foreground">
      {/* Fixed-height top header */}
      <Header isSidebarOpen={isSidebarOpen} onMenuToggle={toggleSidebar} />

      {/* Body row: sidebar + main fills remaining height */}
      <div className="flex flex-1 overflow-hidden">
        {isSidebarOpen ? (
          <button
            type="button"
            aria-label="Close navigation menu"
            className="fixed inset-0 top-14 z-20 bg-foreground/10 md:hidden"
            onClick={closeSidebar}
          />
        ) : null}

        {/* Left sidebar */}
        <AnalysisSidebar isOpen={isSidebarOpen} onNavigate={closeSidebar} />

        {/* Main content panel */}
        <main className="flex-1 overflow-y-auto bg-muted/20">
          <ErrorBoundary>{children || <Outlet />}</ErrorBoundary>
        </main>
      </div>
    </div>
  )
}
