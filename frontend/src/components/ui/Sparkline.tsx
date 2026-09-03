import React from 'react'

interface SparklineProps {
  data: number[]
  color?: string
  height?: number
  width?: number
  className?: string
}

export function Sparkline({
  data = [12, 18, 15, 25, 22, 34, 28, 45, 42, 59],
  color = '#3b82f6',
  height = 24,
  width = 72,
  className = ''
}: SparklineProps) {
  if (!data || data.length === 0) return null

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1

  const points = data
    .map((val, idx) => {
      const x = (idx / (data.length - 1)) * width
      const y = height - ((val - min) / range) * (height - 4) - 2
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')

  return (
    <div className={`inline-flex items-center shrink-0 ${className}`}>
      <svg width={width} height={height} className="overflow-visible">
        <defs>
          <linearGradient id={`spark-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.35} />
            <stop offset="100%" stopColor={color} stopOpacity={0.0} />
          </linearGradient>
        </defs>
        {/* Fill under line */}
        <polygon
          points={`0,${height} ${points} ${width},${height}`}
          fill={`url(#spark-${color.replace('#', '')})`}
        />
        {/* Line */}
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
      </svg>
    </div>
  )
}
