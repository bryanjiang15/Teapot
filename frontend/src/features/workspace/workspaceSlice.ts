import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { Node, Edge } from '@xyflow/react'
import type { ProjectComponent, ProjectWithComponents } from '@/types/project'
import type { NodeData } from '@/types/nodes'
import type { SceneEntity, SceneEntityType, SceneRoot, SceneTransform } from '@/types/scene'
import { DEFAULT_TRANSFORM } from '@/types/scene'
import {
  DEFAULT_NODE_TEMPLATE_ID,
  getNodeTemplate,
  NODE_TEMPLATES,
  resolveTemplateId,
} from '@/lib/nodeRegistry'

function generateSceneEntityId(): string {
  return `entity-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function findEntityInTree(root: SceneEntity | null, id: string): SceneEntity | null {
  if (!root) return null
  if (root.id === id) return root
  for (const child of root.children) {
    const found = findEntityInTree(child, id)
    if (found) return found
  }
  return null
}

function findParentInTree(
  root: SceneEntity | null,
  childId: string
): { parent: SceneEntity; index: number } | null {
  if (!root) return null
  const idx = root.children.findIndex((c) => c.id === childId)
  if (idx >= 0) return { parent: root, index: idx }
  for (const child of root.children) {
    const found = findParentInTree(child, childId)
    if (found) return found
  }
  return null
}

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
  /** Active tab: node graph or scene visual editor. */
  activeWorkspaceTab: 'node' | 'scene'
  /** Selected entity in the scene hierarchy (Scene tab). */
  selectedSceneEntityId: string | null
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
  activeWorkspaceTab: 'node',
  selectedSceneEntityId: null,
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
    setActiveWorkspaceTab: (state, action: PayloadAction<'node' | 'scene'>) => {
      state.activeWorkspaceTab = action.payload
    },
    setSelectedSceneEntityId: (state, action: PayloadAction<string | null>) => {
      state.selectedSceneEntityId = action.payload
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
    /** Shallow-merge fields into one node's data (e.g. behaviorDescription). */
    updateComponentNodeData: (
      state,
      action: PayloadAction<{ componentId: string; nodeId: string; data: Partial<NodeData> }>
    ) => {
      const { componentId, nodeId, data: patch } = action.payload
      const comp = state.components.find((c) => c.id === componentId)
      if (!comp) return
      const node = comp.nodes.find((n) => n.id === nodeId)
      if (!node?.data || typeof node.data !== 'object') return
      Object.assign(node.data as Record<string, unknown>, patch as Record<string, unknown>)
    },
    /** Update a single parameter on a node (preserves compiler-facing eventType sync for custom listeners). */
    updateComponentNodeParameter: (
      state,
      action: PayloadAction<{
        componentId: string
        nodeId: string
        paramId: string
        value: string | number | boolean
      }>
    ) => {
      const { componentId, nodeId, paramId, value } = action.payload
      const comp = state.components.find((c) => c.id === componentId)
      if (!comp) return
      const node = comp.nodes.find((n) => n.id === nodeId)
      if (!node?.data || typeof node.data !== 'object') return
      const data = node.data as NodeData
      const idx = data.parameters.findIndex((p) => p.id === paramId)
      if (idx < 0) return
      data.parameters[idx] = { ...data.parameters[idx], value }
      if (paramId === 'listenEventType') {
        const s = String(value)
        data.eventType = s
        data.event_type = s
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
      const resolvedId = resolveTemplateId(templateId)
      const storedTemplateId = Object.hasOwn(NODE_TEMPLATES, resolvedId)
        ? resolvedId
        : DEFAULT_NODE_TEMPLATE_ID
      const template = getNodeTemplate(templateId)
      const comp = state.components.find((c) => c.id === componentId)
      if (!comp) return
      const nodeId = `node-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
      const count = comp.nodes.length
      const data: NodeData = {
        ...template,
        templateId: storedTemplateId,
        parameters: template.parameters.map((p) => ({ ...p })),
        inputs: template.inputs.map((i) => ({ ...i })),
        outputs: template.outputs.map((o) => ({ ...o })),
        behaviorDescription: template.behaviorDescription ?? '',
      }
      const listenParam = data.parameters.find((p) => p.id === 'listenEventType')
      if (
        listenParam &&
        (data.subkind === 'custom_listener' || storedTemplateId === 'trigger-custom-listener')
      ) {
        const s = String(listenParam.value ?? '')
        data.eventType = s
        data.event_type = s
      }
      const newNode: Node = {
        id: nodeId,
        type: 'custom',
        position: {
          x: 150 + (count % 4) * 220,
          y: 100 + Math.floor(count / 4) * 120,
        },
        data,
      }
      comp.nodes = [...comp.nodes, newNode]
    },
    /** Add a blank component to the project and select it. */
    addComponent: (state, action: PayloadAction<{ id: string; name: string }>) => {
      const newComponent: ProjectComponent = {
        id: action.payload.id,
        name: action.payload.name,
        nodes: [],
        edges: [],
      }
      state.components = [...state.components, newComponent]
      state.selectedComponentId = newComponent.id
    },
    /** Set the full scene root for a component. */
    setComponentScene: (
      state,
      action: PayloadAction<{ componentId: string; sceneRoot: SceneRoot }>
    ) => {
      const comp = state.components.find((c) => c.id === action.payload.componentId)
      if (comp) comp.sceneRoot = action.payload.sceneRoot
    },
    /** Add a scene entity as child of parentEntityId, or as root if parentEntityId is null and no root. */
    addSceneEntity: (
      state,
      action: PayloadAction<{
        componentId: string
        parentEntityId: string | null
        name: string
        type: SceneEntityType
        transform?: Partial<SceneTransform>
      }>
    ) => {
      const { componentId, parentEntityId, name, type, transform } = action.payload
      const comp = state.components.find((c) => c.id === componentId)
      if (!comp) return
      const newEntity: SceneEntity = {
        id: generateSceneEntityId(),
        name,
        type,
        transform: { ...DEFAULT_TRANSFORM, ...transform },
        children: [],
      }
      if (parentEntityId === null) {
        if (!comp.sceneRoot) {
          comp.sceneRoot = newEntity
        } else {
          comp.sceneRoot.children = [...comp.sceneRoot.children, newEntity]
        }
      } else {
        const parent = findEntityInTree(comp.sceneRoot ?? null, parentEntityId)
        if (parent) parent.children = [...parent.children, newEntity]
      }
    },
    /** Update a scene entity by id. */
    updateSceneEntity: (
      state,
      action: PayloadAction<{
        componentId: string
        entityId: string
        patch: Partial<Pick<SceneEntity, 'name' | 'transform' | 'assetId' | 'componentRef' | 'slotKey'>>
      }>
    ) => {
      const { componentId, entityId, patch } = action.payload
      const comp = state.components.find((c) => c.id === componentId)
      if (!comp) return
      const entity = findEntityInTree(comp.sceneRoot ?? null, entityId)
      if (entity) {
        if (patch.name !== undefined) entity.name = patch.name
        if (patch.transform !== undefined) entity.transform = { ...entity.transform, ...patch.transform }
        if (patch.assetId !== undefined) entity.assetId = patch.assetId
        if (patch.componentRef !== undefined) entity.componentRef = patch.componentRef
        if (patch.slotKey !== undefined) entity.slotKey = patch.slotKey
      }
    },
    /** Remove a scene entity by id (and clear selection if it was selected). */
    removeSceneEntity: (
      state,
      action: PayloadAction<{ componentId: string; entityId: string }>
    ) => {
      const { componentId, entityId } = action.payload
      if (state.selectedSceneEntityId === entityId) state.selectedSceneEntityId = null
      const comp = state.components.find((c) => c.id === componentId)
      if (!comp?.sceneRoot) return
      const parentInfo = findParentInTree(comp.sceneRoot, entityId)
      if (parentInfo) {
        parentInfo.parent.children = parentInfo.parent.children.filter((c) => c.id !== entityId)
      } else if (comp.sceneRoot.id === entityId) {
        comp.sceneRoot = comp.sceneRoot.children[0] ?? null
      }
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
  setActiveWorkspaceTab,
  setSelectedSceneEntityId,
  updateComponentGraph,
  updateComponentNodeData,
  updateComponentNodeParameter,
  loadProject,
  addNodeToComponent,
  addComponent,
  setComponentScene,
  addSceneEntity,
  updateSceneEntity,
  removeSceneEntity,
} = workspaceSlice.actions

export default workspaceSlice.reducer
