'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  DollarSign,
  Users,
  AlertCircle,
  TrendingUp,
  Clock,
  Siren,
} from 'lucide-react'
import { MetricCard } from '@/components/dashboard/metric-card'
import { RiskDistributionChart } from '@/components/dashboard/risk-distribution-chart'
import { ActivityFeed } from '@/components/dashboard/activity-feed'
import { TodaysFocus } from '@/components/dashboard/todays-focus'
import { SkeletonMetric } from '@/components/shared/loading-skeleton'
import { analyticsApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import type { DashboardOverview } from '@/lib/types'

const SEED_OVERVIEW: DashboardOverview = {
  totalOutstanding: 47250,
  totalClients: 24,
  overdueInvoices: 7,
  escalationsActive: 3,
  recoveryRateThisMonth: 68.4,
  averageDaysToPayment: 34,
  clientsByRiskLevel: { low: 12, medium: 7, high: 3, critical: 2 },
}

function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export default function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analyticsApi
      .getOverview()
      .then(setOverview)
      .catch(() => setOverview(SEED_OVERVIEW))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-20 w-full rounded-2xl bg-slate-100 animate-pulse" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonMetric key={i} />
          ))}
        </div>
      </div>
    )
  }

  const data = overview ?? SEED_OVERVIEW

  return (
    <div className="space-y-6">
      {/* Welcome banner */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-brand-600 via-brand-700 to-violet-700 px-7 py-6 text-white shadow-lg"
      >
        {/* Background decoration */}
        <div className="absolute right-0 top-0 h-full w-64 opacity-10">
          <div className="absolute right-8 top-4 h-32 w-32 rounded-full bg-white blur-2xl" />
          <div className="absolute right-16 bottom-2 h-20 w-20 rounded-full bg-white blur-xl" />
        </div>

        <div className="relative flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-brand-200">{getGreeting()}</p>
            <h2 className="mt-0.5 text-xl font-bold leading-tight">
              {data.overdueInvoices > 0
                ? `${data.overdueInvoices} invoices need your attention today.`
                : "You're all caught up. Nice work."}
            </h2>
            <p className="mt-1.5 text-sm text-brand-200 max-w-md">
              {data.overdueInvoices > 0
                ? `Bad Cop has ${data.escalationsActive} active escalations running. ${formatCurrency(data.totalOutstanding)} outstanding across ${data.totalClients} clients.`
                : "No overdue invoices right now. Bad Cop is standing by."}
            </p>
          </div>

          <div className="flex-shrink-0 hidden sm:flex flex-col items-end gap-1">
            <span className="text-3xl font-extrabold tabular-nums">
              {formatCurrency(data.totalOutstanding)}
            </span>
            <span className="text-xs text-brand-200 font-medium">total outstanding</span>
          </div>
        </div>

        {/* Progress bar: recovery rate */}
        <div className="relative mt-5">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-medium text-brand-200">Recovery rate this month</span>
            <span className="text-xs font-bold text-white">{data.recoveryRateThisMonth.toFixed(1)}%</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-white/20">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${data.recoveryRateThisMonth}%` }}
              transition={{ duration: 1.2, delay: 0.4, ease: 'easeOut' }}
              className="h-1.5 rounded-full bg-emerald-400"
            />
          </div>
        </div>
      </motion.div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MetricCard
          title="Total Outstanding"
          value={formatCurrency(data.totalOutstanding)}
          trend="up"
          positiveDirection="down"
          change={12.3}
          icon={<DollarSign className="h-4 w-4" />}
          accentColor="danger"
          delay={0}
        />
        <MetricCard
          title="Active Clients"
          value={String(data.totalClients)}
          trend="up"
          positiveDirection="up"
          change={4.2}
          icon={<Users className="h-4 w-4" />}
          accentColor="brand"
          delay={0.05}
        />
        <MetricCard
          title="Overdue Invoices"
          value={String(data.overdueInvoices)}
          trend="down"
          positiveDirection="down"
          change={-1}
          icon={<AlertCircle className="h-4 w-4" />}
          accentColor="danger"
          delay={0.1}
          urgent={data.overdueInvoices > 5}
        />
        <MetricCard
          title="Active Escalations"
          value={String(data.escalationsActive)}
          trend="neutral"
          icon={<Siren className="h-4 w-4" />}
          accentColor="warning"
          delay={0.15}
        />
        <MetricCard
          title="Recovery Rate (MTD)"
          value={`${data.recoveryRateThisMonth.toFixed(1)}%`}
          trend="up"
          positiveDirection="up"
          change={5.7}
          icon={<TrendingUp className="h-4 w-4" />}
          accentColor="success"
          delay={0.2}
        />
        <MetricCard
          title="Avg. Days to Payment"
          value={`${data.averageDaysToPayment}d`}
          trend="down"
          positiveDirection="down"
          change={-3.1}
          icon={<Clock className="h-4 w-4" />}
          accentColor="brand"
          delay={0.25}
        />
      </div>

      {/* Today's Focus + Risk Chart */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <TodaysFocus />
        </div>
        <div className="lg:col-span-2">
          <RiskDistributionChart data={data.clientsByRiskLevel} />
        </div>
      </div>

      {/* Activity Feed */}
      <ActivityFeed />
    </div>
  )
}
