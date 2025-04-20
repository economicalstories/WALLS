"use client"

import { cn } from "@/lib/utils"
import Image from "next/image"
import { SkewedRectanglesBackground } from "./skewed-rectangles-background"

interface HoverCardProps {
  title: string
  description: string
  staticImage?: string
  hoverImage?: string
  className?: string
  height?: string
  darkOverlay?: boolean
}

export function HoverCard({
  title,
  description,
  staticImage = "https://images.unsplash.com/photo-1476842634003-7dcca8f832de",
  hoverImage = "https://images.unsplash.com/photo-1476842634003-7dcca8f832de",
  className,
  height = "h-96",
  darkOverlay = true,
}: HoverCardProps) {
  return (
    <div className={cn("w-full", className)}>
      <div
        className={cn(
          "group relative flex cursor-pointer flex-col justify-end overflow-hidden rounded-md border border-transparent p-4 shadow-xl dark:border-neutral-800",
          height,
          "transition-all duration-500"
        )}
      >
        {/* Base background with skewed rectangles */}
        <SkewedRectanglesBackground rotateTop={30} rotateBottom={-30} />

        {/* Static image */}
        <div className="absolute inset-0">
          <Image
            src={staticImage}
            alt=""
            fill
            className="object-cover transition-opacity duration-500 group-hover:opacity-0"
            priority
          />
        </div>

        {/* Hover image */}
        <div className="absolute inset-0">
          <Image
            src={hoverImage}
            alt=""
            fill
            className="object-cover opacity-0 transition-opacity duration-500 group-hover:opacity-100"
            priority
          />
        </div>

        {/* Permanent dark gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/60 to-black/20" />

        {/* Additional dark overlay on hover */}
        {darkOverlay && (
          <div className="absolute inset-0 bg-black opacity-0 transition-opacity duration-500 group-hover:opacity-30" />
        )}

        {/* Content */}
        <div className="relative z-50">
          <h3 className="relative text-xl font-bold text-white transition-colors duration-500 group-hover:text-white dark:text-white md:text-2xl">
            {title}
          </h3>
          <p className="relative my-4 text-base font-normal text-neutral-100 transition-colors duration-500 group-hover:text-neutral-100 dark:text-neutral-100">
            {description}
          </p>
        </div>
      </div>
    </div>
  )
}
