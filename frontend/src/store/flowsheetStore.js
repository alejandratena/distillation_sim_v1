import { create } from 'zustand'
import { applyNodeChanges, applyEdgeChanges, addEdge } from '@xyflow/react'

const useFlowsheetStore = create((set) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  simulationResult: null,
  mode: 'academic',
  complexityLevel: 'foundational',
  isRunning: false,
  error: null,
  instructorLock: {
    enabled: false,
    maxLevel: 'foundational',
  },

  // React Flow handlers
  onNodesChange: (changes) =>
    set((state) => ({ nodes: applyNodeChanges(changes, state.nodes) })),

  onEdgesChange: (changes) =>
    set((state) => ({ edges: applyEdgeChanges(changes, state.edges) })),

  onConnect: (connection) =>
  set((state) => ({
    edges: addEdge({ ...connection, type: 'stream' }, state.edges),
  })),

  addNode: (node) =>
    set((state) => ({ nodes: [...state.nodes, node] })),

  // Setters
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setSimulationResult: (result) => set({ simulationResult: result }),
  setMode: (mode) => set({ mode }),
  setComplexityLevel: (level) => set({ complexityLevel: level }),
  setIsRunning: (isRunning) => set({ isRunning }),
  setError: (error) => set({ error }),
}))

export { useFlowsheetStore }
export default useFlowsheetStore