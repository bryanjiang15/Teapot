import type { Node, Edge } from '@xyflow/react'

export interface Project {
  id: string
  name: string
  description: string
  status: 'development' | 'published' | 'draft'
  aiAssistantType: string
  createdAt: string
  updatedAt: string
}

/** A component within a project; has its own React Flow graph (nodes/edges) for behavior. */
export interface ProjectComponent {
  id: string
  name: string
  description?: string
  nodes: Node[]
  edges: Edge[]
}

/** Project with components for workspace context. */
export interface ProjectWithComponents {
  id: string
  name: string
  components: ProjectComponent[]
}

export interface CreateProjectRequest {
  name: string
  description: string
  gameType: 'tcg' | 'board'
  aiAssistantType: string
}
