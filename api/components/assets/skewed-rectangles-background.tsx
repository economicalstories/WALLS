"use client"

import { cn } from "@/lib/utils"
import React from "react"

interface SkewedRectanglesBackgroundProps {
  className?: string
  style?: React.CSSProperties
  rotateTop?: number
  rotateBottom?: number
}

export function SkewedRectanglesBackground({
  className,
  style,
  rotateTop = 45,
  rotateBottom = -45,
}: SkewedRectanglesBackgroundProps) {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 z-0 h-full w-full overflow-hidden [perspective:1000px] [transform-style:preserve-3d]",
        className
      )}
      style={style}
    >
      <Rectangles
        style={{ transform: `rotateX(${rotateTop}deg)` }}
        className="[mask-image:linear-gradient(to_top,white,transparent)]"
      />
      <Rectangles
        style={{ transform: `rotateX(${rotateBottom}deg)` }}
        className="[mask-image:linear-gradient(to_bottom,white,transparent)]"
      />
    </div>
  )
}

const Rectangles = ({
  className,
  ...props
}: {
  className?: string
  style?: React.CSSProperties
}) => {
  const rectangleSVGLight = `<svg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'><rect width='40' height='40' x='0' y='0' stroke='rgba(0,0,0,0.1)' fill='none' /></svg>`
  const rectangleSVGDark = `<svg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'><rect width='40' height='40' x='0' y='0' stroke='rgba(255,255,255,0.15)' fill='none' /></svg>`
  const encodedRectangleSVGLight = encodeURIComponent(rectangleSVGLight)
  const encodedRectangleSVGDark = encodeURIComponent(rectangleSVGDark)

  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 z-0 h-full w-full overflow-hidden",
        className
      )}
      {...props}
    >
      <div
        className={cn("h-full w-full dark:hidden")}
        style={{
          backgroundImage: `url("data:image/svg+xml,${encodedRectangleSVGLight}")`,
          backgroundSize: "40px 40px",
          backgroundPosition: "center",
          backgroundRepeat: "repeat",
        }}
      />
      <div
        className={cn("hidden h-full w-full dark:block")}
        style={{
          backgroundImage: `url("data:image/svg+xml,${encodedRectangleSVGDark}")`,
          backgroundSize: "40px 40px",
          backgroundPosition: "center",
          backgroundRepeat: "repeat",
        }}
      />
    </div>
  )
}
