import { afterEach, describe, expect, it, vi } from 'vitest'
import reducer, {
  addNodeToComponent,
  loadProject,
  updateComponentGraph,
} from '../../workspaceSlice'
import type { ProjectWithComponents } from '@/types/project'
import { NODE_TEMPLATES } from '@/lib/nodeRegistry'

function makeProject(components: ProjectWithComponents['components']): ProjectWithComponents {
  return {
    id: 'project-1',
    name: 'Test Project',
    components,
  }
}

describe('workspaceSlice component graph behavior', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('loadProject defaults selected component to the first component', () => {
    const project = makeProject([
      { id: 'card', name: 'Card', nodes: [], edges: [] },
      { id: 'deck', name: 'Deck', nodes: [], edges: [] },
    ])

    const state = reducer(undefined, loadProject(project))

    expect(state.currentProject).toEqual({ id: 'project-1', name: 'Test Project' })
    expect(state.selectedComponentId).toBe('card')
    expect(state.components).toEqual(project.components)
  })

  it('loadProject keeps selected component null when project has no components', () => {
    const state = reducer(undefined, loadProject(makeProject([])))

    expect(state.selectedComponentId).toBeNull()
    expect(state.components).toEqual([])
  })

  it('updateComponentGraph only updates the targeted component graph', () => {
    const project = makeProject([
      {
        id: 'card',
        name: 'Card',
        nodes: [{ id: 'c1', type: 'custom', position: { x: 0, y: 0 }, data: { label: 'A' } }],
        edges: [],
      },
      {
        id: 'deck',
        name: 'Deck',
        nodes: [{ id: 'd1', type: 'custom', position: { x: 10, y: 10 }, data: { label: 'B' } }],
        edges: [],
      },
    ])
    const loaded = reducer(undefined, loadProject(project))

    const nextNodes = [
      { id: 'c2', type: 'custom', position: { x: 100, y: 100 }, data: { label: 'Updated' } },
    ]
    const nextEdges = [{ id: 'e1', source: 'c2', target: 'c2' }]
    const updated = reducer(
      loaded,
      updateComponentGraph({ componentId: 'card', nodes: nextNodes as any, edges: nextEdges as any })
    )

    expect(updated.components[0].nodes).toEqual(nextNodes)
    expect(updated.components[0].edges).toEqual(nextEdges)
    expect(updated.components[1].nodes).toEqual(project.components[1].nodes)
    expect(updated.components[1].edges).toEqual(project.components[1].edges)
  })

  it('addNodeToComponent falls back to default template for unknown template id', () => {
    vi.spyOn(Date, 'now').mockReturnValue(1700000000000)
    vi.spyOn(Math, 'random').mockReturnValue(0.123456789)

    const project = makeProject([
      {
        id: 'card',
        name: 'Card',
        nodes: [{ id: 'existing', type: 'custom', position: { x: 0, y: 0 }, data: { label: 'N1' } }],
        edges: [],
      },
    ])
    const loaded = reducer(undefined, loadProject(project))
    const next = reducer(
      loaded,
      addNodeToComponent({ componentId: 'card', templateId: 'missing-template' })
    )

    const addedNode = next.components[0].nodes[1]
    expect(addedNode.id).toBe('node-1700000000000-4fzzzxj')
    expect(addedNode.position).toEqual({ x: 370, y: 100 })
    expect(addedNode.data).toEqual(NODE_TEMPLATES['event-game-start'])
  })

  it('addNodeToComponent does nothing when component does not exist', () => {
    const project = makeProject([
      {
        id: 'card',
        name: 'Card',
        nodes: [],
        edges: [],
      },
    ])
    const loaded = reducer(undefined, loadProject(project))
    const next = reducer(
      loaded,
      addNodeToComponent({ componentId: 'does-not-exist', templateId: 'event-game-start' })
    )

    expect(next.components[0].nodes).toHaveLength(0)
  })
})
