import * as React from "react"
import { Button, type ButtonProps } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export const OrangeButton = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, ...props }, ref) => {
    return (
      <Button
        ref={ref}
        variant="orange"
        className={cn(className)}
        {...props}
      />
    )
  }
)

OrangeButton.displayName = "OrangeButton"
