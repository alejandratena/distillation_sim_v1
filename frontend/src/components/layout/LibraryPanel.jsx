export default function LibraryPanel() {
  return (
    <aside className="flex flex-col w-56 shrink-0 border-r overflow-y-auto"
      style={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border)' }}>

      {/* Unit Operations */}
      <div className="p-3 border-b" style={{ borderColor: 'var(--border)' }}>
        <p className="text-xs font-semibold uppercase tracking-widest mb-2"
          style={{ color: 'var(--text-muted)' }}>
          Unit Operations
        </p>
        {['Feed Tank', 'Distillation Column', 'Condenser', 'Reboiler', 'Heat Exchanger'].map((op) => (
          <div key={op} className="text-xs py-1.5 px-2 rounded cursor-pointer"
            style={{ color: 'var(--text-secondary)' }}>
            {op}
          </div>
        ))}
      </div>

      {/* Projects */}
      <div className="p-3 border-b" style={{ borderColor: 'var(--border)' }}>
        <p className="text-xs font-semibold uppercase tracking-widest mb-2"
          style={{ color: 'var(--text-muted)' }}>
          Projects
        </p>
        <div className="text-xs py-1" style={{ color: 'var(--text-muted)' }}>
          No projects yet
        </div>
      </div>

      {/* Simulation Summary */}
      <div className="p-3">
        <p className="text-xs font-semibold uppercase tracking-widest mb-2"
          style={{ color: 'var(--text-muted)' }}>
          Simulation Summary
        </p>
        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
          Run a simulation to see results
        </div>
      </div>

    </aside>
  )
}