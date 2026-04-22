import { useSimulation } from '../../hooks/useSimulation'

export default function PropertyPanel() {
  const { inputs, updateInput, runSimulation, isRunning, simulationResult, error } = useSimulation()

  return (
    <aside className="flex flex-col w-72 shrink-0 border-l overflow-y-auto"
      style={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border)' }}>

      {/* Empty State */}
      <div className="p-4 border-b" style={{ borderColor: 'var(--border)' }}>
        <p className="text-xs font-semibold uppercase tracking-widest"
          style={{ color: 'var(--text-muted)' }}>
          Properties
        </p>
        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
          Select a unit operation
        </p>
      </div>

      {/* Operating Conditions */}
      <div className="p-4 border-b" style={{ borderColor: 'var(--border)' }}>
        <p className="text-xs font-semibold uppercase tracking-widest mb-3"
          style={{ color: 'var(--text-muted)' }}>
          Operating Conditions
        </p>
        {[
          { label: 'Feed Mass Flow', field: 'feedMassFlow' },
          { label: 'Feed Temperature', field: 'feedTemperature' },
          { label: 'Feed Pressure', field: 'feedPressure' },
          { label: 'Distillate Temp', field: 'distillateTemperature' },
          { label: 'Bottoms Temp', field: 'bottomsTemperature' },
          { label: 'Column Pressure', field: 'columnPressure' },
          { label: 'Water Fraction', field: 'waterFraction' },
          { label: 'Ethanol Fraction', field: 'ethanolFraction' },
          { label: 'Water → Distillate', field: 'waterToDistillate' },
          { label: 'Ethanol → Distillate', field: 'ethanolToDistillate' },
        ].map(({ label, field }) => (
          <div key={field} className="flex justify-between items-center mb-2">
            <label className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              {label}
            </label>
            <input
              type="text"
              inputMode="decimal"
              value={inputs[field]}
              onFocus={(e) => e.target.select()}
              onChange={(e) => updateInput(field, e.target.value)}
              className="w-20 text-xs text-right px-2 py-1 rounded"
              style={{
                backgroundColor: 'var(--bg-surface)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border)',
              }}
            />
          </div>
        ))}
      </div>

      {/* Run Button */}
      <div className="p-4 border-b" style={{ borderColor: 'var(--border)' }}>
        <button
          onClick={runSimulation}
          disabled={isRunning}
          className="w-full py-2 text-xs font-semibold uppercase tracking-widest rounded"
          style={{
            backgroundColor: isRunning ? 'var(--text-muted)' : 'var(--accent)',
            color: 'var(--bg-primary)',
            cursor: isRunning ? 'not-allowed' : 'pointer',
          }}
        >
          {isRunning ? 'Running...' : 'Run Simulation'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 border-b" style={{ borderColor: 'var(--border)' }}>
          <p className="text-xs" style={{ color: 'var(--error)' }}>{error}</p>
        </div>
      )}

      {/* Raw Results */}
      {simulationResult && (
        <div className="p-4">
          <p className="text-xs font-semibold uppercase tracking-widest mb-2"
            style={{ color: 'var(--text-muted)' }}>
            Results
          </p>
          <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
            {simulationResult.message}
          </p>
          <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
            Distillate Flow: {simulationResult.distillate?.mass_flow}
          </p>
          <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
            Distillate Temp: {simulationResult.distillate?.temperature}
          </p>
          <p className="text-xs mb-1" style={{ color: 'var(--text-secondary)' }}>
            Bottoms Flow: {simulationResult.bottoms?.mass_flow}
          </p>
          <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
            Bottoms Temp: {simulationResult.bottoms?.temperature}
          </p>
        </div>
      )}

    </aside>
  )
}