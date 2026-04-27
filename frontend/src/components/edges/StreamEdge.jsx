import { BaseEdge, EdgeLabelRenderer, getStraightPath } from '@xyflow/react'

export default function StreamEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  data,
}) {
  const [edgePath, labelX, labelY] = getStraightPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
  })

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: 'var(--accent)',
          strokeWidth: 2,
          strokeDasharray: 'none',
        }}
      />
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
              fontSize: 9,
              padding: '2px 6px',
              borderRadius: 4,
              backgroundColor: 'var(--bg-panel)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border)',
              pointerEvents: 'none',
            }}
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  )
}