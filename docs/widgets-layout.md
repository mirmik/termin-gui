# Layout и контейнеры

## HStack

Горизонтальная раскладка.

API:
- поля: `spacing`, `alignment` (`top|center|bottom`), `justify` (`start|center|end`)
- поддерживает `child.stretch = True` для растягивания по ширине

## VStack

Вертикальная раскладка.

API:
- поля: `spacing`, `alignment` (`left|center|right`), `justify` (`start|center|end`)
- поддерживает `child.stretch = True` для растягивания по высоте

## GridLayout

Сетка с явным позиционированием.

API:
- `GridLayout(columns=2)`
- `add(child, row, col, row_span=1, col_span=1)`
- `clear()`
- `set_column_stretch(column, stretch)`
- `set_row_stretch(row, stretch)`
- поля: `row_spacing`, `column_spacing`, `padding`

## Panel

Контейнер с фоном и паддингом.

API:
- поля: `padding`, `background_color`, `border_radius`
- фон-изображение: `background_image`, `background_tint`

Поведение:
- child раскладываются с учетом `anchor`/`offset`/`position_*`.

## ScrollArea

Скроллируемый контейнер (обычно один child с большим контентом).

API:
- поля: `scroll_x`, `scroll_y`, `scroll_speed`
- scrollbar: `show_scrollbar`, `scrollbar_width`, `scrollbar_color`, `scrollbar_hover_color`

Поведение:
- wheel меняет `scroll_y`;
- drag по scrollbar поддерживается из коробки.

## GroupBox

Сворачиваемая секция с заголовком.

API:
- поля: `title`, `expanded`, `title_height`, `content_padding`, `spacing`
- callback: `on_toggle(expanded: bool)`

## Splitter

Перетаскиваемый разделитель для изменения размера соседней панели.

API:
- `Splitter(target: Widget, side="left|right|top|bottom")`
- поля: `color`, `hover_color`, `bar_width`

Поведение:
- при drag меняет `target.preferred_width` или `target.preferred_height`.

## Пример

```python
layout = HStack()
layout.spacing = 8

left = Panel(); left.preferred_width = px(260)
right = Panel(); right.stretch = True

splitter = Splitter(target=left, side="right")
layout.add_child(left)
layout.add_child(splitter)
layout.add_child(right)
```
