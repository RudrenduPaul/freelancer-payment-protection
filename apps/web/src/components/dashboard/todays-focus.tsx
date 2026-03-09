'use client'

import { motion } from 'framer-motion'
import { AlertTriangle, Zap, ArrowRight } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface FocusItem {
  id: string
  label: string
  title: string
  detail: string
  urgency: 'critical' | 'high' | 'medium'
  cta: string
  href: string
}

const MOCK_FOCUS: FocusItem[] = [
  {
    id: '1',
    label: '47 days overdue',
    title: 'Acme Corp — $12,500',
    detail: 'Final Warning stage. Last contact: 8 days ago.',
    urgency: 'critical',
    cta: 'Send Legal Demand',
    href: '/escalations',
  },
  {
    id: '2',
    label: 'Next escalation ready',
    title: 'Global Retail — $8,750',
    detail: 'Firm Notice window opens today. Strike while it's hot.',
    urgency: 'high',
    cta: 'Draft Email',
    href: '/escalations',
  },
  {
    id: '3',
    label: 'New critical risk',
    title: 'TechVentures Inc — Risk 82',
    detail: 'Risk score jumped from 48 → 82. Consider 50% upfront on next project.',
    urgency: 'medium',
    cta: 'View Profile',
    href: '/clients',
  },
]

const URGENCY_STYLES: Record<FocusItem['urgency'], { border: string; bg: string; label: string; dot: string }> = {
  critical: {
    border: 'border-red-200',
    bg: 'bg-red-50/60',
    label: 'text-red-700 bg-red-100',
    dot: 'bg-red-500',
  },
  high: {
    border: 'border-amber-200',
    bg: 'bg-amber-50/60',
    label: 'text-amber-700 bg-amber-100',
    dot: 'bg-amber-500',
  },
  medium: {
    border: 'border-brand-200',
    bg: 'bg-brand-50/40',
    label: 'text-brand-700 bg-brand-100',
    dot: 'bg-brand-500',
  },
}

export function TodaysFocus() {
  const router = useRouter()

  return (
    <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
      <div className="flex items-center gap-2 px-5 py-4 border-b border-slate-100">
        <Zap className="h-4 w-4 text-amber-500" />
        <h3 className="text-sm font-semibold text-slate-900">Today's Focus</h3>
        <span className="ml-2 inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700">
          <AlertTriangle className="h-2.5 w-2.5" />
          3 actions needed
        </span>
      </div>

      <div className="divide-y divide-slate-100">
        {MOCK_FOCUS.map((item, i) => {
          const styles = URGENCY_STYLES[item.urgency]
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25, delay: i * 0.07, ease: 'easeOut' }}
              className={`flex items-start gap-4 px-5 py-4 ${styles.bg} border-l-4 ${styles.border}`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold ${styles.label}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${styles.dot}`} />
                    {item.label}
                  </span>
                </div>
                <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{item.detail}</p>
              </div>

              <button
                onClick={() => router.push(item.href)}
                className="flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50 hover:border-slate-300 transition-all flex-shrink-0 mt-0.5"
              >
                {item.cta}
                <ArrowRight className="h-3 w-3" />
              </button>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
