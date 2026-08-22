export type CookFunction =
  | 'AIR FRY'
  | 'MAX CRISP'
  | 'ROAST'
  | 'BAKE'
  | 'REHEAT'
  | 'DEHYDRATE'

export type DualMode = 'SYNC' | 'MATCH' | 'DUAL' | 'SINGLE'

export type RecipeCategory =
  | 'chicken'
  | 'meat'
  | 'fish'
  | 'veg'
  | 'snacks'
  | 'desserts'
  | 'basics'

export interface SourceRef {
  /** Короткая подпись источника, видна пользователю */
  label: string
  url?: string
}

export interface ZoneSetting {
  zone: 1 | 2
  /** Что именно готовится в этой корзине */
  title: string
  fn: CookFunction
  /** У MAX CRISP температура не регулируется */
  tempC?: number
  minutes: number
  /** Решётка-подставка (crisper plate) */
  plate: boolean
  /** Подсказка «когда встряхнуть», минуты от начала */
  shakeAt?: number[]
}

export interface IngredientGroup {
  title?: string
  items: string[]
}

export interface Recipe {
  id: string
  title: string
  /** Оригинальное название, чтобы можно было найти первоисточник */
  titleOriginal?: string
  category: RecipeCategory
  vegetarian?: boolean
  /** Короткое описание-подводка */
  summary: string
  servings: string
  prepMinutes?: number
  totalMinutes: number
  mode: DualMode
  zones: ZoneSetting[]
  ingredients: IngredientGroup[]
  steps: string[]
  tips?: string[]
  source: SourceRef
}

export interface ChartRow {
  ingredient: string
  amount?: string
  prep?: string
  oil?: string
  temp?: string
  time: string
}

export interface ChartGroup {
  title: string
  rows: ChartRow[]
}

export interface ChartSection {
  id: string
  title: string
  fn: CookFunction
  intro: string
  notes?: string[]
  /** Какие колонки показывать */
  columns: Array<keyof ChartRow>
  groups: ChartGroup[]
}

export interface SyncPair {
  id: string
  title: string
  amount: string
  mix: string
  fn: CookFunction
  temp?: string
  time: string
}

export type GuideBlock =
  | { kind: 'text'; text: string }
  | { kind: 'list'; items: string[] }
  | { kind: 'steps'; items: string[] }
  | { kind: 'note'; text: string }
  | { kind: 'table'; head: string[]; rows: string[][] }

export interface GuideSection {
  id: string
  title: string
  icon: string
  blocks: GuideBlock[]
}

export interface RecipeNote {
  favorite?: boolean
  rating?: number
  note?: string
  cooked?: number
  lastCookedAt?: string
}

export interface UserData {
  version: number
  recipes: Record<string, RecipeNote>
}
