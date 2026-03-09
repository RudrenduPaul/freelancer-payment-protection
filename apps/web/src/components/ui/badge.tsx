import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-brand-600 text-white hover:bg-brand-700',
        secondary:
          'border-transparent bg-slate-100 text-slate-700 hover:bg-slate-200',
        destructive:
          'border-transparent bg-red-600 text-white hover:bg-red-700',
        outline: 'border-slate-200 text-slate-700 bg-white',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
