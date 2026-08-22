import { useEffect, useState } from 'react'
import type { Recipe, RecipeNote } from '../types'
import { formatMinutes, formatTemp, functionLabels, modeLabels } from '../lib/labels'
import { formatSeconds } from '../hooks/useTimers'
import type { Timers } from '../hooks/useTimers'

interface Props {
  recipe: Recipe
  note?: RecipeNote
  timers: Timers
  onBack: () => void
  onToggleFavorite: () => void
  onSaveNote: (text: string) => void
  onRate: (value: number) => void
  onCooked: () => void
  onStartTimer: (zone: 1 | 2, minutes: number, label: string, shakeAt: number[]) => void
  onStopTimer: (zone: 1 | 2) => void
}

export function RecipeDetail({
  recipe,
  note,
  timers,
  onBack,
  onToggleFavorite,
  onSaveNote,
  onRate,
  onCooked,
  onStartTimer,
  onStopTimer,
}: Props) {
  const [draft, setDraft] = useState(note?.note ?? '')

  useEffect(() => {
    setDraft(note?.note ?? '')
    window.scrollTo(0, 0)
  }, [recipe.id, note?.note])

  return (
    <div>
      <div className="detail-header">
        <button className="back-btn" onClick={onBack} type="button">
          ‹ Назад
        </button>
        <button
          className="heart-btn"
          style={{ marginLeft: 'auto' }}
          onClick={onToggleFavorite}
          type="button"
          aria-label="Избранное"
        >
          {note?.favorite ? '❤️' : '🤍'}
        </button>
      </div>

      <h1 className="detail-title">{recipe.title}</h1>
      <p className="detail-summary">{recipe.summary}</p>

      <div className="meta-row" style={{ marginBottom: 16 }}>
        <span className="chip mode">{modeLabels[recipe.mode]}</span>
        <span className="chip plain">{recipe.servings}</span>
        {recipe.prepMinutes ? (
          <span className="chip plain">Подготовка {recipe.prepMinutes} мин</span>
        ) : null}
        <span className="chip plain">Готовка {formatMinutes(recipe.totalMinutes)}</span>
        {recipe.vegetarian && <span className="chip veg">Вегетарианское</span>}
      </div>

      <h2 className="section-heading" style={{ marginTop: 0 }}>
        Настройки прибора
      </h2>
      {recipe.zones.map((zone) => {
        const timer = timers[zone.zone]
        const left = timer ? Math.max(0, Math.round((timer.endsAt - Date.now()) / 1000)) : null
        const isThisRecipe = timer?.label.startsWith(recipe.title) ?? false
        return (
          <div className="zone-card" key={`${zone.zone}-${zone.title}`}>
            <span className={`zone-badge z${zone.zone}`}>Зона {zone.zone}</span>
            <div className="zone-title">{zone.title}</div>
            <div className="zone-settings">
              <span>
                Режим: <b>{functionLabels[zone.fn]}</b>
              </span>
              <span>
                Температура: <b>{formatTemp(zone)}</b>
              </span>
              <span>
                Время: <b>{zone.minutes} мин</b>
              </span>
              <span>
                Решётка: <b>{zone.plate ? 'нужна' : 'убрать'}</b>
              </span>
            </div>
            {zone.shakeAt?.length ? (
              <div className="zone-settings" style={{ marginTop: 6 }}>
                <span>Встряхнуть на: {zone.shakeAt.map((m) => `${m} мин`).join(', ')}</span>
              </div>
            ) : null}

            {timer && isThisRecipe ? (
              <div className="timer-live">
                <span>{timer.finished ? 'Готово!' : 'Осталось'}</span>
                <span className="timer-value">
                  {timer.finished ? '00:00' : formatSeconds(left ?? 0)}
                </span>
                <button
                  className="btn"
                  style={{ flex: '0 0 auto', padding: '8px 12px' }}
                  onClick={() => onStopTimer(zone.zone)}
                  type="button"
                >
                  Сбросить
                </button>
              </div>
            ) : (
              <button
                className="timer-btn"
                type="button"
                onClick={() =>
                  onStartTimer(
                    zone.zone,
                    zone.minutes,
                    `${recipe.title} — зона ${zone.zone}`,
                    zone.shakeAt ?? [],
                  )
                }
              >
                Запустить таймер на {zone.minutes} мин
              </button>
            )}
          </div>
        )
      })}

      <h2 className="section-heading">Ингредиенты</h2>
      <div className="card">
        {recipe.ingredients.map((group, index) => (
          <div key={group.title ?? index}>
            {group.title && <div className="ingredient-group-title">{group.title}</div>}
            <ul className="clean">
              {group.items.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <h2 className="section-heading">Приготовление</h2>
      <div className="card">
        <ol className="clean">
          {recipe.steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </div>

      {recipe.tips?.length ? (
        <>
          <h2 className="section-heading">Советы</h2>
          {recipe.tips.map((tip) => (
            <div className="tip" key={tip}>
              {tip}
            </div>
          ))}
        </>
      ) : null}

      <h2 className="section-heading">Твои заметки, Наталья</h2>
      <div className="card">
        <div style={{ fontSize: 14, color: 'var(--ink-soft)' }}>Как получилось?</div>
        <div className="stars">
          {[1, 2, 3, 4, 5].map((value) => (
            <button
              key={value}
              type="button"
              className={`star ${note?.rating && value <= note.rating ? 'on' : ''}`}
              onClick={() => onRate(value)}
              aria-label={`Оценка ${value}`}
            >
              ⭐
            </button>
          ))}
        </div>
        <textarea
          className="note-area"
          value={draft}
          placeholder="Например: соли в два раза меньше, картошку держать 22 минуты, Серёже очень понравилось"
          onChange={(event) => setDraft(event.target.value)}
        />
        <div className="row-btns">
          <button className="btn primary" type="button" onClick={() => onSaveNote(draft)}>
            Сохранить заметку
          </button>
          <button className="btn" type="button" onClick={onCooked}>
            Готовила ✓
          </button>
        </div>
        {note?.cooked ? (
          <div style={{ fontSize: 13, color: 'var(--ink-soft)', marginTop: 10 }}>
            Приготовлено раз: {note.cooked}
            {note.lastCookedAt
              ? `, последний — ${new Date(note.lastCookedAt).toLocaleDateString('ru-RU')}`
              : ''}
          </div>
        ) : null}
      </div>

      <div className="source-note">
        Источник:{' '}
        {recipe.source.url ? (
          <a href={recipe.source.url} target="_blank" rel="noreferrer">
            {recipe.source.label}
          </a>
        ) : (
          recipe.source.label
        )}
        {recipe.titleOriginal ? ` · оригинальное название: ${recipe.titleOriginal}` : ''}
      </div>
    </div>
  )
}
