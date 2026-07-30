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

## Документы
- [Подбор оснастки 30.00.01.002](./podbor-osnastki-30.00.01.002.md)
