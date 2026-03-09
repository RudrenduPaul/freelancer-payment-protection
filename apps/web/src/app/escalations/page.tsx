'use client'

import { useCallback, useEffect, useState } from 'react'
import { Siren } from 'lucide-react'
import { escalationsApi } from '@/lib/api'
import type { ActiveEscalation, EscalationStage } from '@/lib/types'
import { SkeletonCard } from '@/components/shared/loading-skeleton'
import { EmptyState } from '@/components/shared/empty-state'
import { StageColumn } from '@/components/escalations/stage-column'

const STAGES: EscalationStage[] = [
  'polite_reminder',
  'firm_notice',
  'final_warning',
  'legal_demand',
  'legal_action',
]

export default function EscalationsPage() {
  const [escalations, setEscalations] = useState<ActiveEscalation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchEscalations = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await escalationsApi.listActive()
      setEscalations(data)
    } catch (err) {
      setError('Failed to load escalations. Please refresh.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchEscalations()
  }, [fetchEscalations])

  const grouped = STAGES.reduce<Record<EscalationStage, ActiveEscalation[]>>(
    (acc, stage) => {
      acc[stage] = escalations.filter((e) => e.stage === stage)
      return acc
    },
    {} as Record<EscalationStage, ActiveEscalation[]>,
  )

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Page header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 bg-white flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Escalation Pipeline</h1>
          <p className="text-sm text-slate-500 mt-0.5">Your bad cop is on the case</p>
        </div>
        {!loading && (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-semibold text-slate-700">
            <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
            {escalations.length} active
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading && (
          <div className="flex gap-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="w-64 flex-shrink-0">
                <SkeletonCard />
              </div>
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p className="text-sm text-red-600 font-medium">{error}</p>
              <button
                onClick={fetchEscalations}
                className="mt-3 text-sm text-brand-600 underline underline-offset-4 hover:text-brand-700"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {!loading && !error && escalations.length === 0 && (
          <EmptyState
            icon={<Siren className="h-8 w-8" />}
            heading="Pipeline clear 🎉"
            subheading="No active escalations. Either your clients pay on time, or Bad Cop already won."
          />
        )}

        {!loading && !error && escalations.length > 0 && (
          <div className="flex gap-4 min-w-max pb-4">
            {STAGES.map((stage) => (
              <StageColumn
                key={stage}
                stage={stage}
                cards={grouped[stage]}
                onRefresh={fetchEscalations}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
