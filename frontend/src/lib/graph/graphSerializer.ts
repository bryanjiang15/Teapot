import type { Node, Edge } from '@xyflow/react'

/**
 * Serializes React Flow graph to TeapotEngine-compatible JSON format
 */
export function serializeGraphToEngine(nodes: Node[], edges: Edge[]): any {
  const serialized: any = {
    nodes: [],
    connections: [],
  }

  // Serialize nodes
  nodes.forEach((node) => {
    serialized.nodes.push({
      id: node.id,
      type: node.type,
      data: node.data,
      position: node.position,
    })
  })

  // Serialize edges/connections
  edges.forEach((edge) => {
    serialized.connections.push({
      id: edge.id,
      source: edge.source,
      sourceHandle: edge.sourceHandle,
      target: edge.target,
      targetHandle: edge.targetHandle,
    })
  })

  return serialized
}

/**
 * Deserializes TeapotEngine JSON to React Flow graph
 */
export function deserializeGraphFromEngine(data: any): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = []
  const edges: Edge[] = []

  // Deserialize nodes
  if (data.nodes) {
    data.nodes.forEach((nodeData: any) => {
      nodes.push({
        id: nodeData.id,
        type: nodeData.type || 'custom',
        position: nodeData.position || { x: 0, y: 0 },
        data: nodeData.data,
      })
    })
  }

  // Deserialize connections
  if (data.connections) {
    data.connections.forEach((conn: any) => {
      edges.push({
        id: conn.id,
        source: conn.source,
        sourceHandle: conn.sourceHandle,
        target: conn.target,
        targetHandle: conn.targetHandle,
        type: 'smoothstep',
      })
    })
  }

  return { nodes, edges }
}

/**
 * Validates that connections are type-safe
 */
export function validateConnection(
  sourceNode: Node,
  sourceHandle: string,
  targetNode: Node,
  targetHandle: string
): boolean {
  // Get port types from node data
  const nodeData = sourceNode.data as any
  const targetData = targetNode.data as any
  const sourcePort = nodeData.outputs?.find((o: any) => o.id === sourceHandle)
  const targetPort = targetData.inputs?.find((i: any) => i.id === targetHandle)

  if (!sourcePort || !targetPort) return false

  // Exec pins can only connect to exec pins
  if (sourcePort.type === 'exec') {
    return targetPort.type === 'exec'
  }

  // Data pins can connect to compatible types
  return sourcePort.type === targetPort.type || targetPort.type === 'object'
}
