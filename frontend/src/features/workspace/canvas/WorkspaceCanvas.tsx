import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  type Connection,
  type NodeChange,
  type EdgeChange,
  BackgroundVariant,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { CustomNode } from '../nodes/CustomNode'
import { Button } from '@/components/ui/button'
import { ChevronDown, ZoomIn, ZoomOut } from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import {
  loadProject,
  setSelectedComponentId,
  updateComponentGraph,
} from '../workspaceSlice'
import { getMockProject } from '../mockProjectData'
import { NODE_CATEGORIES } from '@/types/nodes'
import { cn } from '@/lib/utils'

interface WorkspaceCanvasProps {
  projectId: string
}

export function WorkspaceCanvas({ projectId }: WorkspaceCanvasProps) {
  const dispatch = useAppDispatch()
  const { currentProject, components, selectedComponentId } = useAppSelector(
    (state) => state.workspace
  )
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const selectedComponent = useMemo(
    () => components.find((c) => c.id === selectedComponentId) ?? null,
    [components, selectedComponentId]
  )
  const nodes = selectedComponent?.nodes ?? []
  const edges = selectedComponent?.edges ?? []

  // Load mock project when projectId is available
  useEffect(() => {
    if (!projectId) return
    const project = getMockProject(projectId)
    if (project) {
      dispatch(loadProject(project))
    }
  }, [projectId, dispatch])

  // Click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [dropdownOpen])

  const nodeTypes = useMemo(
    () => ({
      custom: CustomNode as React.ComponentType<any>,
    }),
    []
  )

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      if (!selectedComponentId) return
      const nextNodes = applyNodeChanges(changes, nodes)
      dispatch(
        updateComponentGraph({
          componentId: selectedComponentId,
          nodes: nextNodes,
          edges,
        })
      )
    },
    [selectedComponentId, nodes, edges, dispatch]
  )

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      if (!selectedComponentId) return
      const nextEdges = applyEdgeChanges(changes, edges)
      dispatch(
        updateComponentGraph({
          componentId: selectedComponentId,
          nodes,
          edges: nextEdges,
        })
      )
    },
    [selectedComponentId, nodes, edges, dispatch]
  )

  const onConnect = useCallback(
    (params: Connection) => {
      if (!selectedComponentId) return
      const nextEdges = addEdge({ ...params, type: 'smoothstep' }, edges)
      dispatch(
        updateComponentGraph({
          componentId: selectedComponentId,
          nodes,
          edges: nextEdges,
        })
      )
    },
    [selectedComponentId, nodes, edges, dispatch]
  )

  const edgeOptions = useMemo(
    () => ({
      type: 'smoothstep' as const,
      style: { stroke: '#8B7355', strokeWidth: 2 },
    }),
    []
  )

  return (
    <div className="relative h-full bg-cream-bg">
      {/* Top Toolbar */}
      <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-white/80 backdrop-blur-sm border-b-2 border-wood-brown">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative" ref={dropdownRef}>
            <Button
              variant="outline"
              className="flex items-center gap-2 min-w-[180px] justify-between"
              onClick={() => setDropdownOpen((o) => !o)}
              aria-expanded={dropdownOpen}
              aria-haspopup="listbox"
            >
              <span className="font-heading truncate">
                {currentProject?.name ?? 'Project'}
              </span>
              <ChevronDown
                className={cn('w-4 h-4 shrink-0 transition-transform', dropdownOpen && 'rotate-180')}
              />
            </Button>
            {dropdownOpen && (
              <div
                className="absolute top-full left-0 mt-1 py-1 min-w-[200px] bg-card border border-card-border rounded-lg shadow-lg z-20"
                role="listbox"
              >
                <div className="px-3 py-1.5 text-xs font-medium text-muted-foreground border-b border-border">
                  Components
                </div>
                {components.length === 0 ? (
                  <div className="px-3 py-4 text-sm text-muted-foreground">
                    No components
                  </div>
                ) : (
                  components.map((c) => (
                    <button
                      key={c.id}
                      role="option"
                      aria-selected={selectedComponentId === c.id}
                      className={cn(
                        'w-full text-left px-3 py-2 text-sm transition-colors',
                        selectedComponentId === c.id
                          ? 'bg-primary/10 text-primary font-medium'
                          : 'text-card-foreground hover:bg-secondary'
                      )}
                      onClick={() => {
                        dispatch(setSelectedComponentId(c.id))
                        setDropdownOpen(false)
                      }}
                    >
                      {c.name}
                    </button>
                  ))
                )}
              </div>
            )}
            </div>
            {selectedComponent && (
              <span className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">{selectedComponent.name}</span>
              </span>
            )}
          </div>

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
      {selectedComponentId ? (
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
              const data = node.data as { category?: keyof typeof NODE_CATEGORIES }
              return data?.category
                ? NODE_CATEGORIES[data.category]?.color ?? '#ccc'
                : '#ccc'
            }}
          />
        </ReactFlow>
      ) : (
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <p className="text-sm">Select a component from the dropdown</p>
        </div>
      )}
    </div>
  )
}
