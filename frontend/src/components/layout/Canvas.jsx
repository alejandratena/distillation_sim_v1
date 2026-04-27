import { useCallback, useRef } from 'react'
import { ReactFlow, ReactFlowProvider, Background, Controls, MiniMap, useReactFlow } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import nodeTypes from '../nodes/index.js'
import StreamEdge from '../edges/StreamEdge'
import { useFlowsheetStore } from '../../store/flowsheetStore'
import { useFlowsheet } from '../../hooks/useFlowsheet'
import unitOperations from '../../constants/unitOperations'

const edgeTypes = { stream: StreamEdge }

function FlowCanvas() {
  const reactFlowWrapper = useRef(null)
  const { screenToFlowPosition } = useReactFlow()
  const { onNodeClick } = useFlowsheet()

  const nodes = useFlowsheetStore((s) => s.nodes)
  const edges = useFlowsheetStore((s) => s.edges)
  const onNodesChange = useFlowsheetStore((s) => s.onNodesChange)
  const onEdgesChange = useFlowsheetStore((s) => s.onEdgesChange)
  const onConnect = useFlowsheetStore((s) => s.onConnect)
  const addNode = useFlowsheetStore((s) => s.addNode)

  const onDragOver = useCallback((e) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    const nodeType = e.dataTransfer.getData('nodeType')
    if (!nodeType) return

    const op = unitOperations.find((o) => o.nodeType === nodeType)
    const position = screenToFlowPosition({ x: e.clientX, y: e.clientY })

    const newNode = {
      id: crypto.randomUUID(),
      type: nodeType,
      position,
      data: { label: op?.label ?? nodeType },
    }

    addNode(newNode)
  }, [screenToFlowPosition, addNode])

  return (
    <div ref={reactFlowWrapper} style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        style={{ width: '100%', height: '100%' }}
      >
        <Background color="var(--border)" gap={24} size={1} />
        <Controls />
        <MiniMap style={{ backgroundColor: 'var(--bg-panel)' }} />
      </ReactFlow>
    </div>
  )
}

export default function Canvas() {
  return (
    <main
      className="flex-1 overflow-hidden"
      style={{ backgroundColor: 'var(--bg-primary)', height: '100%' }}
    >
      <ReactFlowProvider>
        <div style={{ width: '100%', height: '100%' }}>
          <FlowCanvas />
        </div>
      </ReactFlowProvider>
    </main>
  )
}