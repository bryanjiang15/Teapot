import { memo, useCallback, type ChangeEvent } from 'react'
import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { NodeData, NodeCategory } from '@/types/nodes'
import { NODE_CATEGORIES } from '@/types/nodes'
import { cn } from '@/lib/utils'
import { useWorkspaceGraphEdit } from '../canvas/WorkspaceGraphEditContext'
import { updateComponentNodeData, updateComponentNodeParameter } from '../workspaceSlice'

export const CustomNode = memo(({ id, data, selected }: NodeProps) => {
  const graphEdit = useWorkspaceGraphEdit()
  const d = data as NodeData
  const categoryStyle =
    NODE_CATEGORIES[d.category as NodeCategory] ?? NODE_CATEGORIES.function

  const compact = Boolean(d.compact)
  const hideBehavior = Boolean(d.hideBehaviorDescription)

  const onBehaviorChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      if (!graphEdit?.componentId) return
      graphEdit.dispatch(
        updateComponentNodeData({
          componentId: graphEdit.componentId,
          nodeId: id,
          data: { behaviorDescription: e.target.value },
        })
      )
    },
    [graphEdit, id]
  )

  const onParamChange = useCallback(
    (paramId: string, value: string | number | boolean) => {
      if (!graphEdit?.componentId) return
      graphEdit.dispatch(
        updateComponentNodeParameter({
          componentId: graphEdit.componentId,
          nodeId: id,
          paramId,
          value,
        })
      )
    },
    [graphEdit, id]
  )

  return (
    <div
      className={cn(
        'rounded-lg shadow-lg border-2 transition-all',
        compact ? 'min-w-[150px]' : 'min-w-[200px]',
        selected ? 'border-orange-primary shadow-xl' : 'border-wood-brown'
      )}
      style={{
        backgroundColor: categoryStyle.color,
      }}
    >
      {/* Header */}
      <div
        className={cn(
          'bg-black/10 rounded-t-md',
          compact ? 'px-2.5 py-1.5' : 'px-4 py-2'
        )}
      >
        <div className={cn('font-semibold text-white', compact ? 'text-xs' : 'text-sm')}>
          {d.label}
        </div>
        <div className={cn('text-white/80', compact ? 'text-[10px] leading-tight' : 'text-xs')}>
          {categoryStyle.label}
        </div>
      </div>

      {/* Body */}
      <div className={cn(compact ? 'px-2.5 py-2 space-y-1.5' : 'px-4 py-3 space-y-2')}>
        {/* Parameters */}
        {d.parameters.map((param) => (
          <div key={param.id} className="space-y-1">
            <label
              className={cn(
                'text-white/90 font-medium',
                compact ? 'text-[10px]' : 'text-xs'
              )}
            >
              {param.label}
            </label>
            {param.type === 'number' && (
              <input
                type="number"
                value={param.value}
                onChange={(e) =>
                  onParamChange(param.id, e.target.value === '' ? 0 : Number(e.target.value))
                }
                disabled={!graphEdit?.componentId}
                className={cn(
                  'w-full rounded bg-white/80 border border-wood-brown disabled:opacity-60',
                  compact ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm'
                )}
              />
            )}
            {param.type === 'string' && (
              <input
                type="text"
                value={String(param.value ?? '')}
                onChange={(e) => onParamChange(param.id, e.target.value)}
                disabled={!graphEdit?.componentId}
                className={cn(
                  'w-full rounded bg-white/80 border border-wood-brown disabled:opacity-60',
                  compact ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm'
                )}
              />
            )}
            {param.type === 'boolean' && (
              <input
                type="checkbox"
                checked={Boolean(param.value)}
                onChange={(e) => onParamChange(param.id, e.target.checked)}
                disabled={!graphEdit?.componentId}
                className="h-4 w-4 rounded border-wood-brown"
              />
            )}
            {param.type === 'select' && (
              <select
                value={param.value}
                onChange={(e) => onParamChange(param.id, e.target.value)}
                disabled={!graphEdit?.componentId}
                className={cn(
                  'w-full rounded bg-white/80 border border-wood-brown disabled:opacity-60',
                  compact ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm'
                )}
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

        {!hideBehavior && (
          <div
            className="space-y-1 pt-1 border-t border-black/10"
            onPointerDown={(e) => e.stopPropagation()}
          >
            <label className="text-xs text-white/90 font-medium" htmlFor={`behavior-${id}`}>
              What this node does
            </label>
            <textarea
              id={`behavior-${id}`}
              rows={3}
              placeholder="Describe behavior in plain language for AI / compilation…"
              value={d.behaviorDescription ?? ''}
              onChange={onBehaviorChange}
              readOnly={!graphEdit?.componentId}
              className={cn(
                'w-full px-2 py-1.5 text-sm rounded bg-white/90 border border-wood-brown text-foreground resize-y min-h-[4rem]',
                !graphEdit?.componentId && 'opacity-70 cursor-not-allowed'
              )}
            />
          </div>
        )}
      </div>

      {/* Input Handles */}
      {d.inputs.map((input, index) => (
        <Handle
          key={input.id}
          type="target"
          position={Position.Left}
          id={input.id}
          style={{
            top: `${((index + 1) / (d.inputs.length + 1)) * 100}%`,
            background: input.type === 'exec' ? '#fff' : getPortColor(input.type),
            width: input.type === 'exec' ? '12px' : '10px',
            height: input.type === 'exec' ? '12px' : '10px',
            borderRadius: input.type === 'exec' ? '2px' : '50%',
          }}
        />
      ))}

      {/* Output Handles */}
      {d.outputs.map((output, index) => (
        <Handle
          key={output.id}
          type="source"
          position={Position.Right}
          id={output.id}
          style={{
            top: `${((index + 1) / (d.outputs.length + 1)) * 100}%`,
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
