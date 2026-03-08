import type { NodeData } from '@/types/nodes'

export const NODE_TEMPLATES: Record<string, NodeData> = {
  // Event Nodes
  'event-game-start': {
    label: 'On Game Start',
    category: 'event',
    inputs: [],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [],
  },
  'event-turn-start': {
    label: 'On Turn Start',
    category: 'event',
    inputs: [],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [],
  },
  'event-card-played': {
    label: 'On Card Played',
    category: 'event',
    inputs: [],
    outputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'card', type: 'object', label: 'Card' },
    ],
    parameters: [],
  },
  'event-damage-dealt': {
    label: 'On Damage Dealt',
    category: 'event',
    inputs: [],
    outputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'amount', type: 'number', label: 'Amount' },
    ],
    parameters: [],
  },

  // Function Nodes
  'function-draw-card': {
    label: 'Draw Card',
    category: 'function',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'amount', type: 'number', label: 'Amount', defaultValue: 1 },
    ],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [
      { id: 'amount', label: 'Amount', type: 'number', value: 1 },
    ],
  },
  'function-deal-damage': {
    label: 'Deal Damage',
    category: 'function',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'target', type: 'object', label: 'Target' },
      { id: 'amount', type: 'number', label: 'Amount' },
    ],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [
      { id: 'amount', label: 'Amount', type: 'number', value: 1 },
    ],
  },
  'function-heal': {
    label: 'Heal',
    category: 'function',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'target', type: 'object', label: 'Target' },
      { id: 'amount', type: 'number', label: 'Amount' },
    ],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [
      { id: 'amount', label: 'Amount', type: 'number', value: 1 },
    ],
  },

  // Flow Control Nodes
  'flow-branch': {
    label: 'Branch',
    category: 'flow',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'condition', type: 'boolean', label: 'Condition' },
    ],
    outputs: [
      { id: 'true', type: 'exec', label: 'True' },
      { id: 'false', type: 'exec', label: 'False' },
    ],
    parameters: [],
  },
  'flow-sequence': {
    label: 'Sequence',
    category: 'flow',
    inputs: [{ id: 'exec', type: 'exec', label: '' }],
    outputs: [
      { id: 'then-1', type: 'exec', label: 'Then 1' },
      { id: 'then-2', type: 'exec', label: 'Then 2' },
    ],
    parameters: [],
  },

  // Variable Nodes
  'variable-constant': {
    label: 'Constant',
    category: 'variable',
    inputs: [],
    outputs: [{ id: 'value', type: 'number', label: 'Value' }],
    parameters: [
      { id: 'value', label: 'Value', type: 'number', value: 0 },
    ],
  },
  'variable-get-property': {
    label: 'Get Property',
    category: 'variable',
    inputs: [{ id: 'target', type: 'object', label: 'Target' }],
    outputs: [{ id: 'value', type: 'number', label: 'Value' }],
    parameters: [
      {
        id: 'property',
        label: 'Property',
        type: 'select',
        value: 'attack',
        options: ['attack', 'health', 'cost'],
      },
    ],
  },

  // Target Selector Nodes
  'target-select-all': {
    label: 'Select All Cards',
    category: 'target',
    inputs: [{ id: 'exec', type: 'exec', label: '' }],
    outputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'cards', type: 'object', label: 'Cards' },
    ],
    parameters: [
      {
        id: 'zone',
        label: 'Zone',
        type: 'select',
        value: 'board',
        options: ['board', 'hand', 'deck'],
      },
    ],
  },
  'target-random': {
    label: 'Random Selection',
    category: 'target',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'collection', type: 'object', label: 'Collection' },
    ],
    outputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'selected', type: 'object', label: 'Selected' },
    ],
    parameters: [
      { id: 'count', label: 'Count', type: 'number', value: 1 },
    ],
  },

  // Input Nodes (wait for user input)
  'input-wait': {
    label: 'Wait for Input',
    category: 'input',
    inputs: [{ id: 'exec', type: 'exec', label: '' }],
    outputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'value', type: 'object', label: 'Input' },
    ],
    parameters: [],
  },
}

export function getNodeTemplate(type: string): NodeData {
  return NODE_TEMPLATES[type] || NODE_TEMPLATES['event-game-start']
}
