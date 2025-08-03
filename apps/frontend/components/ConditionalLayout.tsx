"use client"

import { usePathname } from "next/navigation"
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarProvider } from "@/components/ui/sidebar"

interface ConditionalLayoutProps {
  children: React.ReactNode
}

export default function ConditionalLayout({ children }: ConditionalLayoutProps) {
  const pathname = usePathname()
  
  // Don't show sidebar on login page
  const showSidebar = !pathname.startsWith('/login')
  
  if (!showSidebar) {
    return <>{children}</>
  }
  
  return (
    <SidebarProvider>
      <AppSidebar />
      <main className="flex-1 overflow-hidden">
        {children}
      </main>
    </SidebarProvider>
  )
}