import { useCallback, useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  type Connection,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { CustomNode } from '../nodes/CustomNode'
import { Button } from '@/components/ui/button'
import { ChevronDown, ZoomIn, ZoomOut } from 'lucide-react'

interface WorkspaceCanvasProps {
  projectId: string
}

export function WorkspaceCanvas({ }: WorkspaceCanvasProps) {
  const [nodes, , onNodesChange] = useNodesState<any>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([])

  const nodeTypes = useMemo(
    () => ({
      custom: CustomNode as any,
    }),
    []
  )

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds: any) => addEdge({ ...params, type: 'smoothstep' }, eds))
    },
    [setEdges]
  )

  const edgeOptions = {
    type: 'smoothstep',
    style: { stroke: '#8B7355', strokeWidth: 2 },
  }

  return (
    <div className="relative h-full bg-cream-bg">
      {/* Top Toolbar */}
      <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-white/80 backdrop-blur-sm border-b-2 border-wood-brown">
        <div className="flex items-center justify-between">
          <Button variant="outline" className="flex items-center gap-2">
            <span className="font-heading">Dragon Legends TCG</span>
            <ChevronDown className="w-4 h-4" />
          </Button>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <ZoomOut className="w-4 h-4" />
            </Button>
            <span className="text-sm text-text-secondary">100%</span>
            <Button variant="outline" size="sm">
              <ZoomIn className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* React Flow Canvas */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={edgeOptions}
        fitView
        className="wood-texture"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#8B7355"
        />
        <Controls className="bg-white/80 border-wood-brown" />
        <MiniMap
          className="bg-white/80 border-2 border-wood-brown"
          nodeColor={(node) => {
            const data = node.data as any
            return data.category ? NODE_CATEGORIES[data.category as keyof typeof NODE_CATEGORIES]?.color || '#ccc' : '#ccc'
          }}
        />
      </ReactFlow>
    </div>
  )
}

// Import NODE_CATEGORIES for MiniMap color
import { NODE_CATEGORIES } from '@/types/nodes'
