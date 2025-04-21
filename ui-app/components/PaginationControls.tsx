import { Button } from "@/components/ui/button"

interface Props {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export function PaginationControls({ currentPage, totalPages, onPageChange }: Props) {
  return (
    <div className="flex justify-between mt-4">
      <Button
        variant="outline"
        disabled={currentPage === 1}
        onClick={() => onPageChange(currentPage - 1)}
      >
        Trước
      </Button>
      <span>Trang {currentPage} / {totalPages}</span>
      <Button
        variant="outline"
        disabled={currentPage === totalPages}
        onClick={() => onPageChange(currentPage + 1)}
      >
        Tiếp
      </Button>
    </div>
  )
}

