import { useAppDispatch, useAppSelector } from '@/app/hooks'
import { setSelectedTool } from '../workspaceSlice'
import { Button } from '@/components/ui/button'
import { 
  MousePointer2, 
  Square, 
  Type, 
  Circle, 
  Plus 
} from 'lucide-react'
import { cn } from '@/lib/utils'

const tools = [
  { id: 'select', icon: MousePointer2, label: 'Select' },
  { id: 'card', icon: Square, label: 'Card' },
  { id: 'text', icon: Type, label: 'Text' },
  { id: 'shape', icon: Circle, label: 'Shape' },
  { id: 'add', icon: Plus, label: 'Add Node' },
]

export function ToolSidebar() {
  const dispatch = useAppDispatch()
  const { selectedTool } = useAppSelector((state) => state.workspace)

  return (
    <div className="w-16 bg-white/80 backdrop-blur-sm border-r-2 border-wood-brown flex flex-col items-center py-4 gap-2">
      {tools.map((tool) => {
        const Icon = tool.icon
        const isActive = selectedTool === tool.id
        
        return (
          <Button
            key={tool.id}
            variant="ghost"
            size="icon"
            onClick={() => dispatch(setSelectedTool(tool.id))}
            className={cn(
              "w-12 h-12 rounded-lg transition-all",
              isActive && "bg-orange-primary text-white hover:bg-orange-hover hover:text-white"
            )}
            title={tool.label}
          >
            <Icon className="w-5 h-5" />
          </Button>
        )
      })}
    </div>
  )
}
