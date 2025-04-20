"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import Image from "next/image"
import { cn } from "@/lib/utils"

export interface SectorFeature {
  columnText: string
  verticalText: string
  horizontalText: string
  heading: string
  description: string
  image?: {
    src: string
    alt?: string
  }
}

// Helper function to convert HTML string to React elements
function parseDescription(description: string) {
  const parts = description.split("<br /><br />")
  return parts.map((part, index) => {
    // Extract "Why We Matter" and "What We Need" sections
    if (part.includes("class='text-white font-semibold'>")) {
      const [label, content] = part.split("</span>")
      const labelText = label.split(">").pop()
      return (
        <div key={index} className="mb-4 last:mb-0">
          <span className="font-semibold text-white">{labelText}</span>
          {content}
        </div>
      )
    }
    return (
      <div key={index} className="mb-4 last:mb-0">
        {part}
      </div>
    )
  })
}

interface ExpandableSectorsProps {
  tagline?: string
  heading: string
  description: string
  features: SectorFeature[]
  className?: string
}

export function ExpandableSectors({
  tagline,
  heading,
  description,
  features,
  className,
}: ExpandableSectorsProps) {
  const [activeIndex, setActiveIndex] = useState<number>(0)

  const handleSetActive = (index: number) => {
    setActiveIndex(index)
  }

  return (
    <div className={cn("w-full", className)}>
      <div className="mx-auto max-w-4xl">
        {tagline && (
          <p className="mb-3 text-sm font-semibold uppercase tracking-wider text-neutral-600 dark:text-neutral-400">
            {tagline}
          </p>
        )}
        <h2 className="mb-4 text-3xl font-bold text-neutral-900 dark:text-neutral-100 md:text-4xl">
          {heading}
        </h2>
        <p className="mb-12 text-lg text-neutral-600 dark:text-neutral-400">
          {description}
        </p>
      </div>

      <div className="flex w-full flex-col overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900">
        {/* Sector Labels */}
        <div className="flex border-b border-neutral-200 dark:border-neutral-800">
          {features.map((feature, index) => (
            <button
              key={index}
              onClick={() => handleSetActive(index)}
              className={cn(
                "flex-1 px-4 py-3 text-center transition-colors",
                activeIndex === index
                  ? "bg-neutral-100 font-semibold text-neutral-900 dark:bg-neutral-800 dark:text-neutral-100"
                  : "text-neutral-500 hover:bg-neutral-50 dark:text-neutral-400 dark:hover:bg-neutral-800/50"
              )}
            >
              {feature.horizontalText}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="flex">
          {/* Emoji Sidebar */}
          <div className="flex w-20 flex-shrink-0 flex-col border-r border-neutral-200 dark:border-neutral-800">
            {features.map((feature, index) => (
              <button
                key={index}
                onClick={() => handleSetActive(index)}
                className={cn(
                  "flex h-20 items-center justify-center border-b border-neutral-200 text-3xl transition-all dark:border-neutral-800",
                  activeIndex === index
                    ? "bg-neutral-100 dark:bg-neutral-800"
                    : "grayscale hover:bg-neutral-50 dark:hover:bg-neutral-800/50"
                )}
              >
                <span className={activeIndex === index ? "" : "opacity-50"}>
                  {feature.columnText}
                </span>
              </button>
            ))}
          </div>

          {/* Main Content */}
          <div className="flex-grow">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="h-full"
              >
                <div className="flex h-full flex-col px-6 pb-8 pt-4 md:px-10 md:pb-12 md:pt-8">
                  <h4 className="mb-4 text-2xl font-bold text-neutral-900 dark:text-neutral-100 md:text-3xl">
                    {features[activeIndex].heading}
                  </h4>
                  <div className="mb-8 whitespace-pre-wrap text-neutral-600 dark:text-neutral-400">
                    {parseDescription(features[activeIndex].description)}
                  </div>
                  {features[activeIndex].image && (
                    <div className="relative mt-auto aspect-video w-full overflow-hidden rounded-lg">
                      <Image
                        src={features[activeIndex].image.src}
                        alt={features[activeIndex].image.alt || ""}
                        fill
                        className="object-cover"
                      />
                    </div>
                  )}
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  )
}
