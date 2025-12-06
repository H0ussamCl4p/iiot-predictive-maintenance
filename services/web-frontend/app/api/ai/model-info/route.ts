import { NextResponse } from 'next/server'

const AI_ENGINE_URL = process.env.AI_ENGINE_URL || 'http://localhost:8000'

export async function GET() {
  try {
    const response = await fetch(`${AI_ENGINE_URL}/model-info`, {
      cache: 'no-store'
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch model info')
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Model info error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch model information' },
      { status: 500 }
    )
  }
}
