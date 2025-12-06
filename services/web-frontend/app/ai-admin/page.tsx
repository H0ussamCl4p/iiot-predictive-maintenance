"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, Play, RotateCcw, Trash2, CheckCircle, XCircle } from "lucide-react"

interface ModelInfo {
  exists: boolean
  type: string
  n_estimators?: number
  contamination?: number
  last_trained?: string
  sample_count?: number
}

export default function AIAdminPage() {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [isTraining, setIsTraining] = useState(false)
  const [trainStatus, setTrainStatus] = useState<{ type: 'success' | 'error' | null, message: string }>({ type: null, message: '' })
  
  // Training parameters
  const [nEstimators, setNEstimators] = useState(100)
  const [contamination, setContamination] = useState(0.1)
  const [randomState, setRandomState] = useState(42)

  useEffect(() => {
    fetchModelInfo()
    const interval = setInterval(fetchModelInfo, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchModelInfo = async () => {
    try {
      const response = await fetch('/api/ai/model-info')
      const data = await response.json()
      setModelInfo(data)
    } catch (error) {
      console.error('Failed to fetch model info:', error)
    }
  }

  const handleTrain = async () => {
    setIsTraining(true)
    setTrainStatus({ type: null, message: '' })

    try {
      const response = await fetch('/api/ai/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          n_estimators: nEstimators,
          contamination: contamination,
          random_state: randomState
        })
      })

      const data = await response.json()

      if (response.ok) {
        setTrainStatus({ type: 'success', message: data.message || 'Model trained successfully!' })
        fetchModelInfo()
      } else {
        setTrainStatus({ type: 'error', message: data.error || 'Training failed' })
      }
    } catch (error) {
      setTrainStatus({ type: 'error', message: 'Failed to train model' })
    } finally {
      setIsTraining(false)
    }
  }

  const handleReset = async () => {
    if (!confirm('Are you sure you want to delete the trained model?')) return

    try {
      const response = await fetch('/api/ai/reset', { method: 'POST' })
      const data = await response.json()

      if (response.ok) {
        setTrainStatus({ type: 'success', message: 'Model reset successfully' })
        fetchModelInfo()
      } else {
        setTrainStatus({ type: 'error', message: data.error || 'Reset failed' })
      }
    } catch (error) {
      setTrainStatus({ type: 'error', message: 'Failed to reset model' })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">AI Model Administration</h1>
          <p className="text-slate-400">Train and manage your anomaly detection model</p>
        </div>

        {/* Status Alert */}
        {trainStatus.type && (
          <Alert className={`mb-6 ${trainStatus.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/50' : 'bg-red-500/10 border-red-500/50'}`}>
            <AlertDescription className="flex items-center gap-2">
              {trainStatus.type === 'success' ? (
                <CheckCircle className="h-4 w-4 text-emerald-400" />
              ) : (
                <XCircle className="h-4 w-4 text-red-400" />
              )}
              <span className={trainStatus.type === 'success' ? 'text-emerald-400' : 'text-red-400'}>
                {trainStatus.message}
              </span>
            </AlertDescription>
          </Alert>
        )}

        {/* Model Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white">Model Status</CardTitle>
            </CardHeader>
            <CardContent>
              {modelInfo ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className={`h-3 w-3 rounded-full ${modelInfo.exists ? 'bg-emerald-500' : 'bg-slate-600'}`} />
                    <span className="text-slate-300">{modelInfo.exists ? 'Active' : 'Not Trained'}</span>
                  </div>
                  {modelInfo.exists && (
                    <>
                      <div className="text-sm text-slate-400">Type: {modelInfo.type}</div>
                      <div className="text-sm text-slate-400">Estimators: {modelInfo.n_estimators}</div>
                      <div className="text-sm text-slate-400">Contamination: {modelInfo.contamination}</div>
                    </>
                  )}
                </div>
              ) : (
                <div className="text-slate-400">Loading...</div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white">Training Data</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-white">{modelInfo?.sample_count || 0}</div>
                <div className="text-sm text-slate-400">samples available</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-white">Last Trained</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-slate-300">
                {modelInfo?.last_trained || 'Never'}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Training Controls */}
        <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm mb-8">
          <CardHeader>
            <CardTitle className="text-white">Training Parameters</CardTitle>
            <CardDescription>Adjust model hyperparameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="text-sm text-slate-300 mb-2 block">
                Number of Estimators: {nEstimators}
              </label>
              <Slider
                value={[nEstimators]}
                onValueChange={(value) => setNEstimators(value[0])}
                min={50}
                max={300}
                step={10}
                className="w-full"
              />
              <p className="text-xs text-slate-500 mt-1">More estimators = better accuracy but slower training</p>
            </div>

            <div>
              <label className="text-sm text-slate-300 mb-2 block">
                Contamination: {contamination.toFixed(2)}
              </label>
              <Slider
                value={[contamination * 100]}
                onValueChange={(value) => setContamination(value[0] / 100)}
                min={1}
                max={50}
                step={1}
                className="w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Expected proportion of anomalies in the dataset</p>
            </div>

            <div>
              <label className="text-sm text-slate-300 mb-2 block">
                Random State: {randomState}
              </label>
              <Slider
                value={[randomState]}
                onValueChange={(value) => setRandomState(value[0])}
                min={0}
                max={1000}
                step={1}
                className="w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Seed for reproducibility</p>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4">
          <Button
            onClick={handleTrain}
            disabled={isTraining}
            className="bg-emerald-600 hover:bg-emerald-700 text-white"
            size="lg"
          >
            {isTraining ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Training...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                {modelInfo?.exists ? 'Retrain Model' : 'Train Model'}
              </>
            )}
          </Button>

          {modelInfo?.exists && (
            <Button
              onClick={handleReset}
              disabled={isTraining}
              variant="destructive"
              size="lg"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Reset Model
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
