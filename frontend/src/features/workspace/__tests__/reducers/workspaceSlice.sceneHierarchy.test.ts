import { afterEach, describe, expect, it, vi } from 'vitest'
import reducer, {
  addSceneEntity,
  loadProject,
  removeSceneEntity,
  setSelectedSceneEntityId,
  updateSceneEntity,
} from '../../workspaceSlice'
import type { ProjectWithComponents } from '@/types/project'
import type { SceneEntity } from '@/types/scene'

function makeProject(components: ProjectWithComponents['components']): ProjectWithComponents {
  return {
    id: 'project-1',
    name: 'Test Project',
    components,
  }
}

function makeEntity(partial: Partial<SceneEntity> & Pick<SceneEntity, 'id' | 'name' | 'type'>): SceneEntity {
  return {
    id: partial.id,
    name: partial.name,
    type: partial.type,
    transform: partial.transform ?? { x: 0, y: 0, rotation: 0, scaleX: 1, scaleY: 1 },
    children: partial.children ?? [],
    slotKey: partial.slotKey,
    assetId: partial.assetId,
    componentRef: partial.componentRef,
  }
}

describe('workspaceSlice scene hierarchy behavior', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('addSceneEntity creates root with merged default transform when scene is empty', () => {
    vi.spyOn(Date, 'now').mockReturnValue(1700000000000)
    vi.spyOn(Math, 'random').mockReturnValue(0.123456789)

    const loaded = reducer(
      undefined,
      loadProject(makeProject([{ id: 'card', name: 'Card', nodes: [], edges: [] }]))
    )
    const next = reducer(
      loaded,
      addSceneEntity({
        componentId: 'card',
        parentEntityId: null,
        name: 'Root Slot',
        type: 'slot',
        transform: { x: 42 },
      })
    )

    expect(next.components[0].sceneRoot).toEqual({
      id: 'entity-1700000000000-4fzzzxj',
      name: 'Root Slot',
      type: 'slot',
      transform: { x: 42, y: 0, rotation: 0, scaleX: 1, scaleY: 1 },
      children: [],
    })
  })

  it('addSceneEntity adds child to an existing parent and ignores unknown parent ids', () => {
    const root = makeEntity({ id: 'root', name: 'Root', type: 'slot' })
    const loaded = reducer(
      undefined,
      loadProject(
        makeProject([{ id: 'card', name: 'Card', nodes: [], edges: [], sceneRoot: root }])
      )
    )

    const withChild = reducer(
      loaded,
      addSceneEntity({
        componentId: 'card',
        parentEntityId: 'root',
        name: 'Artwork',
        type: 'sprite',
      })
    )

    expect(withChild.components[0].sceneRoot?.children).toHaveLength(1)
    expect(withChild.components[0].sceneRoot?.children[0].name).toBe('Artwork')

    const unchanged = reducer(
      withChild,
      addSceneEntity({
        componentId: 'card',
        parentEntityId: 'missing-parent',
        name: 'Should Not Attach',
        type: 'text',
      })
    )

    expect(unchanged.components[0].sceneRoot?.children).toHaveLength(1)
  })

  it('updateSceneEntity patches only targeted entity fields and merges transforms', () => {
    const entity = makeEntity({ id: 'entity-1', name: 'Name', type: 'component' })
    const otherEntity = makeEntity({ id: 'entity-1', name: 'Other Name', type: 'component' })
    const loaded = reducer(
      undefined,
      loadProject(
        makeProject([
          { id: 'card', name: 'Card', nodes: [], edges: [], sceneRoot: entity },
          { id: 'deck', name: 'Deck', nodes: [], edges: [], sceneRoot: otherEntity },
        ])
      )
    )

    const next = reducer(
      loaded,
      updateSceneEntity({
        componentId: 'card',
        entityId: 'entity-1',
        patch: {
          name: 'Card Body',
          transform: { x: 10, scaleX: 1.5 },
          componentRef: 'component-2',
          slotKey: 'body',
          assetId: 'asset-9',
        },
      })
    )

    expect(next.components[0].sceneRoot).toMatchObject({
      name: 'Card Body',
      transform: { x: 10, y: 0, rotation: 0, scaleX: 1.5, scaleY: 1 },
      componentRef: 'component-2',
      slotKey: 'body',
      assetId: 'asset-9',
    })
    expect(next.components[1].sceneRoot).toMatchObject({
      name: 'Other Name',
      transform: { x: 0, y: 0, rotation: 0, scaleX: 1, scaleY: 1 },
    })
  })

  it('removeSceneEntity removes selected nested entity and clears selection', () => {
    const selectedChild = makeEntity({ id: 'child-1', name: 'Child', type: 'sprite' })
    const sibling = makeEntity({ id: 'child-2', name: 'Sibling', type: 'text' })
    const root = makeEntity({
      id: 'root',
      name: 'Root',
      type: 'slot',
      children: [selectedChild, sibling],
    })
    const loaded = reducer(
      undefined,
      loadProject(
        makeProject([{ id: 'card', name: 'Card', nodes: [], edges: [], sceneRoot: root }])
      )
    )
    const withSelection = reducer(loaded, setSelectedSceneEntityId('child-1'))

    const next = reducer(withSelection, removeSceneEntity({ componentId: 'card', entityId: 'child-1' }))

    expect(next.selectedSceneEntityId).toBeNull()
    expect(next.components[0].sceneRoot?.children.map((child) => child.id)).toEqual(['child-2'])
  })

  it('removeSceneEntity promotes first child when removing the root', () => {
    const nextRoot = makeEntity({ id: 'child-a', name: 'A', type: 'slot' })
    const secondChild = makeEntity({ id: 'child-b', name: 'B', type: 'slot' })
    const root = makeEntity({
      id: 'root',
      name: 'Root',
      type: 'slot',
      children: [nextRoot, secondChild],
    })
    const loaded = reducer(
      undefined,
      loadProject(
        makeProject([{ id: 'card', name: 'Card', nodes: [], edges: [], sceneRoot: root }])
      )
    )

    const next = reducer(loaded, removeSceneEntity({ componentId: 'card', entityId: 'root' }))

    expect(next.components[0].sceneRoot?.id).toBe('child-a')
  })
})
