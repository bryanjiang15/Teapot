import { useState } from 'react'
import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { addNodeToComponent } from '../workspaceSlice'
import { NODE_CATEGORIES } from '@/types/nodes'
import type { NodeCategory } from '@/types/nodes'
import { NODE_FAMILY_TEMPLATES } from '@/lib/nodeRegistry'
import { cn } from '@/lib/utils'
import { Zap, Database, TextCursorInput, GitBranch, Workflow } from 'lucide-react'

const FAMILY_ICONS: Record<NodeCategory, typeof Zap> = {
  trigger: Zap,
  state: Database,
  input: TextCursorInput,
  flow: GitBranch,
  function: Workflow,
}

export function ToolSidebar() {
  const dispatch = useAppDispatch()
  const { selectedComponentId } = useAppSelector((state) => state.workspace)
  const canAddNode = Boolean(selectedComponentId)
  const [openFamily, setOpenFamily] = useState<NodeCategory | null>(null)

  const handleAddNode = (templateId: string) => {
    if (!selectedComponentId) return
    dispatch(addNodeToComponent({ componentId: selectedComponentId, templateId }))
    setOpenFamily(null)
  }

  return (
    <div className="relative w-20 bg-white/80 backdrop-blur-sm border-r-2 border-wood-brown flex flex-col py-4 overflow-visible shrink-0">
      <div className="px-2 pb-2 border-b border-border mb-2 text-center">
        <h2 className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider leading-tight">
          Add
        </h2>
        <p className="text-[10px] text-muted-foreground mt-0.5 leading-tight">
          {canAddNode ? 'Pick family' : 'Select component'}
        </p>
      </div>
      <nav className="flex flex-col gap-2 px-2 overflow-visible">
        {NODE_FAMILY_TEMPLATES.map((family) => {
          const Icon = FAMILY_ICONS[family.category]
          const color = NODE_CATEGORIES[family.category].color
          const isOpen = openFamily === family.category

          return (
            <div key={family.category} className="relative flex flex-col items-center gap-1">
              <span className="text-[9px] font-medium text-muted-foreground uppercase tracking-wider text-center leading-tight px-0.5">
                {family.label}
              </span>
              <button
                type="button"
                onClick={() => canAddNode && setOpenFamily(isOpen ? null : family.category)}
                disabled={!canAddNode}
                title={canAddNode ? family.description : 'Select a component from the dropdown first'}
                className={cn(
                  'w-10 h-10 rounded-lg flex items-center justify-center border-2 transition-all shrink-0 cursor-pointer',
                  'hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed',
                  isOpen && canAddNode && 'ring-2 ring-offset-1 ring-wood-brown/60'
                )}
                style={{
                  backgroundColor: `${color}20`,
                  color,
                  borderColor: canAddNode ? (isOpen ? color : 'transparent') : 'transparent',
                }}
              >
                <Icon className="w-5 h-5" />
              </button>

              {isOpen && canAddNode && (
                <div
                  className="absolute left-full top-0 ml-1 z-[100] min-w-[200px] max-w-[260px] rounded-lg border border-card-border bg-card shadow-lg py-1 text-left"
                  onMouseLeave={() => setOpenFamily(null)}
                >
                  <div className="px-2 py-1.5 border-b border-border text-[10px] text-muted-foreground">
                    {family.description}
                  </div>
                  <ul className="py-1 max-h-[220px] overflow-y-auto" role="listbox">
                    {family.items.map((item) => (
                      <li key={item.templateId}>
                        <button
                          type="button"
                          role="option"
                          className="w-full text-left px-3 py-2 text-xs hover:bg-secondary transition-colors"
                          onClick={() => handleAddNode(item.templateId)}
                        >
                          {item.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )
        })}
      </nav>
    </div>
  )
}
