import type { Recipe, RecipeCategory } from '../types'
import { officialRecipes } from './recipes-official'
import { siteRecipes } from './recipes-site'
import { basicRecipes } from './recipes-basics'

export const recipes: Recipe[] = [...officialRecipes, ...siteRecipes, ...basicRecipes]

export const categories: Array<{ id: RecipeCategory; title: string; icon: string }> = [
  { id: 'chicken', title: 'Курица', icon: '🍗' },
  { id: 'meat', title: 'Мясо', icon: '🥩' },
  { id: 'fish', title: 'Рыба', icon: '🐟' },
  { id: 'veg', title: 'Овощи', icon: '🥦' },
  { id: 'snacks', title: 'Закуски', icon: '🧀' },
  { id: 'desserts', title: 'Десерты', icon: '🍰' },
  { id: 'basics', title: 'Основы', icon: '🍟' },
]

export const recipeById = new Map(recipes.map((recipe) => [recipe.id, recipe]))
