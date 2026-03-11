import { useState } from 'react'
import { ProjectCard } from './ProjectCard'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Grid, List, Search, Plus, Sparkles } from 'lucide-react'
import { useGetProjectsQuery, useCreateProjectMutation } from '@/lib/api/projectsApi'

export function Dashboard() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')

  const { data: projects = [], isLoading } = useGetProjectsQuery()
  const [createProject, { isLoading: isCreating }] = useCreateProjectMutation()

  const filteredProjects = projects.filter(
    (project) =>
      project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="gradient-hero border-b border-border py-12 md:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Badge variant="secondary" className="mb-4 border-0">
            <Sparkles className="h-4 w-4 mr-1" />
            Your Studio
          </Badge>
          <h1 className="text-4xl font-heading font-bold text-foreground mb-4">
            Your Game Studio
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mb-8">
            Create amazing Trading Card Games with the power of AI. Design, balance, and publish with intelligent assistance.
          </p>
          <Button
            variant="hero"
            size="lg"
            className="gap-2"
            disabled={isCreating}
            onClick={async () => {
              try {
                await createProject({
                  name: 'New Project',
                  description: 'New Teapot project',
                  gameType: 'tcg',
                  aiAssistantType: 'Creative Master AI',
                }).unwrap()
              } catch {
                // In a real app we might show a toast; for now, fail silently.
              }
            }}
          >
            <Plus className="h-5 w-5" />
            {isCreating ? 'Creating…' : 'Create New Project'}
          </Button>
        </div>
      </section>

      {/* Search and controls */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-11"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('grid')}
              aria-label="Grid view"
            >
              <Grid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('list')}
              aria-label="List view"
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Projects grid */}
        {isLoading ? (
          <div className="py-16 text-center text-muted-foreground">Loading projects...</div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProjects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>

            {filteredProjects.length === 0 && (
              <div className="text-center py-16 rounded-lg border border-border bg-card/50">
                <p className="text-muted-foreground">
                  {projects.length === 0
                    ? 'You have no projects yet. Create your first project to get started.'
                    : 'No projects match your search. Try a different query or create a new project.'}
                </p>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  )
}
