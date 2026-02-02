import { useEffect, useState } from 'react'

export function useAnimation(delay = 0) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, delay)

    return () => clearTimeout(timer)
  }, [delay])

  return isVisible
}

export function useStaggeredAnimation(count: number, staggerDelay = 50) {
  const [visibleIndices, setVisibleIndices] = useState<Set<number>>(new Set())

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = []

    for (let i = 0; i < count; i++) {
      const timer = setTimeout(() => {
        setVisibleIndices((prev) => new Set(prev).add(i))
      }, i * staggerDelay)
      timers.push(timer)
    }

    return () => {
      timers.forEach((timer) => clearTimeout(timer))
    }
  }, [count, staggerDelay])

  return visibleIndices
}
