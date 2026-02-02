import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type PastelColor = "green" | "blue" | "purple" | "yellow"

interface PastelBadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  color: PastelColor
  children: React.ReactNode
}

export function PastelBadge({ color, children, className, ...props }: PastelBadgeProps) {
  return (
    <Badge
      variant={color}
      className={cn("rounded-full", className)}
      {...props}
    >
      {children}
    </Badge>
  )
}
