# termin-gui

`termin-gui` — Python UI-фреймворк на виджетах для Termin.

Документация ниже отражает текущую реализацию в `python/tcgui/widgets/*` и примеры из `examples/*`.

## Рекомендуемый маршрут

1. [Быстрый старт](getting-started.md)
2. [Core API](core-api.md)
3. [Layout и контейнеры](widgets-layout.md)
4. [Базовые контролы](widgets-basic.md)
5. [Ввод и редактирование](widgets-input.md)
6. [Данные и навигация](widgets-data-nav.md)
7. [Диалоги и overlay](widgets-dialogs.md)
8. [Canvas и Viewport3D](widgets-canvas-viewport.md)

## Пакетные точки входа

- `from tcgui import *` — полный публичный API.
- `from tcgui.widgets.basic import ...` — базовые контролы.
- `from tcgui.widgets.containers import ...` — контейнеры.

## Что считать «публичным API»

В этом разделе под API подразумеваются:
- классы и функции, экспортируемые через `tcgui.widgets.__all__`;
- публичные поля и callbacks, используемые в примерах;
- публичные методы (без `_` в начале), доступные для прикладного кода.
