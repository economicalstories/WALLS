"use client"

import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import { Switch } from "@/components/ui/switch"
import { ScrollArea } from "@/components/ui/scroll-area"
import Image from "next/image"
import { motion, AnimatePresence } from "framer-motion"
import {
  IconRobot,
  IconEye,
  IconRocket,
  IconBulb,
  IconShieldLock,
  IconSparkles,
  IconBuilding,
  IconStars,
} from "@tabler/icons-react"
import { QuoteCard } from "@/components/ui/quote-card"

interface PersonaLevel {
  capability: "high" | "low"
  opportunity: "high" | "low"
  motivation: "high" | "low"
}

interface PersonaQuote {
  perspective: string
  quote: string
}

interface ExampleItem {
  text: string
  icon: string
}

interface Persona {
  name: string
  levels: PersonaLevel
  description: string
  examples: ExampleItem[]
  quotes: PersonaQuote[]
  collaborationPotential: string
}

interface PersonaDashboardProps {
  personas: Persona[]
}

function PulsingBadge({
  children,
  isActive,
}: {
  children: React.ReactNode
  isActive: boolean
}) {
  return (
    <div className="relative inline-flex">
      {isActive && (
        <>
          <motion.span
            className="absolute inset-0 rounded-full border-2 border-emerald-500/60 shadow-[0_0_10px_2px_rgba(16,185,129,0.3)]"
            initial={{ opacity: 0.7, scale: 0.85 }}
            animate={{ opacity: 0, scale: 1.8 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: [0.4, 0, 0.6, 1],
              opacity: {
                duration: 1.8,
              },
            }}
          />
          <motion.span
            className="absolute inset-0 rounded-full border-2 border-emerald-500/60 shadow-[0_0_10px_2px_rgba(16,185,129,0.3)]"
            initial={{ opacity: 0.7, scale: 0.85 }}
            animate={{ opacity: 0, scale: 1.8 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: [0.4, 0, 0.6, 1],
              delay: 1,
              opacity: {
                duration: 1.8,
                delay: 1,
              },
            }}
          />
        </>
      )}
      <div className="relative z-10 flex">{children}</div>
    </div>
  )
}

// Mapping of personas to their visual elements
const personaVisuals = {
  "Skeptical Spectators": {
    icon: IconEye,
    color: "neutral",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-slate-900 to-slate-700",
    bgColor: "bg-neutral-600 dark:bg-neutral-500",
  },
  "Eager Explorers": {
    icon: IconRocket,
    color: "blue",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-blue-900 to-blue-700",
    bgColor: "bg-blue-600 dark:bg-blue-500",
  },
  "Latent Luminaries": {
    icon: IconBulb,
    color: "amber",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-amber-900 to-amber-700",
    bgColor: "bg-amber-600 dark:bg-amber-500",
  },
  "Capable Catalysts": {
    icon: IconRobot,
    color: "emerald",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-emerald-900 to-emerald-700",
    bgColor: "bg-emerald-600 dark:bg-emerald-500",
  },
  "Watchful Wardens": {
    icon: IconShieldLock,
    color: "purple",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-purple-900 to-purple-700",
    bgColor: "bg-purple-600 dark:bg-purple-500",
  },
  "Aspiring Accelerators": {
    icon: IconSparkles,
    color: "orange",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-orange-900 to-orange-700",
    bgColor: "bg-orange-600 dark:bg-orange-500",
  },
  "Dormant Dynamos": {
    icon: IconBuilding,
    color: "violet",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-violet-900 to-violet-700",
    bgColor: "bg-violet-600 dark:bg-violet-500",
  },
  "Transformative Trailblazers": {
    icon: IconStars,
    color: "sky",
    headerImage:
      "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop",
    gradient: "from-sky-900 to-sky-700",
    bgColor: "bg-sky-600 dark:bg-sky-500",
  },
} as const

function PersonaBadge({ name }: { name: string }) {
  const visual = personaVisuals[name as keyof typeof personaVisuals]
  const Icon = visual.icon

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-full px-3 py-1.5",
        `bg-${visual.color}-100 text-${visual.color}-900`,
        `dark:bg-${visual.color}-900/20 dark:text-${visual.color}-300`
      )}
    >
      <Icon className="h-4 w-4" />
      <span className="text-sm font-medium">{name}</span>
    </div>
  )
}

export function PersonaDashboard({ personas }: PersonaDashboardProps) {
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null)
  const [sidebarHeight, setSidebarHeight] = useState<number>(0)
  const sidebarRef = useRef<HTMLDivElement>(null)
  const resizeObserverRef = useRef<ResizeObserver | null>(null)
  const [levels, setLevels] = useState<PersonaLevel>({
    capability: "low",
    opportunity: "low",
    motivation: "low",
  })

  // Optimized height measurement
  useEffect(() => {
    if (!sidebarRef.current) return

    const updateHeight = () => {
      if (sidebarRef.current) {
        setSidebarHeight(sidebarRef.current.offsetHeight)
      }
    }

    // Initial measurement
    updateHeight()

    // Set up ResizeObserver for more efficient monitoring
    resizeObserverRef.current = new ResizeObserver(updateHeight)
    resizeObserverRef.current.observe(sidebarRef.current)

    return () => {
      resizeObserverRef.current?.disconnect()
    }
  }, [selectedPersona]) // Only re-run when content changes

  // Find persona matching current toggle settings
  const matchingPersona = personas.find(
    (p) =>
      p.levels.capability === levels.capability &&
      p.levels.opportunity === levels.opportunity &&
      p.levels.motivation === levels.motivation
  )

  // Update selected persona when toggles change
  if (
    matchingPersona &&
    (!selectedPersona || selectedPersona.name !== matchingPersona.name)
  ) {
    setSelectedPersona(matchingPersona)
  }

  const handleToggle = (dimension: keyof PersonaLevel) => {
    setLevels((prev) => ({
      ...prev,
      [dimension]: prev[dimension] === "high" ? "low" : "high",
    }))
  }

  return (
    <div className="relative flex flex-col gap-6 lg:flex-row lg:gap-0">
      {/* Sidebar - natural height */}
      <div className="lg:sticky lg:top-6 lg:w-64 lg:shrink-0">
        <div className="rounded-lg border bg-card">
          {/* Toggles section with reduced height */}
          <div className="border-b p-2.5">
            <div className="space-y-0.5">
              {(["capability", "opportunity", "motivation"] as const).map(
                (dimension) => (
                  <div
                    key={dimension}
                    className={cn(
                      "group flex w-full cursor-pointer items-center justify-between rounded-lg px-1.5 py-0.5 transition-colors",
                      levels[dimension] === "high"
                        ? "bg-emerald-500/10 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400"
                        : "hover:bg-muted"
                    )}
                    onClick={() => handleToggle(dimension)}
                  >
                    <div>
                      <p className="text-sm capitalize">{dimension}</p>
                    </div>
                    <Switch
                      checked={levels[dimension] === "high"}
                      onCheckedChange={() => handleToggle(dimension)}
                      className={cn(
                        "data-[state=checked]:bg-emerald-500/90 data-[state=checked]:hover:bg-emerald-600/90"
                      )}
                    />
                  </div>
                )
              )}
            </div>
          </div>

          {/* Persona list with natural height */}
          <ScrollArea>
            <div className="divide-y pb-1">
              {personas.map((persona) => (
                <button
                  key={persona.name}
                  onClick={() => {
                    setSelectedPersona(persona)
                    setLevels(persona.levels)
                  }}
                  className={cn(
                    "flex h-[4.5rem] w-full items-center px-3 text-left transition-colors hover:bg-accent/50",
                    selectedPersona?.name === persona.name
                      ? "bg-accent"
                      : "bg-background"
                  )}
                >
                  <div className="flex w-full items-center justify-between">
                    <div className="flex items-center gap-2">
                      {(() => {
                        const Icon =
                          personaVisuals[
                            persona.name as keyof typeof personaVisuals
                          ].icon
                        return (
                          <Icon
                            className={cn("h-4 w-4", {
                              "text-neutral-600 dark:text-neutral-400":
                                persona.name === "Skeptical Spectators",
                              "text-blue-600 dark:text-blue-400":
                                persona.name === "Eager Explorers",
                              "text-amber-600 dark:text-amber-400":
                                persona.name === "Latent Luminaries",
                              "text-emerald-600 dark:text-emerald-400":
                                persona.name === "Capable Catalysts",
                              "text-purple-600 dark:text-purple-400":
                                persona.name === "Watchful Wardens",
                              "text-orange-600 dark:text-orange-400":
                                persona.name === "Aspiring Accelerators",
                              "text-violet-600 dark:text-violet-400":
                                persona.name === "Dormant Dynamos",
                              "text-sky-600 dark:text-sky-400":
                                persona.name === "Transformative Trailblazers",
                            })}
                          />
                        )
                      })()}
                      <span className="flex flex-col pl-1 text-sm leading-tight">
                        {persona.name.split(" ").map((word, i) => (
                          <span key={i} className="font-medium">
                            {word}
                          </span>
                        ))}
                      </span>
                    </div>
                    <div className="flex shrink-0 gap-1">
                      {Object.entries(persona.levels).map(([key, value]) => (
                        <PulsingBadge key={key} isActive={value === "high"}>
                          <span
                            className={cn(
                              "relative rounded px-1 py-0.5 text-xs",
                              value === "high"
                                ? "bg-emerald-500/90 text-emerald-50 shadow-[0_0_10px_2px_rgba(16,185,129,0.3)] backdrop-blur-sm transition-all duration-300"
                                : "bg-muted text-muted-foreground opacity-50"
                            )}
                          >
                            {key[0].toUpperCase()}
                          </span>
                        </PulsingBadge>
                      ))}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* Main Content - height based on sidebar */}
      <div className="flex-1 lg:pl-6">
        <div
          className="overflow-hidden rounded-lg border"
          style={{ height: sidebarHeight > 0 ? `${sidebarHeight}px` : "auto" }}
        >
          <ScrollArea className="h-full">
            {/* Persona Details */}
            {selectedPersona && (
              <div className="bg-card">
                {/* Header Image */}
                <div
                  className="relative h-[240px] w-full"
                  style={{
                    backgroundImage: `url(${personaVisuals[selectedPersona.name as keyof typeof personaVisuals].headerImage})`,
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                >
                  {/* Gradient overlay */}
                  <div
                    className={cn(
                      "absolute inset-0 z-10",
                      "bg-gradient-to-t from-black/80 to-transparent"
                    )}
                  />
                  <div
                    className={cn(
                      "absolute inset-0 z-10 mix-blend-soft-light",
                      "bg-gradient-to-br opacity-60",
                      personaVisuals[
                        selectedPersona.name as keyof typeof personaVisuals
                      ].gradient
                    )}
                  />
                  {/* Text content */}
                  <div className="absolute inset-x-0 bottom-0 z-20 p-6 pb-12">
                    <h2 className="mt-3 text-3xl font-bold text-white drop-shadow-xl">
                      {selectedPersona.name}
                    </h2>
                    <div className="mt-2 flex gap-2">
                      {Object.entries(selectedPersona.levels).map(
                        ([key, value]) => (
                          <PulsingBadge key={key} isActive={value === "high"}>
                            <span
                              className={cn(
                                "relative rounded-full px-3 py-1 text-xs font-medium shadow-md backdrop-blur-sm",
                                value === "high"
                                  ? "bg-emerald-500/90 text-emerald-50 shadow-[0_0_15px_3px_rgba(16,185,129,0.3)] backdrop-blur-md transition-all duration-300"
                                  : "bg-muted/90 text-muted-foreground opacity-50"
                              )}
                            >
                              {key.charAt(0).toUpperCase() + key.slice(1)}
                            </span>
                          </PulsingBadge>
                        )
                      )}
                    </div>
                  </div>
                </div>

                {/* Icon that straddles header and content */}
                <div className="relative z-30 mx-6 -mt-8">
                  <div
                    className={cn(
                      "flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-lg dark:bg-black"
                    )}
                  >
                    {(() => {
                      const Icon =
                        personaVisuals[
                          selectedPersona.name as keyof typeof personaVisuals
                        ].icon
                      return (
                        <Icon
                          className={cn("h-6 w-6", {
                            "text-neutral-600 dark:text-neutral-400":
                              selectedPersona.name === "Skeptical Spectators",
                            "text-blue-600 dark:text-blue-400":
                              selectedPersona.name === "Eager Explorers",
                            "text-amber-600 dark:text-amber-400":
                              selectedPersona.name === "Latent Luminaries",
                            "text-emerald-600 dark:text-emerald-400":
                              selectedPersona.name === "Capable Catalysts",
                            "text-purple-600 dark:text-purple-400":
                              selectedPersona.name === "Watchful Wardens",
                            "text-orange-600 dark:text-orange-400":
                              selectedPersona.name === "Aspiring Accelerators",
                            "text-violet-600 dark:text-violet-400":
                              selectedPersona.name === "Dormant Dynamos",
                            "text-sky-600 dark:text-sky-400":
                              selectedPersona.name ===
                              "Transformative Trailblazers",
                          })}
                        />
                      )
                    })()}
                  </div>
                </div>

                <div className="p-6">
                  <div className="space-y-6">
                    {/* Description without heading */}
                    <p className="text-muted-foreground">
                      {selectedPersona.description}
                    </p>

                    {/* Enhanced Examples Section */}
                    <div className="relative rounded-lg border bg-muted/50 px-6 pb-4">
                      <div className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-background shadow-md">
                        👥
                      </div>
                      <h3 className="mt-4 text-lg font-semibold">
                        Examples in the Wild
                      </h3>
                      <div className="mt-4 grid gap-2">
                        {selectedPersona.examples.map((example, index) => (
                          <div
                            key={index}
                            className="flex items-center gap-3 rounded-md bg-background px-3 py-2"
                          >
                            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-muted">
                              {example.icon}
                            </span>
                            <p className="text-sm text-muted-foreground">
                              {example.text}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold">Perspectives</h3>
                      <div className="mt-4 grid gap-4 md:grid-cols-3">
                        {selectedPersona.quotes.map((quote, index) => (
                          <QuoteCard
                            key={index}
                            quote={quote.quote}
                            perspective={quote.perspective}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Enhanced Collaboration Potential Section */}
                    <div className="relative rounded-lg border bg-muted/50 px-6 pb-4">
                      <div className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-background shadow-md">
                        🤝
                      </div>
                      <h3 className="mt-4 text-lg font-semibold">
                        Ways to Work Together
                      </h3>
                      <div className="mt-4 rounded-md bg-background p-4">
                        <p className="text-sm text-muted-foreground">
                          {selectedPersona.collaborationPotential}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </ScrollArea>
        </div>
      </div>
    </div>
  )
}
