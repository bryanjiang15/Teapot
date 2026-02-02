export interface Project {
  id: string
  name: string
  description: string
  status: 'development' | 'published' | 'draft'
  aiAssistantType: string
  createdAt: string
  updatedAt: string
}

export interface CreateProjectRequest {
  name: string
  description: string
  gameType: 'tcg' | 'board'
  aiAssistantType: string
}
