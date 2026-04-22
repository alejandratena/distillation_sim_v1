import { create } from 'zustand'

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
    maxLevel: 'foundational'
  },

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setSimulationResult: (result) => set({ simulationResult: result }),
  setMode: (mode) => set({ mode }),
  setComplexityLevel: (level) => set({ complexityLevel: level }),
  setIsRunning: (isRunning) => set({ isRunning }),
  setError: (error) => set({ error }),
}))

export default useFlowsheetStore