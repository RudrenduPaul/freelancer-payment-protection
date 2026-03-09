'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, useMotionValue, animate } from 'framer-motion'
import { cn, getRiskColor } from '@/lib/utils'
import type { RiskLevel } from '@/lib/types'

interface RiskBadgeProps {
  level: RiskLevel
  score?: number
  animate?: boolean
}

const LEVEL_LABELS: Record<RiskLevel, string> = {
  low: 'Low Risk',
  medium: 'Medium Risk',
  high: 'High Risk',
  critical: 'Critical',
}

function AnimatedScore({ target }: { target: number }) {
  const [display, setDisplay] = useState(0)
  const motionVal = useMotionValue(0)
  const hasAnimated = useRef(false)

  useEffect(() => {
    if (hasAnimated.current) return
    hasAnimated.current = true

    const controls = animate(motionVal, target, {
      duration: 1,
      ease: 'easeOut',
      onUpdate: (v) => setDisplay(Math.round(v)),
    })

    return () => controls.stop()
  }, [target, motionVal])

  return <span>{display}</span>
}

export function RiskBadge({ level, score, animate: shouldAnimate = false }: RiskBadgeProps) {
  return (
    <motion.span
      initial={shouldAnimate ? { opacity: 0, scale: 0.9 } : false}
      animate={shouldAnimate ? { opacity: 1, scale: 1 } : false}
      transition={{ duration: 0.2 }}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold',
        getRiskColor(level),
      )}
    >
      <span
        className={cn('h-1.5 w-1.5 rounded-full', {
          'bg-emerald-500': level === 'low',
          'bg-amber-500': level === 'medium',
          'bg-orange-500': level === 'high',
          'bg-red-500': level === 'critical',
        })}
      />
      {LEVEL_LABELS[level]}
      {score !== undefined && (
        <span className="font-bold tabular-nums">
          (
          {shouldAnimate ? <AnimatedScore target={score} /> : score}
          )
        </span>
      )}
    </motion.span>
  )
}
