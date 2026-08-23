#!/usr/bin/env python3
"""Собирает docs/zakupka-lazera-2026.md в одностраничный HTML для показа и печати.

Результат самодостаточный: без внешних шрифтов, CSS и скриптов. Открывается
двойным щелчком, печатается в PDF из браузера (Ctrl+P), нормально читается с телефона.
"""

from __future__ import annotations

from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "zakupka-lazera-2026.md"
OUT = ROOT / "docs" / "zakupka-lazera-2026.html"

TITLE = "ЛазерПроф — закупка лазера мощнее L3030"

CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  margin: 0 auto; padding: 32px 20px 96px; max-width: 900px;
  font: 16px/1.6 -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #16181d; background: #fff; overflow-wrap: break-word;
}
h1 { font-size: 30px; line-height: 1.25; margin: 0 0 20px; }
h2 { font-size: 22px; margin: 40px 0 12px; padding-bottom: 6px; border-bottom: 2px solid #e6e8ec; }
h3 { font-size: 18px; margin: 28px 0 10px; }
p, ul, ol { margin: 0 0 14px; }
li { margin-bottom: 6px; }
a { color: #0b62d0; }
strong { color: #000; }
code { background: #f2f4f7; padding: 2px 5px; border-radius: 4px; font-size: 0.9em; }
pre { background: #f6f8fa; padding: 14px 16px; border-radius: 8px; overflow-x: auto; font-size: 13px; line-height: 1.5; }
pre code { background: none; padding: 0; }
hr { border: 0; border-top: 1px solid #e6e8ec; margin: 36px 0; }
blockquote { margin: 0 0 14px; padding: 8px 16px; border-left: 3px solid #d0d4da; color: #4a5057; }

.table-wrap { overflow-x: auto; margin: 0 0 18px; -webkit-overflow-scrolling: touch; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { border: 1px solid #dfe2e7; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #f2f4f7; font-weight: 600; }
tbody tr:nth-child(even) { background: #fafbfc; }

.print-hint {
  margin: 0 0 28px; padding: 10px 14px; border: 1px solid #dfe2e7;
  border-left: 3px solid #0b62d0; border-radius: 6px;
  background: #f7f9fc; font-size: 14px; color: #4a5057;
}

@media (prefers-color-scheme: dark) {
  body { color: #e6e8ec; background: #14161a; }
  strong { color: #fff; }
  h2 { border-color: #2a2e36; }
  code, pre { background: #1c1f25; }
  th { background: #1c1f25; }
  tbody tr:nth-child(even) { background: #181b20; }
  th, td { border-color: #2a2e36; }
  hr { border-color: #2a2e36; }
  a { color: #6aa9f5; }
  .print-hint { background: #1a1d23; border-color: #2a2e36; color: #a8aeb8; }
}

@media print {
  @page { size: A4; margin: 14mm; }
  body { max-width: none; padding: 0; font-size: 10.5pt; color: #000; background: #fff; }
  h1 { font-size: 19pt; }
  h2 { font-size: 14pt; margin-top: 18pt; page-break-after: avoid; }
  h3 { font-size: 12pt; page-break-after: avoid; }
  table { font-size: 8.5pt; page-break-inside: avoid; }
  pre { font-size: 8pt; white-space: pre-wrap; page-break-inside: avoid; }
  .table-wrap { overflow: visible; }
  .print-hint { display: none; }
  a { color: #000; text-decoration: none; }
}
"""

HINT = (
    '<div class="print-hint">Печать или PDF — <b>Ctrl+P</b> '
    "(на Mac <b>&#8984;P</b>), «Сохранить как PDF». Вёрстка под A4 уже настроена.</div>"
)

TEMPLATE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="Варианты закупки волоконного лазера взамен TRUMPF L3030: цены, за и против, деньги, планировка цеха.">
<meta property="og:title" content="{title}">
<meta property="og:description" content="Fiber 12 кВт на Raycus CE: станок 7,8–8,9 млн ₽, проект 9,5–13,5 млн. Без азота — кислород и воздух 16 бар.">
<meta property="og:type" content="article">
<style>{css}</style>
</head>
<body>
{hint}
{body}
</body>
</html>
"""


def build() -> Path:
    html = markdown.markdown(
        SRC.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    # Узкие экраны: таблицы должны скроллиться, а не ломать вёрстку.
    html = html.replace("<table>", '<div class="table-wrap"><table>').replace(
        "</table>", "</table></div>"
    )
    OUT.write_text(
        TEMPLATE.format(title=TITLE, css=CSS.strip(), hint=HINT, body=html),
        encoding="utf-8",
    )
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"{path.relative_to(ROOT)} — {path.stat().st_size / 1024:.0f} КБ")
