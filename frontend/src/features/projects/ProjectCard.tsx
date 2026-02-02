import { useNavigate } from 'react-router-dom'
import { WoodCard } from '@/components/shared/WoodCard'
import { PastelBadge } from '@/components/shared/PastelBadge'
import { CardContent, CardFooter } from '@/components/ui/card'
import type { Project } from '@/types/project'

interface ProjectCardProps {
  project: Project
}

const statusColors = {
  development: 'yellow' as const,
  published: 'green' as const,
  draft: 'blue' as const,
}

export function ProjectCard({ project }: ProjectCardProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    navigate(`/workspace/${project.id}`)
  }

  return (
    <WoodCard
      onClick={handleClick}
      className="cursor-pointer hover:shadow-xl transition-all"
    >
      <div className="p-6">
        {/* Status Badge */}
        <div className="flex justify-between items-start mb-4">
          <PastelBadge color={statusColors[project.status]}>
            {project.status}
          </PastelBadge>
        </div>

        {/* Play Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-24 h-24 rounded-lg bg-beige-light flex items-center justify-center group-hover:bg-orange-primary/10 transition-colors">
            <div className="w-0 h-0 border-t-[20px] border-t-transparent border-l-[30px] border-l-orange-primary border-b-[20px] border-b-transparent ml-2" />
          </div>
        </div>

        {/* Project Info */}
        <CardContent className="p-0">
          <h3 className="text-xl font-heading text-text-primary mb-2">
            {project.name}
          </h3>
          <p className="text-sm text-text-secondary line-clamp-2">
            {project.description}
          </p>
        </CardContent>

        {/* AI Assistant Badge */}
        <CardFooter className="p-0 pt-4">
          <div className="w-full flex justify-center">
            <PastelBadge color="yellow" className="bg-orange-primary text-white">
              {project.aiAssistantType}
            </PastelBadge>
          </div>
        </CardFooter>
      </div>
    </WoodCard>
  )
}
