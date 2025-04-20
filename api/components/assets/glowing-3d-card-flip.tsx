"use client"

import Image from "next/image"
import React, { useState } from "react"
import { CardBody, CardContainer, CardItem } from "./3d-card"
import { GlowingEffect } from "./glowing-effect"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { motion, useMotionValue, useTransform, useSpring } from "framer-motion"
import {
  CardBackgroundGenerator,
  BackgroundStyle,
  ColorScheme,
} from "./card-background-generator"

interface Glowing3DCardFlipProps {
  title: string
  description: string
  imageSrc?: string
  imageAlt?: string
  content: React.ReactNode
  icon?: React.ReactNode
  primaryAction?: {
    text: string
    href: string
  }
  secondaryAction?: {
    text: string
    onClick: () => void
  }
  className?: string
  backgroundStyle?: BackgroundStyle
  colorScheme?: string | ColorScheme
}

export function Glowing3DCardFlip({
  title,
  description,
  imageSrc,
  imageAlt,
  content,
  icon,
  primaryAction,
  secondaryAction,
  className,
  backgroundStyle,
  colorScheme,
}: Glowing3DCardFlipProps) {
  const [isFlipped, setIsFlipped] = useState(false)

  // Create a motion value for the flip rotation
  const flipRotation = useSpring(0, {
    stiffness: 300,
    damping: 30,
  })

  // Create transforms for each side's opacity based on the rotation
  const frontOpacity = useTransform(flipRotation, [-90, 0, 90], [0, 1, 0])
  const backOpacity = useTransform(flipRotation, [-90, 0, 90], [1, 0, 1])

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
    flipRotation.set(isFlipped ? 0 : 180)
  }

  return (
    <div className={cn("relative isolate h-full w-full", className)}>
      <div className="preserve-3d perspective-[2000px] relative h-full w-full">
        {/* Front of card */}
        <motion.div
          className="backface-hidden absolute inset-0 h-full w-full"
          style={{
            rotateY: flipRotation,
            opacity: frontOpacity,
            transformStyle: "preserve-3d",
          }}
        >
          <CardContainer className="h-full w-full">
            <div onClick={handleFlip}>
              <CardBody className="group/card relative h-[400px] w-full cursor-pointer rounded-xl border border-black/[0.1] bg-white p-6 dark:border-white/[0.2] dark:bg-black dark:hover:shadow-2xl dark:hover:shadow-emerald-500/[0.1]">
                <GlowingEffect
                  spread={40}
                  glow={true}
                  disabled={false}
                  proximity={64}
                  inactiveZone={0.01}
                />
                {/* Front of card icon */}
                {icon && (
                  <CardItem
                    translateZ={0}
                    className="absolute bottom-1.5 left-0 flex w-full justify-center"
                  >
                    <div className="text-neutral-600 dark:text-white">
                      {icon}
                    </div>
                  </CardItem>
                )}
                <CardItem
                  translateZ="50"
                  className="text-xl font-bold text-neutral-600 dark:text-white"
                >
                  {title}
                </CardItem>
                <CardItem
                  as="p"
                  translateZ="60"
                  className="mt-2 text-sm text-neutral-500 dark:text-neutral-300"
                >
                  {description}
                </CardItem>
                <CardItem translateZ="50" className="mt-4 h-48">
                  {imageSrc ? (
                    <Image
                      src={imageSrc}
                      height="1000"
                      width="1000"
                      className="h-full w-full rounded-xl object-cover group-hover/card:shadow-xl"
                      alt={imageAlt || "Card image"}
                    />
                  ) : (
                    <div className="h-full w-full overflow-hidden rounded-xl">
                      <CardBackgroundGenerator
                        width={1000}
                        height={192}
                        style={backgroundStyle || "gradient"}
                        colorScheme={colorScheme || "emerald"}
                        icon={icon}
                        iconScale={2}
                        className="h-full w-full"
                      />
                    </div>
                  )}
                </CardItem>
                {(primaryAction || secondaryAction) && (
                  <div className="mt-4 flex items-center justify-between">
                    {primaryAction && (
                      <CardItem
                        translateZ={20}
                        as={Link}
                        href={primaryAction.href}
                        target="_blank"
                        className="rounded-xl px-4 text-xs font-normal dark:text-white"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {primaryAction.text} →
                      </CardItem>
                    )}
                    {secondaryAction && (
                      <CardItem
                        translateZ={20}
                        as="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          secondaryAction.onClick()
                        }}
                        className="rounded-xl bg-black px-4 py-0 text-xs font-bold text-white dark:bg-white dark:text-black"
                      >
                        {secondaryAction.text}
                      </CardItem>
                    )}
                  </div>
                )}
              </CardBody>
            </div>
          </CardContainer>
        </motion.div>

        {/* Back of card */}
        <motion.div
          className="backface-hidden absolute inset-0 h-full w-full"
          style={{
            rotateY: useTransform(flipRotation, (r) => r + 180),
            opacity: backOpacity,
            transformStyle: "preserve-3d",
          }}
        >
          <CardContainer className="h-full w-full">
            <div onClick={handleFlip}>
              <CardBody className="group/card relative h-[400px] w-full cursor-pointer rounded-xl border border-black/[0.1] bg-white dark:border-white/[0.2] dark:bg-black dark:hover:shadow-2xl dark:hover:shadow-emerald-500/[0.1]">
                <GlowingEffect
                  spread={40}
                  glow={true}
                  disabled={false}
                  proximity={64}
                  inactiveZone={0.01}
                />
                {/* Back of card icon as watermark */}
                {icon && (
                  <CardItem
                    translateZ={0}
                    className="absolute inset-0 flex items-center justify-center opacity-10"
                  >
                    <div className="scale-[4] transform text-neutral-600 dark:text-white">
                      {icon}
                    </div>
                  </CardItem>
                )}
                <div className="flex h-full flex-col">
                  <div className="flex items-center justify-between bg-neutral-50 px-6 py-4 dark:bg-neutral-900">
                    <CardItem
                      translateZ="50"
                      className="text-xl font-bold text-neutral-600 dark:text-white"
                    >
                      {title}
                    </CardItem>
                    <CardItem
                      translateZ="50"
                      as="button"
                      onClick={handleFlip}
                      className="text-sm text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200"
                    >
                      ← Back
                    </CardItem>
                  </div>
                  <CardItem translateZ="60" className="min-h-0 flex-1 pl-6">
                    <div className="prose prose-sm h-full overflow-y-auto pb-4 pr-2 dark:prose-invert">
                      {content}
                    </div>
                  </CardItem>
                </div>
              </CardBody>
            </div>
          </CardContainer>
        </motion.div>
      </div>
    </div>
  )
}
