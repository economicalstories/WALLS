"use client"

import { cn } from "@/lib/utils"
import React from "react"
import { GlowingEffect } from "@/components/ui/glowing-effect"
import Link from "next/link"
import { motion } from "framer-motion"

export interface Value {
  title: string
  description: string
  icon?: React.ReactNode
  className?: string
  id: string
  href?: string
  color?: "blue" | "purple" | "emerald" | "amber"
}

interface ValuesGridProps {
  values: Value[]
  className?: string
}

export function ValuesGrid({ values, className }: ValuesGridProps) {
  return (
    <ul className={cn("grid grid-cols-1 gap-6", className)}>
      {values.map((value) => (
        <GridItem key={value.id} {...value} />
      ))}
    </ul>
  )
}

interface GridItemProps extends Value {}

const GridItem = ({
  icon,
  title,
  description,
  className,
  href,
  color = "blue",
}: GridItemProps) => {
  const colorStyles = {
    blue: {
      border: "border-blue-900/50",
      bg: "bg-blue-950/30",
      text: "text-blue-400",
      glow: "#60A5FA",
      hover: "hover:border-blue-800/80 hover:bg-blue-950/50",
    },
    purple: {
      border: "border-purple-900/50",
      bg: "bg-purple-950/30",
      text: "text-purple-400",
      glow: "#A78BFA",
      hover: "hover:border-purple-800/80 hover:bg-purple-950/50",
    },
    emerald: {
      border: "border-emerald-900/50",
      bg: "bg-emerald-950/30",
      text: "text-emerald-400",
      glow: "#34D399",
      hover: "hover:border-emerald-800/80 hover:bg-emerald-950/50",
    },
    amber: {
      border: "border-amber-900/50",
      bg: "bg-amber-950/30",
      text: "text-amber-400",
      glow: "#FBBF24",
      hover: "hover:border-amber-800/80 hover:bg-amber-950/50",
    },
  }

  const content = (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 400, damping: 10 }}
      className={cn(
        "relative h-full w-full rounded-3xl border p-6",
        colorStyles[color].border,
        colorStyles[color].bg,
        colorStyles[color].hover,
        "transition-colors duration-300"
      )}
    >
      <GlowingEffect
        spread={40}
        glow={true}
        disabled={false}
        proximity={64}
        inactiveZone={0.01}
        color={colorStyles[color].glow}
      />
      <div className="relative flex h-full w-full flex-col gap-6">
        {icon && (
          <div
            className={cn(
              "w-fit rounded-lg border p-3",
              colorStyles[color].border,
              colorStyles[color].bg,
              colorStyles[color].text
            )}
          >
            <div>{icon}</div>
          </div>
        )}
        <div className="space-y-3">
          <h3 className="font-sans text-2xl font-semibold text-white">
            {title}
          </h3>
          <p className="font-sans text-base text-neutral-400">{description}</p>
        </div>
      </div>
    </motion.div>
  )

  if (href) {
    return (
      <li className={cn("h-full w-full cursor-pointer list-none", className)}>
        <Link href={href} className="block h-full w-full no-underline">
          {content}
        </Link>
      </li>
    )
  }

  return <li className={cn("h-full w-full list-none", className)}>{content}</li>
}
