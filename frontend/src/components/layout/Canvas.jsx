import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import nodeTypes from '../nodes/index.js'

export default function Canvas() {
  return (
    <main className="flex-1 overflow-hidden"
      style={{ backgroundColor: 'var(--bg-primary)' }}>
      <ReactFlow
        nodeTypes={nodeTypes}
        fitView
        style={{ width: '100%', height: '100%' }}
      >
        <Background
          color="var(--border)"
          gap={24}
          size={1}
        />
        <Controls />
        <MiniMap
          style={{ backgroundColor: 'var(--bg-panel)' }}
        />
      </ReactFlow>
    </main>
  )
}