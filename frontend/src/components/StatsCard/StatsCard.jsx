import React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import * as LucideIcons from 'lucide-react'
import './StatsCard.css'

const colorMap = {
  purple: { bg: 'rgba(124, 92, 252, 0.12)', icon: '#7c5cfc', border: 'rgba(124,92,252,0.2)' },
  green:  { bg: 'rgba(34, 197, 94, 0.12)',  icon: '#22c55e', border: 'rgba(34,197,94,0.2)' },
  yellow: { bg: 'rgba(245, 158, 11, 0.12)', icon: '#f59e0b', border: 'rgba(245,158,11,0.2)' },
  blue:   { bg: 'rgba(56, 189, 248, 0.12)', icon: '#38bdf8', border: 'rgba(56,189,248,0.2)' },
}

function StatsCard({ label, value, change, changeType, icon, color = 'purple' }) {
  const IconComponent = LucideIcons[icon] || LucideIcons.BarChart2
  const colors = colorMap[color] || colorMap.purple

  const ChangeIcon =
    changeType === 'positive' ? TrendingUp :
    changeType === 'negative' ? TrendingDown : Minus

  return (
    <div className="stats-card card">
      <div className="stats-card-top">
        <div
          className="stats-card-icon-wrap"
          style={{ background: colors.bg, border: `1px solid ${colors.border}` }}
        >
          <IconComponent size={20} color={colors.icon} strokeWidth={1.8} />
        </div>
        <span className={`stats-card-change stats-card-change-${changeType}`}>
          <ChangeIcon size={12} />
          {change}
        </span>
      </div>

      <div className="stats-card-bottom">
        <div className="stats-card-value">{value}</div>
        <div className="stats-card-label">{label}</div>
      </div>
    </div>
  )
}

export default StatsCard
