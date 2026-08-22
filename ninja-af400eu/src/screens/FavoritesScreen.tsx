import { useMemo, useState } from 'react'
import type { UserData } from '../types'
import { recipes } from '../data/recipes'
import { RecipeCard } from '../components/RecipeCard'

interface Props {
  data: UserData
  onOpenRecipe: (id: string) => void
  onToggleFavorite: (id: string) => void
}

type Tab = 'favorites' | 'notes'

export function FavoritesScreen({ data, onOpenRecipe, onToggleFavorite }: Props) {
  const [tab, setTab] = useState<Tab>('favorites')

  const favorites = useMemo(
    () => recipes.filter((recipe) => data.recipes[recipe.id]?.favorite),
    [data],
  )

  const withNotes = useMemo(
    () =>
      recipes.filter((recipe) => {
        const note = data.recipes[recipe.id]
        return Boolean(note?.note?.trim()) || Boolean(note?.rating) || Boolean(note?.cooked)
      }),
    [data],
  )

  const list = tab === 'favorites' ? favorites : withNotes

  return (
    <div>
      <h1 className="screen-title">Любимое</h1>
      <p className="screen-sub">Твой личный раздел, Наталья: что понравилось и что ты записала.</p>

      <div className="pill-row">
        <button
          className={`pill ${tab === 'favorites' ? 'active' : ''}`}
          type="button"
          onClick={() => setTab('favorites')}
        >
          ❤️ Избранное {favorites.length}
        </button>
        <button
          className={`pill ${tab === 'notes' ? 'active' : ''}`}
          type="button"
          onClick={() => setTab('notes')}
        >
          📝 С заметками {withNotes.length}
        </button>
      </div>

      {list.length === 0 ? (
        <div className="empty">
          <span className="empty-emoji">{tab === 'favorites' ? '🤍' : '📝'}</span>
          {tab === 'favorites'
            ? 'Пока пусто. Нажми на сердечко у любого рецепта — и он появится здесь.'
            : 'Пока пусто. Поставь оценку или запиши комментарий к рецепту — всё сохранится тут.'}
        </div>
      ) : (
        list.map((recipe) => (
          <div key={recipe.id}>
            <RecipeCard
              recipe={recipe}
              note={data.recipes[recipe.id]}
              onOpen={() => onOpenRecipe(recipe.id)}
              onToggleFavorite={() => onToggleFavorite(recipe.id)}
            />
            {data.recipes[recipe.id]?.note?.trim() ? (
              <div className="tip" style={{ marginTop: -4, marginBottom: 14 }}>
                {data.recipes[recipe.id]!.note}
              </div>
            ) : null}
          </div>
        ))
      )}
    </div>
  )
}
