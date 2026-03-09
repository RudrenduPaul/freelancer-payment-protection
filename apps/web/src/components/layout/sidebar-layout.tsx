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
  TrendingUp,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  shortcut?: string
  badge?: number
  badgeColor?: string
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, shortcut: '⌘1' },
  { label: 'Clients', href: '/clients', icon: Users, shortcut: '⌘2' },
  { label: 'Invoices', href: '/invoices', icon: FileText, shortcut: '⌘3' },
  {
    label: 'Escalations',
    href: '/escalations',
    icon: AlertTriangle,
    shortcut: '⌘4',
    badge: 3,
    badgeColor: 'bg-red-500',
  },
  { label: 'Legal Docs', href: '/legal', icon: Scale, shortcut: '⌘5' },
]

const PAGE_TITLES: Record<string, { title: string; subtitle?: string }> = {
  '/dashboard': { title: 'Dashboard', subtitle: 'Your collection overview' },
  '/clients': { title: 'Clients', subtitle: 'Risk-sorted client list' },
  '/invoices': { title: 'Invoices', subtitle: 'Track every dollar owed' },
  '/escalations': { title: 'Escalation Pipeline', subtitle: 'Bad Cop is on the case' },
  '/legal': { title: 'Legal Docs', subtitle: 'AI-generated demand letters' },
}

function getPageMeta(pathname: string) {
  if (PAGE_TITLES[pathname]) return PAGE_TITLES[pathname]
  const segment = '/' + pathname.split('/')[1]
  return PAGE_TITLES[segment] ?? { title: 'Bad Cop CRM' }
}

export function SidebarLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { title, subtitle } = getPageMeta(pathname)

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Sidebar */}
      <aside className="flex w-60 flex-shrink-0 flex-col border-r border-slate-200 bg-white">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2.5 border-b border-slate-100 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white shadow-sm">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-bold text-slate-900">Bad Cop</span>
            <span className="text-[10px] font-medium uppercase tracking-widest text-brand-500">
              Payment CRM
            </span>
          </div>
          {/* Live indicator */}
          <div className="ml-auto flex items-center gap-1.5">
            <span className="status-dot-live" />
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
            Navigation
          </p>
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
                        'group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all',
                        isActive
                          ? 'bg-brand-50 text-brand-700'
                          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                      )}
                    >
                      <item.icon
                        className={cn(
                          'h-4 w-4 flex-shrink-0 transition-colors',
                          isActive ? 'text-brand-600' : 'text-slate-400 group-hover:text-slate-600',
                        )}
                      />
                      <span className="flex-1">{item.label}</span>

                      {/* Badge for active count */}
                      {item.badge != null && item.badge > 0 && !isActive && (
                        <span
                          className={cn(
                            'inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px] font-bold text-white',
                            item.badgeColor ?? 'bg-brand-500',
                          )}
                        >
                          {item.badge}
                        </span>
                      )}

                      {/* Active dot */}
                      {isActive && (
                        <motion.div
                          layoutId="nav-indicator"
                          className="ml-auto h-1.5 w-1.5 rounded-full bg-brand-500"
                          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        />
                      )}

                      {/* Keyboard shortcut — show on hover when not active */}
                      {!isActive && item.shortcut && (
                        <span className="hidden group-hover:block text-[10px] text-slate-400 font-mono">
                          {item.shortcut}
                        </span>
                      )}
                    </Link>
                  </motion.div>
                </li>
              )
            })}
          </ul>

          {/* Recovery Stat mini-widget */}
          <div className="mt-6 mx-1 rounded-xl bg-gradient-to-br from-brand-50 to-brand-100/60 border border-brand-200/60 p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-3.5 w-3.5 text-brand-600" />
              <span className="text-xs font-semibold text-brand-700">Recovery Rate</span>
            </div>
            <p className="text-2xl font-bold text-brand-700 tabular-nums">68.4%</p>
            <p className="text-[10px] text-brand-500 mt-0.5">+5.7% vs last month</p>
            <div className="mt-2 h-1.5 w-full rounded-full bg-brand-200/60">
              <div
                className="h-1.5 rounded-full bg-brand-500"
                style={{ width: '68.4%' }}
              />
            </div>
          </div>
        </nav>

        {/* User avatar placeholder */}
        <div className="border-t border-slate-100 px-3 py-4">
          <div className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer">
            <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-brand-600 text-white text-xs font-bold">
              F
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-semibold text-slate-700 truncate text-xs">
                Freelancer
              </span>
              <span className="text-[10px] text-slate-400 truncate">
                Pro Plan · 10 clients
              </span>
            </div>
            <UserCircle2 className="h-4 w-4 text-slate-300 flex-shrink-0 ml-auto" />
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top header */}
        <header className="flex h-16 flex-shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6">
          <div className="flex flex-col">
            <h1 className="text-base font-bold text-slate-900 leading-tight">{title}</h1>
            {subtitle && (
              <p className="text-xs text-slate-500 leading-tight">{subtitle}</p>
            )}
          </div>

          {/* Header right: overdue alert pill */}
          <div className="flex items-center gap-3">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 0.3 }}
              className="hidden sm:flex items-center gap-1.5 rounded-full bg-red-50 border border-red-200 px-3 py-1 text-xs font-semibold text-red-700"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
              7 overdue
            </motion.div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
