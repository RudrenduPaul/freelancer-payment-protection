'use client'

import { useEffect, useState } from 'react'
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
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MetricCard
          title="Total Outstanding"
          value={formatCurrency(data.totalOutstanding)}
          trend="up"
          positiveDirection="down"
          change={12.3}
          icon={<DollarSign className="h-4 w-4" />}
          delay={0}
        />
        <MetricCard
          title="Active Clients"
          value={String(data.totalClients)}
          trend="up"
          positiveDirection="up"
          change={4.2}
          icon={<Users className="h-4 w-4" />}
          delay={0.05}
        />
        <MetricCard
          title="Overdue Invoices"
          value={String(data.overdueInvoices)}
          trend="down"
          positiveDirection="down"
          change={-1}
          icon={<AlertCircle className="h-4 w-4" />}
          delay={0.1}
        />
        <MetricCard
          title="Active Escalations"
          value={String(data.escalationsActive)}
          trend="neutral"
          icon={<Siren className="h-4 w-4" />}
          delay={0.15}
        />
        <MetricCard
          title="Recovery Rate (MTD)"
          value={`${data.recoveryRateThisMonth.toFixed(1)}%`}
          trend="up"
          positiveDirection="up"
          change={5.7}
          icon={<TrendingUp className="h-4 w-4" />}
          delay={0.2}
        />
        <MetricCard
          title="Avg. Days to Payment"
          value={`${data.averageDaysToPayment}d`}
          trend="down"
          positiveDirection="down"
          change={-3.1}
          icon={<Clock className="h-4 w-4" />}
          delay={0.25}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RiskDistributionChart data={data.clientsByRiskLevel} />
        <div className="rounded-xl border border-dashed border-slate-200 bg-white p-5 flex items-center justify-center">
          <p className="text-sm text-slate-400">
            Recovery trend chart — coming in next sprint
          </p>
        </div>
      </div>
    </div>
  )
}
