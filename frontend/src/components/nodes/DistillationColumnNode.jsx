import { Handle, Position } from '@xyflow/react'
import { Columns2 } from 'lucide-react'

export default function DistillationColumnNode({ data, selected }) {
  return (
    <div
      className="rounded-lg flex flex-col items-center relative"
      style={{
        width: 80,
        backgroundColor: 'var(--bg-panel)',
        border: `1.5px solid ${selected ? 'var(--accent)' : 'var(--border)'}`,
        boxShadow: selected ? '0 0 0 2px var(--accent-muted)' : 'none',
      }}
    >
      {/* Distillate outlet label — top right */}
      <span
        className="absolute text-[9px] right-[-38px] top-[14px]"
        style={{ color: 'var(--text-muted)' }}
      >
        Distillate
      </span>

      {/* Bottoms outlet label — bottom right */}
      <span
        className="absolute text-[9px] right-[-36px] bottom-[14px]"
        style={{ color: 'var(--text-muted)' }}
      >
        Bottoms
      </span>

      {/* Top section — condenser zone */}
      <div
        className="w-full flex items-center justify-center pt-3 pb-2 rounded-t-lg"
        style={{ borderBottom: '1px dashed var(--border)' }}
      >
        <Columns2 size={16} style={{ color: 'var(--accent)' }} />
      </div>

      {/* Tray section — middle */}
      <div className="w-full flex flex-col gap-0 py-1">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="w-full"
            style={{
              height: 10,
              borderBottom: '1px solid var(--border)',
              opacity: 0.4,
            }}
          />
        ))}
      </div>

      {/* Bottom section — reboiler zone */}
      <div
        className="w-full flex items-center justify-center pt-2 pb-3 rounded-b-lg"
        style={{ borderTop: '1px dashed var(--border)' }}
      >
        <span className="text-[9px] font-semibold tracking-wide" style={{ color: 'var(--text-muted)' }}>
          {data.label ?? 'Dist. Column'}
        </span>
      </div>

      {/* Feed inlet — left, vertically centered */}
      <Handle
        id="feed"
        type="target"
        position={Position.Left}
        style={{
          top: '50%',
          background: 'var(--text-muted)',
          width: 8,
          height: 8,
          border: 'none',
        }}
      />

      {/* Distillate outlet — right, upper */}
      <Handle
        id="distillate"
        type="source"
        position={Position.Right}
        style={{
          top: '18%',
          background: 'var(--accent)',
          width: 8,
          height: 8,
          border: 'none',
        }}
      />

      {/* Bottoms outlet — right, lower */}
      <Handle
        id="bottoms"
        type="source"
        position={Position.Right}
        style={{
          top: '82%',
          background: 'var(--accent)',
          width: 8,
          height: 8,
          border: 'none',
        }}
      />
    </div>
  )
}