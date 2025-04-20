"use client"

import Image from "next/image"
import React from "react"
import { motion } from "framer-motion"
import { Spotlight } from "@/components/ui/spotlight"
import Link from "next/link"

interface Logo {
  name: string
  src: string
  darkMode:
    | { type: "full-invert" }
    | { type: "partial-invert" }
    | { type: "preserve-color" }
    | { type: "custom"; filter: string }
}

export function ParticipantsLogoCloud() {
  const logos: Logo[] = [
    {
      name: "ANZSOG",
      src: "/images/logos/anzsog.jpg",
      darkMode: {
        type: "custom",
        filter:
          "dark:brightness-[2] dark:contrast-[2] dark:grayscale dark:invert rounded-lg",
      },
    },
    {
      name: "Australian Government",
      src: "/images/logos/Australian-Government.svg",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "Dragonfly Thinking",
      src: "/images/logos/DragonflyThinking.png",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "Gradient Institute",
      src: "/images/logos/GradientInstitute.svg",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "IBM",
      src: "/images/logos/IBM.svg",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "Inclusive Design Collective",
      src: "/images/logos/InclusiveDesignCollective.png",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "InfoXChange",
      src: "/images/logos/InfoXChange.svg",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "NSW Government",
      src: "/images/logos/NSWGovt.svg",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "Nous Group",
      src: "/images/logos/Nous.png",
      darkMode: {
        type: "custom",
        filter: "dark:invert-[85%] dark:saturate-[200%] dark:hue-rotate-180",
      },
    },
    {
      name: "Tech Council of Australia",
      src: "/images/logos/Tech_council.svg",
      darkMode: {
        type: "custom",
        filter:
          "invert-[0.7] hue-rotate-[180deg] brightness-[1.4] contrast-[1.3] saturate-[0.6] dark:invert-[0] dark:brightness-[0.8] dark:contrast-[1.2] dark:hue-rotate-[0deg] dark:saturate-[3]",
      },
    },
  ]

  const getDarkModeClass = (darkMode: Logo["darkMode"]) => {
    return darkMode.type === "custom" ? darkMode.filter : ""
  }

  return (
    <div className="relative w-full overflow-hidden py-6">
      <div className="relative overflow-hidden rounded-lg bg-gradient-to-br from-blue-50/50 to-blue-100/50 backdrop-blur-sm dark:from-blue-900/30 dark:to-blue-800/30">
        <Spotlight
          gradientFirst="radial-gradient(68.54% 68.72% at 55.02% 31.46%, hsla(210, 100%, 85%, .2) 0, hsla(210, 100%, 55%, .1) 50%, hsla(210, 100%, 45%, .05) 80%)"
          gradientSecond="radial-gradient(50% 50% at 50% 50%, hsla(210, 100%, 85%, .15) 0, hsla(210, 100%, 45%, .1) 80%, transparent 100%)"
          gradientThird="radial-gradient(50% 50% at 50% 50%, hsla(210, 100%, 85%, .1) 0, hsla(210, 100%, 45%, .05) 80%, transparent 100%)"
          translateY={-200}
          width={400}
          height={800}
          smallWidth={200}
          duration={10}
          xOffset={50}
        />
        <div className="relative z-10 p-12">
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {logos.map((logo) => (
              <motion.div
                key={logo.src}
                className="flex items-center justify-center p-2"
                whileHover={{ scale: 1.1 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                <Image
                  src={logo.src}
                  alt={logo.name}
                  width={
                    logo.name === "IBM" || logo.name === "Nous Group"
                      ? 160
                      : logo.name === "Australian Government"
                        ? 320
                        : 280
                  }
                  height={
                    logo.name === "IBM" || logo.name === "Nous Group"
                      ? 80
                      : logo.name === "Australian Government"
                        ? 160
                        : 140
                  }
                  className={`select-none object-contain ${
                    logo.name === "ANZSOG" ? "rounded-lg" : ""
                  } ${getDarkModeClass(logo.darkMode)} ${
                    logo.name === "NSW Government"
                      ? "h-16"
                      : logo.name === "IBM" || logo.name === "Nous Group"
                        ? "h-10"
                        : logo.name === "Australian Government"
                          ? "h-32"
                          : "h-24"
                  }`}
                  draggable={false}
                />
              </motion.div>
            ))}
          </div>
          <p className="mt-8 text-center text-lg text-muted-foreground">
            ...and 50+ more signatories from government agencies,
            not-for-profits, industry, and universities
          </p>
          <div className="relative mt-10">
            <div className="absolute inset-0" />
            <div className="relative flex flex-col items-center">
              <div className="w-full max-w-fit">
                <Link
                  href="https://join.aicolab.org"
                  className="block rounded-full bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition-all hover:from-blue-600 hover:to-blue-700 hover:shadow-xl"
                >
                  Join Us →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
