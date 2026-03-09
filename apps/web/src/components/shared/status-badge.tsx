import { cn, getStatusColor } from '@/lib/utils'
import type { InvoiceStatus } from '@/lib/types'

interface StatusBadgeProps {
  status: InvoiceStatus
  className?: string
}

function toTitleCase(str: string): string {
  return str
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold',
        getStatusColor(status),
        className,
      )}
    >
      {toTitleCase(status)}
    </span>
  )
}
