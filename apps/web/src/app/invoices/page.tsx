'use client'

import { useEffect, useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Plus, CheckCircle, Eye } from 'lucide-react'
import { toast } from 'sonner'
import { invoicesApi } from '@/lib/api'
import type { Invoice, InvoiceStatus } from '@/lib/types'
import { formatCurrency, formatDate, daysSince, STAGE_LABELS, STAGE_COLORS, cn } from '@/lib/utils'
import { StatusBadge } from '@/components/shared/status-badge'
import { EmptyState } from '@/components/shared/empty-state'
import { SkeletonTable } from '@/components/shared/loading-skeleton'
import { Button } from '@/components/ui/button'
import { AddInvoiceDialog } from '@/components/invoices/add-invoice-dialog'

type FilterStatus = InvoiceStatus | 'all'

const STATUS_FILTERS: { label: string; value: FilterStatus }[] = [
  { label: 'All', value: 'all' },
  { label: 'Draft', value: 'draft' },
  { label: 'Sent', value: 'sent' },
  { label: 'Overdue', value: 'overdue' },
  { label: 'Disputed', value: 'disputed' },
  { label: 'Paid', value: 'paid' },
]

const tableVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.04 } },
}

const rowVariants = {
  hidden: { opacity: 0, y: 6 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.22, ease: 'easeOut' } },
}

function daysOverdue(dueDate: string, status: InvoiceStatus): number {
  if (status === 'paid' || status === 'written_off') return 0
  const diff = daysSince(dueDate)
  return diff > 0 ? diff : 0
}

export default function InvoicesPage() {
  const router = useRouter()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [activeFilter, setActiveFilter] = useState<FilterStatus>('all')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [markingPaidId, setMarkingPaidId] = useState<string | null>(null)

  async function loadInvoices() {
    setLoading(true)
    try {
      const res = await invoicesApi.list()
      setInvoices(res.items)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load invoices'
      toast.error('Could not load invoices', { description: message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadInvoices()
  }, [])

  const overdueCount = useMemo(
    () => invoices.filter((inv) => inv.status === 'overdue').length,
    [invoices],
  )

  const totalOutstanding = useMemo(
    () =>
      invoices
        .filter((inv) => inv.status !== 'paid' && inv.status !== 'written_off')
        .reduce((sum, inv) => sum + inv.amount, 0),
    [invoices],
  )

  const filtered = useMemo(() => {
    if (activeFilter === 'all') return invoices
    return invoices.filter((inv) => inv.status === activeFilter)
  }, [invoices, activeFilter])

  async function handleMarkPaid(e: React.MouseEvent, invoice: Invoice) {
    e.stopPropagation()
    setMarkingPaidId(invoice.id)
    // Optimistic update
    setInvoices((prev) =>
      prev.map((inv) => (inv.id === invoice.id ? { ...inv, status: 'paid' as InvoiceStatus } : inv)),
    )
    try {
      await invoicesApi.updateStatus(invoice.id, 'paid')
      toast.success('Invoice marked as paid', {
        description: `${invoice.invoiceNumber} — ${formatCurrency(invoice.amount, invoice.currency)}`,
      })
    } catch (err) {
      // Revert optimistic update
      setInvoices((prev) =>
        prev.map((inv) =>
          inv.id === invoice.id ? { ...inv, status: invoice.status } : inv,
        ),
      )
      const message = err instanceof Error ? err.message : 'Update failed'
      toast.error('Could not mark as paid', { description: message })
    } finally {
      setMarkingPaidId(null)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Invoices</h1>
          {!loading && (
            <p className="mt-1 text-3xl font-extrabold text-slate-900 tabular-nums">
              {formatCurrency(totalOutstanding)}
              <span className="ml-2 text-base font-normal text-slate-500">outstanding</span>
            </p>
          )}
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="h-4 w-4" />
          Add Invoice
        </Button>
      </div>

      {/* Filter bar */}
      {!loading && invoices.length > 0 && (
        <div className="flex items-center gap-1.5 flex-wrap">
          {STATUS_FILTERS.map((filter) => {
            const isActive = activeFilter === filter.value
            const isOverdue = filter.value === 'overdue'
            return (
              <div key={filter.value} className="relative">
                <motion.button
                  onClick={() => setActiveFilter(filter.value)}
                  className={cn(
                    'relative rounded-lg px-3.5 py-1.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'text-white'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                  )}
                >
                  {isActive && (
                    <motion.span
                      layoutId="invoice-filter-bg"
                      className="absolute inset-0 rounded-lg bg-brand-600"
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    />
                  )}
                  <span className="relative z-10 flex items-center gap-1.5">
                    {filter.label}
                    {isOverdue && overdueCount > 0 && (
                      <span
                        className={cn(
                          'inline-flex items-center justify-center rounded-full px-1.5 py-0.5 text-xs font-bold leading-none',
                          isActive
                            ? 'bg-white/20 text-white'
                            : 'bg-red-100 text-red-600',
                        )}
                      >
                        {overdueCount}
                      </span>
                    )}
                  </span>
                </motion.button>
              </div>
            )
          })}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <SkeletonTable rows={7} />
      ) : invoices.length === 0 ? (
        <EmptyState
          icon={<FileText className="h-8 w-8" />}
          heading="No invoices tracked"
          subheading="Add your first invoice and let Bad Cop handle the awkward conversations."
          action={{ label: 'Add Invoice', onClick: () => setDialogOpen(true) }}
        />
      ) : filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 bg-white px-8 py-14 text-center">
          <p className="text-sm text-slate-500">
            No {activeFilter} invoices right now.
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
          {/* Table header */}
          <div className="grid grid-cols-[140px_1fr_110px_110px_110px_80px_140px_100px] items-center gap-3 border-b border-slate-200 bg-slate-50 px-6 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span>Invoice #</span>
            <span>Client</span>
            <span>Amount</span>
            <span>Status</span>
            <span>Due Date</span>
            <span>Overdue</span>
            <span>Stage</span>
            <span className="text-right">Actions</span>
          </div>

          <motion.div variants={tableVariants} initial="hidden" animate="visible">
            <AnimatePresence>
              {filtered.map((invoice) => {
                const overdueDays = daysOverdue(invoice.dueDate, invoice.status)
                const isOverdue = overdueDays > 0

                return (
                  <motion.div
                    key={invoice.id}
                    variants={rowVariants}
                    layout
                    onClick={() => router.push(`/invoices/${invoice.id}`)}
                    className={cn(
                      'grid grid-cols-[140px_1fr_110px_110px_110px_80px_140px_100px] items-center gap-3 border-b border-slate-100 px-6 py-4 last:border-0 cursor-pointer hover:bg-slate-50 transition-colors',
                      isOverdue && 'bg-red-50 hover:bg-red-100/60',
                    )}
                  >
                    {/* Invoice # */}
                    <span className="truncate text-sm font-mono font-medium text-slate-800">
                      {invoice.invoiceNumber}
                    </span>

                    {/* Client */}
                    <span className="truncate text-sm text-slate-700">
                      {invoice.clientName ?? '—'}
                    </span>

                    {/* Amount */}
                    <span className="text-sm font-semibold text-slate-800 tabular-nums">
                      {formatCurrency(invoice.amount, invoice.currency)}
                    </span>

                    {/* Status */}
                    <div>
                      <StatusBadge status={invoice.status} />
                    </div>

                    {/* Due Date */}
                    <span className="text-sm text-slate-600">{formatDate(invoice.dueDate)}</span>

                    {/* Days Overdue */}
                    <span
                      className={cn(
                        'text-sm tabular-nums',
                        isOverdue ? 'font-semibold text-red-600' : 'text-slate-400',
                      )}
                    >
                      {isOverdue ? `+${overdueDays}d` : '—'}
                    </span>

                    {/* Escalation Stage */}
                    <div>
                      {invoice.escalationStage ? (
                        <span
                          className={cn(
                            'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
                            STAGE_COLORS[invoice.escalationStage],
                          )}
                        >
                          {STAGE_LABELS[invoice.escalationStage]}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">—</span>
                      )}
                    </div>

                    {/* Actions */}
                    <div
                      className="flex items-center justify-end gap-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => router.push(`/invoices/${invoice.id}`)}
                        title="View invoice"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {invoice.status !== 'paid' && invoice.status !== 'written_off' && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => handleMarkPaid(e, invoice)}
                          disabled={markingPaidId === invoice.id}
                          title="Mark as paid"
                          className="text-slate-400 hover:text-emerald-600 hover:bg-emerald-50"
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </motion.div>
        </div>
      )}

      <AddInvoiceDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSuccess={loadInvoices}
      />
    </div>
  )
}
