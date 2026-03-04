# Базовые контролы

## Label

API:
- поля: `text`, `color`, `font_size`, `alignment` (`left|center|right`)

## Button

API:
- поля: `text`, `icon`, `checkable`, `checked`
- цвета: `background_color`, `hover_color`, `pressed_color`, `checked_color`, `text_color`
- callback: `on_click()`

## Checkbox

API:
- поля: `text`, `checked`, `box_size`, `font_size`, `spacing`
- callback: `on_changed(checked: bool)`

## IconButton

API:
- поля: `icon`, `active`, `size`, `font_size`, `tooltip`
- callback: `on_click()`

## Separator

API:
- поля: `orientation` (`vertical|horizontal`), `color`, `thickness`, `margin`

## ImageWidget

API:
- поля: `image_path`, `tint`
- размер без `preferred_*`: из реального размера картинки (после загрузки)

## ProgressBar

API:
- поля: `value` (`0..1`), `show_text`
- цвета: `background_color`, `fill_color`, `text_color`

## FrameTimeGraph

API:
- `add_frame(ms)`, `clear()`
- поле: `max_values`

## Пример

```python
row = HStack(); row.spacing = 10

ok = Button(); ok.text = "OK"
ok.on_click = lambda: print("ok")

ch = Checkbox(); ch.text = "Enable"; ch.checked = True
ch.on_changed = lambda v: print("checkbox", v)

pb = ProgressBar(); pb.value = 0.42; pb.show_text = True

row.add_child(ok)
row.add_child(ch)
row.add_child(pb)
```
