// components/MetricCard.tsx
// Reusable metric display component

interface MetricCardProps {
  title: string;
  value: number;
  unit: string;
  status?: 'normal' | 'warning' | 'danger';
  trend?: number;
  icon?: React.ReactNode;
}

export default function MetricCard({ 
  title, 
  value, 
  unit, 
  status = 'normal',
  trend,
  icon 
}: MetricCardProps) {
  const statusColors = {
    normal: 'border-status-normal/30 bg-status-normal/5',
    warning: 'border-status-warning/30 bg-status-warning/5',
    danger: 'border-status-anomaly/30 bg-status-anomaly/5'
  }

  const trendColor = trend && trend > 0 ? 'text-status-anomaly' : 'text-status-normal'

  return (
    <div className={`p-6 rounded-xl border backdrop-blur-sm transition-all hover:scale-105 ${statusColors[status]}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-industrial-400">{title}</h3>
        {icon && <div className="text-industrial-500">{icon}</div>}
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-4xl font-bold text-white">{value.toFixed(2)}</span>
        <span className="text-lg text-industrial-500">{unit}</span>
      </div>
      {trend !== undefined && (
        <div className={`mt-2 text-sm ${trendColor}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}% from average
        </div>
      )}
    </div>
  )
}
