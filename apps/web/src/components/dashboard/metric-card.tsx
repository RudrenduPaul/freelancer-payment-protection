'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: string
  change?: number
  /** true = "up" is a good thing (e.g. recovery rate); false = "up" is bad (e.g. overdue count) */
  positiveDirection?: 'up' | 'down'
  trend?: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
  delay?: number
}

export function MetricCard({
  title,
  value,
  change,
  positiveDirection = 'up',
  trend = 'neutral',
  icon,
  delay = 0,
}: MetricCardProps) {
  const isPositive =
    trend === 'neutral'
      ? null
      : (trend === 'up') === (positiveDirection === 'up')

  const trendColor =
    isPositive === null
      ? 'text-slate-500'
      : isPositive
        ? 'text-emerald-600'
        : 'text-red-600'

  const TrendIcon =
    trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay, ease: 'easeOut' }}
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div className="flex items-start justify-between mb-4">
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 text-brand-600 flex-shrink-0">
          {icon}
        </div>
      </div>

      <div className="flex items-end justify-between gap-2">
        <p className="text-2xl font-bold tracking-tight text-slate-900 tabular-nums">
          {value}
        </p>

        {change !== undefined && trend !== 'neutral' && (
          <div
            className={cn(
              'flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold',
              isPositive
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-red-50 text-red-700',
              trendColor,
            )}
          >
            <TrendIcon className="h-3 w-3" />
            <span>
              {change > 0 ? '+' : ''}
              {change.toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {change !== undefined && (
        <p className="mt-1 text-xs text-slate-400">vs. last month</p>
      )}
    </motion.div>
  )
}
