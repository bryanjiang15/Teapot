import { useCallback, useState } from 'react'
import { ChevronRight, LayoutTemplate, Image, Type, Package, Trash2, Plus, Pencil } from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import {
  addSceneEntity,
  removeSceneEntity,
  setSelectedSceneEntityId,
  updateSceneEntity,
} from '../workspaceSlice'
import type { SceneEntity, SceneEntityType } from '@/types/scene'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const ENTITY_TYPE_ICONS: Record<SceneEntityType, React.ComponentType<{ className?: string }>> = {
  slot: LayoutTemplate,
  sprite: Image,
  text: Type,
  component: Package,
}

interface EntityRowProps {
  entity: SceneEntity
  depth: number
  isExpanded: boolean
  onToggleExpand: () => void
  isSelected: boolean
  onSelect: () => void
  onAddChild: () => void
  onDelete: () => void
  onRename: (newName: string) => void
}

function EntityRow({
  entity,
  depth,
  isExpanded,
  onToggleExpand,
  isSelected,
  onSelect,
  onAddChild,
  onDelete,
  onRename,
}: EntityRowProps) {
  const [editingName, setEditingName] = useState(false)
  const [editValue, setEditValue] = useState(entity.name)
  const Icon = ENTITY_TYPE_ICONS[entity.type]

  const handleRenameSubmit = useCallback(() => {
    setEditingName(false)
    const trimmed = editValue.trim()
    if (trimmed && trimmed !== entity.name) onRename(trimmed)
    else setEditValue(entity.name)
  }, [editValue, entity.name, onRename])

  return (
    <div className="flex flex-col">
      <div
        className={cn(
          'flex items-center gap-1 py-1 px-2 rounded-md group cursor-pointer',
          isSelected && 'bg-primary/15 text-primary'
        )}
        style={{ paddingLeft: `${depth * 12 + 8}px` }}
      >
        <button
          type="button"
          className="p-0.5 rounded hover:bg-black/10 shrink-0"
          onClick={(e) => {
            e.stopPropagation()
            onToggleExpand()
          }}
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          <ChevronRight
            className={cn('w-4 h-4 transition-transform', isExpanded && 'rotate-90')}
          />
        </button>
        <button
          type="button"
          className="flex items-center gap-1.5 min-w-0 flex-1 text-left"
          onClick={() => onSelect()}
        >
          <Icon className="w-4 h-4 shrink-0 text-muted-foreground" />
          {editingName ? (
            <input
              className="flex-1 min-w-0 bg-background border rounded px-1 py-0.5 text-sm"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={handleRenameSubmit}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleRenameSubmit()
                if (e.key === 'Escape') {
                  setEditingName(false)
                  setEditValue(entity.name)
                }
              }}
              autoFocus
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <span className="truncate text-sm">{entity.name}</span>
          )}
        </button>
        <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 shrink-0">
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={(e) => {
              e.stopPropagation()
              setEditingName(true)
              setEditValue(entity.name)
            }}
            title="Rename"
          >
            <Pencil className="w-3 h-3" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={(e) => {
              e.stopPropagation()
              onAddChild()
            }}
            title="Add child"
          >
            <Plus className="w-3 h-3" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-destructive"
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            title="Delete"
          >
            <Trash2 className="w-3 h-3" />
          </Button>
        </div>
      </div>
    </div>
  )
}

interface RecursiveEntityTreeProps {
  entity: SceneEntity
  depth: number
  componentId: string
  selectedSceneEntityId: string | null
  expandedIds: Set<string>
  setExpanded: (id: string, value: boolean) => void
}

function RecursiveEntityTree({
  entity,
  depth,
  componentId,
  selectedSceneEntityId,
  expandedIds,
  setExpanded,
}: RecursiveEntityTreeProps) {
  const dispatch = useAppDispatch()
  const isExpanded = expandedIds.has(entity.id)
  const isSelected = selectedSceneEntityId === entity.id

  return (
    <>
      <EntityRow
        entity={entity}
        depth={depth}
        isExpanded={isExpanded}
        onToggleExpand={() => setExpanded(entity.id, !isExpanded)}
        isSelected={isSelected}
        onSelect={() => dispatch(setSelectedSceneEntityId(entity.id))}
        onAddChild={() =>
          dispatch(
            addSceneEntity({
              componentId,
              parentEntityId: entity.id,
              name: 'New Slot',
              type: 'slot',
            })
          )
        }
        onDelete={() => dispatch(removeSceneEntity({ componentId, entityId: entity.id }))}
        onRename={(newName) =>
          dispatch(updateSceneEntity({ componentId, entityId: entity.id, patch: { name: newName } }))
        }
      />
      {isExpanded &&
        entity.children.map((child) => (
          <RecursiveEntityTree
            key={child.id}
            entity={child}
            depth={depth + 1}
            componentId={componentId}
            selectedSceneEntityId={selectedSceneEntityId}
            expandedIds={expandedIds}
            setExpanded={setExpanded}
          />
        ))}
    </>
  )
}

export function SceneHierarchyPanel() {
  const dispatch = useAppDispatch()
  const { components, selectedComponentId, selectedSceneEntityId } = useAppSelector(
    (state) => state.workspace
  )
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set())

  const setExpanded = useCallback((id: string, value: boolean) => {
    setExpandedIds((prev) => {
      const next = new Set(prev)
      if (value) next.add(id)
      else next.delete(id)
      return next
    })
  }, [])

  const sceneRoot = components.find((c) => c.id === selectedComponentId)?.sceneRoot ?? null

  if (!selectedComponentId) return null

  const handleAddRoot = () => {
    dispatch(
      addSceneEntity({
        componentId: selectedComponentId,
        parentEntityId: null,
        name: 'Root',
        type: 'slot',
      })
    )
    setExpandedIds((prev) => new Set(prev))
  }

  if (!sceneRoot) {
    return (
      <div className="h-full flex flex-col p-2 border-r border-border bg-card">
        <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 py-1.5">
          Composition
        </h2>
        <div className="flex-1 flex items-center justify-center p-4">
          <Button variant="outline" size="sm" onClick={handleAddRoot}>
            Add slot
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col w-60 shrink-0 border-r border-border bg-card overflow-hidden">
      <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 py-1.5 border-b border-border shrink-0">
        Composition
      </h2>
      <div className="flex-1 overflow-y-auto py-1">
        <RecursiveEntityTree
          entity={sceneRoot}
          depth={0}
          componentId={selectedComponentId}
          selectedSceneEntityId={selectedSceneEntityId}
          expandedIds={expandedIds}
          setExpanded={setExpanded}
        />
      </div>
    </div>
  )
}
