// components/StatusBadge.tsx
// Animated status indicator component

interface StatusBadgeProps {
  status: 'NORMAL' | 'WARNING' | 'ANOMALY';
  size?: 'sm' | 'md' | 'lg';
}

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const statusConfig = {
    NORMAL: {
      color: 'bg-status-normal',
      text: 'text-status-normal',
      border: 'border-status-normal',
      glow: 'shadow-status-normal/50'
    },
    WARNING: {
      color: 'bg-status-warning',
      text: 'text-status-warning',
      border: 'border-status-warning',
      glow: 'shadow-status-warning/50'
    },
    ANOMALY: {
      color: 'bg-status-anomaly',
      text: 'text-status-anomaly',
      border: 'border-status-anomaly',
      glow: 'shadow-status-anomaly/50'
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
