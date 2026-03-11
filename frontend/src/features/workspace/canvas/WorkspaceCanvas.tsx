import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
// Save status: 'idle' | 'saving' | 'saved' | 'error'
type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'
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
import { ChevronDown, Layout, Plus, Workflow } from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import {
  addComponent,
  loadProject,
  setActiveWorkspaceTab,
  setSelectedComponentId,
  updateComponentGraph,
} from '../workspaceSlice'
import { SceneEditor } from '../scene/SceneEditor'
import { useGetProjectWithComponentsQuery, useSaveProjectComponentsMutation } from '@/lib/api/projectsApi'
import { NODE_CATEGORIES } from '@/types/nodes'
import { cn } from '@/lib/utils'

interface WorkspaceCanvasProps {
  projectId: string
}

export function WorkspaceCanvas({ projectId }: WorkspaceCanvasProps) {
  const dispatch = useAppDispatch()
  const { activeWorkspaceTab, currentProject, components, selectedComponentId } =
    useAppSelector((state) => state.workspace)
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle')
  const dropdownRef = useRef<HTMLDivElement>(null)
  const hasLoadedRef = useRef(false)
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const savedStatusTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const selectedComponent = useMemo(
    () => components.find((c) => c.id === selectedComponentId) ?? null,
    [components, selectedComponentId]
  )
  const nodes = selectedComponent?.nodes ?? []
  const edges = selectedComponent?.edges ?? []

  // Fetch real project data from the API
  const { data: projectData } = useGetProjectWithComponentsQuery(projectId, {
    skip: !projectId,
  })
  const [saveComponents] = useSaveProjectComponentsMutation()

  // Load project into Redux when API data arrives
  useEffect(() => {
    if (!projectData) return
    dispatch(loadProject(projectData))
    hasLoadedRef.current = true
  }, [projectData, dispatch])

  // Debounced auto-save — fires 2s after any change to the component list
  useEffect(() => {
    if (!hasLoadedRef.current || !currentProject) return

    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)

    saveTimerRef.current = setTimeout(async () => {
      setSaveStatus('saving')
      try {
        await saveComponents({
          projectId: currentProject.id,
          components: components.map((c, i) => ({
            id: c.id,
            name: c.name,
            description: c.description,
            sort_order: i,
            nodes: c.nodes,
            edges: c.edges,
            scene_root: c.sceneRoot,
          })),
        }).unwrap()
        setSaveStatus('saved')
        if (savedStatusTimerRef.current) clearTimeout(savedStatusTimerRef.current)
        savedStatusTimerRef.current = setTimeout(() => setSaveStatus('idle'), 2000)
      } catch {
        setSaveStatus('error')
      }
    }, 2000)

    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    }
  }, [components, currentProject, saveComponents])

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
    <div className="flex flex-col h-full bg-cream-bg">
      {/* Top Toolbar */}
      <div className="z-10 p-4 bg-white/80 backdrop-blur-sm border-b-2 border-wood-brown">
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
                <div className="flex items-center justify-between px-3 py-1.5 border-b border-border">
                  <span className="text-xs font-medium text-muted-foreground">Components</span>
                  <button
                    className="text-muted-foreground hover:text-foreground transition-colors rounded p-0.5 hover:bg-secondary"
                    title="Add component"
                    onClick={(e) => {
                      e.stopPropagation()
                      const id = `comp-${Date.now()}`
                      const name = `Component ${components.length + 1}`
                      dispatch(addComponent({ id, name }))
                    }}
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
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
            {/* Node / Scene tab toggle */}
            <div className="flex rounded-lg border border-border p-0.5 bg-muted/50">
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  'gap-1.5 rounded-md',
                  activeWorkspaceTab === 'node' &&
                    'bg-background text-foreground shadow-sm'
                )}
                onClick={() => dispatch(setActiveWorkspaceTab('node'))}
              >
                <Workflow className="w-4 h-4" />
                Node
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className={cn(
                  'gap-1.5 rounded-md',
                  activeWorkspaceTab === 'scene' &&
                    'bg-background text-foreground shadow-sm'
                )}
                onClick={() => dispatch(setActiveWorkspaceTab('scene'))}
              >
                <Layout className="w-4 h-4" />
                Scene
              </Button>
            </div>
          </div>

          {/* Save status indicator */}
          {saveStatus !== 'idle' && (
            <span
              className={cn(
                'text-xs ml-auto',
                saveStatus === 'saving' && 'text-muted-foreground',
                saveStatus === 'saved' && 'text-green-600',
                saveStatus === 'error' && 'text-destructive',
              )}
            >
              {saveStatus === 'saving' && 'Saving…'}
              {saveStatus === 'saved' && 'Saved'}
              {saveStatus === 'error' && 'Save failed'}
            </span>
          )}
        </div>
      </div>

      {/* Node tab: React Flow | Scene tab: Scene editor */}
      <div className="flex-1 relative">
        {selectedComponentId ? (
          activeWorkspaceTab === 'node' ? (
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
            <SceneEditor />
          )
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p className="text-sm">Select a component from the dropdown</p>
          </div>
        )}
      </div>
    </div>
  )
}
