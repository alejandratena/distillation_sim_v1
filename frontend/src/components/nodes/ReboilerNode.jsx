import { Handle, Position } from '@xyflow/react'
import { Flame } from 'lucide-react'

export default function ReboilerNode({ data, selected }) {
  return (
    <div
      className="rounded-lg px-4 py-3 flex flex-col items-center gap-1.5 min-w-[100px]"
      style={{
        backgroundColor: 'var(--bg-panel)',
        border: `1.5px solid ${selected ? 'var(--accent)' : 'var(--border)'}`,
        boxShadow: selected ? '0 0 0 2px var(--accent-muted)' : 'none',
      }}
    >
      <Flame size={20} style={{ color: 'var(--accent)' }} />
      <span className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
        {data.label ?? 'Reboiler'}
      </span>
      <Handle type="target" position={Position.Left}
        style={{ background: 'var(--text-muted)', width: 8, height: 8, border: 'none' }} />
      <Handle type="source" position={Position.Right}
        style={{ background: 'var(--accent)', width: 8, height: 8, border: 'none' }} />
    </div>
  )
}