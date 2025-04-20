"use client"

import { cn } from "@/lib/utils"
import React from "react"
import { GlowingEffect } from "@/components/ui/glowing-effect"

export interface Feature {
  title: string
  description: string
  icon?: React.ReactNode
  area?: string
  id: string
  content?: React.ReactNode
}

interface FeaturesGridProps {
  features: Feature[]
  className?: string
}

const DEFAULT_GRID_AREAS = [
  "md:[grid-area:1/1/2/4] xl:[grid-area:1/1/2/1]", // Common Agenda - left top
  "md:[grid-area:1/10/2/13] xl:[grid-area:1/3/2/3]", // Reinforcing Activities - right top (swapped)
  "md:[grid-area:1/4/3/10] xl:[grid-area:1/2/3/2]", // Shared Measurement - middle (swapped)
  "md:[grid-area:2/1/3/4] xl:[grid-area:2/1/3/1]", // Continuous Communication - left bottom
  "md:[grid-area:2/10/3/13] xl:[grid-area:2/3/3/3]", // Backbone Support - right bottom
]

export function FeaturesGrid({ features, className }: FeaturesGridProps) {
  return (
    <ul
      className={cn(
        "grid grid-cols-1 grid-rows-none gap-6 md:grid-cols-12 md:grid-rows-2 xl:grid-rows-2",
        className
      )}
    >
      {features.map((feature, index) => (
        <GridItem
          key={feature.id}
          {...feature}
          area={feature.area || DEFAULT_GRID_AREAS[index]}
        />
      ))}
    </ul>
  )
}

interface GridItemProps extends Feature {
  area: string
}

const GridItem = ({
  area,
  icon,
  title,
  description,
  content,
}: GridItemProps) => {
  return (
    <li className={`h-full min-h-[14rem] w-full list-none ${area}`}>
      <div className="relative h-full w-full rounded-3xl border border-neutral-800 bg-[#0A0A0A] p-6">
        <GlowingEffect
          spread={40}
          glow={true}
          disabled={false}
          proximity={64}
          inactiveZone={0.01}
        />
        <div className="relative flex h-full w-full flex-col gap-6">
          {icon && (
            <div className="w-fit rounded-lg border border-blue-900/50 bg-blue-950/30 p-3">
              <div className="text-blue-400">{icon}</div>
            </div>
          )}
          <div className="space-y-3">
            <h3 className="font-sans text-2xl font-semibold text-white">
              {title}
            </h3>
            <p className="font-sans text-base text-neutral-400">
              {description}
            </p>
            {content && <div className="mt-4 text-neutral-400">{content}</div>}
          </div>
        </div>
      </div>
    </li>
  )
}
