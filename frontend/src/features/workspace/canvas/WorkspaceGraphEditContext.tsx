import { createContext, useContext } from 'react'
import type { AppDispatch } from '@/app/store'

export interface WorkspaceGraphEditContextValue {
  componentId: string | null
  dispatch: AppDispatch
}

export const WorkspaceGraphEditContext = createContext<WorkspaceGraphEditContextValue | null>(null)

export function useWorkspaceGraphEdit(): WorkspaceGraphEditContextValue | null {
  return useContext(WorkspaceGraphEditContext)
}
