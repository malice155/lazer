# lazer

Подбор гибочной оснастки и DXF для лазера.

## Документы
- [Подбор пуансона и матрицы для 30.00.01.002](./podbor-osnastki-30.00.01.002.md)
- [Карта реза пуансона R47](./dxf/punch-R47-cutting-card.md)

## DXF для лазера (лист 5 мм)
- [`dxf/punch-R47-plate-5mm.dxf`](./dxf/punch-R47-plate-5mm.dxf) — 1 пластина профиля
- [`dxf/punch-R47-nest-32pcs-5mm.dxf`](./dxf/punch-R47-nest-32pcs-5mm.dxf) — нестинг 32 шт (пакет L=160 мм)
- [`dxf/punch-R47-gauge-5mm.dxf`](./dxf/punch-R47-gauge-5mm.dxf) — калибры R47

Перегенерация:

```bash
python3 tools/generate_punch_r47_dxf.py
```
