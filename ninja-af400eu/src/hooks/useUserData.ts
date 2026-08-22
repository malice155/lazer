import { useCallback, useEffect, useMemo, useState } from 'react'
import type { RecipeNote, UserData } from '../types'

const STORAGE_KEY = 'ninja-af400eu.natalia.v1'

const emptyData: UserData = { version: 1, recipes: {} }

function read(): UserData {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return emptyData
    const parsed = JSON.parse(raw) as UserData
    if (!parsed || typeof parsed !== 'object' || !parsed.recipes) return emptyData
    return { version: 1, recipes: parsed.recipes }
  } catch {
    return emptyData
  }
}

export function useUserData() {
  const [data, setData] = useState<UserData>(read)

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    } catch {
      // Приватный режим Safari может запретить запись — молча продолжаем.
    }
  }, [data])

  const update = useCallback((id: string, patch: Partial<RecipeNote>) => {
    setData((current) => ({
      version: 1,
      recipes: {
        ...current.recipes,
        [id]: { ...current.recipes[id], ...patch },
      },
    }))
  }, [])

  /** Возвращает новое состояние «в избранном», чтобы показать нужный комплимент. */
  const toggleFavorite = useCallback(
    (id: string) => {
      const next = !data.recipes[id]?.favorite
      setData((current) => ({
        version: 1,
        recipes: { ...current.recipes, [id]: { ...current.recipes[id], favorite: next } },
      }))
      return next
    },
    [data],
  )

  const markCooked = useCallback((id: string) => {
    setData((current) => {
      const previous = current.recipes[id]
      return {
        version: 1,
        recipes: {
          ...current.recipes,
          [id]: {
            ...previous,
            cooked: (previous?.cooked ?? 0) + 1,
            lastCookedAt: new Date().toISOString(),
          },
        },
      }
    })
  }, [])

  const importData = useCallback((raw: string) => {
    const parsed = JSON.parse(raw) as UserData
    if (!parsed || typeof parsed !== 'object' || !parsed.recipes) {
      throw new Error('Файл не похож на резервную копию заметок')
    }
    setData({ version: 1, recipes: parsed.recipes })
  }, [])

  const stats = useMemo(() => {
    const entries = Object.values(data.recipes)
    return {
      favorites: entries.filter((item) => item.favorite).length,
      notes: entries.filter((item) => item.note && item.note.trim().length > 0).length,
      cooked: entries.reduce((sum, item) => sum + (item.cooked ?? 0), 0),
    }
  }, [data])

  return { data, update, toggleFavorite, markCooked, importData, stats }
}

export type UserDataApi = ReturnType<typeof useUserData>
