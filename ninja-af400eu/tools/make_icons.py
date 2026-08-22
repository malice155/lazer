"""Генерация иконок приложения для домашнего экрана iPhone."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "public" / "icons"
TOP = (206, 118, 62)
BOTTOM = (163, 71, 24)
CREAM = (253, 247, 240)
HEART = (232, 122, 108)


def gradient(size: int) -> Image.Image:
    image = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(image)
    for y in range(size):
        ratio = y / max(1, size - 1)
        draw.line(
            [(0, y), (size, y)],
            fill=tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * ratio) for i in range(3)),
        )
    return image


def heart(draw: ImageDraw.ImageDraw, cx: float, cy: float, width: float, fill) -> None:
    points = []
    for step in range(721):
        t = math.radians(step / 2)
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        scale = width / 32
        points.append((cx + x * scale, cy - y * scale))
    draw.polygon(points, fill=fill)


def draw_art(image: Image.Image, size: int) -> None:
    draw = ImageDraw.Draw(image)
    unit = size / 100

    # Корпус аэрогриля
    body = [12 * unit, 30 * unit, 88 * unit, 88 * unit]
    draw.rounded_rectangle(body, radius=12 * unit, fill=CREAM)

    # Две корзины — главная особенность модели
    for left in (20 * unit, 54 * unit):
        draw.rounded_rectangle(
            [left, 58 * unit, left + 26 * unit, 80 * unit],
            radius=5 * unit,
            fill=BOTTOM,
        )
        draw.rounded_rectangle(
            [left + 8 * unit, 63 * unit, left + 18 * unit, 66 * unit],
            radius=2 * unit,
            fill=CREAM,
        )

    # Панель управления
    draw.rounded_rectangle(
        [20 * unit, 38 * unit, 62 * unit, 48 * unit], radius=4 * unit, fill=(238, 226, 214)
    )
    draw.ellipse([68 * unit, 36 * unit, 82 * unit, 50 * unit], fill=BOTTOM)

    # Сердечко вместо пара — это приложение сделано с любовью
    heart(draw, size / 2, 18 * unit, 30 * unit, HEART)


def rounded_mask(size: int, radius_ratio: float) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=int(size * radius_ratio), fill=255
    )
    return mask


def build(size: int, path: Path, radius_ratio: float | None = 0.22, safe_zone: bool = False) -> None:
    canvas = gradient(size)
    if safe_zone:
        # Для maskable-иконки рисуем внутри 80 % площади, чтобы ничего не срезалось
        inner = int(size * 0.8)
        art = gradient(inner)
        draw_art(art, inner)
        canvas.paste(art, ((size - inner) // 2, (size - inner) // 2))
    else:
        draw_art(canvas, size)

    if radius_ratio is None:
        canvas.save(path)
        return

    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(canvas, (0, 0), rounded_mask(size, radius_ratio))
    result.save(path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build(192, OUT / "icon-192.png")
    build(512, OUT / "icon-512.png")
    build(512, OUT / "icon-512-maskable.png", radius_ratio=None, safe_zone=True)
    build(180, OUT / "apple-touch-icon.png", radius_ratio=None)
    print("Иконки готовы:", OUT)


if __name__ == "__main__":
    main()
