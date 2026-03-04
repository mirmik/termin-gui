# Диалоги и overlay

## Overlay API (через UI)

- `ui.show_overlay(widget, modal=False, dismiss_on_outside=True, on_dismiss=None)`
- `ui.hide_overlay(widget)`

Этим механизмом пользуются `Menu`, `ComboBox`, `Dialog`, file dialogs.

## Dialog

Базовый диалог с `title/content/buttons`.

API:
- поля: `title`, `content`, `buttons`, `default_button`, `cancel_button`, `on_result`, `min_width`
- методы: `show(ui, windowed=False)`, `close()`

Поведение:
- overlay mode (`windowed=False`) — центрируется внутри текущего `UI`;
- windowed mode (`windowed=True`) — использует `ui.create_window`, если задан.

## MessageBox

Готовые фабрики:
- `MessageBox.info(...)`
- `MessageBox.warning(...)`
- `MessageBox.error(...)`
- `MessageBox.question(...)`

Пресеты кнопок: `Buttons.OK`, `Buttons.OK_CANCEL`, `Buttons.YES_NO`, `Buttons.YES_NO_CANCEL`.

## Input Dialog

- `show_input_dialog(ui, title, message, default="", on_result=...)`
- в callback возвращает `str` на OK и `None` на Cancel.

## ColorDialog

- `ColorDialog.pick_color(ui, initial=(r,g,b,a), show_alpha=True, on_result=...)`
- callback: `(r,g,b,a)` или `None`.

## File dialogs

- `show_open_file_dialog(ui, on_result, *, title="Open File", directory="", filter_str="", filetypes=None, windowed=False)`
- `show_save_file_dialog(...)`
- `show_open_directory_dialog(...)`
- helper: `parse_filter_string("Images | *.png *.jpg;;All files | *.*")`

`on_result` всегда получает `path: str | None`.

## Пример

```python
from tcgui.widgets.message_box import MessageBox
from tcgui.widgets.file_dialog_overlay import show_open_file_dialog

MessageBox.question(
    ui,
    "Confirm",
    "Delete selected item?",
    on_result=lambda btn: print("result", btn),
)

show_open_file_dialog(
    ui,
    on_result=lambda path: print("picked", path),
    filter_str="Images | *.png *.jpg;;All files | *.*",
)
```
