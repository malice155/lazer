import type { CookFunction, DualMode, ZoneSetting } from '../types'

export const functionLabels: Record<CookFunction, string> = {
  'AIR FRY': 'Обжарка (AIR FRY)',
  'MAX CRISP': 'Хрустящая корочка (MAX CRISP)',
  ROAST: 'Запекание (ROAST)',
  BAKE: 'Выпечка (BAKE)',
  REHEAT: 'Разогрев (REHEAT)',
  DEHYDRATE: 'Сушка (DEHYDRATE)',
}

export const modeLabels: Record<DualMode, string> = {
  SYNC: 'SYNC — обе корзины закончат одновременно',
  MATCH: 'MATCH — одинаковые настройки в обеих корзинах',
  DUAL: 'Две зоны — стартуют вместе, заканчивают по-своему',
  SINGLE: 'Одна корзина',
}

export const modeShort: Record<DualMode, string> = {
  SYNC: 'SYNC',
  MATCH: 'MATCH',
  DUAL: '2 зоны',
  SINGLE: '1 зона',
}

export function formatTemp(zone: ZoneSetting): string {
  return zone.tempC ? `${zone.tempC} °C` : '240 °C (фиксировано)'
}

export function formatMinutes(total: number): string {
  if (total < 60) return `${total} мин`
  const hours = Math.floor(total / 60)
  const minutes = total % 60
  return minutes ? `${hours} ч ${minutes} мин` : `${hours} ч`
}

export function plural(count: number, one: string, few: string, many: string): string {
  const mod10 = count % 10
  const mod100 = count % 100
  if (mod10 === 1 && mod100 !== 11) return one
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few
  return many
}
