// API Configuration
// This dynamically detects the host to work on both localhost and network IPs

function getBaseUrl(port: number): string {
  // Check if we're in the browser
  if (typeof window !== 'undefined') {
    // Use the current host (works for localhost, 192.168.x.x, etc.)
    const protocol = window.location.protocol
    const hostname = window.location.hostname
    return `${protocol}//${hostname}:${port}`
  }
  
  // Fallback for SSR (server-side rendering)
  return process.env.NEXT_PUBLIC_API_URL || `http://localhost:${port}`
}

export const API_BASE_URL = getBaseUrl(8000)
export const AUTH_BASE_URL = getBaseUrl(8001)

// Helper function to build API URLs
export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}

export function authUrl(path: string): string {
  return `${AUTH_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}
