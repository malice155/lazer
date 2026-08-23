# lazer

Подбор гибочной оснастки и DXF для лазера (Amada / Promecam).

## Важно
Станок: **Amada Operateur**, зажим Promecam — нужен хвостовик **13 мм** с канавкой.
Старый файл с прямоугольным хвостовиком 80 мм **не использовать**.

## DXF под Amada (лист 5 мм)
- [`dxf/punch-R47-amada-nest-32pcs-5mm.dxf`](./dxf/punch-R47-amada-nest-32pcs-5mm.dxf) — **резать этот** (32 шт)
- [`dxf/punch-R47-amada-plate-5mm.dxf`](./dxf/punch-R47-amada-plate-5mm.dxf) — 1 пластина
- [`dxf/punch-R47-amada-preview.png`](./dxf/punch-R47-amada-preview.png) — эскиз
- [`dxf/punch-R47-amada-cutting-card.md`](./dxf/punch-R47-amada-cutting-card.md) — карта

```bash
python3 tools/generate_punch_r47_amada_dxf.py
```

## Раскладки на лист 3015 / 4020
- [`dxf/punch-R47-sheet-nests.md`](./dxf/punch-R47-sheet-nests.md) — компакт 32 / полоса 3015 / полный 3015 / полный 4020
- DXF полосы: `dxf/punch-R47-amada-nest-3015-strip.dxf`. Полные листы — скриптом ниже.

```bash
python3 tools/generate_punch_r47_sheet_nests.py
```

## Закупка лазера мощнее L3030
- [Решение директора, пакеты, цех, ТСО](./docs/zakupka-lazera-2026.md)
- Промпт: [`.cursor/prompts/laserprof-director-stanok.md`](./.cursor/prompts/laserprof-director-stanok.md)

## Документы
- [Подбор оснастки 30.00.01.002](./podbor-osnastki-30.00.01.002.md)
