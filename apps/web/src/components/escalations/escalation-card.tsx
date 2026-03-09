'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { toast } from 'sonner'
import { RefreshCw, Send, Mail, AlertCircle } from 'lucide-react'
import { escalationsApi } from '@/lib/api'
import type { ActiveEscalation, EscalationEvent } from '@/lib/types'
import { formatCurrency, cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'

interface EscalationCardProps {
  escalation: ActiveEscalation
  index: number
  onRefresh: () => void
}

function EscalationEmailPreview({
  invoiceId,
  open,
  onOpenChange,
  onSent,
}: {
  invoiceId: string
  open: boolean
  onOpenChange: (open: boolean) => void
  onSent: () => void
}) {
  const [draft, setDraft] = useState<EscalationEvent | null>(null)
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)

  const fetchDraft = async () => {
    setLoading(true)
    try {
      const result = await escalationsApi.draftEmail(invoiceId)
      setDraft(result)
    } catch (err) {
      toast.error('Failed to generate email draft. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Fetch on open
  const handleOpenChange = (next: boolean) => {
    if (next && !draft && !loading) {
      fetchDraft()
    }
    if (!next) {
      setDraft(null)
    }
    onOpenChange(next)
  }

  const handleSend = async () => {
    setSending(true)
    try {
      await escalationsApi.sendEmail(invoiceId)
      toast.success('Email sent — Bad Cop is on it 🚔')
      onOpenChange(false)
      onSent()
    } catch (err) {
      toast.error('Failed to send email. Please try again.')
    } finally {
      setSending(false)
    }
  }

  const confidencePct = draft?.aiConfidenceScore != null
    ? Math.round(draft.aiConfidenceScore * 100)
    : null

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between pr-8">
            <DialogTitle className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-brand-600" />
              Email Preview
            </DialogTitle>
            {confidencePct != null && (
              <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                AI confidence: {confidencePct}%
              </span>
            )}
          </div>
        </DialogHeader>

        <div className="px-6 pb-2">
          {loading && (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                className="mb-3"
              >
                <RefreshCw className="h-6 w-6" />
              </motion.div>
              <p className="text-sm">Generating email draft…</p>
            </div>
          )}

          {!loading && draft && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className="space-y-4"
            >
              {/* Subject */}
              <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Subject
                </p>
                <p className="text-sm font-medium text-slate-900">
                  {draft.emailSubject ?? '(no subject)'}
                </p>
              </div>

              {/* Body */}
              <div className="rounded-lg border border-slate-200 bg-white px-4 py-4">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Body
                </p>
                <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-700">
                  {draft.emailBody ?? '(empty body)'}
                </pre>
              </div>

              {/* Legal disclaimer */}
              <p className="text-center text-xs text-slate-400">
                All communications are logged for evidentiary purposes.
              </p>
            </motion.div>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchDraft}
            disabled={loading || sending}
            className="gap-1.5"
          >
            <RefreshCw className={cn('h-3.5 w-3.5', loading && 'animate-spin')} />
            Regenerate
          </Button>
          <Button
            size="sm"
            onClick={handleSend}
            disabled={!draft || loading || sending}
            className="gap-1.5"
          >
            <Send className="h-3.5 w-3.5" />
            {sending ? 'Sending…' : 'Send Email'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export function EscalationCard({ escalation, index, onRefresh }: EscalationCardProps) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const isUrgent = escalation.daysPastDue > 30

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, delay: index * 0.05, ease: 'easeOut' }}
        whileHover={{ scale: 1.01, boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}
        className={cn(
          'rounded-xl border bg-white p-4 shadow-sm cursor-default',
          isUrgent ? 'border-red-200 bg-red-50/30' : 'border-slate-200',
        )}
      >
        {/* Client info */}
        <div className="mb-3">
          <p className="font-semibold text-slate-900 text-sm leading-tight">
            {escalation.clientName}
          </p>
          {escalation.clientCompany && (
            <p className="text-xs text-slate-500 mt-0.5">{escalation.clientCompany}</p>
          )}
        </div>

        {/* Invoice details */}
        <div className="mb-3 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Invoice</span>
            <span className="text-xs font-mono font-medium text-slate-700">
              {escalation.invoiceNumber}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Amount</span>
            <span className="text-sm font-bold text-slate-900">
              {formatCurrency(escalation.amount, escalation.currency)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Days past due</span>
            <span
              className={cn(
                'text-xs font-semibold tabular-nums',
                isUrgent ? 'text-red-600' : 'text-slate-700',
              )}
            >
              {isUrgent && <AlertCircle className="inline h-3 w-3 mr-0.5 -mt-0.5" />}
              {escalation.daysPastDue}d
            </span>
          </div>
        </div>

        {/* Action */}
        <Button
          size="sm"
          className="w-full text-xs"
          onClick={() => setDialogOpen(true)}
        >
          Next Action
        </Button>
      </motion.div>

      <EscalationEmailPreview
        invoiceId={escalation.invoiceId}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onSent={onRefresh}
      />
    </>
  )
}
