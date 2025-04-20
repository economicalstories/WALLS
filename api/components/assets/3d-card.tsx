"use client"

import { cn } from "@/lib/utils"
import React, {
  createContext,
  useState,
  useContext,
  useRef,
  useEffect,
} from "react"

const MouseEnterContext = createContext<{
  mouseX: number
  mouseY: number
  setMouseX: React.Dispatch<React.SetStateAction<number>>
  setMouseY: React.Dispatch<React.SetStateAction<number>>
}>({
  mouseX: 0,
  mouseY: 0,
  setMouseX: () => {},
  setMouseY: () => {},
})

export const CardContainer = ({
  children,
  className,
  containerClassName,
}: {
  children: React.ReactNode
  className?: string
  containerClassName?: string
}) => {
  const [mouseX, setMouseX] = useState(0)
  const [mouseY, setMouseY] = useState(0)

  return (
    <MouseEnterContext.Provider
      value={{ mouseX, mouseY, setMouseX, setMouseY }}
    >
      <div
        className={cn("group/card relative", containerClassName)}
        onMouseMove={(e) => {
          const rect = e.currentTarget.getBoundingClientRect()
          const x = e.clientX - rect.left
          const y = e.clientY - rect.top
          setMouseX(x)
          setMouseY(y)
        }}
      >
        <div className={cn("relative", className)}>{children}</div>
      </div>
    </MouseEnterContext.Provider>
  )
}

export const CardBody = ({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) => {
  const { mouseX, mouseY } = useContext(MouseEnterContext)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const rotateElement = () => {
      if (!ref.current) return
      const rect = ref.current.getBoundingClientRect()
      const centerX = rect.width / 2
      const centerY = rect.height / 2
      const rotateX = -(mouseY - centerY) / 25
      const rotateY = (mouseX - centerX) / 25

      ref.current.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`
    }

    requestAnimationFrame(rotateElement)
  }, [mouseX, mouseY])

  return (
    <div
      ref={ref}
      className={cn(
        "relative transition-transform duration-200 ease-out",
        className
      )}
      style={{
        transformStyle: "preserve-3d",
      }}
    >
      {children}
    </div>
  )
}

export const CardItem = ({
  as: Component = "div",
  children,
  className,
  translateX = 0,
  translateY = 0,
  translateZ = 0,
  rotateX = 0,
  rotateY = 0,
  rotateZ = 0,
  ...rest
}: {
  as?: any
  children: React.ReactNode
  className?: string
  translateX?: number | string
  translateY?: number | string
  translateZ?: number | string
  rotateX?: number | string
  rotateY?: number | string
  rotateZ?: number | string
  [key: string]: any
}) => {
  const transform = [
    `translateX(${translateX}px)`,
    `translateY(${translateY}px)`,
    `translateZ(${translateZ}px)`,
    `rotateX(${rotateX}deg)`,
    `rotateY(${rotateY}deg)`,
    `rotateZ(${rotateZ}deg)`,
  ].join(" ")

  return (
    <Component
      className={cn("transition-transform duration-200 ease-out", className)}
      style={{
        transform,
        transformStyle: "preserve-3d",
      }}
      {...rest}
    >
      {children}
    </Component>
  )
}
