import { useMemo, useState } from 'react'
import type { Recipe, UserData } from '../types'
import { recipes } from '../data/recipes'
import { greetingForNow, homeFooter, pick } from '../data/compliments'
import { RecipeCard } from '../components/RecipeCard'
import { plural } from '../lib/labels'

interface Props {
  data: UserData
  stats: { favorites: number; notes: number; cooked: number }
  onOpenRecipe: (id: string) => void
  onToggleFavorite: (id: string) => void
  onGoTo: (tab: 'recipes' | 'charts' | 'guide' | 'favorites') => void
  onExport: () => void
  onImport: (file: File) => void
}

export function HomeScreen({
  data,
  stats,
  onOpenRecipe,
  onToggleFavorite,
  onGoTo,
  onExport,
  onImport,
}: Props) {
  const [greeting] = useState(greetingForNow)
  const [footer] = useState(() => pick('footer', homeFooter))
  const [suggestion, setSuggestion] = useState(
    () => recipes[Math.floor(Math.random() * recipes.length)]!,
  )

  const recentlyCooked = useMemo(() => {
    return Object.entries(data.recipes)
      .filter(([, note]) => note.lastCookedAt)
      .sort(([, a], [, b]) => (b.lastCookedAt ?? '').localeCompare(a.lastCookedAt ?? ''))
      .slice(0, 3)
      .map(([id]) => recipes.find((recipe) => recipe.id === id))
      .filter((recipe): recipe is Recipe => Boolean(recipe))
  }, [data])

  return (
    <div>
      <div className="hero">
        <div className="hero-eyebrow">Ninja Foodi MAX AF400EU</div>
        <div className="hero-title">{greeting}</div>
        <p className="hero-note">
          Здесь вся инструкция и {recipes.length}{' '}
          {plural(recipes.length, 'рецепт', 'рецепта', 'рецептов')} на русском языке — специально
          для тебя.
        </p>
      </div>

      <div className="stat-row">
        <div className="stat">
          <div className="stat-value">{stats.favorites}</div>
          <div className="stat-label">в избранном</div>
        </div>
        <div className="stat">
          <div className="stat-value">{stats.notes}</div>
          <div className="stat-label">заметок</div>
        </div>
        <div className="stat">
          <div className="stat-value">{stats.cooked}</div>
          <div className="stat-label">раз готовила</div>
        </div>
      </div>

      <h2 className="section-heading" style={{ marginTop: 8 }}>
        Что приготовим сегодня?
      </h2>
      <RecipeCard
        recipe={suggestion}
        note={data.recipes[suggestion.id]}
        onOpen={() => onOpenRecipe(suggestion.id)}
        onToggleFavorite={() => onToggleFavorite(suggestion.id)}
      />
      <button
        className="btn"
        type="button"
        onClick={() => setSuggestion(recipes[Math.floor(Math.random() * recipes.length)]!)}
      >
        Предложи другое
      </button>

      <h2 className="section-heading">Быстрый доступ</h2>
      <div className="tile-grid">
        <button className="tile" type="button" onClick={() => onGoTo('recipes')}>
          <span className="tile-emoji">📖</span>
          <div className="tile-title">Все рецепты</div>
          <div className="tile-sub">{recipes.length} штук по категориям</div>
        </button>
        <button className="tile" type="button" onClick={() => onGoTo('charts')}>
          <span className="tile-emoji">📊</span>
          <div className="tile-title">Таблицы</div>
          <div className="tile-sub">Время и градусы для всего</div>
        </button>
        <button className="tile" type="button" onClick={() => onGoTo('guide')}>
          <span className="tile-emoji">🎛️</span>
          <div className="tile-title">Как пользоваться</div>
          <div className="tile-sub">Кнопки, SYNC, MATCH, уход</div>
        </button>
        <button className="tile" type="button" onClick={() => onGoTo('favorites')}>
          <span className="tile-emoji">❤️</span>
          <div className="tile-title">Любимое</div>
          <div className="tile-sub">Избранное и заметки</div>
        </button>
      </div>

      {recentlyCooked.length > 0 && (
        <>
          <h2 className="section-heading">Недавно готовила</h2>
          {recentlyCooked.map((recipe) => (
            <RecipeCard
              key={recipe.id}
              recipe={recipe}
              note={data.recipes[recipe.id]}
              onOpen={() => onOpenRecipe(recipe.id)}
              onToggleFavorite={() => onToggleFavorite(recipe.id)}
            />
          ))}
        </>
      )}

      <h2 className="section-heading">Заметки в безопасности</h2>
      <div className="card">
        <div style={{ fontSize: 14, color: 'var(--ink-soft)' }}>
          Все твои оценки и комментарии хранятся прямо в телефоне. Сохрани копию, если меняешь
          устройство.
        </div>
        <div className="row-btns">
          <button className="btn" type="button" onClick={onExport}>
            Сохранить копию
          </button>
          <label className="btn" style={{ cursor: 'pointer' }}>
            Загрузить копию
            <input
              type="file"
              accept="application/json"
              style={{ display: 'none' }}
              onChange={(event) => {
                const file = event.target.files?.[0]
                if (file) onImport(file)
                event.target.value = ''
              }}
            />
          </label>
        </div>
      </div>

      <div className="love-note">{footer}</div>
    </div>
  )
}
