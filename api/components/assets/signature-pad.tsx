"use client"

import { useRef, useEffect } from "react"
import SignatureCanvas from "react-signature-canvas"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface SignaturePadProps {
  value?: {
    type: "draw" | "type" | "upload"
    text?: string
    image?: File
  }
  onChange?: (value: { type: "draw"; image: File }) => void
  className?: string
}

export function SignaturePad({
  value,
  onChange,
  className,
}: SignaturePadProps) {
  const signatureRef = useRef<SignatureCanvas>(null)

  useEffect(() => {
    // Clear the canvas when switching signature types
    if (value?.type !== "draw") {
      signatureRef.current?.clear()
    }
  }, [value?.type])

  const handleClear = () => {
    signatureRef.current?.clear()
    onChange?.({
      type: "draw",
      image: new File([], "signature.png"), // Empty file to trigger form validation
    })
  }

  const handleEnd = () => {
    if (!signatureRef.current || signatureRef.current.isEmpty()) return

    // Convert the signature to a PNG file
    signatureRef.current.getTrimmedCanvas().toBlob((blob: Blob | null) => {
      if (!blob) return
      const file = new File([blob], "signature.png", { type: "image/png" })
      onChange?.({
        type: "draw",
        image: file,
      })
    }, "image/png")
  }

  if (value?.type && value.type !== "draw") return null

  return (
    <Card className={cn("p-4", className)}>
      <div className="relative aspect-[3/1] w-full">
        <SignatureCanvas
          ref={signatureRef}
          canvasProps={{
            className: "w-full h-full border rounded-md cursor-crosshair",
          }}
          backgroundColor="white"
          onEnd={handleEnd}
        />
      </div>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="mt-2"
        onClick={handleClear}
      >
        Clear
      </Button>
    </Card>
  )
}
