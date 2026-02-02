import { useState } from 'react'
import { OrangeButton } from '@/components/shared/OrangeButton'
import { PastelBadge } from '@/components/shared/PastelBadge'
import { ProjectCard } from './ProjectCard'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Grid, List, Search, Plus, Sparkles } from 'lucide-react'
import type { Project } from '@/types/project'

// Mock data for now
const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Dragon Legends TCG',
    description: 'Epic fantasy trading card game with dragons, magic, and ancient artifacts. Features...',
    status: 'development',
    aiAssistantType: 'Creative Master AI',
    createdAt: '2024-01-15',
    updatedAt: '2024-01-20',
  },
  {
    id: '2',
    name: 'Cyber Wars',
    description: 'Futuristic cyberpunk TCG set in a dystopian world where hackers battle through digital...',
    status: 'published',
    aiAssistantType: 'Strategy AI Pro',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-18',
  },
  {
    id: '3',
    name: "Nature's Guardians",
    description: 'Environmental-themed card game focusing on protecting nature and wildlife through...',
    status: 'draft',
    aiAssistantType: 'Eco Design AI',
    createdAt: '2024-01-12',
    updatedAt: '2024-01-19',
  },
]

export function Dashboard() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredProjects = mockProjects.filter((project) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="mb-8 wood-texture bg-beige-light/50 rounded-xl p-8 border-2 border-wood-brown">
          <div className="flex items-center gap-3 mb-4">
            <PastelBadge color="purple" className="flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              AI-Powered
            </PastelBadge>
            <PastelBadge color="blue">
              {filteredProjects.length} Active Projects
            </PastelBadge>
          </div>
          
          <h1 className="text-4xl font-heading text-text-primary mb-4">
            Your Game Studio
          </h1>
          
          <p className="text-text-secondary max-w-3xl mb-6">
            Create amazing Trading Card Games with the power of AI. Design, balance,
            and publish your games with intelligent assistance.
          </p>
          
          <OrangeButton size="lg" className="flex items-center gap-2">
            <Plus className="w-5 h-5" />
            Create New Project
          </OrangeButton>
        </div>

        {/* Search and Controls */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" />
            <Input
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('grid')}
            >
              <Grid className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('list')}
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>

        {/* Empty State */}
        {filteredProjects.length === 0 && (
          <div className="text-center py-16">
            <p className="text-text-secondary text-lg">
              No projects found. Try a different search or create a new project!
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
