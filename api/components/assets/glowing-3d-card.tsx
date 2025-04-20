"use client"

import Image from "next/image"
import React from "react"
import { CardBody, CardContainer, CardItem } from "./3d-card"
import { GlowingEffect } from "./glowing-effect"
import { cn } from "@/lib/utils"
import Link from "next/link"

interface Glowing3DCardProps {
  title: string
  description: string
  imageSrc: string
  imageAlt: string
  primaryAction?: {
    text: string
    href: string
  }
  secondaryAction?: {
    text: string
    onClick: () => void
  }
  className?: string
}

export function Glowing3DCard({
  title,
  description,
  imageSrc,
  imageAlt,
  primaryAction,
  secondaryAction,
  className,
}: Glowing3DCardProps) {
  return (
    <CardContainer className={cn("h-full w-full", className)}>
      <CardBody className="group/card relative h-full w-full rounded-xl border border-black/[0.1] p-6 dark:border-white/[0.2] dark:bg-black dark:hover:shadow-2xl dark:hover:shadow-emerald-500/[0.1]">
        <GlowingEffect
          spread={40}
          glow={true}
          disabled={false}
          proximity={64}
          inactiveZone={0.01}
        />
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
        <CardItem translateZ="100" className="mt-4">
          <Image
            src={imageSrc}
            height="1000"
            width="1000"
            className="h-48 w-full rounded-xl object-cover group-hover/card:shadow-xl"
            alt={imageAlt}
          />
        </CardItem>
        {(primaryAction || secondaryAction) && (
          <div className="mt-4 flex items-center justify-between">
            {primaryAction && (
              <CardItem
                translateZ={20}
                as={Link}
                href={primaryAction.href}
                target="_blank"
                className="rounded-xl px-4 py-2 text-xs font-normal dark:text-white"
              >
                {primaryAction.text} →
              </CardItem>
            )}
            {secondaryAction && (
              <CardItem
                translateZ={20}
                as="button"
                onClick={secondaryAction.onClick}
                className="rounded-xl bg-black px-4 py-2 text-xs font-bold text-white dark:bg-white dark:text-black"
              >
                {secondaryAction.text}
              </CardItem>
            )}
          </div>
        )}
      </CardBody>
    </CardContainer>
  )
}
