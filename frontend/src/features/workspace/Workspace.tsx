import { useParams } from 'react-router-dom'
import { useAppSelector } from '@/app/hooks'
import { WorkspaceCanvas } from './canvas/WorkspaceCanvas'
import { ToolSidebar } from './panels/ToolSidebar'
import { AIAssistant } from '../ai-assistant/AIAssistant'

export function Workspace() {
  const { projectId } = useParams<{ projectId: string }>()
  const { isAiPanelOpen, aiPanelWidth } = useAppSelector((state) => state.workspace)

  return (
    <div className="h-[calc(100vh-4rem)] flex min-h-0">
      {/* Left Sidebar — not inside overflow-hidden so template flyouts can extend over the canvas */}
      <div className="relative z-50 shrink-0">
        <ToolSidebar />
      </div>

      {/* Center Canvas — clip scroll/zoom to this region only */}
      <div className="flex-1 min-w-0 min-h-0 overflow-hidden relative">
        <WorkspaceCanvas projectId={projectId || ''} />
      </div>

      {/* Right Sidebar - AI Assistant */}
      {isAiPanelOpen && (
        <div
          style={{ width: `${aiPanelWidth}px` }}
          className="shrink-0 border-l-2 border-wood-brown bg-white/80 backdrop-blur-sm overflow-hidden min-h-0"
        >
          <AIAssistant />
        </div>
      )}
    </div>
  )
}
