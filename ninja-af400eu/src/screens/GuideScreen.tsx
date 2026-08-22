import { useState } from 'react'
import type { GuideBlock } from '../types'
import { guide } from '../data/guide'

function Block({ block }: { block: GuideBlock }) {
  switch (block.kind) {
    case 'text':
      return <p>{block.text}</p>
    case 'note':
      return <div className="note-box">{block.text}</div>
    case 'list':
      return (
        <ul className="clean">
          {block.items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )
    case 'steps':
      return (
        <ol className="clean">
          {block.items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
      )
    case 'table':
      return (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {block.head.map((cell) => (
                  <th key={cell}>{cell}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {block.rows.map((row, index) => (
                <tr key={`${row[0]}-${index}`}>
                  {row.map((cell, cellIndex) => (
                    <td key={`${cell}-${cellIndex}`}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
  }
}

export function GuideScreen() {
  const [open, setOpen] = useState<string | null>(guide[0]!.id)

  return (
    <div>
      <h1 className="screen-title">Как пользоваться</h1>
      <p className="screen-sub">
        Вся инструкция к Ninja AF400EU по-русски: что означает каждая кнопка и как получить лучший
        результат.
      </p>

      {guide.map((section) => {
        const isOpen = open === section.id
        return (
          <div className="guide-item" key={section.id}>
            <button
              className="guide-head"
              type="button"
              onClick={() => setOpen(isOpen ? null : section.id)}
            >
              <span style={{ fontSize: 20 }}>{section.icon}</span>
              <span>{section.title}</span>
              <span className={`arrow ${isOpen ? 'open' : ''}`}>›</span>
            </button>
            {isOpen && (
              <div className="guide-body">
                {section.blocks.map((block, index) => (
                  <Block block={block} key={index} />
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
