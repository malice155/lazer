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

## Закупка лазера мощнее L3030
Job-shop, **без азота** (O₂ + воздух), кран 3 т уже есть. Пуансон R47 выше — просто один заказ, не ТЗ на станок.
- [Варианты с ценами, за и против, деньги, цех](./docs/zakupka-lazera-2026.md) — вывод: **fiber 12 кВт 3015 на Raycus CE, станок 7,8–8,9 млн ₽, проект 9,5–13,5 млн**
- [Готовые письма](./docs/pisma-po-zakupke.md): запрос КП поставщику, письмо партнёру, сообщение в мессенджер
- Промпт: [`.cursor/prompts/laserprof-director-stanok.md`](./.cursor/prompts/laserprof-director-stanok.md)

Чтобы отправить почтой: `docs/zakupka-lazera-2026.html` — один файл, вложение открывается в любом браузере, печатается в PDF через Ctrl+P. Пересобрать после правок `.md`:

```bash
pip install markdown && python3 tools/build_zakupka_page.py
```

## Документы
- [Подбор оснастки 30.00.01.002](./podbor-osnastki-30.00.01.002.md)
