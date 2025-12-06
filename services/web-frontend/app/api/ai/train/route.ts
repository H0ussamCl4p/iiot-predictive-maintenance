import { NextRequest, NextResponse } from 'next/server'

const AI_ENGINE_URL = process.env.AI_ENGINE_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${AI_ENGINE_URL}/train`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(
        { error: data.detail || 'Training failed' },
        { status: response.status }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Training error:', error)
    return NextResponse.json(
      { error: 'Failed to train model' },
      { status: 500 }
    )
  }
}
