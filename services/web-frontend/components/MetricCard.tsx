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
  const statusStyles = {
    normal: 'border-emerald-500/30 bg-emerald-500/5',
    warning: 'border-yellow-500/30 bg-yellow-500/5',
    danger: 'border-red-500/30 bg-red-500/5'
  }

  const trendColor = trend && trend > 0 ? 'text-red-500' : 'text-emerald-500'

  return (
    <div className={`p-6 rounded-xl border backdrop-blur-sm transition-all hover:scale-105 ${statusStyles[status]}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-400">{title}</h3>
        {icon && <div className="text-slate-500">{icon}</div>}
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-4xl font-bold text-white">{value.toFixed(2)}</span>
        <span className="text-lg text-slate-500">{unit}</span>
      </div>
      {trend !== undefined && (
        <div className={`mt-2 text-sm ${trendColor}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}% from average
        </div>
      )}
    </div>
  )
}
