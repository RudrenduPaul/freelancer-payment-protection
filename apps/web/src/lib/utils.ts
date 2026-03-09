import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { RiskLevel, InvoiceStatus, EscalationStage } from './types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function daysSince(dateString: string): number {
  const diff = Date.now() - new Date(dateString).getTime()
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}

export function getRiskColor(level: RiskLevel): string {
  return {
    low: 'text-emerald-600 bg-emerald-50 border-emerald-200',
    medium: 'text-amber-600 bg-amber-50 border-amber-200',
    high: 'text-orange-600 bg-orange-50 border-orange-200',
    critical: 'text-red-600 bg-red-50 border-red-200',
  }[level]
}

export function getRiskBarColor(level: RiskLevel): string {
  return {
    low: 'bg-emerald-500',
    medium: 'bg-amber-500',
    high: 'bg-orange-500',
    critical: 'bg-red-500',
  }[level]
}

export function getStatusColor(status: InvoiceStatus): string {
  return {
    draft: 'text-slate-600 bg-slate-50 border-slate-200',
    sent: 'text-blue-600 bg-blue-50 border-blue-200',
    overdue: 'text-red-600 bg-red-50 border-red-200',
    disputed: 'text-orange-600 bg-orange-50 border-orange-200',
    paid: 'text-emerald-600 bg-emerald-50 border-emerald-200',
    written_off: 'text-slate-400 bg-slate-50 border-slate-200',
  }[status]
}

export const STAGE_LABELS: Record<EscalationStage, string> = {
  polite_reminder: 'Polite Reminder',
  firm_notice: 'Firm Notice',
  final_warning: 'Final Warning',
  legal_demand: 'Legal Demand',
  legal_action: 'Legal Action',
}

export const STAGE_COLORS: Record<EscalationStage, string> = {
  polite_reminder: 'text-blue-600 bg-blue-50 border-blue-200',
  firm_notice: 'text-amber-600 bg-amber-50 border-amber-200',
  final_warning: 'text-orange-600 bg-orange-50 border-orange-200',
  legal_demand: 'text-red-600 bg-red-50 border-red-200',
  legal_action: 'text-red-800 bg-red-100 border-red-300',
}
