import { useMemo, useState } from 'react'
import type { ChartRow } from '../types'
import { charts, syncPairs } from '../data/charts'
import { functionLabels } from '../lib/labels'

const columnTitles: Record<keyof ChartRow, string> = {
  ingredient: 'Продукт',
  amount: 'Количество',
  prep: 'Подготовка',
  oil: 'Масло',
  temp: 'Температура',
  time: 'Время',
}

type Tab = string

export function ChartsScreen() {
  const [tab, setTab] = useState<Tab>(charts[0]!.id)
  const [query, setQuery] = useState('')

  const active = charts.find((chart) => chart.id === tab)

  const filteredGroups = useMemo(() => {
    if (!active) return []
    const search = query.trim().toLowerCase()
    if (!search) return active.groups
    return active.groups
      .map((group) => ({
        ...group,
        rows: group.rows.filter((row) =>
          Object.values(row).join(' ').toLowerCase().includes(search),
        ),
      }))
      .filter((group) => group.rows.length > 0)
  }, [active, query])

  const filteredPairs = useMemo(() => {
    const search = query.trim().toLowerCase()
    if (!search) return syncPairs
    return syncPairs.filter((pair) =>
      `${pair.title} ${pair.mix} ${pair.amount}`.toLowerCase().includes(search),
    )
  }, [query])

  return (
    <div>
      <h1 className="screen-title">Таблицы приготовления</h1>
      <p className="screen-sub">
        Официальные значения Ninja для AF400EU. Время — ориентир, подстраивай под свой вкус.
      </p>

      <input
        className="search"
        value={query}
        placeholder="Найти продукт: картофель, крылышки, лосось…"
        onChange={(event) => setQuery(event.target.value)}
      />

      <div className="pill-row">
        {charts.map((chart) => (
          <button
            key={chart.id}
            className={`pill ${tab === chart.id ? 'active' : ''}`}
            type="button"
            onClick={() => setTab(chart.id)}
          >
            {chart.title}
          </button>
        ))}
        <button
          className={`pill ${tab === 'sync' ? 'active' : ''}`}
          type="button"
          onClick={() => setTab('sync')}
        >
          Пары для SYNC
        </button>
      </div>

      {tab === 'sync' ? (
        <>
          <div className="note-box">
            Выбери любые два блюда, положи по одному в каждую корзину, задай их настройки и нажми
            SYNC — обе зоны закончат одновременно. Соль и перец по вкусу.
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Блюдо</th>
                  <th>Количество</th>
                  <th>Добавить</th>
                  <th>Режим и время</th>
                </tr>
              </thead>
              <tbody>
                {filteredPairs.map((pair) => (
                  <tr key={pair.id}>
                    <td>{pair.title}</td>
                    <td>{pair.amount}</td>
                    <td>{pair.mix}</td>
                    <td>
                      {pair.fn}
                      {pair.temp ? `\n${pair.temp}` : ''}
                      {`\n${pair.time}`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filteredPairs.length === 0 && (
            <div className="empty">
              <span className="empty-emoji">🔎</span>
              Здесь такого нет — посмотри в других таблицах.
            </div>
          )}
        </>
      ) : active ? (
        <>
          <div className="note-box">
            <b>{functionLabels[active.fn]}</b>
            <br />
            {active.intro}
          </div>
          {active.notes?.map((note) => (
            <div className="note-box" key={note}>
              {note}
            </div>
          ))}

          {filteredGroups.length === 0 ? (
            <div className="empty">
              <span className="empty-emoji">🔎</span>
              В этой таблице ничего не нашлось. Попробуй другую вкладку.
            </div>
          ) : (
            filteredGroups.map((group) => (
              <div key={group.title}>
                <div className="group-title">{group.title}</div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        {active.columns.map((column) => (
                          <th key={column}>{columnTitles[column]}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {group.rows.map((row, index) => (
                        <tr key={`${row.ingredient}-${index}`}>
                          {active.columns.map((column) => (
                            <td key={column}>{row[column] ?? '—'}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))
          )}
        </>
      ) : null}
    </div>
  )
}
