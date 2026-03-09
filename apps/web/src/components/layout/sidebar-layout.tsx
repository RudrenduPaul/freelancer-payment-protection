'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Users,
  FileText,
  AlertTriangle,
  Scale,
  UserCircle2,
  ShieldAlert,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Clients', href: '/clients', icon: Users },
  { label: 'Invoices', href: '/invoices', icon: FileText },
  { label: 'Escalations', href: '/escalations', icon: AlertTriangle },
  { label: 'Legal Docs', href: '/legal', icon: Scale },
]

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/clients': 'Clients',
  '/invoices': 'Invoices',
  '/escalations': 'Escalations',
  '/legal': 'Legal Docs',
}

function getPageTitle(pathname: string): string {
  // Exact match first
  if (PAGE_TITLES[pathname]) return PAGE_TITLES[pathname]
  // Prefix match for nested routes
  const segment = '/' + pathname.split('/')[1]
  return PAGE_TITLES[segment] ?? 'Bad Cop CRM'
}

export function SidebarLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Sidebar */}
      <aside className="flex w-60 flex-shrink-0 flex-col border-r border-slate-200 bg-white">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2.5 border-b border-slate-200 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white shadow-sm">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-bold text-slate-900">Bad Cop</span>
            <span className="text-[10px] font-medium uppercase tracking-widest text-brand-500">
              Payment CRM
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-0.5">
            {NAV_ITEMS.map((item) => {
              const isActive =
                pathname === item.href ||
                (item.href !== '/dashboard' && pathname.startsWith(item.href))

              return (
                <li key={item.href}>
                  <motion.div whileHover={{ x: 2 }} transition={{ duration: 0.15 }}>
                    <Link
                      href={item.href}
                      className={cn(
                        'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-brand-50 text-brand-700'
                          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                      )}
                    >
                      <item.icon
                        className={cn(
                          'h-4 w-4 flex-shrink-0',
                          isActive ? 'text-brand-600' : 'text-slate-400',
                        )}
                      />
                      {item.label}
                      {isActive && (
                        <motion.div
                          layoutId="nav-indicator"
                          className="ml-auto h-1.5 w-1.5 rounded-full bg-brand-500"
                          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        />
                      )}
                    </Link>
                  </motion.div>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* User avatar placeholder */}
        <div className="border-t border-slate-200 px-3 py-4">
          <div className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer">
            <UserCircle2 className="h-6 w-6 text-slate-400 flex-shrink-0" />
            <div className="flex flex-col min-w-0">
              <span className="font-medium text-slate-700 truncate text-xs">
                Freelancer
              </span>
              <span className="text-[10px] text-slate-400 truncate">
                your@email.com
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top header */}
        <header className="flex h-16 flex-shrink-0 items-center border-b border-slate-200 bg-white px-6">
          <h1 className="text-lg font-semibold text-slate-900">
            {getPageTitle(pathname)}
          </h1>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
