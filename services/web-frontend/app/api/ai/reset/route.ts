import { NextResponse } from 'next/server'

const AI_ENGINE_URL = process.env.AI_ENGINE_URL || 'http://localhost:8000'

export async function POST() {
  try {
    const response = await fetch(`${AI_ENGINE_URL}/reset-model`, {
      method: 'POST'
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || 'Reset failed' },
        { status: response.status }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Reset error:', error)
    return NextResponse.json(
      { error: 'Failed to reset model' },
      { status: 500 }
    )
  }
}
