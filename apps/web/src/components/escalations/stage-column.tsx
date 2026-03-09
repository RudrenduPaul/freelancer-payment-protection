'use client'

import { AnimatePresence } from 'framer-motion'
import type { EscalationStage, ActiveEscalation } from '@/lib/types'
import { STAGE_LABELS, cn } from '@/lib/utils'
import { EscalationCard } from './escalation-card'

// Maps each stage to a solid top-border accent color used on the column header
const STAGE_BORDER_TOP: Record<EscalationStage, string> = {
  polite_reminder: 'border-t-blue-400',
  firm_notice: 'border-t-amber-400',
  final_warning: 'border-t-orange-400',
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

interface StageColumnProps {
  stage: EscalationStage
  cards: ActiveEscalation[]
  onRefresh: () => void
}

export function StageColumn({ stage, cards, onRefresh }: StageColumnProps) {
  return (
    <div
      className={cn(
        'flex w-64 flex-shrink-0 flex-col rounded-xl border border-slate-200 bg-slate-50/60 border-t-4',
        STAGE_BORDER_TOP[stage],
      )}
    >
      {/* Column header */}
      <div className="flex items-center justify-between px-3 py-3 border-b border-slate-200 bg-white rounded-tl-xl rounded-tr-xl">
        <span className="text-xs font-semibold text-slate-700 tracking-wide">
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

      {/* Scrollable card list */}
      <div className="flex flex-col gap-3 overflow-y-auto p-3" style={{ maxHeight: '70vh' }}>
        <AnimatePresence initial={false}>
          {cards.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-200 bg-white/60 px-4 py-8 text-center">
              <p className="text-xs text-slate-400">No invoices here</p>
            </div>
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
    </div>
  )
}
