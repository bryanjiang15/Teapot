import type { ProjectWithComponents } from '@/types/project'
import type { Node } from '@xyflow/react'
import { NODE_TEMPLATES } from '@/lib/nodeRegistry'

function node(id: string, templateKey: string, x: number, y: number): Node {
  const data = NODE_TEMPLATES[templateKey]
  return {
    id,
    type: 'custom',
    position: { x, y },
    data: { ...(data ?? NODE_TEMPLATES['event-game-start']) },
  }
}

/** Mock project "Dragon Legends TCG" (id "1") with components and sample nodes. */
export const MOCK_PROJECT_WITH_COMPONENTS: ProjectWithComponents = {
  id: '1',
  name: 'Dragon Legends TCG',
  components: [
    {
      id: 'card',
      name: 'Card',
      description: 'Card component behavior',
      nodes: [
        node('n1', 'event-card-played', 100, 80),
        node('n2', 'function-draw-card', 380, 80),
      ],
      edges: [
        { id: 'e1', source: 'n1', target: 'n2', sourceHandle: 'exec', targetHandle: 'exec', type: 'smoothstep' },
      ],
    },
    {
      id: 'deck',
      name: 'Deck',
      description: 'Deck component behavior',
      nodes: [
        node('n1', 'event-game-start', 80, 100),
        node('n2', 'function-draw-card', 320, 100),
      ],
      edges: [
        { id: 'e1', source: 'n1', target: 'n2', sourceHandle: 'exec', targetHandle: 'exec', type: 'smoothstep' },
      ],
    },
    {
      id: 'game-rule',
      name: 'Game Rule',
      description: 'Turn and phase rules',
      nodes: [
        node('n1', 'event-turn-start', 120, 120),
        node('n2', 'flow-branch', 360, 120),
      ],
      edges: [
        { id: 'e1', source: 'n1', target: 'n2', sourceHandle: 'exec', targetHandle: 'exec', type: 'smoothstep' },
      ],
    },
  ],
}

/** Get mock project by id; returns undefined if not found. */
export function getMockProject(projectId: string): ProjectWithComponents | undefined {
  if (projectId === MOCK_PROJECT_WITH_COMPONENTS.id) {
    return MOCK_PROJECT_WITH_COMPONENTS
  }
  return undefined
}
