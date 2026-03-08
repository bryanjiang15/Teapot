import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { Node, Edge } from '@xyflow/react'
import type { ProjectComponent, ProjectWithComponents } from '@/types/project'
import { NODE_TEMPLATES } from '@/lib/nodeRegistry'

interface WorkspaceState {
  nodes: Node[]
  edges: Edge[]
  selectedNodes: string[]
  selectedTool: string
  isAiPanelOpen: boolean
  aiPanelWidth: number
  /** Current project (id + name) for the workspace. */
  currentProject: { id: string; name: string } | null
  /** Components for the current project; each has its own nodes/edges. */
  components: ProjectComponent[]
  /** ID of the component whose graph is shown on the canvas. */
  selectedComponentId: string | null
}

const initialState: WorkspaceState = {
  nodes: [],
  edges: [],
  selectedNodes: [],
  selectedTool: 'select',
  isAiPanelOpen: true,
  aiPanelWidth: 300,
  currentProject: null,
  components: [],
  selectedComponentId: null,
}

const workspaceSlice = createSlice({
  name: 'workspace',
  initialState,
  reducers: {
    setNodes: (state, action: PayloadAction<Node[]>) => {
      state.nodes = action.payload
    },
    setEdges: (state, action: PayloadAction<Edge[]>) => {
      state.edges = action.payload
    },
    addNode: (state, action: PayloadAction<Node>) => {
      state.nodes.push(action.payload)
    },
    removeNode: (state, action: PayloadAction<string>) => {
      state.nodes = state.nodes.filter(node => node.id !== action.payload)
      state.edges = state.edges.filter(
        edge => edge.source !== action.payload && edge.target !== action.payload
      )
    },
    addEdge: (state, action: PayloadAction<Edge>) => {
      state.edges.push(action.payload)
    },
    setSelectedNodes: (state, action: PayloadAction<string[]>) => {
      state.selectedNodes = action.payload
    },
    setSelectedTool: (state, action: PayloadAction<string>) => {
      state.selectedTool = action.payload
    },
    toggleAiPanel: (state) => {
      state.isAiPanelOpen = !state.isAiPanelOpen
    },
    setAiPanelWidth: (state, action: PayloadAction<number>) => {
      state.aiPanelWidth = action.payload
    },
    clearWorkspace: (state) => {
      state.nodes = []
      state.edges = []
      state.selectedNodes = []
    },
    setCurrentProject: (state, action: PayloadAction<{ id: string; name: string } | null>) => {
      state.currentProject = action.payload
    },
    setComponents: (state, action: PayloadAction<ProjectComponent[]>) => {
      state.components = action.payload
    },
    setSelectedComponentId: (state, action: PayloadAction<string | null>) => {
      state.selectedComponentId = action.payload
    },
    /** Update nodes and edges for the component with the given id. */
    updateComponentGraph: (
      state,
      action: PayloadAction<{ componentId: string; nodes: Node[]; edges: Edge[] }>
    ) => {
      const comp = state.components.find((c) => c.id === action.payload.componentId)
      if (comp) {
        comp.nodes = action.payload.nodes
        comp.edges = action.payload.edges
      }
    },
    /** Load project and its components; selects first component by default. */
    loadProject: (state, action: PayloadAction<ProjectWithComponents>) => {
      const project = action.payload
      state.currentProject = { id: project.id, name: project.name }
      state.components = project.components
      state.selectedComponentId = project.components[0]?.id ?? null
    },
    /** Add a node to a component's graph from a template. */
    addNodeToComponent: (
      state,
      action: PayloadAction<{ componentId: string; templateId: string }>
    ) => {
      const { componentId, templateId } = action.payload
      const template = NODE_TEMPLATES[templateId] ?? NODE_TEMPLATES['event-game-start']
      const comp = state.components.find((c) => c.id === componentId)
      if (!comp) return
      const nodeId = `node-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
      const count = comp.nodes.length
      const newNode: Node = {
        id: nodeId,
        type: 'custom',
        position: {
          x: 150 + (count % 4) * 220,
          y: 100 + Math.floor(count / 4) * 120,
        },
        data: { ...template },
      }
      comp.nodes = [...comp.nodes, newNode]
    },
  },
})

export const {
  setNodes,
  setEdges,
  addNode,
  removeNode,
  addEdge,
  setSelectedNodes,
  setSelectedTool,
  toggleAiPanel,
  setAiPanelWidth,
  clearWorkspace,
  setCurrentProject,
  setComponents,
  setSelectedComponentId,
  updateComponentGraph,
  loadProject,
  addNodeToComponent,
} = workspaceSlice.actions

export default workspaceSlice.reducer
