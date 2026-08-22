import { useCallback, useEffect, useRef, useState } from 'react'

export interface TimerState {
  /** Метка времени окончания, мс */
  endsAt: number
  totalSeconds: number
  label: string
  /** Минуты от начала, когда нужно встряхнуть корзину */
  shakeAt: number[]
  shakeDone: number[]
  finished: boolean
}

export type Timers = Partial<Record<1 | 2, TimerState>>

const STORAGE_KEY = 'ninja-af400eu.timers.v1'

function readTimers(): Timers {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Timers) : {}
  } catch {
    return {}
  }
}

/** Короткий сигнал через Web Audio — работает без файлов и без загрузки. */
function beep() {
  try {
    const Ctor =
      window.AudioContext ??
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
    if (!Ctor) return
    const ctx = new Ctor()
    const play = (start: number) => {
      const oscillator = ctx.createOscillator()
      const gain = ctx.createGain()
      oscillator.type = 'sine'
      oscillator.frequency.value = 880
      gain.gain.setValueAtTime(0.001, ctx.currentTime + start)
      gain.gain.exponentialRampToValueAtTime(0.3, ctx.currentTime + start + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + 0.35)
      oscillator.connect(gain).connect(ctx.destination)
      oscillator.start(ctx.currentTime + start)
      oscillator.stop(ctx.currentTime + start + 0.4)
    }
    play(0)
    play(0.5)
    play(1)
    window.setTimeout(() => void ctx.close(), 2000)
  } catch {
    // Звук не критичен.
  }
}

function vibrate(pattern: number[]) {
  try {
    navigator.vibrate?.(pattern)
  } catch {
    // Не поддерживается — не страшно.
  }
}

export function useTimers(onFinish?: (label: string) => void, onShake?: (label: string) => void) {
  const [timers, setTimers] = useState<Timers>(readTimers)
  const [, forceTick] = useState(0)
  const finishRef = useRef(onFinish)
  const shakeRef = useRef(onShake)
  finishRef.current = onFinish
  shakeRef.current = onShake

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(timers))
    } catch {
      // Ничего страшного.
    }
  }, [timers])

  useEffect(() => {
    const id = window.setInterval(() => {
      forceTick((value) => value + 1)
      setTimers((current) => {
        let changed = false
        const next: Timers = { ...current }
        for (const key of [1, 2] as const) {
          const timer = current[key]
          if (!timer || timer.finished) continue
          const left = Math.round((timer.endsAt - Date.now()) / 1000)
          const elapsedMinutes = Math.floor((timer.totalSeconds - left) / 60)
          const dueShake = timer.shakeAt.find(
            (minute) => minute <= elapsedMinutes && !timer.shakeDone.includes(minute),
          )
          if (dueShake !== undefined && left > 0) {
            next[key] = { ...timer, shakeDone: [...timer.shakeDone, dueShake] }
            changed = true
            vibrate([200, 100, 200])
            shakeRef.current?.(timer.label)
          }
          if (left <= 0) {
            next[key] = { ...(next[key] ?? timer), finished: true }
            changed = true
            beep()
            vibrate([400, 150, 400, 150, 400])
            finishRef.current?.(timer.label)
          }
        }
        return changed ? next : current
      })
    }, 1000)
    return () => window.clearInterval(id)
  }, [])

  const start = useCallback(
    (zone: 1 | 2, minutes: number, label: string, shakeAt: number[] = []) => {
      setTimers((current) => ({
        ...current,
        [zone]: {
          endsAt: Date.now() + minutes * 60_000,
          totalSeconds: minutes * 60,
          label,
          shakeAt,
          shakeDone: [],
          finished: false,
        },
      }))
    },
    [],
  )

  const stop = useCallback((zone: 1 | 2) => {
    setTimers((current) => {
      const next = { ...current }
      delete next[zone]
      return next
    })
  }, [])

  const secondsLeft = useCallback(
    (zone: 1 | 2) => {
      const timer = timers[zone]
      if (!timer) return null
      return Math.max(0, Math.round((timer.endsAt - Date.now()) / 1000))
    },
    [timers],
  )

  return { timers, start, stop, secondsLeft }
}

export function formatSeconds(total: number): string {
  const minutes = Math.floor(total / 60)
  const seconds = total % 60
  return `${minutes}:${String(seconds).padStart(2, '0')}`
}
