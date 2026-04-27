import unitOperations from '../../constants/unitOperations'

export default function LibraryPanel() {
  function handleDragStart(e, op) {
    e.dataTransfer.setData('nodeType', op.nodeType)
    e.dataTransfer.effectAllowed = 'move'
  }

  return (
    <aside
      className="flex flex-col w-56 shrink-0 border-r overflow-y-auto"
      style={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border)' }}
    >
      {/* Unit Operations */}
      <div className="p-3 border-b" style={{ borderColor: 'var(--border)' }}>
        <p
          className="text-xs font-semibold uppercase tracking-widest mb-2"
          style={{ color: 'var(--text-muted)' }}
        >
          Unit Operations
        </p>

        {unitOperations.map((op) => {
          const Icon = op.icon
          return (
            <div
              key={op.id}
              draggable
              onDragStart={(e) => handleDragStart(e, op)}
              className="flex items-center gap-2 text-xs py-1.5 px-2 rounded cursor-grab active:cursor-grabbing"
              style={{ color: 'var(--text-secondary)' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
                e.currentTarget.style.color = 'var(--text-primary)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.color = 'var(--text-secondary)'
              }}
            >
              <Icon size={14} style={{ color: 'var(--accent)', flexShrink: 0 }} />
              {op.label}
            </div>
          )
        })}
      </div>

      {/* Projects */}
      <div className="p-3 border-b" style={{ borderColor: 'var(--border)' }}>
        <p
          className="text-xs font-semibold uppercase tracking-widest mb-2"
          style={{ color: 'var(--text-muted)' }}
        >
          Projects
        </p>
        <div className="text-xs py-1" style={{ color: 'var(--text-muted)' }}>
          No projects yet
        </div>
      </div>

      {/* Simulation Summary */}
      <div className="p-3">
        <p
          className="text-xs font-semibold uppercase tracking-widest mb-2"
          style={{ color: 'var(--text-muted)' }}
        >
          Simulation Summary
        </p>
        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
          Run a simulation to see results
        </div>
      </div>
    </aside>
  )
}