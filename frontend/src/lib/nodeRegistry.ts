import type { NodeCategory, NodeData } from '@/types/nodes'

export const DEFAULT_NODE_TEMPLATE_ID = 'trigger-lifecycle-game-started'

/** Sidebar: five families → concrete templates (label + id). */
export const NODE_FAMILY_TEMPLATES: {
  category: NodeCategory
  label: string
  description: string
  items: { templateId: string; label: string }[]
}[] = [
  {
    category: 'trigger',
    label: 'Trigger',
    description: 'When to run: lifecycle, custom event, or emit to other components',
    items: [
      { templateId: 'trigger-lifecycle-game-started', label: 'On game started (lifecycle)' },
      { templateId: 'trigger-custom-listener', label: 'On custom event…' },
      { templateId: 'trigger-emit-event', label: 'Emit event' },
    ],
  },
  {
    category: 'state',
    label: 'State',
    description: 'Named variables and set-property steps',
    items: [
      { templateId: 'state-variable', label: 'Variable Definition' },
      { templateId: 'state-set-property', label: 'Set property' },
    ],
  },
  {
    category: 'input',
    label: 'Input',
    description: 'Constants, variable references, or player target selection',
    items: [
      { templateId: 'input-constant', label: 'Constant value' },
      { templateId: 'input-variable-reference', label: 'Variable' },
      { templateId: 'input-target-selection', label: 'Target selection' },
    ],
  },
  {
    category: 'flow',
    label: 'Flow',
    description: 'Branch with multiple conditions',
    items: [{ templateId: 'flow-multibranch', label: 'Multi-branch' }],
  },
  {
    category: 'function',
    label: 'Function',
    description: 'Game state change (describe behavior for AI)',
    items: [{ templateId: 'function-effect', label: 'Effect' }],
  },
]

export const NODE_TEMPLATES: Record<string, NodeData> = {
  'trigger-lifecycle-game-started': {
    label: 'On game started (lifecycle)',
    category: 'trigger',
    subkind: 'lifecycle_trigger',
    eventType: 'game_started',
    event_type: 'game_started',
    inputs: [],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [],
  },
  'trigger-custom-listener': {
    label: 'On custom event…',
    category: 'trigger',
    subkind: 'custom_listener',
    eventType: '',
    event_type: '',
    inputs: [],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [
      {
        id: 'listenEventType',
        label: 'Event type to listen for',
        type: 'string',
        value: '',
      },
    ],
  },
  'trigger-emit-event': {
    label: 'Emit event',
    category: 'trigger',
    subkind: 'emit_event',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'payload', type: 'object', label: 'Payload', defaultValue: undefined },
    ],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [
      {
        id: 'emitEventType',
        label: 'Event type to emit',
        type: 'string',
        value: '',
      },
    ],
  },

  'state-variable': {
    label: 'Variable Definition',
    category: 'state',
    subkind: 'variable',
    inputs: [],
    outputs: [{ id: 'value', type: 'string', label: 'Value' }],
    parameters: [{ id: 'name', label: 'Property name', type: 'string', value: '' }],
  },
  'state-set-property': {
    label: 'Set property',
    category: 'state',
    subkind: 'set_property',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'value', type: 'string', label: 'Value' },
    ],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [
      {
        id: 'description',
        label: 'What variable to set (describe for AI)',
        type: 'string',
        value: '',
      },
    ],
  },

  'input-constant': {
    label: 'Constant value',
    category: 'input',
    subkind: 'constant',
    inputs: [],
    outputs: [{ id: 'value', type: 'string', label: 'Value' }],
    parameters: [
      {
        id: 'constantKind',
        label: 'Kind',
        type: 'select',
        value: 'integer',
        options: ['integer', 'string', 'enum'],
      },
      { id: 'intValue', label: 'Integer', type: 'number', value: 0 },
      { id: 'stringValue', label: 'String', type: 'string', value: '' },
      { id: 'enumId', label: 'Enum id (project/schema)', type: 'string', value: '' },
      { id: 'enumValue', label: 'Enum case', type: 'string', value: '' },
      {
        id: 'asPropertyKey',
        label: 'Export as component property key (optional)',
        type: 'string',
        value: '',
      },
    ],
  },
  'input-variable-reference': {
    label: 'Variable',
    category: 'input',
    subkind: 'variable_reference',
    inputs: [],
    outputs: [{ id: 'value', type: 'string', label: 'Value' }],
    parameters: [{ id: 'name', label: 'Variable name', type: 'string', value: '' }],
    compact: true,
    hideBehaviorDescription: true,
  },

  'input-target-selection': {
    label: 'Target selection',
    category: 'input',
    subkind: 'target_selection',
    inputs: [{ id: 'exec', type: 'exec', label: '' }],
    outputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'selected', type: 'object', label: 'Selected' },
    ],
    parameters: [
      {
        id: 'filterHint',
        label: 'Selectable group / filter (describe for AI)',
        type: 'string',
        value: '',
      },
    ],
  },

  'flow-multibranch': {
    label: 'Multi-branch',
    category: 'flow',
    subkind: 'multibranch',
    inputs: [{ id: 'exec', type: 'exec', label: '' }],
    outputs: [
      { id: 'branch-0', type: 'exec', label: 'Branch 0' },
      { id: 'branch-1', type: 'exec', label: 'Branch 1' },
      { id: 'branch-2', type: 'exec', label: 'Branch 2' },
      { id: 'else', type: 'exec', label: 'Else' },
    ],
    parameters: [
      {
        id: 'condition0',
        label: 'Condition 0',
        type: 'string',
        value: '',
      },
      {
        id: 'condition1',
        label: 'Condition 1',
        type: 'string',
        value: '',
      },
      {
        id: 'condition2',
        label: 'Condition 2',
        type: 'string',
        value: '',
      },
    ],
  },

  'function-effect': {
    label: 'Effect',
    category: 'function',
    subkind: 'effect',
    inputs: [
      { id: 'exec', type: 'exec', label: '' },
      { id: 'ctxA', type: 'object', label: 'Context A' },
      { id: 'ctxB', type: 'object', label: 'Context B' },
    ],
    outputs: [{ id: 'exec', type: 'exec', label: '' }],
    parameters: [],
  },
}

/** Old template ids saved in projects → current id (shape may still differ in stored nodes). */
const LEGACY_TEMPLATE_IDS: Record<string, string> = {
  'state-get-property': 'state-variable',
}

export function resolveTemplateId(templateId: string): string {
  return LEGACY_TEMPLATE_IDS[templateId] ?? templateId
}

export function getNodeTemplate(templateId: string): NodeData {
  const id = resolveTemplateId(templateId)
  return NODE_TEMPLATES[id] ?? NODE_TEMPLATES[DEFAULT_NODE_TEMPLATE_ID]
}
