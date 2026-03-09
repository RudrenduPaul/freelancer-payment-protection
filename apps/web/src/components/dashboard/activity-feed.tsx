'use client'

import { motion } from 'framer-motion'
import {
  Send,
  DollarSign,
  AlertTriangle,
  FileText,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface ActivityItem {
  id: string
  type: 'escalation_sent' | 'payment_received' | 'risk_elevated' | 'demand_generated' | 'new_client'
  title: string
  description: string
  time: string
  amount?: string
}

const MOCK_ACTIVITY: ActivityItem[] = [
  {
    id: '1',
    type: 'escalation_sent',
    title: 'Final Warning sent',
    description: 'Acme Corp — INV-2024-087',
    time: '2 min ago',
    amount: '$12,500',
  },
  {
    id: '2',
    type: 'payment_received',
    title: 'Payment received',
    description: 'Bright Digital — INV-2024-081',
    time: '1 hr ago',
    amount: '$5,200',
  },
  {
    id: '3',
    type: 'risk_elevated',
    title: 'Risk score elevated',
    description: 'TechVentures Inc → Critical (82)',
    time: '3 hrs ago',
  },
  {
    id: '4',
    type: 'demand_generated',
    title: 'Demand letter generated',
    description: 'Global Retail Co — US-CA jurisdiction',
    time: '5 hrs ago',
    amount: '$8,750',
  },
  {
    id: '5',
    type: 'escalation_sent',
    title: 'Polite Reminder sent',
    description: 'StartupXYZ — INV-2024-092',
    time: 'Yesterday',
    amount: '$3,400',
  },
  {
    id: '6',
    type: 'new_client',
    title: 'New client added',
    description: 'Momentum Studios',
    time: 'Yesterday',
  },
]

const TYPE_CONFIG: Record<
  ActivityItem['type'],
  { icon: React.ComponentType<{ className?: string }>; bg: string; text: string }
> = {
  escalation_sent: {
    icon: Send,
    bg: 'bg-blue-100',
    text: 'text-blue-600',
  },
  payment_received: {
    icon: DollarSign,
    bg: 'bg-emerald-100',
    text: 'text-emerald-600',
  },
  risk_elevated: {
    icon: AlertTriangle,
    bg: 'bg-red-100',
    text: 'text-red-600',
  },
  demand_generated: {
    icon: FileText,
    bg: 'bg-violet-100',
    text: 'text-violet-600',
  },
  new_client: {
    icon: TrendingUp,
    bg: 'bg-slate-100',
    text: 'text-slate-600',
  },
}

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06 } },
}

const itemVariants = {
  hidden: { opacity: 0, x: -8 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.25, ease: 'easeOut' } },
}

export function ActivityFeed() {
  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <div className="flex items-center gap-2 px-5 py-4 border-b border-slate-100">
        <ShieldAlert className="h-4 w-4 text-brand-600" />
        <h3 className="text-sm font-semibold text-slate-900">Bad Cop Activity</h3>
        <span className="ml-auto text-xs text-slate-400">Last 24 hours</span>
      </div>

      <motion.ul
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="divide-y divide-slate-50"
      >
        {MOCK_ACTIVITY.map((item) => {
          const config = TYPE_CONFIG[item.type]
          const Icon = config.icon

          return (
            <motion.li
              key={item.id}
              variants={itemVariants}
              className="flex items-start gap-3 px-5 py-3.5 hover:bg-slate-50/70 transition-colors"
            >
              <div
                className={cn(
                  'flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full mt-0.5',
                  config.bg,
                )}
              >
                <Icon className={cn('h-3.5 w-3.5', config.text)} />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-baseline justify-between gap-2">
                  <p className="text-xs font-semibold text-slate-800 truncate">{item.title}</p>
                  {item.amount && (
                    <span
                      className={cn(
                        'text-xs font-bold tabular-nums flex-shrink-0',
                        item.type === 'payment_received'
                          ? 'text-emerald-600'
                          : 'text-slate-600',
                      )}
                    >
                      {item.type === 'payment_received' ? '+' : ''}{item.amount}
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 truncate">{item.description}</p>
              </div>

              <span className="text-[10px] text-slate-400 flex-shrink-0 mt-0.5">{item.time}</span>
            </motion.li>
          )
        })}
      </motion.ul>

      <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/60">
        <button className="text-xs font-medium text-brand-600 hover:text-brand-700 transition-colors">
          View full history →
        </button>
      </div>
    </div>
  )
}
