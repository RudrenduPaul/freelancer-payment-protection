'use client'

import { useEffect, useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Users, Search, Plus, Trash2, Eye } from 'lucide-react'
import { toast } from 'sonner'
import { clientsApi } from '@/lib/api'
import type { Client } from '@/lib/types'
import { formatCurrency, formatDate } from '@/lib/utils'
import { RiskBadge } from '@/components/shared/risk-badge'
import { EmptyState } from '@/components/shared/empty-state'
import { SkeletonTable } from '@/components/shared/loading-skeleton'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AddClientDialog } from '@/components/clients/add-client-dialog'

const tableVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.045,
    },
  },
}

const rowVariants = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.25, ease: 'easeOut' } },
}

export default function ClientsPage() {
  const router = useRouter()
  const [clients, setClients] = useState<Client[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  async function loadClients() {
    setLoading(true)
    try {
      const res = await clientsApi.list()
      // Sort by risk score descending
      const sorted = [...res.items].sort((a, b) => b.riskScore - a.riskScore)
      setClients(sorted)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load clients'
      toast.error('Could not load clients', { description: message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadClients()
  }, [])

  const filtered = useMemo(() => {
    if (!search.trim()) return clients
    const q = search.trim().toLowerCase()
    return clients.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.company && c.company.toLowerCase().includes(q)),
    )
  }, [clients, search])

  async function handleDelete(e: React.MouseEvent, client: Client) {
    e.stopPropagation()
    if (!confirm(`Remove ${client.name} from your CRM? This cannot be undone.`)) return
    setDeletingId(client.id)
    try {
      await clientsApi.delete(client.id)
      toast.success('Client removed', { description: `${client.name} has been deleted.` })
      setClients((prev) => prev.filter((c) => c.id !== client.id))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Delete failed'
      toast.error('Could not delete client', { description: message })
    } finally {
      setDeletingId(null)
    }
  }

  function handleRowClick(id: string) {
    router.push(`/clients/${id}`)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-900">Clients</h1>
          {!loading && (
            <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600">
              {clients.length}
            </span>
          )}
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="h-4 w-4" />
          Add Client
        </Button>
      </div>

      {/* Search */}
      {!loading && clients.length > 0 && (
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <Input
            placeholder="Search by name or company…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      )}

      {/* Content */}
      {loading ? (
        <SkeletonTable rows={6} />
      ) : clients.length === 0 ? (
        <EmptyState
          icon={<Users className="h-8 w-8" />}
          heading="No clients yet"
          subheading="Add your first client to start tracking payments. Your bad cop is ready."
          action={{ label: 'Add Client', onClick: () => setDialogOpen(true) }}
        />
      ) : filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 bg-white px-8 py-14 text-center">
          <p className="text-sm text-slate-500">
            No clients match &ldquo;{search}&rdquo;
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
          {/* Table header */}
          <div className="grid grid-cols-[1fr_140px_130px_110px_120px_100px] items-center gap-4 border-b border-slate-200 bg-slate-50 px-6 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span>Name / Company</span>
            <span>Risk</span>
            <span>Outstanding</span>
            <span>Avg Delay</span>
            <span>Terms</span>
            <span className="text-right">Actions</span>
          </div>

          {/* Table rows */}
          <motion.div
            variants={tableVariants}
            initial="hidden"
            animate="visible"
          >
            <AnimatePresence>
              {filtered.map((client) => (
                <motion.div
                  key={client.id}
                  variants={rowVariants}
                  layout
                  onClick={() => handleRowClick(client.id)}
                  className="grid grid-cols-[1fr_140px_130px_110px_120px_100px] items-center gap-4 border-b border-slate-100 px-6 py-4 last:border-0 cursor-pointer hover:bg-slate-50 transition-colors"
                >
                  {/* Name / Company */}
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-900">
                      {client.name}
                    </p>
                    {client.company && (
                      <p className="truncate text-xs text-slate-500">{client.company}</p>
                    )}
                  </div>

                  {/* Risk */}
                  <div>
                    <RiskBadge
                      level={client.riskLevel}
                      score={client.riskScore}
                      animate={false}
                    />
                  </div>

                  {/* Outstanding */}
                  <span className="text-sm font-medium text-slate-700">
                    {formatCurrency(client.totalOutstanding)}
                  </span>

                  {/* Avg Delay */}
                  <span className="text-sm text-slate-600">
                    {client.averagePaymentDelay > 0
                      ? `+${client.averagePaymentDelay}d`
                      : `${client.averagePaymentDelay}d`}
                  </span>

                  {/* Payment Terms */}
                  <span className="text-sm text-slate-600">
                    Net {client.paymentTermsDays}
                  </span>

                  {/* Actions */}
                  <div
                    className="flex items-center justify-end gap-1"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => router.push(`/clients/${client.id}`)}
                      title="View client"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => handleDelete(e, client)}
                      disabled={deletingId === client.id}
                      title="Delete client"
                      className="text-slate-400 hover:text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        </div>
      )}

      <AddClientDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSuccess={loadClients}
      />
    </div>
  )
}
