import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { addNodeToComponent } from '../workspaceSlice'
import { NODE_CATEGORIES } from '@/types/nodes'
import { cn } from '@/lib/utils'
import { Zap, Workflow, GitBranch, MousePointerClick } from 'lucide-react'

/** One node option per category for the canvas. */
const NODE_CATEGORY_OPTIONS = [
  {
    id: 'event',
    label: 'Event',
    description: 'Start of a graph (e.g. On Game Start, On Card Played)',
    icon: Zap,
    templateId: 'event-game-start',
    color: NODE_CATEGORIES.event.color,
  },
  {
    id: 'function',
    label: 'Function',
    description: 'Do effects',
    icon: Workflow,
    templateId: 'function-draw-card',
    color: NODE_CATEGORIES.function.color,
  },
  {
    id: 'condition',
    label: 'Condition',
    description: 'Branch by condition (multiple output directions)',
    icon: GitBranch,
    templateId: 'flow-branch',
    color: NODE_CATEGORIES.flow.color,
  },
  {
    id: 'input',
    label: 'Input',
    description: 'Wait for user input',
    icon: MousePointerClick,
    templateId: 'input-wait',
    color: NODE_CATEGORIES.input.color,
  },
] as const

export function ToolSidebar() {
  const dispatch = useAppDispatch()
  const { selectedComponentId } = useAppSelector((state) => state.workspace)
  const canAddNode = Boolean(selectedComponentId)

  const handleAddNode = (templateId: string) => {
    if (!selectedComponentId) return
    dispatch(addNodeToComponent({ componentId: selectedComponentId, templateId }))
  }

  return (
    <div className="w-20 bg-white/80 backdrop-blur-sm border-r-2 border-wood-brown flex flex-col py-4 overflow-hidden">
      <div className="px-2 pb-2 border-b border-border mb-2 text-center">
        <h2 className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider leading-tight">
          Add
        </h2>
        <p className="text-[10px] text-muted-foreground mt-0.5 leading-tight">
          {canAddNode ? 'Click icon' : 'Select component'}
        </p>
      </div>
      <nav className="flex flex-col gap-3 px-2 overflow-y-auto">
        {NODE_CATEGORY_OPTIONS.map((option) => {
          const Icon = option.icon
          return (
            <div key={option.id} className="flex flex-col items-center gap-1">
              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                {option.label}
              </span>
              <button
                type="button"
                onClick={() => handleAddNode(option.templateId)}
                disabled={!canAddNode}
                title={canAddNode ? option.description : 'Select a component from the dropdown first'}
                className={cn(
                  'w-10 h-10 rounded-lg flex items-center justify-center border-2 transition-all shrink-0 cursor-pointer',
                  'hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed',
                  'border-transparent hover:border-current/30'
                )}
                style={{
                  backgroundColor: `${option.color}20`,
                  color: option.color,
                  borderColor: canAddNode ? undefined : 'transparent',
                }}
              >
                <Icon className="w-5 h-5" />
              </button>
            </div>
          )
        })}
      </nav>
    </div>
  )
}
