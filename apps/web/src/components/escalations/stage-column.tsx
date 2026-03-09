'use client'

import { AnimatePresence, motion } from 'framer-motion'
import type { EscalationStage, ActiveEscalation } from '@/lib/types'
import { STAGE_LABELS, formatCurrency, cn } from '@/lib/utils'
import { EscalationCard } from './escalation-card'

const STAGE_BORDER_TOP: Record<EscalationStage, string> = {
  polite_reminder: 'border-t-blue-400',
  firm_notice: 'border-t-amber-400',
  final_warning: 'border-t-orange-500',
  legal_demand: 'border-t-red-500',
  legal_action: 'border-t-red-700',
}

const STAGE_COUNT_COLORS: Record<EscalationStage, string> = {
  polite_reminder: 'bg-blue-100 text-blue-700',
  firm_notice: 'bg-amber-100 text-amber-700',
  final_warning: 'bg-orange-100 text-orange-700',
  legal_demand: 'bg-red-100 text-red-700',
  legal_action: 'bg-red-200 text-red-800',
}

const STAGE_EMPTY_COPY: Record<EscalationStage, string> = {
  polite_reminder: 'All friendly here',
  firm_notice: 'No firm notices',
  final_warning: 'Clear for now',
  legal_demand: 'No demands needed',
  legal_action: 'No legal action',
}

interface StageColumnProps {
  stage: EscalationStage
  cards: ActiveEscalation[]
  onRefresh: () => void
}

export function StageColumn({ stage, cards, onRefresh }: StageColumnProps) {
  const totalAtStake = cards.reduce((sum, c) => sum + c.amount, 0)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={cn(
        'flex w-64 flex-shrink-0 flex-col rounded-xl border border-slate-200 bg-slate-50/70 border-t-4',
        STAGE_BORDER_TOP[stage],
      )}
    >
      {/* Column header */}
      <div className="px-3 py-3 border-b border-slate-200 bg-white rounded-tl-xl rounded-tr-xl">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700 tracking-wide">
            {STAGE_LABELS[stage]}
          </span>
          <span
            className={cn(
              'inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-bold tabular-nums',
              STAGE_COUNT_COLORS[stage],
            )}
          >
            {cards.length}
          </span>
        </div>
        {cards.length > 0 && (
          <p className="mt-1 text-[10px] text-slate-400 tabular-nums">
            {formatCurrency(totalAtStake)} at stake
          </p>
        )}
      </div>

      {/* Scrollable card list */}
      <div className="flex flex-col gap-3 overflow-y-auto p-3" style={{ maxHeight: '68vh' }}>
        <AnimatePresence initial={false}>
          {cards.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="rounded-lg border border-dashed border-slate-200 bg-white/70 px-4 py-10 text-center"
            >
              <p className="text-xs font-medium text-slate-400">
                {STAGE_EMPTY_COPY[stage]}
              </p>
              <p className="text-[10px] text-slate-300 mt-0.5">
                No invoices at this stage
              </p>
            </motion.div>
          ) : (
            cards.map((card, index) => (
              <EscalationCard
                key={card.invoiceId}
                escalation={card}
                index={index}
                onRefresh={onRefresh}
              />
            ))
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
