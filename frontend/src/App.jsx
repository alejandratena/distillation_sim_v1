import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [result, setResult] = useState(null)
  const [feedMassFlow, setFeedMassFlow] = useState(100)
  const [feedTemperature, setFeedTemperature] = useState("85")

  async function runSimulation() {
    const response = await fetch("http://127.0.0.1:8000/simulate/distillation", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
          feed_stream: {
            temperature: Number(feedTemperature),
            pressure: 101.3,
            mass_flow: feedMassFlow,
            composition: {
              Water: 0.5,
              Ethanol: 0.5
            }
          },
          distillate_split: {
            Water: 0.1,
            Ethanol: 0.9
          },
          bottoms_split: {
            Water: 0.9,
            Ethanol: 0.1
          },
          distillate_temperature: 78.0,
          bottoms_temperature: 100.0,
          pressure: 101.3
        })
      })

        const data = await response.json()
        console.log("Sending temperature:", Number(feedTemperature))
        setResult(data)
  }

  return (
  <div style={{ padding: "2rem", color: "white" }}>
    <h1>Equilibria</h1>

    <div style={{ marginTop: "1rem" }}>
      <label>Feed Mass Flow: </label>
      <input
        type="number"
        value={feedMassFlow}
        onFocus={(e) => e.target.select()}
        onChange={(e) => setFeedMassFlow(parseFloat(e.target.value) || 0)}
        min="0"
        step="1"
      />
    </div>

    <button onClick={runSimulation}>
      Run Simulation
    </button>

    <div style={{ marginTop: "1rem" }}>
      <label>Feed Temperature: </label>
      <input
        type="text"
        inputMode="numeric"
        value={feedTemperature}
        onFocus={(e) => e.target.select()}
        onChange={(e) => setFeedTemperature(parseFloat(e.target.value) || 0)}
        step="1"
      />
    </div>

    {result && (
      <div style={{ marginTop: "2rem" }}>
        <h2>Results</h2>

        <p><strong>Message:</strong> {result.message}</p>

        <h3>Distillate</h3>
        <p>Flow: {result.distillate.mass_flow}</p>
        <p>Temperature: {result.distillate.temperature}</p>

        <h3>Bottoms</h3>
        <p>Flow: {result.bottoms.mass_flow}</p>
        <p>Temperature: {result.bottoms.temperature}</p>
      </div>
    )}
  </div>
)
}

export default App
