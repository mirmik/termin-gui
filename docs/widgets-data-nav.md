# Данные и навигация

## ListWidget

API:
- `set_items(items: list[dict])`
- `items`, `selected_item`, `selected_index`
- callbacks:
  - `on_select(index, item)`
  - `on_activate(index, item)` (double click)
  - `on_context_menu(index, item, x, y)`

Формат `item`: обычно `{"text": ..., "subtitle": ..., "data": ...}`.

## TableWidget

API:
- `set_columns(columns: list[TableColumn])`
- `set_rows(rows: list[list[str]], data: list[Any] | None = None)`
- `selected_data`, `selected_index`
- callbacks: `on_select(index, data)`, `on_activate(index, data)`

`TableColumn(header, width=0, min_width=40)`:
- `width=0` означает stretch-колонку.

Есть drag resize колонок в header.

## TreeWidget / TreeNode

`TreeNode`:
- поля: `content`, `subnodes`, `expanded`, `data`, `has_subnodes`
- методы: `add_node(node)`, `remove_node(node)`, `toggle()`

`TreeWidget`:
- методы: `add_root(node)`, `remove_root(node)`, `clear()`
- поля: `selected_node`, `draggable`, `row_height`, `indent_size`
- callbacks:
  - `on_select(node)`
  - `on_activate(node)`
  - `on_expand(node)`, `on_collapse(node)`
  - `on_drop(dragged, target, position)`
  - `on_context_menu(node_or_none, x, y)`

`position` в `on_drop`: `"above" | "below" | "inside" | "root"`.

## Tabs

`TabBar`:
- `tabs`, `selected_index`
- callback: `on_changed(index)`

`TabView`:
- методы: `add_tab(title, content)`, `remove_tab(index)`
- property: `selected_index`
- поле: `tab_position` (`top|bottom`)

## Menu / MenuBar

`MenuItem(label, icon=None, shortcut=None, enabled=True, separator=False, on_click=None)`
- shortcut helper: `MenuItem.sep()`

`Menu`:
- `items`, `add_item(item)`, `show(ui, x, y)`

`MenuBar`:
- `add_menu(label, menu)`
- `register_shortcuts(ui)` — зарегистрирует `shortcut` всех пунктов

## ToolBar / StatusBar

`ToolBar`:
- `add_action(...)`, `add_separator()`, `add_item(item)`
- `ToolBarItem.sep()`

`StatusBar`:
- `text` / `set_text(text)`
- `show_message(text, timeout_ms=3000)`

## Пример

```python
menu = Menu()
menu.items = [
    MenuItem("Open", shortcut="Ctrl+O", on_click=lambda: print("open")),
    MenuItem.sep(),
    MenuItem("Quit", shortcut="Ctrl+Q", on_click=lambda: print("quit")),
]

bar = MenuBar()
bar.add_menu("File", menu)
bar.register_shortcuts(ui)
```
