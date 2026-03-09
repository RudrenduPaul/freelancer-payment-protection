'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'

type AccentColor = 'brand' | 'danger' | 'warning' | 'success'

interface MetricCardProps {
  title: string
  value: string
  change?: number
  positiveDirection?: 'up' | 'down'
  trend?: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
  delay?: number
  accentColor?: AccentColor
  urgent?: boolean
}

const ACCENT_TOP: Record<AccentColor, string> = {
  brand: 'border-t-brand-500',
  danger: 'border-t-red-500',
  warning: 'border-t-amber-500',
  success: 'border-t-emerald-500',
}

const ACCENT_ICON_BG: Record<AccentColor, string> = {
  brand: 'bg-brand-50 text-brand-600',
  danger: 'bg-red-50 text-red-600',
  warning: 'bg-amber-50 text-amber-600',
  success: 'bg-emerald-50 text-emerald-600',
}

export function MetricCard({
  title,
  value,
  change,
  positiveDirection = 'up',
  trend = 'neutral',
  icon,
  delay = 0,
  accentColor = 'brand',
  urgent = false,
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
      whileHover={{ y: -2, transition: { duration: 0.15 } }}
      className={cn(
        'rounded-xl border bg-white p-5 border-t-4 transition-shadow',
        ACCENT_TOP[accentColor],
        urgent
          ? 'shadow-red-100 shadow-[0_0_0_1px_rgba(239,68,68,0.15),0_4px_16px_rgba(239,68,68,0.08)]'
          : 'shadow-sm hover:shadow-md',
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <div
          className={cn(
            'flex h-9 w-9 items-center justify-center rounded-lg flex-shrink-0',
            ACCENT_ICON_BG[accentColor],
          )}
        >
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

      {urgent && (
        <div className="mt-3 flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs font-medium text-red-600">Needs attention</span>
        </div>
      )}
    </motion.div>
  )
}
