import { useEffect, useRef } from "react"
import * as THREE from "three"
import { cn } from "@/lib/utils"

export type BackgroundStyle =
  | "gradient"
  | "particles"
  | "waves"
  | "noise"
  | "geometric"

export type ColorScheme = {
  primary: string
  secondary: string
  accent?: string
}

const presetColorSchemes: Record<string, ColorScheme> = {
  emerald: {
    primary: "#047857",
    secondary: "#10B981",
    accent: "#34D399",
  },
  ocean: {
    primary: "#1E40AF",
    secondary: "#3B82F6",
    accent: "#60A5FA",
  },
  sunset: {
    primary: "#C2410C",
    secondary: "#F97316",
    accent: "#FB923C",
  },
  purple: {
    primary: "#7E22CE",
    secondary: "#A855F7",
    accent: "#C084FC",
  },
  midnight: {
    primary: "#1E293B",
    secondary: "#334155",
    accent: "#475569",
  },
}

interface CardBackgroundGeneratorProps {
  width: number
  height: number
  style: BackgroundStyle
  colorScheme: string | ColorScheme
  icon?: React.ReactNode
  iconScale?: number
  className?: string
}

export function CardBackgroundGenerator({
  width,
  height,
  style = "gradient",
  colorScheme = "emerald",
  icon,
  iconScale = 6,
  className,
}: CardBackgroundGeneratorProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sceneRef = useRef<THREE.Scene>(new THREE.Scene())
  const cameraRef = useRef<THREE.Camera>(
    new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 10)
  )
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const materialRef = useRef<THREE.ShaderMaterial | null>(null)
  const frameRef = useRef<number>(0)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!canvasRef.current || !containerRef.current) return

    // Get actual container dimensions
    const container = containerRef.current
    const rect = container.getBoundingClientRect()
    const actualWidth = rect.width
    const actualHeight = rect.height

    // Initialize Three.js scene
    const scene = sceneRef.current
    const camera = cameraRef.current
    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      alpha: true,
      antialias: true,
    })

    renderer.setSize(actualWidth, actualHeight, false) // Use false to avoid setting canvas style
    camera.position.z = 1

    // Get colors from scheme
    const colors =
      typeof colorScheme === "string"
        ? presetColorSchemes[colorScheme]
        : colorScheme

    // Create shader material based on style
    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        resolution: { value: new THREE.Vector2(actualWidth, actualHeight) },
        color1: { value: new THREE.Color(colors.primary) },
        color2: { value: new THREE.Color(colors.secondary) },
        color3: { value: new THREE.Color(colors.accent || colors.secondary) },
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: getFragmentShader(style),
    })

    // Create mesh
    const geometry = new THREE.PlaneGeometry(2, 2)
    const mesh = new THREE.Mesh(geometry, material)
    scene.add(mesh)

    // Store refs
    rendererRef.current = renderer
    materialRef.current = material

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !renderer || !material) return
      const rect = containerRef.current.getBoundingClientRect()
      const width = rect.width
      const height = rect.height

      renderer.setSize(width, height, false)
      material.uniforms.resolution.value.set(width, height)
    }

    window.addEventListener("resize", handleResize)

    // Animation loop
    const animate = (time: number) => {
      if (materialRef.current) {
        materialRef.current.uniforms.time.value = time * 0.001
      }

      if (rendererRef.current && scene && camera) {
        rendererRef.current.render(scene, camera)
      }

      frameRef.current = requestAnimationFrame(animate)
    }

    animate(0)

    return () => {
      window.removeEventListener("resize", handleResize)
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current)
      }
      renderer.dispose()
    }
  }, [width, height, style, colorScheme])

  return (
    <div
      ref={containerRef}
      className={cn("relative h-full w-full", className)}
      style={{
        width: "100%",
        height: "100%",
      }}
    >
      <canvas ref={canvasRef} className="h-full w-full" />
      {icon && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div
            className="[&>*]:!text-white [&>*]:!opacity-100 [&_circle]:!opacity-100 [&_path]:!opacity-100 [&_rect]:!opacity-100"
            style={{ transform: `scale(${iconScale})` }}
          >
            {icon}
          </div>
        </div>
      )}
    </div>
  )
}

function getFragmentShader(style: BackgroundStyle): string {
  switch (style) {
    case "gradient":
      return `
        varying vec2 vUv;
        uniform float time;
        uniform vec3 color1;
        uniform vec3 color2;
        
        void main() {
          vec2 uv = vUv;
          float mixture = sin(time + uv.x * 2.0 + uv.y * 2.0) * 0.5 + 0.5;
          vec3 color = mix(color1, color2, mixture);
          gl_FragColor = vec4(color, 1.0);
        }
      `
    case "particles":
      return `
        varying vec2 vUv;
        uniform float time;
        uniform vec3 color1;
        uniform vec3 color2;
        uniform vec3 color3;
        
        float random(vec2 st) {
          return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
        }
        
        void main() {
          vec2 uv = vUv;
          float particles = 0.0;
          
          for(float i = 0.0; i < 50.0; i++) {
            vec2 position = vec2(
              random(vec2(i, 0.0)) + sin(time * random(vec2(i, 1.0))) * 0.2,
              random(vec2(i, 2.0)) + cos(time * random(vec2(i, 3.0))) * 0.2
            );
            float dist = length(uv - position);
            particles += 0.003 / dist;
          }
          
          vec3 color = mix(color1, color2, particles);
          gl_FragColor = vec4(color, 1.0);
        }
      `
    case "waves":
      return `
        varying vec2 vUv;
        uniform float time;
        uniform vec3 color1;
        uniform vec3 color2;
        
        void main() {
          vec2 uv = vUv;
          float waves = sin(uv.x * 10.0 + time) * 0.5 + 0.5;
          waves *= sin(uv.y * 8.0 + time * 1.5) * 0.5 + 0.5;
          vec3 color = mix(color1, color2, waves);
          gl_FragColor = vec4(color, 1.0);
        }
      `
    case "noise":
      return `
        varying vec2 vUv;
        uniform float time;
        uniform vec3 color1;
        uniform vec3 color2;
        
        float random(vec2 st) {
          return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
        }
        
        void main() {
          vec2 uv = vUv;
          float noise = random(uv + time * 0.1);
          vec3 color = mix(color1, color2, noise);
          gl_FragColor = vec4(color, 1.0);
        }
      `
    case "geometric":
      return `
        varying vec2 vUv;
        uniform float time;
        uniform vec3 color1;
        uniform vec3 color2;
        uniform vec3 color3;
        
        void main() {
          vec2 uv = vUv;
          float pattern = abs(sin(uv.x * 5.0 + time) + sin(uv.y * 5.0 + time));
          vec3 color = mix(color1, color2, pattern);
          color = mix(color, color3, sin(time) * 0.5 + 0.5);
          gl_FragColor = vec4(color, 1.0);
        }
      `
  }
}
