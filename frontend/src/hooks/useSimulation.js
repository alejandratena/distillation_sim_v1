import { useState } from 'react'
import { runDistillationSimulation } from '../api/simulate'
import useFlowsheetStore from '../store/flowsheetStore'

export function useSimulation() {
  const [inputs, setInputs] = useState({
    feedMassFlow: '100',
    feedTemperature: '85',
    feedPressure: '101.3',
    distillateTemperature: '78',
    bottomsTemperature: '100',
    columnPressure: '101.3',
    waterFraction: '0.5',
    ethanolFraction: '0.5',
    waterToDistillate: '0.1',
    ethanolToDistillate: '0.9',
  })

  const setSimulationResult = useFlowsheetStore((s) => s.setSimulationResult)
  const setIsRunning = useFlowsheetStore((s) => s.setIsRunning)
  const setError = useFlowsheetStore((s) => s.setError)
  const isRunning = useFlowsheetStore((s) => s.isRunning)
  const simulationResult = useFlowsheetStore((s) => s.simulationResult)
  const error = useFlowsheetStore((s) => s.error)

  function updateInput(field, value) {
    setInputs((prev) => ({ ...prev, [field]: value }))
  }

  async function runSimulation() {
    setIsRunning(true)
    setError(null)
    try {
      const result = await runDistillationSimulation(inputs)
      setSimulationResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsRunning(false)
    }
  }

  return {
    inputs,
    updateInput,
    runSimulation,
    isRunning,
    simulationResult,
    error,
  }
}