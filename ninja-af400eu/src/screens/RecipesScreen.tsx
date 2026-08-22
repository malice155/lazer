import { useMemo, useState } from 'react'
import type { RecipeCategory, UserData } from '../types'
import { categories, recipes } from '../data/recipes'
import { RecipeCard } from '../components/RecipeCard'

interface Props {
  data: UserData
  onOpenRecipe: (id: string) => void
  onToggleFavorite: (id: string) => void
}

type Filter = RecipeCategory | 'all'

export function RecipesScreen({ data, onOpenRecipe, onToggleFavorite }: Props) {
  const [filter, setFilter] = useState<Filter>('all')
  const [query, setQuery] = useState('')

  const visible = useMemo(() => {
    const search = query.trim().toLowerCase()
    return recipes.filter((recipe) => {
      if (filter !== 'all' && recipe.category !== filter) return false
      if (!search) return true
      const haystack = [
        recipe.title,
        recipe.summary,
        recipe.titleOriginal ?? '',
        ...recipe.ingredients.flatMap((group) => group.items),
        ...recipe.zones.map((zone) => zone.title),
      ]
        .join(' ')
        .toLowerCase()
      return haystack.includes(search)
    })
  }, [filter, query])

  return (
    <div>
      <h1 className="screen-title">Рецепты</h1>
      <p className="screen-sub">
        Все проверенные рецепты для этой модели, переведённые на русский.
      </p>

      <input
        className="search"
        value={query}
        placeholder="Найти рецепт или ингредиент"
        onChange={(event) => setQuery(event.target.value)}
      />

      <div className="pill-row">
        <button
          className={`pill ${filter === 'all' ? 'active' : ''}`}
          type="button"
          onClick={() => setFilter('all')}
        >
          Все {recipes.length}
        </button>
        {categories.map((category) => {
          const count = recipes.filter((recipe) => recipe.category === category.id).length
          if (count === 0) return null
          return (
            <button
              key={category.id}
              className={`pill ${filter === category.id ? 'active' : ''}`}
              type="button"
              onClick={() => setFilter(category.id)}
            >
              {category.icon} {category.title} {count}
            </button>
          )
        })}
      </div>

      {visible.length === 0 ? (
        <div className="empty">
          <span className="empty-emoji">🔎</span>
          Ничего не нашлось. Попробуй другое слово — например, «курица» или «картофель».
        </div>
      ) : (
        visible.map((recipe) => (
          <RecipeCard
            key={recipe.id}
            recipe={recipe}
            note={data.recipes[recipe.id]}
            onOpen={() => onOpenRecipe(recipe.id)}
            onToggleFavorite={() => onToggleFavorite(recipe.id)}
          />
        ))
      )}
    </div>
  )
}
