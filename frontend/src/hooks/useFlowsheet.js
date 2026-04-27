import { useFlowsheetStore } from '../store/flowsheetStore'

export function useFlowsheet() {
  const nodes = useFlowsheetStore((s) => s.nodes)
  const selectedNodeId = useFlowsheetStore((s) => s.selectedNodeId)
  const setSelectedNodeId = useFlowsheetStore((s) => s.setSelectedNodeId)

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) ?? null

  function onNodeClick(_event, node) {
    setSelectedNodeId(node.id)
  }

  function clearSelection() {
    setSelectedNodeId(null)
  }

  return { selectedNode, onNodeClick, clearSelection }
}