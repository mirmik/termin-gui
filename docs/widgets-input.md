# Ввод и редактирование

## TextInput (однострочный)

API:
- поля: `text`, `placeholder`, `cursor_pos`, `read_only`
- callbacks: `on_changed(text)`, `on_submit(text)`

Поддерживаемые клавиши:
- `Left/Right/Home/End`, `Backspace`, `Delete`, `Enter`

## TextArea (многострочный)

API:
- поле `text` (property)
- поля: `placeholder`, `max_lines`, `read_only`, `word_wrap`, `line_height`
- scrollbar: `show_scrollbar`, `scrollbar_width`
- callback: `on_changed(text)`

Поддерживает:
- multiline-редактирование, scroll wheel, cursor navigation, word wrap.

## Slider

API:
- поля: `value`, `min_value`, `max_value`, `step` (`0` = continuous)
- callback: `on_changed(value)`

## SpinBox

API:
- поля: `value`, `min_value`, `max_value`, `step`, `decimals`
- callback: `on_changed(value)`

## SliderEdit

Составной виджет (`Slider` + `SpinBox`) с общей моделью значения.

API:
- поля: `value`, `min_value`, `max_value`, `step`, `decimals`
- layout: `spacing`, `spinbox_width`
- callback: `on_changed(value)`

## ComboBox

API:
- поля: `items`, `selected_index`, `selected_text`, `placeholder`
- методы: `add_item(text)`, `clear()`, `item_count`, `item_text(index)`
- callback: `on_changed(index, text)`

## Пример

```python
inp = TextInput()
inp.placeholder = "Name"
inp.on_submit = lambda text: print("submit", text)

slider = Slider()
slider.min_value = 0
slider.max_value = 100
slider.step = 5
slider.on_changed = lambda v: print(int(v))

combo = ComboBox()
combo.items = ["Draft", "Ready", "Archived"]
combo.selected_index = 0
combo.on_changed = lambda i, t: print(i, t)
```
