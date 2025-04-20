"use client"

import { useEffect, useRef } from "react"
import { cn } from "@/lib/utils"

export const CanvasRevealEffect = ({
  containerClassName,
  colors = [[255, 255, 255]],
  dotSize = 1,
  animationSpeed = 3,
}: {
  containerClassName?: string
  colors?: number[][]
  dotSize?: number
  animationSpeed?: number
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const mouse = { x: 0, y: 0 }
    const dots: {
      x: number
      y: number
      vx: number
      vy: number
      color: number[]
    }[] = []

    const resize = () => {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
    }
    resize()
    window.addEventListener("resize", resize)

    const addDot = (x: number, y: number) => {
      const color = colors[Math.floor(Math.random() * colors.length)]
      dots.push({
        x,
        y,
        vx: (Math.random() - 0.5) * animationSpeed,
        vy: (Math.random() - 0.5) * animationSpeed,
        color,
      })
    }

    // Create initial dots
    for (let i = 0; i < 100; i++) {
      addDot(Math.random() * canvas.width, Math.random() * canvas.height)
    }

    canvas.addEventListener("mousemove", (e) => {
      const rect = canvas.getBoundingClientRect()
      mouse.x = e.clientX - rect.left
      mouse.y = e.clientY - rect.top

      // Add dots on mouse move
      for (let i = 0; i < 2; i++) {
        addDot(mouse.x, mouse.y)
      }
    })

    const animate = () => {
      ctx.fillStyle = "rgba(0, 0, 0, 0.1)"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      for (let i = dots.length - 1; i >= 0; i--) {
        const dot = dots[i]
        dot.x += dot.vx
        dot.y += dot.vy

        const alpha = Math.max(0, 1 - dots.length / 1000)

        ctx.fillStyle = `rgba(${dot.color.join(",")}, ${alpha})`
        ctx.fillRect(dot.x - dotSize / 2, dot.y - dotSize / 2, dotSize, dotSize)

        // Remove dots that are off screen
        if (
          dot.x < 0 ||
          dot.x > canvas.width ||
          dot.y < 0 ||
          dot.y > canvas.height
        ) {
          dots.splice(i, 1)
        }
      }

      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", resize)
    }
  }, [colors, dotSize, animationSpeed])

  return (
    <canvas
      ref={canvasRef}
      className={cn("h-full w-full", containerClassName)}
    ></canvas>
  )
}
