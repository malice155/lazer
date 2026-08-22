import type { Recipe, RecipeNote } from '../types'
import { formatMinutes, modeShort } from '../lib/labels'

interface Props {
  recipe: Recipe
  note?: RecipeNote
  onOpen: () => void
  onToggleFavorite: () => void
}

export function RecipeCard({ recipe, note, onOpen, onToggleFavorite }: Props) {
  return (
    <div className="recipe-card">
      <button className="recipe-card-body" onClick={onOpen} type="button">
        <div className="recipe-card-title">{recipe.title}</div>
        <div className="recipe-card-sub">{recipe.summary}</div>
        <div className="meta-row">
          <span className="chip mode">{modeShort[recipe.mode]}</span>
          <span className="chip plain">{formatMinutes(recipe.totalMinutes)}</span>
          <span className="chip plain">{recipe.servings}</span>
          {recipe.vegetarian && <span className="chip veg">Вегетарианское</span>}
          {note?.rating ? <span className="chip">{'★'.repeat(note.rating)}</span> : null}
          {note?.cooked ? <span className="chip">Готовила {note.cooked}</span> : null}
        </div>
      </button>
      <button
        className="heart-btn"
        onClick={onToggleFavorite}
        type="button"
        aria-label={note?.favorite ? 'Убрать из избранного' : 'Добавить в избранное'}
      >
        {note?.favorite ? '❤️' : '🤍'}
      </button>
    </div>
  )
}
