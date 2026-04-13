/** Canonical five node families for the workspace graph. */
export type NodeCategory = 'trigger' | 'state' | 'input' | 'flow' | 'function'

export type PortType = 'exec' | 'object' | 'number' | 'boolean' | 'string'

export interface InputPort {
  id: string
  type: PortType
  label: string
  defaultValue?: any
}

export interface OutputPort {
  id: string
  type: PortType
  label: string
}

export interface Parameter {
  id: string
  label: string
  type: 'number' | 'string' | 'boolean' | 'select'
  value: any
  options?: string[]
}

export interface NodeData {
  label: string
  category: NodeCategory
  /** Set when instantiated from NODE_TEMPLATES (for compiler / round-trip). */
  templateId?: string
  /**
   * Fine-grained kind for agents: lifecycle_trigger, custom_listener, emit_event,
   * variable, variable_reference, set_property, constant, target_selection, etc.
   */
  subkind?: string
  /** Domain or system event type this trigger listens for (not used for emit nodes). */
  eventType?: string
  /** Alias for backends that expect snake_case. */
  event_type?: string
  inputs: InputPort[]
  outputs: OutputPort[]
  parameters: Parameter[]
  /** Natural-language behavior for CreatorAPI / compiler node_summary (AI script generation). */
  behaviorDescription?: string
  /** Tighter layout and typography (e.g. variable reference nodes). */
  compact?: boolean
  /** Omit the “What this node does” block in the canvas UI. */
  hideBehaviorDescription?: boolean
}

export const NODE_CATEGORIES: Record<
  NodeCategory,
  { color: string; label: string }
> = {
  trigger: {
    color: '#B8DDB8',
    label: 'Trigger',
  },
  state: {
    color: '#F5E6B8',
    label: 'State / property',
  },
  input: {
    color: '#E8D5B7',
    label: 'Input',
  },
  flow: {
    color: '#D8C7E8',
    label: 'Flow',
  },
  function: {
    color: '#B8D8E8',
    label: 'Function',
  },
}
