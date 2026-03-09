'use client'

import { motion } from 'framer-motion'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'
import type { RiskLevel } from '@/lib/types'

interface RiskDistributionChartProps {
  data: Record<RiskLevel, number>
}

const RISK_CONFIG: {
  key: RiskLevel
  label: string
  color: string
  lightColor: string
}[] = [
  { key: 'low', label: 'Low Risk', color: '#10b981', lightColor: '#d1fae5' },
  { key: 'medium', label: 'Medium Risk', color: '#f59e0b', lightColor: '#fef3c7' },
  { key: 'high', label: 'High Risk', color: '#f97316', lightColor: '#ffedd5' },
  { key: 'critical', label: 'Critical', color: '#ef4444', lightColor: '#fee2e2' },
]

interface ChartEntry {
  name: string
  value: number
  color: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: { payload: ChartEntry; value: number }[]
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null
  const { name, value, color } = payload[0].payload
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-lg text-sm">
      <div className="flex items-center gap-2">
        <span
          className="inline-block h-2.5 w-2.5 rounded-full flex-shrink-0"
          style={{ backgroundColor: color }}
        />
        <span className="font-medium text-slate-700">{name}</span>
        <span className="font-bold text-slate-900 tabular-nums">{value}</span>
        <span className="text-slate-400">clients</span>
      </div>
    </div>
  )
}

interface LegendEntry {
  value: string
  color: string
  payload?: { value: number }
}

function CustomLegend({ payload }: { payload?: LegendEntry[] }) {
  if (!payload) return null
  return (
    <ul className="flex flex-wrap justify-center gap-x-4 gap-y-2 mt-4">
      {payload.map((entry) => (
        <li key={entry.value} className="flex items-center gap-1.5 text-xs text-slate-600">
          <span
            className="inline-block h-2.5 w-2.5 rounded-full flex-shrink-0"
            style={{ backgroundColor: entry.color }}
          />
          {entry.value}
          {entry.payload && (
            <span className="font-semibold text-slate-800 tabular-nums">
              ({entry.payload.value})
            </span>
          )}
        </li>
      ))}
    </ul>
  )
}

export function RiskDistributionChart({ data }: RiskDistributionChartProps) {
  const chartData: ChartEntry[] = RISK_CONFIG.filter(
    (cfg) => (data[cfg.key] ?? 0) > 0,
  ).map((cfg) => ({
    name: cfg.label,
    value: data[cfg.key] ?? 0,
    color: cfg.color,
  }))

  const total = chartData.reduce((sum, d) => sum + d.value, 0)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">
          Client Risk Distribution
        </h3>
        <p className="text-sm text-slate-500">{total} total clients</p>
      </div>

      {total === 0 ? (
        <div className="flex h-48 items-center justify-center text-sm text-slate-400">
          No clients yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="45%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={3}
              dataKey="value"
              stroke="none"
            >
              {chartData.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={entry.color}
                  opacity={0.9}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend content={<CustomLegend />} />
          </PieChart>
        </ResponsiveContainer>
      )}
    </motion.div>
  )
}
