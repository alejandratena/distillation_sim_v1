import { Handle, Position } from '@xyflow/react'
import { Cylinder } from 'lucide-react'

export default function FeedTankNode({ data, selected }) {
  return (
    <div
      className="rounded-lg px-4 py-3 flex flex-col items-center gap-1.5 min-w-[100px]"
      style={{
        backgroundColor: 'var(--bg-panel)',
        border: `1.5px solid ${selected ? 'var(--accent)' : 'var(--border)'}`,
        boxShadow: selected ? '0 0 0 2px var(--accent-muted)' : 'none',
      }}
    >
      <Cylinder size={20} style={{ color: 'var(--accent)' }} />
      <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
        {data.label ?? 'Feed Tank'}
      </span>

      {/* Outlet — right side */}
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: 'var(--accent)', width: 8, height: 8, border: 'none' }}
      />
    </div>
  )
}