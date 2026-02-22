import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Settings, Sparkles, Calendar, MoreVertical } from 'lucide-react'
import type { Project } from '@/types/project'

interface ProjectCardProps {
  project: Project
}

const statusVariant: Record<Project['status'], 'success' | 'warning' | 'secondary'> = {
  published: 'success',
  development: 'warning',
  draft: 'secondary',
}

export function ProjectCard({ project }: ProjectCardProps) {
  const navigate = useNavigate()

  const handleOpen = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    navigate(`/workspace/${project.id}`)
  }

  return (
    <Card className="group gradient-card border border-card-border hover:shadow-lg transition-all duration-300 hover:border-primary/30 card-hover overflow-hidden">
      <CardHeader className="relative p-0">
        {/* Thumbnail */}
        <div className="aspect-video bg-muted rounded-t-lg relative overflow-hidden flex items-center justify-center">
          <div className="w-full h-full gradient-hero flex items-center justify-center">
            <Play className="h-12 w-12 text-primary/60" />
          </div>
          <Badge
            variant={statusVariant[project.status]}
            className="absolute top-2 right-2 capitalize"
          >
            {project.status}
          </Badge>
        </div>
        <div className="p-4 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-lg text-card-foreground group-hover:text-primary transition-colors line-clamp-1">
              {project.name}
            </h3>
            <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-muted-foreground text-sm line-clamp-2">{project.description}</p>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 pt-0">
        <div className="flex items-center gap-2 p-2.5 bg-primary-muted rounded-lg">
          <Sparkles className="h-4 w-4 text-primary shrink-0" />
          <span className="text-sm font-medium text-primary truncate">{project.aiAssistantType}</span>
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Calendar className="h-3.5 w-3.5 shrink-0" />
          <span>Updated {project.updatedAt}</span>
        </div>
      </CardContent>

      <CardFooter className="gap-2 pt-0">
        <Button variant="default" size="sm" className="flex-1" onClick={handleOpen}>
          <Play className="h-4 w-4" />
          Open
        </Button>
        <Button variant="outline" size="sm" className="shrink-0">
          <Settings className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  )
}
