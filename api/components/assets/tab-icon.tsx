"use client"

import * as TablerIcons from "@tabler/icons-react"
import { cn } from "@/lib/utils"

function getIconComponent(iconName: string) {
  // Convert kebab-case to PascalCase and add 'Icon' prefix
  const componentName =
    "Icon" +
    iconName
      .split("-")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
      .join("")

  return (TablerIcons as any)[componentName]
}

export function TabIcon({
  name,
  isActive,
  size = 16,
}: {
  name: string
  isActive: boolean
  size?: number
}) {
  const IconComponent = getIconComponent(name)
  if (!IconComponent) return null

  return (
    <IconComponent
      size={size}
      className={cn(
        "relative shrink-0",
        isActive ? "text-primary dark:text-primary" : "text-muted-foreground"
      )}
    />
  )
}
