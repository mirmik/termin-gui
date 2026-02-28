"""File dialogs implemented in tcgui overlay layer."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Callable, Sequence

from tcbase import log
from tcgui.widgets.dialog import Dialog
from tcgui.widgets.hstack import HStack
from tcgui.widgets.label import Label
from tcgui.widgets.list_widget import ListWidget
from tcgui.widgets.text_input import TextInput
from tcgui.widgets.button import Button
from tcgui.widgets.units import px
from tcgui.widgets.vstack import VStack

FilterSpec = tuple[str, str]


def parse_filter_string(filter_str: str) -> list[FilterSpec]:
    """Parse ``'Label | *.ext;;Label2 | *.x *.y'`` to filter list."""
    if not filter_str:
        return [("All files", "*.*")]

    result: list[FilterSpec] = []
    for raw_part in filter_str.split(";;"):
        part = raw_part.strip()
        if not part:
            continue
        if "|" in part:
            label, exts = part.split("|", 1)
            result.append((label.strip() or "Files", exts.strip() or "*.*"))
        else:
            result.append((part, "*.*"))

    return result or [("All files", "*.*")]


class _OverlayFileDialog:
    def __init__(
        self,
        *,
        mode: str,
        title: str,
        directory: str,
        filter_str: str,
        filetypes: Sequence[FilterSpec] | None,
        on_result: Callable[[str | None], None],
    ):
        self._mode = mode
        self._on_result = on_result
        self._filters = (
            parse_filter_string(filter_str)
            if filetypes is None else list(filetypes)
        )
        self._current_dir = self._normalize_start_dir(directory)
        self._selected_path: Path | None = None

        self._dialog = Dialog()
        self._dialog.title = title
        self._dialog.min_width = 780

        self._dir_label = Label()
        self._dir_label.font_size = 13

        self._up_button = Button()
        self._up_button.text = "Up"
        self._up_button.preferred_width = px(70)
        self._up_button.on_click = self._go_up

        self._list = ListWidget()
        self._list.preferred_width = px(740)
        self._list.preferred_height = px(360)
        self._list.item_height = 34
        self._list.on_select = self._on_select
        self._list.on_activate = self._on_activate

        self._name_input = TextInput()
        self._name_input.preferred_width = px(740)
        self._name_input.placeholder = "File name"
        self._name_input.on_submit = lambda _text: self._confirm()

        content = VStack()
        content.spacing = 10

        nav_row = HStack()
        nav_row.spacing = 8
        self._dir_label.stretch = True
        nav_row.add_child(self._up_button)
        nav_row.add_child(self._dir_label)

        content.add_child(nav_row)
        content.add_child(self._list)
        if self._mode == "save_file":
            content.add_child(self._name_input)

        self._dialog.content = content
        if self._mode == "open_file":
            self._dialog.buttons = ["Open", "Cancel"]
            self._dialog.default_button = "Open"
        elif self._mode == "save_file":
            self._dialog.buttons = ["Save", "Cancel"]
            self._dialog.default_button = "Save"
        else:
            self._dialog.buttons = ["Select", "Cancel"]
            self._dialog.default_button = "Select"
        self._dialog.cancel_button = "Cancel"
        self._dialog.on_result = self._on_dialog_result

        self._refresh_list()

    def show(self, ui) -> None:
        self._dialog.show(ui)

    def _normalize_start_dir(self, directory: str) -> Path:
        if directory:
            p = Path(directory).expanduser()
            if p.exists() and p.is_dir():
                return p.resolve()
        return Path.cwd()

    def _go_up(self) -> None:
        parent = self._current_dir.parent
        if parent != self._current_dir and parent.exists():
            self._current_dir = parent
            self._selected_path = None
            self._refresh_list()

    def _refresh_list(self) -> None:
        self._dir_label.text = str(self._current_dir)
        items: list[dict] = []

        try:
            entries = list(os.scandir(self._current_dir))
        except Exception as e:
            log.error(f"[file_dialog_overlay] listdir failed for '{self._current_dir}': {e}")
            entries = []

        dirs = sorted((e for e in entries if e.is_dir(follow_symlinks=False)), key=lambda e: e.name.lower())
        files = sorted((e for e in entries if e.is_file(follow_symlinks=False)), key=lambda e: e.name.lower())

        for e in dirs:
            items.append({
                "text": f"[DIR] {e.name}",
                "subtitle": "",
                "data": {"path": e.path, "is_dir": True},
            })

        if self._mode != "open_directory":
            for e in files:
                if self._accept_file(e.name):
                    items.append({
                        "text": e.name,
                        "subtitle": "",
                        "data": {"path": e.path, "is_dir": False},
                    })

        self._list.set_items(items)

    def _accept_file(self, name: str) -> bool:
        if not self._filters:
            return True
        for _label, pattern_group in self._filters:
            patterns = pattern_group.split()
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    return True
        return False

    def _on_select(self, _index: int, item: dict) -> None:
        data = item.get("data") or {}
        path = data.get("path")
        if not path:
            return
        self._selected_path = Path(path)
        if self._mode == "save_file" and not data.get("is_dir"):
            self._name_input.text = self._selected_path.name
            self._name_input.cursor_pos = len(self._name_input.text)

    def _on_activate(self, _index: int, item: dict) -> None:
        data = item.get("data") or {}
        path = data.get("path")
        if not path:
            return
        p = Path(path)
        is_dir = bool(data.get("is_dir"))

        if is_dir:
            self._current_dir = p
            self._selected_path = None
            self._refresh_list()
            return

        self._selected_path = p
        if self._mode == "open_file":
            self._resolve_and_close(str(p))
        elif self._mode == "save_file":
            self._name_input.text = p.name
            self._name_input.cursor_pos = len(self._name_input.text)

    def _on_dialog_result(self, button: str) -> None:
        if button in ("Cancel", ""):
            self._resolve_and_close(None)
            return
        self._confirm()

    def _confirm(self) -> None:
        if self._mode == "open_file":
            if self._selected_path is None or self._selected_path.is_dir():
                return
            self._resolve_and_close(str(self._selected_path))
            return

        if self._mode == "open_directory":
            if self._selected_path is not None and self._selected_path.is_dir():
                self._resolve_and_close(str(self._selected_path))
            else:
                self._resolve_and_close(str(self._current_dir))
            return

        # save_file
        name = self._name_input.text.strip()
        if not name:
            if self._selected_path is not None and not self._selected_path.is_dir():
                name = self._selected_path.name
            else:
                return
        out = self._current_dir / name
        self._resolve_and_close(str(out))

    def _resolve_and_close(self, path: str | None) -> None:
        try:
            self._on_result(path)
        finally:
            self._dialog.close()


def show_open_file_dialog(
    ui,
    on_result: Callable[[str | None], None],
    *,
    title: str = "Open File",
    directory: str = "",
    filter_str: str = "",
    filetypes: Sequence[FilterSpec] | None = None,
) -> None:
    """Show overlay open-file dialog. Result is delivered via callback."""
    dlg = _OverlayFileDialog(
        mode="open_file",
        title=title,
        directory=directory,
        filter_str=filter_str,
        filetypes=filetypes,
        on_result=on_result,
    )
    dlg.show(ui)


def show_save_file_dialog(
    ui,
    on_result: Callable[[str | None], None],
    *,
    title: str = "Save File",
    directory: str = "",
    filter_str: str = "",
    filetypes: Sequence[FilterSpec] | None = None,
) -> None:
    """Show overlay save-file dialog. Result is delivered via callback."""
    dlg = _OverlayFileDialog(
        mode="save_file",
        title=title,
        directory=directory,
        filter_str=filter_str,
        filetypes=filetypes,
        on_result=on_result,
    )
    dlg.show(ui)


def show_open_directory_dialog(
    ui,
    on_result: Callable[[str | None], None],
    *,
    title: str = "Open Directory",
    directory: str = "",
) -> None:
    """Show overlay open-directory dialog. Result is delivered via callback."""
    dlg = _OverlayFileDialog(
        mode="open_directory",
        title=title,
        directory=directory,
        filter_str="",
        filetypes=None,
        on_result=on_result,
    )
    dlg.show(ui)
