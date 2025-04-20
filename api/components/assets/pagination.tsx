import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface PaginationButtonProps {
  page: number
  currentPage: number
  totalPages: number
  createUrl: (page: number) => string
}

function PaginationButton({
  page,
  currentPage,
  totalPages,
  createUrl,
}: PaginationButtonProps) {
  const isDisabled = page < 1 || page > totalPages
  const isActive = page === currentPage

  return (
    <Button
      variant={isActive ? "primary" : "secondary"}
      size="sm"
      className={cn(
        "h-8 w-8 p-0",
        isDisabled && "cursor-not-allowed opacity-50",
        isActive && "pointer-events-none"
      )}
      asChild
      disabled={isDisabled}
    >
      <a
        href={createUrl(page)}
        className={isDisabled ? "pointer-events-none" : ""}
      >
        {page}
      </a>
    </Button>
  )
}

interface PaginationProps {
  currentPage: number
  totalPages: number
  createUrl: (page: number) => string
}

export function Pagination({
  currentPage,
  totalPages,
  createUrl,
}: PaginationProps) {
  if (totalPages <= 1) return null

  return (
    <div className="flex justify-center gap-2 pt-8">
      <Button
        variant="secondary"
        size="sm"
        className="h-8 w-8 p-0"
        asChild
        disabled={currentPage <= 1}
      >
        <a
          href={createUrl(currentPage - 1)}
          className={currentPage <= 1 ? "pointer-events-none" : ""}
        >
          ←
        </a>
      </Button>

      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
        <PaginationButton
          key={page}
          page={page}
          currentPage={currentPage}
          totalPages={totalPages}
          createUrl={createUrl}
        />
      ))}

      <Button
        variant="secondary"
        size="sm"
        className="h-8 w-8 p-0"
        asChild
        disabled={currentPage >= totalPages}
      >
        <a
          href={createUrl(currentPage + 1)}
          className={currentPage >= totalPages ? "pointer-events-none" : ""}
        >
          →
        </a>
      </Button>
    </div>
  )
}
