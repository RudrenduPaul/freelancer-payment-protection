'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Minus,
  Bell,
  Building2,
  Globe,
  Clock,
  DollarSign,
  BarChart2,
} from 'lucide-react'
import { toast } from 'sonner'
import { clientsApi, invoicesApi } from '@/lib/api'
import type { Client, RiskScore, Invoice } from '@/lib/types'
import { formatCurrency, formatDate, STAGE_LABELS, STAGE_COLORS, cn } from '@/lib/utils'
import { RiskBadge } from '@/components/shared/risk-badge'
import { StatusBadge } from '@/components/shared/status-badge'
import { Button } from '@/components/ui/button'

const sectionVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: (delay: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: 'easeOut', delay },
  }),
}

function StatCard({
  icon,
  label,
  value,
  sub,
}: {
  icon: React.ReactNode
  label: string
  value: string
  sub?: string
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-slate-500">
        {icon}
      </div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-bold text-slate-900">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-slate-400">{sub}</p>}
    </div>
  )
}

export default function ClientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()

  const [client, setClient] = useState<Client | null>(null)
  const [riskScore, setRiskScore] = useState<RiskScore | null>(null)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const [clientData, riskData, invoiceData] = await Promise.all([
          clientsApi.get(id),
          clientsApi.getRiskScore(id),
          invoicesApi.list({ clientId: id }),
        ])
        setClient(clientData)
        setRiskScore(riskData)
        setInvoices(invoiceData.items)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load client'
        setError(message)
        toast.error('Could not load client', { description: message })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse rounded-md bg-slate-200" />
        <div className="h-32 w-full animate-pulse rounded-xl bg-slate-200" />
        <div className="grid grid-cols-4 gap-4">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-28 animate-pulse rounded-xl bg-slate-200" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !client) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <p className="text-base font-semibold text-slate-700">Client not found</p>
        <p className="mt-1 text-sm text-slate-500">{error ?? 'This client does not exist.'}</p>
        <Button variant="outline" className="mt-6" onClick={() => router.push('/clients')}>
          <ArrowLeft className="h-4 w-4" /> Back to Clients
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Back button */}
      <motion.div custom={0} variants={sectionVariants} initial="hidden" animate="visible">
        <Button variant="ghost" size="sm" onClick={() => router.push('/clients')}>
          <ArrowLeft className="h-4 w-4" />
          Back to Clients
        </Button>
      </motion.div>

      {/* Hero */}
      <motion.div
        custom={0.05}
        variants={sectionVariants}
        initial="hidden"
        animate="visible"
        className="rounded-xl border border-slate-200 bg-white p-7"
      >
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1.5">
            <h1 className="text-3xl font-bold text-slate-900">{client.name}</h1>
            <div className="flex flex-wrap items-center gap-2">
              {client.company && (
                <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                  <Building2 className="h-3 w-3" />
                  {client.company}
                </span>
              )}
              {client.industry && (
                <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                  <BarChart2 className="h-3 w-3" />
                  {client.industry}
                </span>
              )}
              {client.country && (
                <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                  <Globe className="h-3 w-3" />
                  {client.country}
                </span>
              )}
            </div>
            <p className="text-sm text-slate-500">{client.email}</p>
          </div>

          <div className="flex flex-col items-end gap-2">
            <RiskBadge
              level={client.riskLevel}
              score={client.riskScore}
              animate={true}
            />
            <p className="text-xs text-slate-400">
              Client since {formatDate(client.createdAt)}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Stats row */}
      <motion.div
        custom={0.1}
        variants={sectionVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-2 gap-4 sm:grid-cols-4"
      >
        <StatCard
          icon={<DollarSign className="h-4 w-4" />}
          label="Total Invoiced"
          value={formatCurrency(client.totalInvoiced)}
        />
        <StatCard
          icon={<DollarSign className="h-4 w-4" />}
          label="Outstanding"
          value={formatCurrency(client.totalOutstanding)}
          sub={client.totalOutstanding > 0 ? 'Awaiting payment' : 'All clear'}
        />
        <StatCard
          icon={<Clock className="h-4 w-4" />}
          label="Avg Payment Delay"
          value={
            client.averagePaymentDelay > 0
              ? `+${client.averagePaymentDelay} days`
              : `${client.averagePaymentDelay} days`
          }
          sub={client.averagePaymentDelay > 0 ? 'Typically late' : 'On time'}
        />
        <StatCard
          icon={<Clock className="h-4 w-4" />}
          label="Payment Terms"
          value={`Net ${client.paymentTermsDays}`}
          sub="days"
        />
      </motion.div>

      {/* Risk breakdown */}
      {riskScore && (
        <motion.div
          custom={0.15}
          variants={sectionVariants}
          initial="hidden"
          animate="visible"
          className="rounded-xl border border-slate-200 bg-white p-6 space-y-5"
        >
          <h2 className="text-base font-semibold text-slate-900">Risk Breakdown</h2>

          <div className="space-y-3">
            {riskScore.factors.map((factor, i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    {factor.impact === 'positive' ? (
                      <TrendingDown className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                    ) : factor.impact === 'negative' ? (
                      <TrendingUp className="h-4 w-4 text-red-500 flex-shrink-0" />
                    ) : (
                      <Minus className="h-4 w-4 text-slate-400 flex-shrink-0" />
                    )}
                    <span className="text-sm font-medium text-slate-700">{factor.name}</span>
                  </div>
                  <span className="text-xs text-slate-500 flex-shrink-0">
                    weight {(factor.weight * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="ml-6 text-xs text-slate-500">{factor.description}</p>
                <div className="ml-6 h-1.5 w-full rounded-full bg-slate-100">
                  <div
                    className={cn(
                      'h-1.5 rounded-full transition-all',
                      factor.impact === 'positive'
                        ? 'bg-emerald-400'
                        : factor.impact === 'negative'
                          ? 'bg-red-400'
                          : 'bg-slate-300',
                    )}
                    style={{ width: `${Math.min(factor.weight * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {riskScore.reasoning && (
            <div className="rounded-lg bg-slate-50 p-4 border border-slate-100">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">
                AI Reasoning
              </p>
              <p className="text-sm text-slate-700 leading-relaxed">{riskScore.reasoning}</p>
            </div>
          )}
        </motion.div>
      )}

      {/* Recent Invoices */}
      <motion.div
        custom={0.2}
        variants={sectionVariants}
        initial="hidden"
        animate="visible"
        className="rounded-xl border border-slate-200 bg-white overflow-hidden"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="text-base font-semibold text-slate-900">Invoices</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push(`/invoices?clientId=${client.id}`)}
          >
            View all
          </Button>
        </div>

        {invoices.length === 0 ? (
          <div className="px-6 py-10 text-center">
            <p className="text-sm text-slate-500">No invoices for this client yet.</p>
          </div>
        ) : (
          <div>
            {invoices.slice(0, 8).map((invoice) => (
              <div
                key={invoice.id}
                onClick={() => router.push(`/invoices/${invoice.id}`)}
                className="flex items-center justify-between gap-4 border-b border-slate-100 px-6 py-3.5 last:border-0 cursor-pointer hover:bg-slate-50 transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-slate-800">
                    {invoice.invoiceNumber}
                  </p>
                  <p className="text-xs text-slate-500">Due {formatDate(invoice.dueDate)}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold text-slate-700">
                    {formatCurrency(invoice.amount, invoice.currency)}
                  </span>
                  <StatusBadge status={invoice.status} />
                  {invoice.escalationStage && (
                    <span
                      className={cn(
                        'hidden sm:inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
                        STAGE_COLORS[invoice.escalationStage],
                      )}
                    >
                      {STAGE_LABELS[invoice.escalationStage]}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Send Reminder */}
      <motion.div
        custom={0.25}
        variants={sectionVariants}
        initial="hidden"
        animate="visible"
        className="flex justify-end"
      >
        <Button
          onClick={() =>
            toast.info('Coming soon', {
              description: 'Escalation draft composer is on the way.',
            })
          }
        >
          <Bell className="h-4 w-4" />
          Send Reminder
        </Button>
      </motion.div>
    </div>
  )
}
