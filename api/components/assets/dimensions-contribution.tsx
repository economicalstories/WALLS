import { motion, useAnimation, AnimatePresence } from "framer-motion"
import { useState, useEffect } from "react"
import { Zap, Hammer, Shield } from "lucide-react"
import { cn } from "@/lib/utils"

export const DimensionsContribution = () => {
  const [activeState, setActiveState] = useState<number>(0)
  const controls = useAnimation()

  const states = [
    {
      title: "Building Motivation",
      subtitle: "Why people get involved and stay involved",
      contributions: {
        Spark: "Shows what's possible and builds excitement",
        Sculpt: "Demonstrates real progress is achievable",
        Steward: "Builds lasting trust and confidence",
      },
    },
    {
      title: "Growing Capability",
      subtitle: "Skills, knowledge, and expertise",
      contributions: {
        Spark: "Builds practical understanding through shared learning",
        Sculpt: "Combines technical and domain expertise",
        Steward: "Creates frameworks for responsible practice",
      },
    },
    {
      title: "Creating Opportunity",
      subtitle: "Resources, networks, and pathways",
      contributions: {
        Spark: "Creates spaces for cross-sector connection",
        Sculpt: "Builds shared infrastructure and tools",
        Steward: "Trusted, inclusive practices unlock new options",
      },
    },
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveState((prev) => (prev + 1) % states.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const getDimensionColor = (dimension: string) => {
    switch (dimension) {
      case "Spark":
        return "rgb(217, 119, 6)" // amber-600
      case "Sculpt":
        return "rgb(147, 51, 234)" // purple-600
      case "Steward":
        return "rgb(15, 118, 110)" // teal-700
      default:
        return "gray"
    }
  }

  const getCenterColor = (state: number) => {
    switch (state) {
      case 0: // Motivation
        return "rgb(234, 88, 12)" // orange-600
      case 1: // Capability
        return "rgb(37, 99, 235)" // blue-600
      case 2: // Opportunity
        return "rgb(22, 163, 74)" // green-600
      default:
        return "gray"
    }
  }

  const getDimensionPosition = (dimension: string) => {
    const containerWidth = 600
    const containerHeight = 600

    switch (dimension) {
      case "Spark":
        return { x: containerWidth * 0.5, y: containerHeight * 0.1 } // top
      case "Sculpt":
        return { x: containerWidth * 0.15, y: containerHeight * 0.65 } // bottom left
      case "Steward":
        return { x: containerWidth * 0.85, y: containerHeight * 0.65 } // bottom right
      default:
        return { x: containerWidth * 0.5, y: containerHeight * 0.5 }
    }
  }

  const getArrowPath = (from: string) => {
    const fromPos = getDimensionPosition(from)
    const toPos = { x: 300, y: 300 } // center
    const nodeRadius = 64
    const centerRadius = 80

    // Calculate angle to center
    const dx = toPos.x - fromPos.x
    const dy = toPos.y - fromPos.y
    const angle = Math.atan2(dy, dx)

    // Start and end points
    const fromX = fromPos.x + Math.cos(angle) * nodeRadius
    const fromY = fromPos.y + Math.sin(angle) * nodeRadius
    const toX = toPos.x + Math.cos(angle + Math.PI) * centerRadius
    const toY = toPos.y + Math.sin(angle + Math.PI) * centerRadius

    // Calculate control point for the curve
    const midX = (fromX + toX) / 2
    const midY = (fromY + toY) / 2
    const perpScale = Math.sqrt((toX - fromX) ** 2 + (toY - fromY) ** 2) * 0.2

    // Calculate perpendicular offset for control point
    const perpX = -dy * (perpScale / Math.sqrt(dx * dx + dy * dy))
    const perpY = dx * (perpScale / Math.sqrt(dx * dx + dy * dy))

    // Adjust control point based on position
    const controlX = midX + (from === "Spark" ? -perpX : perpX)
    const controlY = midY + (from === "Spark" ? -perpY : perpY)

    return `M ${fromX} ${fromY} Q ${controlX} ${controlY} ${toX} ${toY}`
  }

  return (
    <div className="relative mx-auto h-[600px] w-full max-w-[600px]">
      {/* SVG Container for arrows */}
      <svg className="absolute inset-0 h-full w-full">
        {/* Flowing Arrows */}
        {["Spark", "Sculpt", "Steward"].map((dimension) => (
          <motion.path
            key={`arrow-${dimension}`}
            d={getArrowPath(dimension)}
            stroke={getDimensionColor(dimension)}
            strokeWidth="3"
            fill="none"
            className="opacity-50"
            animate={{
              strokeDashoffset: [0, -100],
            }}
            style={{
              strokeDasharray: "10,10",
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </svg>

      {/* Center Circle with State */}
      <motion.div
        className="absolute left-1/2 top-1/2 flex h-40 w-40 -translate-x-1/2 -translate-y-1/2 flex-col items-center justify-center rounded-full text-white shadow-lg"
        style={{
          backgroundColor: getCenterColor(activeState),
          transition: "background-color 0.5s ease-in-out",
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeState}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.3 }}
            className="text-center"
          >
            <div className="text-lg font-bold">
              {states[activeState].title.split(" ")[1]}
            </div>
            <div className="text-xs opacity-80">
              {states[activeState].subtitle}
            </div>
          </motion.div>
        </AnimatePresence>
      </motion.div>

      {/* Dimension Nodes */}
      {["Spark", "Sculpt", "Steward"].map((dimension) => {
        const pos = getDimensionPosition(dimension)
        return (
          <motion.div
            key={dimension}
            className="absolute flex h-32 w-32 -translate-x-1/2 -translate-y-1/2 cursor-pointer flex-col items-center justify-center gap-2 rounded-full text-white shadow-lg"
            style={{
              left: pos.x,
              top: pos.y,
              backgroundColor: getDimensionColor(dimension),
            }}
          >
            <span className="text-xl font-bold">{dimension}</span>
            {dimension === "Spark" && <Zap size={24} />}
            {dimension === "Sculpt" && <Hammer size={24} />}
            {dimension === "Steward" && <Shield size={24} />}
            <motion.div
              className={cn(
                "absolute w-48 text-center",
                dimension === "Spark" ? "-right-48" : "-bottom-16"
              )}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <AnimatePresence mode="wait">
                <motion.p
                  key={`${dimension}-${activeState}`}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="text-sm text-muted-foreground"
                >
                  {states[activeState].contributions[dimension]}
                </motion.p>
              </AnimatePresence>
            </motion.div>
          </motion.div>
        )
      })}
    </div>
  )
}
