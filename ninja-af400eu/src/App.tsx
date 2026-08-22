import { useCallback, useEffect, useState } from 'react'
import { recipeById } from './data/recipes'
import {
  cookedMarked,
  favoriteAdded,
  noteSaved,
  pick,
  timerFinished,
} from './data/compliments'
import { useUserData } from './hooks/useUserData'
import { formatSeconds, useTimers } from './hooks/useTimers'
import { HomeScreen } from './screens/HomeScreen'
import { RecipesScreen } from './screens/RecipesScreen'
import { ChartsScreen } from './screens/ChartsScreen'
import { GuideScreen } from './screens/GuideScreen'
import { FavoritesScreen } from './screens/FavoritesScreen'
import { RecipeDetail } from './components/RecipeDetail'

type Tab = 'home' | 'recipes' | 'charts' | 'guide' | 'favorites'

const tabs: Array<{ id: Tab; title: string; icon: string }> = [
  { id: 'home', title: 'Главная', icon: '🏠' },
  { id: 'recipes', title: 'Рецепты', icon: '📖' },
  { id: 'charts', title: 'Таблицы', icon: '📊' },
  { id: 'guide', title: 'Инструкция', icon: '🎛️' },
  { id: 'favorites', title: 'Любимое', icon: '❤️' },
]

export default function App() {
  const { data, update, toggleFavorite, markCooked, importData, stats } = useUserData()
  const [tab, setTab] = useState<Tab>('home')
  const [openRecipeId, setOpenRecipeId] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  const showToast = useCallback((message: string) => {
    setToast(message)
  }, [])

  useEffect(() => {
    if (!toast) return
    const id = window.setTimeout(() => setToast(null), 3200)
    return () => window.clearTimeout(id)
  }, [toast])

  const { timers, start, stop, secondsLeft } = useTimers(
    () => showToast(pick('timer', timerFinished)),
    (label) => showToast(`Пора встряхнуть корзину: ${label}`),
  )

  const handleToggleFavorite = useCallback(
    (id: string) => {
      const isFavorite = toggleFavorite(id)
      if (isFavorite) showToast(pick('favorite', favoriteAdded))
    },
    [toggleFavorite, showToast],
  )

  const handleExport = useCallback(() => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `zametki-natalii-${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(url)
    showToast('Копия сохранена. Твои записи в безопасности.')
  }, [data, showToast])

  const handleImport = useCallback(
    (file: File) => {
      const reader = new FileReader()
      reader.onload = () => {
        try {
          importData(String(reader.result))
          showToast('Заметки восстановлены. С возвращением, Наталья!')
        } catch {
          showToast('Не получилось прочитать файл. Проверь, тот ли это файл.')
        }
      }
      reader.readAsText(file)
    },
    [importData, showToast],
  )

  const openRecipe = openRecipeId ? recipeById.get(openRecipeId) : undefined

  return (
    <div className="app">
      {openRecipe ? (
        <RecipeDetail
          recipe={openRecipe}
          note={data.recipes[openRecipe.id]}
          timers={timers}
          onBack={() => setOpenRecipeId(null)}
          onToggleFavorite={() => handleToggleFavorite(openRecipe.id)}
          onSaveNote={(text) => {
            update(openRecipe.id, { note: text })
            showToast(pick('note', noteSaved))
          }}
          onRate={(value) => update(openRecipe.id, { rating: value })}
          onCooked={() => {
            markCooked(openRecipe.id)
            showToast(pick('cooked', cookedMarked))
          }}
          onStartTimer={start}
          onStopTimer={stop}
        />
      ) : (
        <>
          {tab === 'home' && (
            <HomeScreen
              data={data}
              stats={stats}
              onOpenRecipe={setOpenRecipeId}
              onToggleFavorite={handleToggleFavorite}
              onGoTo={setTab}
              onExport={handleExport}
              onImport={handleImport}
            />
          )}
          {tab === 'recipes' && (
            <RecipesScreen
              data={data}
              onOpenRecipe={setOpenRecipeId}
              onToggleFavorite={handleToggleFavorite}
            />
          )}
          {tab === 'charts' && <ChartsScreen />}
          {tab === 'guide' && <GuideScreen />}
          {tab === 'favorites' && (
            <FavoritesScreen
              data={data}
              onOpenRecipe={setOpenRecipeId}
              onToggleFavorite={handleToggleFavorite}
            />
          )}
        </>
      )}

      {(timers[1] || timers[2]) && (
        <div className="timer-bar">
          {([1, 2] as const).map((zone) => {
            const timer = timers[zone]
            if (!timer) return null
            const left = secondsLeft(zone) ?? 0
            return (
              <div className={`timer-chip ${timer.finished ? 'done' : ''}`} key={zone}>
                <span>Зона {zone}</span>
                <b>{timer.finished ? 'Готово' : formatSeconds(left)}</b>
                <button type="button" onClick={() => stop(zone)} aria-label="Сбросить таймер">
                  ✕
                </button>
              </div>
            )
          })}
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}

      <nav className="nav">
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`nav-btn ${tab === item.id && !openRecipe ? 'active' : ''}`}
            onClick={() => {
              setOpenRecipeId(null)
              setTab(item.id)
            }}
          >
            <span className="ico">{item.icon}</span>
            <span>{item.title}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
