"use client"

import { motion } from "framer-motion"
import { useEffect, useRef, useState } from "react"
import * as d3 from "d3"

interface Node extends d3.SimulationNodeDatum {
  id: string
  type: "steering" | "working" | "chair" | "partner" | "floating-partner"
  x?: number
  y?: number
  label?: string
  groupId?: string
  fx?: number | null
  fy?: number | null
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: Node
  target: Node
  type: "chair-link" | "partner-link"
}

interface CollaborationNetworkProps {
  className?: string
}

export function CollaborationNetwork({ className }: CollaborationNetworkProps) {
  const [hoveredGroup, setHoveredGroup] = useState<string | null>(null)
  const [nodes, setNodes] = useState<Node[]>([])
  const [links, setLinks] = useState<Link[]>([])
  const simulationRef = useRef<d3.Simulation<Node, Link> | null>(null)

  // Node size configuration
  const nodeSize = {
    steering: 8,
    working: 50,
    chair: 25,
    partner: 6,
    "floating-partner": 6,
  }

  useEffect(() => {
    // Initialize nodes
    const steeringCommittee: Node[] = Array.from({ length: 8 }, (_, i) => ({
      id: `steering-${i}`,
      type: "steering",
      x: 150 + 45 * Math.cos((i * 2 * Math.PI) / 8),
      y: 150 + 45 * Math.sin((i * 2 * Math.PI) / 8),
    }))

    const workingGroups: Node[] = [
      { x: 380, y: 130 }, // Top left
      { x: 580, y: 160 }, // Top right
      { x: 420, y: 250 }, // Middle left
      { x: 620, y: 280 }, // Bottom right
    ].map((pos, i) => ({
      id: `working-${i}`,
      type: "working",
      ...pos,
      fx: pos.x,
      fy: pos.y,
      label: "Action Cluster",
    }))

    const chairs: Node[] = workingGroups.flatMap((group, groupIndex) =>
      Array.from({ length: 2 }, (_, i) => ({
        id: `chair-${groupIndex}-${i}`,
        type: "chair",
        x: group.x! + 60 * Math.cos(i * Math.PI + Math.PI / 3),
        y: group.y! + 60 * Math.sin(i * Math.PI + Math.PI / 3),
        label: "Chair",
        groupId: group.id,
      }))
    )

    const partners: Node[] = workingGroups.flatMap((group, groupIndex) =>
      Array.from({ length: 4 }, (_, i) => ({
        id: `partner-${groupIndex}-${i}`,
        type: "partner",
        x: group.x! + 80 * Math.cos((i * 2 * Math.PI) / 4),
        y: group.y! + 80 * Math.sin((i * 2 * Math.PI) / 4),
        groupId: group.id,
      }))
    )

    const floatingPartners: Node[] = Array.from({ length: 20 }, (_, i) => ({
      id: `floating-partner-${i}`,
      type: "floating-partner",
      x: 400 + Math.random() * 400,
      y: 100 + Math.random() * 300,
    }))

    const allNodes = [
      ...steeringCommittee,
      ...workingGroups,
      ...chairs,
      ...partners,
      ...floatingPartners,
    ]

    // Create links
    const allLinks: Link[] = [
      // Chair links
      ...chairs.map((chair) => ({
        source: workingGroups.find((g) => g.id === chair.groupId)!,
        target: chair,
        type: "chair-link" as const,
      })),
      // Partner links
      ...partners.map((partner) => ({
        source: workingGroups.find((g) => g.id === partner.groupId)!,
        target: partner,
        type: "partner-link" as const,
      })),
    ]

    setLinks(allLinks)

    // Create force simulation
    const simulation = d3
      .forceSimulation<Node>(allNodes)
      .force(
        "link",
        d3
          .forceLink<Node, Link>(allLinks)
          .id((d) => d.id)
          .distance((d) => (d.type === "chair-link" ? 60 : 80))
          .strength((d) => (d.type === "chair-link" ? 0.2 : 0.1))
      )
      .force(
        "collide",
        d3
          .forceCollide<Node>()
          .radius((d) => {
            if (
              d.type === "partner" ||
              d.type === "floating-partner" ||
              d.type === "steering"
            ) {
              return nodeSize[d.type] * 1.5
            }
            return 0
          })
          .strength(0.3)
          .iterations(2)
      )
      .force("center", d3.forceCenter<Node>(400, 250).strength(0.05))
      // Add a gentle charge force to prevent overcrowding
      .force(
        "charge",
        d3
          .forceManyBody<Node>()
          .strength((d) => (d.type === "floating-partner" ? -30 : -10))
      )
      .velocityDecay(0.4)
      .alphaMin(0.001)
      .alphaDecay(0.02)

    // Update nodes on each tick
    simulation.on("tick", () => {
      setNodes([...allNodes])
    })

    simulationRef.current = simulation

    return () => {
      simulation.stop()
    }
  }, [])

  const backboneSupport = [
    "Guide strategy",
    "Support aligned activities",
    "Establish shared measurement",
    "Cultivate community engagement and ownership",
    "Advance policy",
    "Mobilize resources",
  ]

  return (
    <div className={className}>
      <div className="relative h-[500px] w-full overflow-hidden rounded-xl border bg-white p-4 dark:border-neutral-800 dark:bg-neutral-950">
        {/* Background sections */}
        <motion.div
          className="absolute left-0 top-0 h-full w-[300px] bg-blue-50/10 dark:bg-blue-950/10"
          initial={false}
          animate={{
            opacity: hoveredGroup === "steering" ? 1 : 0.5,
          }}
        >
          <div className="p-4 text-sm font-medium text-neutral-500 dark:text-neutral-400">
            STRATEGIC GUIDANCE
          </div>
        </motion.div>
        <motion.div
          className="absolute right-0 top-0 h-full w-[calc(100%-250px)] bg-orange-50/10 dark:bg-orange-950/10"
          initial={false}
          animate={{
            opacity: hoveredGroup?.startsWith("working") ? 1 : 0.5,
          }}
        >
          <div className="p-4 text-right text-sm font-medium text-neutral-500 dark:text-neutral-400">
            PARTNER-DRIVEN ACTION
          </div>
        </motion.div>

        {/* Backbone Support Section */}
        <div className="absolute left-4 top-[200px] w-64 rounded-lg bg-neutral-100/90 p-4 dark:bg-neutral-800/90">
          <div className="mb-2 text-sm font-medium text-neutral-500 dark:text-neutral-400">
            BACKBONE SUPPORT
          </div>
          <ul className="space-y-1 text-xs text-neutral-600 dark:text-neutral-400">
            {backboneSupport.map((item, index) => (
              <li key={index}>• {item}</li>
            ))}
          </ul>
        </div>

        <svg className="h-full w-full">
          {/* Steering Committee background circle */}
          <circle
            cx={150}
            cy={150}
            r={55}
            className="fill-blue-100/30 dark:fill-blue-950/30"
          />
          <text
            x={150}
            y={150}
            textAnchor="middle"
            className="text-xs font-medium text-neutral-500 dark:text-neutral-400"
          >
            Steering
          </text>
          <text
            x={150}
            y={165}
            textAnchor="middle"
            className="text-xs font-medium text-neutral-500 dark:text-neutral-400"
          >
            Committee
          </text>

          {/* Draw connections */}
          {nodes
            .filter((node) => node.type === "working")
            .map((group) => (
              <g key={group.id}>
                {nodes
                  .filter(
                    (node) =>
                      (node.type === "chair" || node.type === "partner") &&
                      node.groupId === group.id
                  )
                  .map((node) => (
                    <motion.line
                      key={`${group.id}-${node.id}`}
                      x1={group.x ?? 0}
                      y1={group.y ?? 0}
                      x2={node.x ?? 0}
                      y2={node.y ?? 0}
                      stroke={
                        hoveredGroup === group.id
                          ? "rgb(249 115 22)"
                          : "rgb(229 229 229)"
                      }
                      strokeWidth={1}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    />
                  ))}
              </g>
            ))}

          {/* Draw nodes */}
          {nodes.map((node) => {
            const isHighlighted =
              hoveredGroup === "steering"
                ? node.type === "steering"
                : hoveredGroup === node.groupId

            const nodeColor = {
              steering: "rgb(219 234 254)",
              working: "rgb(249 115 22)",
              chair: "rgb(191 219 254)",
              partner: "white",
              "floating-partner": "white",
            }[node.type]

            return (
              <g key={node.id}>
                <motion.circle
                  cx={node.x ?? 0}
                  cy={node.y ?? 0}
                  r={nodeSize[node.type]}
                  fill={nodeColor}
                  stroke={
                    node.type.includes("partner")
                      ? "rgb(229 229 229)"
                      : "transparent"
                  }
                  strokeWidth={1}
                  initial={{ scale: 0 }}
                  animate={{
                    scale: 1,
                    opacity: isHighlighted ? 1 : 0.7,
                  }}
                  whileHover={{ scale: 1.1 }}
                  onMouseEnter={() => {
                    if (node.type === "steering") setHoveredGroup("steering")
                    else if (node.type === "working") setHoveredGroup(node.id)
                  }}
                  onMouseLeave={() => setHoveredGroup(null)}
                />
                {(node.type === "chair" || node.type === "working") &&
                  node.label && (
                    <text
                      x={node.x ?? 0}
                      y={(node.y ?? 0) + nodeSize[node.type] + 12}
                      textAnchor="middle"
                      className="text-xs font-medium text-neutral-500 dark:text-neutral-400"
                    >
                      {node.label}
                    </text>
                  )}
              </g>
            )
          })}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-4 right-4 rounded-lg border bg-white/90 p-3 text-sm dark:border-neutral-800 dark:bg-neutral-900/90">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full border border-neutral-200 dark:border-neutral-700" />
            <span className="text-neutral-500 dark:text-neutral-400">
              = community partner (e.g., nonprofit, funder, business, public
              agency, resident)
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
