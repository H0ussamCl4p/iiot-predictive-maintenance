// API Configuration
// This uses environment variables with fallback to localhost for development

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const AUTH_BASE_URL = process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8001'

// Helper function to build API URLs
export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}

export function authUrl(path: string): string {
  return `${AUTH_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}
