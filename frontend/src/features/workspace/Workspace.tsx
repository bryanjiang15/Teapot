import { useParams } from 'react-router-dom'
import { useAppSelector } from '@/app/hooks'
import { WorkspaceCanvas } from './canvas/WorkspaceCanvas'
import { ToolSidebar } from './panels/ToolSidebar'
import { AIAssistant } from '../ai-assistant/AIAssistant'

export function Workspace() {
  const { projectId } = useParams<{ projectId: string }>()
  const { isAiPanelOpen, aiPanelWidth } = useAppSelector((state) => state.workspace)

  return (
    <div className="h-[calc(100vh-4rem)] flex overflow-hidden">
      {/* Left Sidebar - Tools */}
      <ToolSidebar />

      {/* Center Canvas */}
      <div className="flex-1 relative">
        <WorkspaceCanvas projectId={projectId || ''} />
      </div>

      {/* Right Sidebar - AI Assistant */}
      {isAiPanelOpen && (
        <div
          style={{ width: `${aiPanelWidth}px` }}
          className="border-l-2 border-wood-brown bg-white/80 backdrop-blur-sm"
        >
          <AIAssistant />
        </div>
      )}
    </div>
  )
}
