export type NodeCategory = 'event' | 'function' | 'flow' | 'variable' | 'target'

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
  inputs: InputPort[]
  outputs: OutputPort[]
  parameters: Parameter[]
}

export const NODE_CATEGORIES = {
  event: {
    color: '#B8DDB8',
    label: 'Event',
  },
  function: {
    color: '#B8D8E8',
    label: 'Function',
  },
  flow: {
    color: '#D8C7E8',
    label: 'Flow Control',
  },
  variable: {
    color: '#F5E6B8',
    label: 'Variable',
  },
  target: {
    color: '#FF8C42',
    label: 'Target Selector',
  },
}
