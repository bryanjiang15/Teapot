import { useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { setSelectedSceneEntityId, updateSceneEntity } from '../workspaceSlice'
import { SceneHierarchyPanel } from './SceneHierarchyPanel'
import { PixiSceneView } from './PixiSceneView'
import type { SceneRoot } from '@/types/scene'

/** Scene tab: composition tree + 2D PixiJS view. */
export function SceneEditor() {
  const dispatch = useAppDispatch()
  const { components, selectedComponentId, selectedSceneEntityId } = useAppSelector(
    (state) => state.workspace
  )
  const sceneRoot: SceneRoot = components.find((c) => c.id === selectedComponentId)?.sceneRoot ?? null
  const onSelectEntity = useCallback(
    (entityId: string) => dispatch(setSelectedSceneEntityId(entityId)),
    [dispatch]
  )
  const onTransformEntity = useCallback(
    (entityId: string, patch: { transform?: { x?: number; y?: number; rotation?: number; scaleX?: number; scaleY?: number } }) => {
      if (!selectedComponentId) return
      dispatch(updateSceneEntity({ componentId: selectedComponentId, entityId, patch }))
    },
    [dispatch, selectedComponentId]
  )

  return (
    <div className="flex h-full wood-texture">
      <SceneHierarchyPanel />
      <div className="flex-1 min-w-0 relative">
        <PixiSceneView
          className="absolute inset-0"
          sceneRoot={sceneRoot}
          componentId={selectedComponentId ?? ''}
          selectedEntityId={selectedSceneEntityId}
          onSelectEntity={onSelectEntity}
          onTransformEntity={onTransformEntity}
        />
      </div>
    </div>
  )
}
