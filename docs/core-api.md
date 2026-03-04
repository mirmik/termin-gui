# Core API

## Widget (базовый класс)

Общие поля, которые есть у всех виджетов:

- иерархия: `name`, `parent`, `children`
- размер/позиция: `preferred_width`, `preferred_height`, `x`, `y`, `width`, `height`
- якорь: `anchor`, `offset_x`, `offset_y`, `position_x`, `position_y`
- состояние: `visible`, `enabled`, `focusable`, `stretch`, `clip`, `mouse_transparent`
- UX: `tooltip`, `cursor`, `context_menu`

Базовые методы:

- дерево: `add_child(child)`, `remove_child(child)`, `find(name)`, `find_all(name)`
- layout/render: `compute_size(...)`, `layout(...)`, `render(renderer)`
- hit/event hooks: `hit_test(...)`, `on_mouse_*`, `on_key_down`, `on_text_input`, `on_focus`, `on_blur`

## UI

Ключевые свойства и методы `UI`:

- `root`, `font`, `loader`
- layout/render: `request_layout()`, `layout(...)`, `render(...)`
- tree helpers: `find(name)`, `find_all(name)`
- shortcuts: `add_shortcut(...)`, `remove_shortcut(...)`, `add_shortcut_from_string(...)`
- overlays: `show_overlay(...)`, `hide_overlay(widget)`
- focus: `set_focus(widget | None)`
- input API: `mouse_move`, `mouse_down`, `mouse_up`, `mouse_wheel`, `key_down`, `text_input`
- defer API: `defer(callback)`, `process_deferred()`

`UI` также имеет callback-и интеграции с окном:

- `on_cursor_changed(cursor_name)`
- `create_window(title, w, h) -> UI | None`
- `close_window()`
- `on_empty()`

## Units

- `px(x)`: абсолютные пиксели
- `ndc(x)`: доля от опорного размера (`0.0..1.0`)
- `pct(x)`: проценты (`pct(100) == ndc(1.0)`)
- `Value.parse(...)`: парсит `100`, `"120px"`, `"50%"`, `"0.25ndc"`

## Events

- `MouseEvent(x, y, button, mods)`
- `MouseWheelEvent(dx, dy, x, y)`
- `KeyEvent(key, mods)`
- `TextEvent(text)`

Для `MouseEvent`/`KeyEvent` есть удобные свойства: `.shift`, `.ctrl`, `.alt`.

## Theme

- `Theme.dark()`
- `theme.copy()`
- `theme.apply_to(root_widget)`
- глобальная переменная: `current_theme`

Важно: виджеты читают `current_theme` в `__init__`. Если меняете тему после создания, вызывайте `theme.apply_to(root)` или пересоздавайте дерево.

## Loader / Renderer

- `UILoader`: загрузка дерева из YAML (`load(path)`, `load_string(yaml_str)`, `register_type(...)`)
- `UIRenderer`: low-level рендер (`draw_rect`, `draw_text`, `draw_image`, `measure_text`, ...)
