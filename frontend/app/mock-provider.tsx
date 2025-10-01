"use client"

import { useEffect, useState } from "react"

export function MockProvider({ children }: { children: React.ReactNode }) {
  const [mswReady, setMswReady] = useState(false)

  useEffect(() => {
    async function initMocks() {
      if (typeof window !== "undefined") {
        const { worker } = await import("@/lib/mocks/browser")
        await worker.start({
          onUnhandledRequest: "bypass",
        })
        setMswReady(true)
      }
    }

    initMocks()
  }, [])

  if (!mswReady) {
    return null
  }

  return <>{children}</>
}
