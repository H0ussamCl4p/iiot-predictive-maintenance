// Animated status indicator component

interface StatusBadgeProps {
  status: 'NORMAL' | 'WARNING' | 'ANOMALY';
  size?: 'sm' | 'md' | 'lg';
}

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const statusConfig = {
    NORMAL: {
      color: 'bg-emerald-500',
      text: 'text-emerald-500',
      border: 'border-emerald-500',
      glow: 'shadow-emerald-500/50'
    },
    WARNING: {
      color: 'bg-yellow-500',
      text: 'text-yellow-500',
      border: 'border-yellow-500',
      glow: 'shadow-yellow-500/50'
    },
    ANOMALY: {
      color: 'bg-red-500',
      text: 'text-red-500',
      border: 'border-red-500',
      glow: 'shadow-red-500/50'
    }
  }

  const sizeClasses = {
    sm: 'px-3 py-1 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }

  const config = statusConfig[status]

  return (
    <div className={`inline-flex items-center space-x-2 ${sizeClasses[size]} rounded-full border ${config.border} bg-industrial-900/50 backdrop-blur-sm`}>
      <div className={`relative w-2 h-2 ${config.color} rounded-full`}>
        <div className={`absolute inset-0 ${config.color} rounded-full animate-ping opacity-75`}></div>
      </div>
      <span className={`font-semibold ${config.text}`}>{status}</span>
    </div>
  )
}
