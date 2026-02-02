import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import type { NodeData, NodeCategory } from '@/types/nodes'
import { NODE_CATEGORIES } from '@/types/nodes'
import { cn } from '@/lib/utils'

interface CustomNodeProps {
  data: NodeData
  selected?: boolean
}

export const CustomNode = memo(({ data, selected }: CustomNodeProps) => {
  const categoryStyle = NODE_CATEGORIES[data.category as NodeCategory]

  return (
    <div
      className={cn(
        "rounded-lg shadow-lg border-2 transition-all min-w-[200px]",
        selected ? "border-orange-primary shadow-xl" : "border-wood-brown"
      )}
      style={{
        backgroundColor: categoryStyle.color,
      }}
    >
      {/* Header */}
      <div className="px-4 py-2 bg-black/10 rounded-t-md">
        <div className="text-sm font-semibold text-white">
          {data.label}
        </div>
        <div className="text-xs text-white/80">
          {categoryStyle.label}
        </div>
      </div>

      {/* Body */}
      <div className="px-4 py-3 space-y-2">
        {/* Parameters */}
        {data.parameters.map((param) => (
          <div key={param.id} className="space-y-1">
            <label className="text-xs text-white/90 font-medium">
              {param.label}
            </label>
            {param.type === 'number' && (
              <input
                type="number"
                value={param.value}
                className="w-full px-2 py-1 text-sm rounded bg-white/80 border border-wood-brown"
                readOnly
              />
            )}
            {param.type === 'select' && (
              <select
                value={param.value}
                className="w-full px-2 py-1 text-sm rounded bg-white/80 border border-wood-brown"
                disabled
              >
                {param.options?.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            )}
          </div>
        ))}
      </div>

      {/* Input Handles */}
      {data.inputs.map((input, index) => (
        <Handle
          key={input.id}
          type="target"
          position={Position.Left}
          id={input.id}
          style={{
            top: `${((index + 1) / (data.inputs.length + 1)) * 100}%`,
            background: input.type === 'exec' ? '#fff' : getPortColor(input.type),
            width: input.type === 'exec' ? '12px' : '10px',
            height: input.type === 'exec' ? '12px' : '10px',
            borderRadius: input.type === 'exec' ? '2px' : '50%',
          }}
        />
      ))}

      {/* Output Handles */}
      {data.outputs.map((output, index) => (
        <Handle
          key={output.id}
          type="source"
          position={Position.Right}
          id={output.id}
          style={{
            top: `${((index + 1) / (data.outputs.length + 1)) * 100}%`,
            background: output.type === 'exec' ? '#fff' : getPortColor(output.type),
            width: output.type === 'exec' ? '12px' : '10px',
            height: output.type === 'exec' ? '12px' : '10px',
            borderRadius: output.type === 'exec' ? '2px' : '50%',
          }}
        />
      ))}
    </div>
  )
})

CustomNode.displayName = 'CustomNode'

function getPortColor(type: string): string {
  switch (type) {
    case 'object':
      return '#4A90E2'
    case 'number':
      return '#50C878'
    case 'boolean':
      return '#E74C3C'
    case 'string':
      return '#F39C12'
    default:
      return '#95A5A6'
  }
}
