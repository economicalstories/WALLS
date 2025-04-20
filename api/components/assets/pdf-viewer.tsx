import { cn } from "@/lib/utils"

interface PDFViewerProps {
  url: string
  className?: string
  height?: string
}

export function PDFViewer({
  url,
  className,
  height = "100vh",
}: PDFViewerProps) {
  return (
    <iframe
      src={`${url}#toolbar=0&navpanes=0&scrollbar=0`}
      className={cn("w-full border-none bg-white dark:bg-gray-900", className)}
      style={{ height }}
      title="PDF viewer"
    />
  )
}
