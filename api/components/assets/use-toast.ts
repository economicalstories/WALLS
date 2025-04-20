import { useState, useCallback } from "react"

interface Toast {
    description: string
}

interface ToastHook {
    toast: (toast: Toast) => void
}

export function useToast(): ToastHook {
    const [, setToasts] = useState<Toast[]>([])

    const toast = useCallback((newToast: Toast) => {
        setToasts((prevToasts) => [...prevToasts, newToast])
        // For now, we'll just use the browser's alert
        // In a real implementation, we'd want to use a proper toast component
        alert(newToast.description)
    }, [])

    return { toast }
}
