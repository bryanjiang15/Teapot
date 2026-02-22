import * as React from "react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface WoodCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export const WoodCard = React.forwardRef<HTMLDivElement, WoodCardProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <Card
        ref={ref}
        className={cn("gradient-card border border-card-border wood-texture card-hover rounded-lg", className)}
        {...props}
      >
        {children}
      </Card>
    )
  }
)

WoodCard.displayName = "WoodCard"
