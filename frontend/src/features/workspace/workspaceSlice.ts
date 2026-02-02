import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { Node, Edge } from '@xyflow/react'

interface WorkspaceState {
  nodes: Node[]
  edges: Edge[]
  selectedNodes: string[]
  selectedTool: string
  isAiPanelOpen: boolean
  aiPanelWidth: number
}

const initialState: WorkspaceState = {
  nodes: [],
  edges: [],
  selectedNodes: [],
  selectedTool: 'select',
  isAiPanelOpen: true,
  aiPanelWidth: 300,
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
} = workspaceSlice.actions

export default workspaceSlice.reducer
