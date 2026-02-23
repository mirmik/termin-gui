"""Basic widgets: Label, Button, Checkbox, IconButton, Separator, ImageWidget, ListWidget, ProgressBar, Slider."""

from __future__ import annotations
import time
from typing import Any, Callable

from tcbase import MouseButton
from tcgui.widgets.widget import Widget
from tcgui.widgets.events import MouseEvent, MouseWheelEvent, KeyEvent, TextEvent
from tcgui.widgets.theme import current_theme as _t


class Label(Widget):
    """Text label widget."""

    def __init__(self):
        super().__init__()
        self.text: str = ""
        self.color: tuple[float, float, float, float] = _t.text_primary
        self.font_size: float = _t.font_size
        self.alignment: str = "left"  # left, center, right

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        # Approximate text size (will be refined when we have font metrics)
        text_width = len(self.text) * self.font_size * 0.6
        text_height = self.font_size * 1.2
        return (text_width, text_height)

    def render(self, renderer: 'UIRenderer'):
        if self.alignment == "center":
            renderer.draw_text_centered(
                self.x + self.width / 2,
                self.y + self.height / 2,
                self.text,
                self.color,
                self.font_size
            )
        elif self.alignment == "right":
            text_width, _ = renderer.measure_text(self.text, self.font_size)
            renderer.draw_text(
                self.x + self.width - text_width,
                self.y + self.font_size,
                self.text,
                self.color,
                self.font_size
            )
        else:  # left
            renderer.draw_text(
                self.x,
                self.y + self.font_size,
                self.text,
                self.color,
                self.font_size
            )


class Button(Widget):
    """Clickable button widget."""

    def __init__(self):
        super().__init__()
        self.text: str = ""
        self.icon: str | None = None

        # Colors
        self.background_color: tuple[float, float, float, float] = _t.bg_surface
        self.hover_color: tuple[float, float, float, float] = _t.hover
        self.pressed_color: tuple[float, float, float, float] = _t.pressed
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.border_radius: float = _t.border_radius

        # State
        self.hovered: bool = False
        self.pressed: bool = False

        # Callback
        self.on_click: Callable[[], None] | None = None

        # Text settings
        self.font_size: float = _t.font_size
        self.padding: float = 10

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        # Size based on text + padding
        text_width = len(self.text) * self.font_size * 0.6
        return (text_width + self.padding * 2, self.font_size + self.padding * 2)

    def render(self, renderer: 'UIRenderer'):
        # Choose color based on state
        if self.pressed:
            color = self.pressed_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.background_color

        # Draw background
        renderer.draw_rect(
            self.x, self.y, self.width, self.height,
            color, self.border_radius
        )

        # Draw text centered
        if self.text:
            renderer.draw_text_centered(
                self.x + self.width / 2,
                self.y + self.height / 2,
                self.text,
                self.text_color,
                self.font_size
            )

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False
        self.pressed = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        if not self.enabled:
            return False
        self.pressed = True
        return True

    def on_mouse_up(self, event: MouseEvent):
        if self.pressed and self.contains(event.x, event.y):
            if self.on_click:
                self.on_click()
        self.pressed = False


class Checkbox(Widget):
    """Toggle checkbox widget with visual indicator."""

    def __init__(self):
        super().__init__()
        self.text: str = ""
        self.checked: bool = False

        # Colors
        self.box_color: tuple[float, float, float, float] = _t.bg_surface
        self.check_color: tuple[float, float, float, float] = _t.accent_success
        self.hover_color: tuple[float, float, float, float] = _t.hover
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.border_radius: float = _t.border_radius

        # State
        self.hovered: bool = False
        self.pressed: bool = False

        # Callback
        self.on_change: Callable[[bool], None] | None = None

        # Text settings
        self.font_size: float = _t.font_size
        self.box_size: float = 18
        self.spacing: float = _t.spacing

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        # Size based on box + text
        text_width = len(self.text) * self.font_size * 0.6 if self.text else 0
        total_width = self.box_size + (self.spacing + text_width if self.text else 0)
        return (total_width, max(self.box_size, self.font_size))

    def render(self, renderer: 'UIRenderer'):
        # Box background color based on state
        if self.hovered:
            box_bg = self.hover_color
        else:
            box_bg = self.box_color

        # Draw checkbox box
        box_y = self.y + (self.height - self.box_size) / 2
        renderer.draw_rect(
            self.x, box_y, self.box_size, self.box_size,
            box_bg, self.border_radius
        )

        # Draw checkmark if checked
        if self.checked:
            # Inner filled rectangle as checkmark indicator
            inset = 4
            renderer.draw_rect(
                self.x + inset, box_y + inset,
                self.box_size - inset * 2, self.box_size - inset * 2,
                self.check_color, self.border_radius - 1
            )

        # Draw text label
        if self.text:
            text_x = self.x + self.box_size + self.spacing
            renderer.draw_text(
                text_x,
                self.y + self.height / 2 + self.font_size / 3,
                self.text,
                self.text_color,
                self.font_size
            )

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False
        self.pressed = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        self.pressed = True
        return True

    def on_mouse_up(self, event: MouseEvent):
        if self.pressed and self.contains(event.x, event.y):
            self.checked = not self.checked
            if self.on_change:
                self.on_change(self.checked)
        self.pressed = False


class IconButton(Widget):
    """Compact square button with icon/symbol."""

    def __init__(self):
        super().__init__()
        self.icon: str = ""  # Single character or short text as icon
        self.tooltip: str = ""

        # Colors
        _bg = _t.bg_surface
        self.background_color: tuple[float, float, float, float] = (_bg[0], _bg[1], _bg[2], 0.9)
        self.hover_color: tuple[float, float, float, float] = _t.hover
        self.pressed_color: tuple[float, float, float, float] = _t.pressed
        self.active_color: tuple[float, float, float, float] = _t.accent
        self.icon_color: tuple[float, float, float, float] = _t.text_secondary
        self.border_radius: float = _t.border_radius + 1

        # State
        self.hovered: bool = False
        self.pressed: bool = False
        self.active: bool = False  # Toggle state for mode buttons

        # Callback
        self.on_click: Callable[[], None] | None = None

        # Size
        self.size: float = 28
        self.font_size: float = 16

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        return (self.size, self.size)

    def render(self, renderer: 'UIRenderer'):
        # Choose color based on state
        if self.pressed:
            color = self.pressed_color
        elif self.active:
            color = self.active_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.background_color

        # Draw background
        renderer.draw_rect(
            self.x, self.y, self.width, self.height,
            color, self.border_radius
        )

        # Draw icon centered
        if self.icon:
            renderer.draw_text_centered(
                self.x + self.width / 2,
                self.y + self.height / 2,
                self.icon,
                self.icon_color,
                self.font_size
            )

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False
        self.pressed = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        self.pressed = True
        return True

    def on_mouse_up(self, event: MouseEvent):
        if self.pressed and self.contains(event.x, event.y):
            if self.on_click:
                self.on_click()
        self.pressed = False


class Separator(Widget):
    """Visual separator line."""

    def __init__(self):
        super().__init__()
        self.orientation: str = "vertical"  # vertical, horizontal
        self.color: tuple[float, float, float, float] = _t.text_muted
        self.thickness: float = 1
        self.margin: float = 4  # space around separator

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.orientation == "vertical":
            return (self.thickness + self.margin * 2, 0)  # height from parent
        else:
            return (0, self.thickness + self.margin * 2)  # width from parent

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        # Separator takes full extent in the stacking direction
        if self.orientation == "vertical":
            actual_width = self.thickness + self.margin * 2
            super().layout(x, y, actual_width, height, viewport_w, viewport_h)
        else:
            actual_height = self.thickness + self.margin * 2
            super().layout(x, y, width, actual_height, viewport_w, viewport_h)

    def render(self, renderer: 'UIRenderer'):
        if self.orientation == "vertical":
            lx = self.x + self.margin + self.thickness / 2
            renderer.draw_rect(
                lx - self.thickness / 2,
                self.y + self.margin,
                self.thickness,
                self.height - self.margin * 2,
                self.color
            )
        else:
            ly = self.y + self.margin + self.thickness / 2
            renderer.draw_rect(
                self.x + self.margin,
                ly - self.thickness / 2,
                self.width - self.margin * 2,
                self.thickness,
                self.color
            )


class ImageWidget(Widget):
    """Widget that displays an image from a file."""

    def __init__(self):
        super().__init__()
        self.image_path: str = ""
        self.tint: tuple[float, float, float, float] = (1, 1, 1, 1)
        self._texture = None
        self._image_w: int = 0
        self._image_h: int = 0

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        # Use native image size if loaded
        if self._image_w > 0 and self._image_h > 0:
            w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else float(self._image_w)
            h = self.preferred_height.to_pixels(viewport_h) if self.preferred_height else float(self._image_h)
            return (w, h)
        return (64, 64)

    def _ensure_texture(self, renderer: 'UIRenderer'):
        if self._texture is None and self.image_path:
            from PIL import Image
            img = Image.open(self.image_path)
            self._image_w, self._image_h = img.size
            self._texture = renderer.load_image(self.image_path)

    def render(self, renderer: 'UIRenderer'):
        self._ensure_texture(renderer)
        if self._texture is not None:
            renderer.draw_image(
                self.x, self.y, self.width, self.height,
                self._texture, self.tint
            )


class TextInput(Widget):
    """Single-line text input widget."""

    def __init__(self):
        super().__init__()
        self.focusable: bool = True

        # Text content
        self.text: str = ""
        self.placeholder: str = ""
        self.cursor_pos: int = 0

        # Visual configuration
        self.font_size: float = _t.font_size
        self.padding: float = 6
        self.border_width: float = 1
        self.border_radius: float = _t.border_radius
        self.background_color: tuple[float, float, float, float] = _t.bg_input
        self.focused_background_color: tuple[float, float, float, float] = _t.bg_input_focus
        self.border_color: tuple[float, float, float, float] = _t.border
        self.focused_border_color: tuple[float, float, float, float] = _t.border_focus
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.placeholder_color: tuple[float, float, float, float] = _t.text_muted
        self.cursor_color: tuple[float, float, float, float] = _t.text_primary

        # State
        self.focused: bool = False
        self.hovered: bool = False
        self._scroll_offset: float = 0.0
        self._cursor_blink_time: float = 0.0
        self._cursor_visible: bool = True
        self._renderer: 'UIRenderer | None' = None

        # Callbacks
        self.on_change: Callable[[str], None] | None = None
        self.on_submit: Callable[[str], None] | None = None

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 200
        h = self.font_size + self.padding * 2 + self.border_width * 2
        return (w, h)

    def render(self, renderer: 'UIRenderer'):
        self._renderer = renderer
        bw = self.border_width

        # Border
        border_col = self.focused_border_color if self.focused else self.border_color
        renderer.draw_rect(
            self.x, self.y, self.width, self.height,
            border_col, self.border_radius
        )

        # Background (inset by border)
        bg_color = self.focused_background_color if self.focused else self.background_color
        renderer.draw_rect(
            self.x + bw, self.y + bw,
            self.width - bw * 2, self.height - bw * 2,
            bg_color, max(0, self.border_radius - bw)
        )

        # Text area bounds
        text_x = self.x + self.padding + bw
        text_area_width = self.width - (self.padding + bw) * 2
        text_area_height = self.height - bw * 2
        baseline_y = self.y + bw + self.padding + self.font_size

        # Clip text and cursor to the inner area
        renderer.begin_clip(text_x, self.y + bw, text_area_width, text_area_height)

        if self.text:
            self._update_scroll(renderer, text_area_width)
            renderer.draw_text(
                text_x - self._scroll_offset, baseline_y,
                self.text, self.text_color, self.font_size
            )
        elif not self.focused and self.placeholder:
            renderer.draw_text(
                text_x, baseline_y,
                self.placeholder, self.placeholder_color, self.font_size
            )

        # Cursor
        if self.focused:
            self._update_cursor_blink()
            if self._cursor_visible:
                cursor_px = self._get_cursor_x(renderer)
                cursor_screen_x = text_x + cursor_px - self._scroll_offset
                cursor_y = self.y + bw + self.padding
                renderer.draw_rect(
                    cursor_screen_x, cursor_y,
                    1.5, self.font_size,
                    self.cursor_color
                )

        renderer.end_clip()

    # --- Text measurement helpers ---

    def _measure_text_width(self, renderer: 'UIRenderer', text: str) -> float:
        w, _ = renderer.measure_text(text, self.font_size)
        return w

    def _get_cursor_x(self, renderer: 'UIRenderer') -> float:
        return self._measure_text_width(renderer, self.text[:self.cursor_pos])

    def _update_scroll(self, renderer: 'UIRenderer', text_area_width: float):
        cursor_x = self._get_cursor_x(renderer)
        if cursor_x - self._scroll_offset > text_area_width:
            self._scroll_offset = cursor_x - text_area_width
        if cursor_x - self._scroll_offset < 0:
            self._scroll_offset = cursor_x
        if self._scroll_offset < 0:
            self._scroll_offset = 0

    # --- Cursor blink ---

    def _update_cursor_blink(self):
        now = time.monotonic()
        if now - self._cursor_blink_time >= 0.5:
            self._cursor_visible = not self._cursor_visible
            self._cursor_blink_time = now

    def _reset_cursor_blink(self):
        self._cursor_visible = True
        self._cursor_blink_time = time.monotonic()

    # --- Cursor positioning from click ---

    def _cursor_pos_from_x(self, renderer: 'UIRenderer', click_x: float) -> int:
        text_start_x = self.x + self.padding + self.border_width
        relative_x = click_x - text_start_x + self._scroll_offset
        x_acc = 0.0
        for i, ch in enumerate(self.text):
            char_w = self._measure_text_width(renderer, ch)
            if relative_x < x_acc + char_w / 2:
                return i
            x_acc += char_w
        return len(self.text)

    # --- Mouse events ---

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        if self._renderer is not None:
            self.cursor_pos = self._cursor_pos_from_x(self._renderer, event.x)
        self._reset_cursor_blink()
        return True

    # --- Focus events ---

    def on_focus(self):
        self.focused = True
        self._reset_cursor_blink()

    def on_blur(self):
        self.focused = False

    # --- Keyboard events ---

    def on_key_down(self, event: KeyEvent) -> bool:
        from tcbase import Key

        key = event.key
        if key == Key.BACKSPACE:
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
                self._fire_on_change()
            self._reset_cursor_blink()
            return True

        if key == Key.DELETE:
            if self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
                self._fire_on_change()
            self._reset_cursor_blink()
            return True

        if key == Key.LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
            self._reset_cursor_blink()
            return True

        if key == Key.RIGHT:
            if self.cursor_pos < len(self.text):
                self.cursor_pos += 1
            self._reset_cursor_blink()
            return True

        if key == Key.HOME:
            self.cursor_pos = 0
            self._reset_cursor_blink()
            return True

        if key == Key.END:
            self.cursor_pos = len(self.text)
            self._reset_cursor_blink()
            return True

        if key == Key.ENTER:
            if self.on_submit is not None:
                self.on_submit(self.text)
            return True

        return False

    def on_text_input(self, event: TextEvent) -> bool:
        self.text = self.text[:self.cursor_pos] + event.text + self.text[self.cursor_pos:]
        self.cursor_pos += len(event.text)
        self._fire_on_change()
        self._reset_cursor_blink()
        return True

    def _fire_on_change(self):
        if self.on_change is not None:
            self.on_change(self.text)


class ListWidget(Widget):
    """Vertical list with selectable items, hover highlight, and double-click."""

    def __init__(self):
        super().__init__()
        self._items: list[dict] = []
        self.selected_index: int = -1
        self.item_height: float = 44
        self.item_spacing: float = 2
        self.font_size: float = _t.font_size
        self.subtitle_font_size: float = _t.font_size_small
        self.border_radius: float = _t.border_radius + 1
        self.item_padding: float = 10

        # Colors
        _bif = _t.bg_input_focus
        self.item_background: tuple[float, float, float, float] = (_bif[0], _bif[1], _bif[2], 0.6)
        self.selected_background: tuple[float, float, float, float] = _t.selected
        self.hover_background: tuple[float, float, float, float] = _t.hover_subtle
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.subtitle_color: tuple[float, float, float, float] = _t.text_muted
        self.selected_text_color: tuple[float, float, float, float] = _t.text_primary
        self.empty_text: str = "No items"
        self.empty_color: tuple[float, float, float, float] = _t.text_muted

        # Callbacks: (index, item_dict)
        self.on_select: Callable[[int, dict], None] | None = None
        self.on_activate: Callable[[int, dict], None] | None = None

        # Internal
        self._scroll_offset: float = 0.0
        self._hovered_index: int = -1
        self._last_click_index: int = -1
        self._last_click_time: float = 0.0
        self._DOUBLE_CLICK_INTERVAL: float = 0.4

    def set_items(self, items: list[dict]) -> None:
        """Set list items. Each dict should have 'text' and optionally 'subtitle', 'data'."""
        self._items = list(items)
        if self.selected_index >= len(self._items):
            self.selected_index = -1

    @property
    def items(self) -> list[dict]:
        return self._items

    @property
    def selected_item(self) -> dict | None:
        if 0 <= self.selected_index < len(self._items):
            return self._items[self.selected_index]
        return None

    def _index_at(self, y: float) -> int:
        rel_y = y - self.y + self._scroll_offset
        stride = self.item_height + self.item_spacing
        if stride <= 0:
            return -1
        idx = int(rel_y / stride)
        if 0 <= idx < len(self._items):
            if rel_y - idx * stride <= self.item_height:
                return idx
        return -1

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h),
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 400
        n = len(self._items)
        h = n * self.item_height + max(0, n - 1) * self.item_spacing if n else self.item_height
        if self.preferred_height:
            h = self.preferred_height.to_pixels(viewport_h)
        return (w, h)

    def render(self, renderer: 'UIRenderer'):
        if not self._items:
            renderer.draw_text(
                self.x + self.item_padding,
                self.y + self.font_size + 4,
                self.empty_text,
                self.empty_color,
                self.font_size,
            )
            return

        renderer.begin_clip(self.x, self.y, self.width, self.height)

        stride = self.item_height + self.item_spacing
        for i, item in enumerate(self._items):
            iy = self.y + i * stride - self._scroll_offset

            # Skip rows outside visible area
            if iy + self.item_height < self.y or iy > self.y + self.height:
                continue

            # Background
            if i == self.selected_index:
                bg = self.selected_background
            elif i == self._hovered_index:
                bg = self.hover_background
            else:
                bg = self.item_background

            renderer.draw_rect(
                self.x, iy, self.width, self.item_height, bg, self.border_radius
            )

            # Text colors
            tc = self.selected_text_color if i == self.selected_index else self.text_color

            text = item.get("text", "")
            subtitle = item.get("subtitle", "")

            if subtitle:
                renderer.draw_text(
                    self.x + self.item_padding,
                    iy + self.font_size + 4,
                    text, tc, self.font_size,
                )
                renderer.draw_text(
                    self.x + self.item_padding,
                    iy + self.font_size + self.subtitle_font_size + 8,
                    subtitle, self.subtitle_color, self.subtitle_font_size,
                )
            else:
                renderer.draw_text(
                    self.x + self.item_padding,
                    iy + self.item_height / 2 + self.font_size / 3,
                    text, tc, self.font_size,
                )

        renderer.end_clip()

    # --- Mouse events ---

    def on_mouse_wheel(self, event: MouseWheelEvent) -> bool:
        """Scroll list with mouse wheel."""
        n = len(self._items)
        if n == 0:
            return False
        stride = self.item_height + self.item_spacing
        total_content = n * stride
        max_scroll = max(0.0, total_content - self.height)
        if max_scroll <= 0:
            return False
        self._scroll_offset -= event.dy * 30
        self._scroll_offset = max(0.0, min(self._scroll_offset, max_scroll))
        return True

    def on_mouse_move(self, event: MouseEvent):
        self._hovered_index = self._index_at(event.y)

    def on_mouse_leave(self):
        self._hovered_index = -1

    def on_mouse_down(self, event: MouseEvent) -> bool:
        idx = self._index_at(event.y)
        if idx < 0:
            return False

        now = time.monotonic()

        # Double-click detection
        if (idx == self._last_click_index
                and now - self._last_click_time < self._DOUBLE_CLICK_INTERVAL):
            if self.on_activate:
                self.on_activate(idx, self._items[idx])
            self._last_click_index = -1
            self._last_click_time = 0.0
            return True

        # Single click — select
        self._last_click_index = idx
        self._last_click_time = now
        self.selected_index = idx
        if self.on_select:
            self.on_select(idx, self._items[idx])
        return True


class ProgressBar(Widget):
    """Progress bar widget displaying a value between 0.0 and 1.0."""

    def __init__(self):
        super().__init__()
        self.value: float = 0.0
        self.background_color: tuple[float, float, float, float] = _t.bg_surface
        self.fill_color: tuple[float, float, float, float] = _t.accent
        self.border_radius: float = _t.border_radius
        self.show_text: bool = False
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.font_size: float = _t.font_size_small + 1

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h),
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 200
        h = self.preferred_height.to_pixels(viewport_h) if self.preferred_height else 20
        return (w, h)

    def render(self, renderer: 'UIRenderer'):
        # Background
        renderer.draw_rect(
            self.x, self.y, self.width, self.height,
            self.background_color, self.border_radius
        )

        # Fill
        clamped = max(0.0, min(1.0, self.value))
        fill_w = self.width * clamped
        if fill_w > 0:
            renderer.draw_rect(
                self.x, self.y, fill_w, self.height,
                self.fill_color, self.border_radius
            )

        # Optional percentage text
        if self.show_text:
            text = f"{int(clamped * 100)}%"
            renderer.draw_text_centered(
                self.x + self.width / 2,
                self.y + self.height / 2,
                text, self.text_color, self.font_size
            )


class Slider(Widget):
    """Slider widget for selecting a numeric value from a range."""

    def __init__(self):
        super().__init__()
        self.value: float = 0.0
        self.min_value: float = 0.0
        self.max_value: float = 1.0
        self.step: float = 0.0  # 0 = continuous

        self.track_color: tuple[float, float, float, float] = _t.bg_surface
        self.fill_color: tuple[float, float, float, float] = _t.accent
        self.thumb_color: tuple[float, float, float, float] = _t.text_secondary
        self.thumb_hover_color: tuple[float, float, float, float] = _t.text_primary
        self.track_height: float = 4.0
        self.thumb_radius: float = 8.0
        self.border_radius: float = 2.0

        # State
        self._dragging: bool = False
        self.hovered: bool = False

        # Callback
        self.on_change: Callable[[float], None] | None = None

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h),
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 200
        h = self.preferred_height.to_pixels(viewport_h) if self.preferred_height else self.thumb_radius * 2
        return (w, h)

    def _value_to_x(self) -> float:
        """Convert current value to x position of thumb center."""
        rng = self.max_value - self.min_value
        if rng <= 0:
            return self.x + self.thumb_radius
        ratio = (self.value - self.min_value) / rng
        track_start = self.x + self.thumb_radius
        track_end = self.x + self.width - self.thumb_radius
        return track_start + ratio * (track_end - track_start)

    def _x_to_value(self, x: float) -> float:
        """Convert x position to value."""
        track_start = self.x + self.thumb_radius
        track_end = self.x + self.width - self.thumb_radius
        track_len = track_end - track_start
        if track_len <= 0:
            return self.min_value
        ratio = (x - track_start) / track_len
        ratio = max(0.0, min(1.0, ratio))
        val = self.min_value + ratio * (self.max_value - self.min_value)
        if self.step > 0:
            val = round((val - self.min_value) / self.step) * self.step + self.min_value
        return max(self.min_value, min(self.max_value, val))

    def render(self, renderer: 'UIRenderer'):
        cy = self.y + self.height / 2
        track_y = cy - self.track_height / 2

        # Track background
        renderer.draw_rect(
            self.x + self.thumb_radius, track_y,
            self.width - self.thumb_radius * 2, self.track_height,
            self.track_color, self.border_radius
        )

        # Fill up to thumb
        thumb_x = self._value_to_x()
        fill_w = thumb_x - (self.x + self.thumb_radius)
        if fill_w > 0:
            renderer.draw_rect(
                self.x + self.thumb_radius, track_y,
                fill_w, self.track_height,
                self.fill_color, self.border_radius
            )

        # Thumb
        tc = self.thumb_hover_color if (self.hovered or self._dragging) else self.thumb_color
        renderer.draw_rect(
            thumb_x - self.thumb_radius, cy - self.thumb_radius,
            self.thumb_radius * 2, self.thumb_radius * 2,
            tc, self.thumb_radius
        )

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        self._dragging = True
        self._set_value_from_x(event.x)
        return True

    def on_mouse_move(self, event: MouseEvent):
        if self._dragging:
            self._set_value_from_x(event.x)

    def on_mouse_up(self, event: MouseEvent):
        self._dragging = False

    def _set_value_from_x(self, x: float):
        new_val = self._x_to_value(x)
        if new_val != self.value:
            self.value = new_val
            if self.on_change:
                self.on_change(self.value)


class ComboBox(Widget):
    """Dropdown select widget. Click to open a list of options as overlay."""

    def __init__(self):
        super().__init__()
        self.items: list[str] = []
        self.selected_index: int = -1
        self.placeholder: str = "Select..."

        # Style
        self.background_color: tuple[float, float, float, float] = _t.bg_input
        self.border_color: tuple[float, float, float, float] = _t.border
        self.focused_border_color: tuple[float, float, float, float] = _t.border_focus
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.placeholder_color: tuple[float, float, float, float] = _t.text_muted
        self.arrow_color: tuple[float, float, float, float] = _t.text_secondary
        self.font_size: float = _t.font_size
        self.border_radius: float = _t.border_radius
        self.border_width: float = 1.0
        self.padding: float = 8.0

        # Dropdown style
        self.dropdown_background: tuple[float, float, float, float] = (0.18, 0.18, 0.22, 0.98)
        self.dropdown_item_hover: tuple[float, float, float, float] = _t.hover_subtle
        self.dropdown_max_visible: int = 8
        self.dropdown_item_height: float = 28.0

        # State
        self.hovered: bool = False
        self._open: bool = False
        self._dropdown: Widget | None = None

        # Callback
        self.on_change: Callable[[int, str], None] | None = None

    @property
    def selected_text(self) -> str:
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return ""

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h),
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 200
        h = self.font_size + self.padding * 2 + self.border_width * 2
        return (w, h)

    def render(self, renderer: 'UIRenderer'):
        bw = self.border_width

        # Border
        bc = self.focused_border_color if self._open else self.border_color
        renderer.draw_rect(self.x, self.y, self.width, self.height,
                           bc, self.border_radius)

        # Background
        renderer.draw_rect(self.x + bw, self.y + bw,
                           self.width - bw * 2, self.height - bw * 2,
                           self.background_color, max(0, self.border_radius - bw))

        # Text
        text = self.selected_text or self.placeholder
        tc = self.text_color if self.selected_text else self.placeholder_color
        renderer.draw_text(
            self.x + self.padding + bw,
            self.y + bw + self.padding + self.font_size * 0.85,
            text, tc, self.font_size
        )

        # Arrow indicator
        arrow_x = self.x + self.width - self.padding - bw - 8
        arrow_y = self.y + self.height / 2
        arrow = "\u25BC" if not self._open else "\u25B2"
        renderer.draw_text_centered(arrow_x, arrow_y, arrow,
                                    self.arrow_color, self.font_size * 0.7)

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        if event.button != MouseButton.LEFT:
            return False
        if self._open:
            self._close_dropdown()
        else:
            self._open_dropdown()
        return True

    def _open_dropdown(self):
        if not self.items or self._ui is None:
            return

        from tcgui.widgets.containers import Panel

        self._open = True
        n_visible = min(len(self.items), self.dropdown_max_visible)
        dd_height = n_visible * self.dropdown_item_height

        # Build dropdown as a Panel containing a custom _DropdownList
        dropdown = _DropdownList(self)
        dropdown.x = self.x
        dropdown.y = self.y + self.height
        dropdown.width = self.width
        dropdown.height = dd_height

        vw, vh = self._ui._viewport_w, self._ui._viewport_h

        # Flip upward if dropdown would go off-screen
        if dropdown.y + dd_height > vh:
            dropdown.y = self.y - dd_height

        dropdown.layout(dropdown.x, dropdown.y, dropdown.width, dropdown.height, vw, vh)
        self._dropdown = dropdown
        self._ui.show_overlay(dropdown, dismiss_on_outside=True,
                              on_dismiss=self._on_dropdown_closed)

    def _close_dropdown(self):
        if self._dropdown is not None and self._ui is not None:
            self._ui.hide_overlay(self._dropdown)
            # on_dismiss callback handles state reset

    def _on_dropdown_closed(self):
        self._open = False
        self._dropdown = None

    def _select_item(self, index: int):
        if 0 <= index < len(self.items):
            old = self.selected_index
            self.selected_index = index
            if old != index and self.on_change:
                self.on_change(index, self.items[index])
        self._close_dropdown()


class SpinBox(Widget):
    """Numeric input with increment/decrement buttons."""

    def __init__(self):
        super().__init__()
        self.focusable: bool = True

        # Numeric parameters
        self.value: float = 0.0
        self.min_value: float = -1e9
        self.max_value: float = 1e9
        self.step: float = 1.0
        self.decimals: int = 2

        # Visual configuration
        self.font_size: float = _t.font_size
        self.padding: float = 6
        self.border_width: float = 1
        self.border_radius: float = _t.border_radius
        self.button_width: float = 20

        # Colors
        self.background_color: tuple[float, float, float, float] = _t.bg_input
        self.focused_background_color: tuple[float, float, float, float] = _t.bg_input_focus
        self.border_color: tuple[float, float, float, float] = _t.border
        self.focused_border_color: tuple[float, float, float, float] = _t.border_focus
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.cursor_color: tuple[float, float, float, float] = _t.text_primary
        self.button_color: tuple[float, float, float, float] = _t.bg_surface
        self.button_hover_color: tuple[float, float, float, float] = _t.hover
        self.arrow_color: tuple[float, float, float, float] = _t.text_secondary

        # State
        self.focused: bool = False
        self.hovered: bool = False
        self._editing: bool = False
        self._edit_text: str = ""
        self._cursor_pos: int = 0
        self._hovered_button: str = ""  # "" / "up" / "down"
        self._cursor_blink_time: float = 0.0
        self._cursor_visible: bool = True
        self._renderer: 'UIRenderer | None' = None

        # Callback
        self.on_change: Callable[[float], None] | None = None

    def _format_value(self) -> str:
        if self.decimals <= 0:
            return str(int(self.value))
        return f"{self.value:.{self.decimals}f}"

    def _clamp(self, val: float) -> float:
        return max(self.min_value, min(self.max_value, val))

    def _set_value(self, val: float):
        val = self._clamp(val)
        if val != self.value:
            self.value = val
            if self.on_change:
                self.on_change(self.value)

    def _increment(self):
        self._set_value(self.value + self.step)

    def _decrement(self):
        self._set_value(self.value - self.step)

    def _begin_edit(self):
        self._editing = True
        self._edit_text = self._format_value()
        self._cursor_pos = len(self._edit_text)
        self._reset_cursor_blink()

    def _commit_edit(self):
        if not self._editing:
            return
        self._editing = False
        try:
            val = float(self._edit_text)
        except ValueError:
            return
        self._set_value(val)

    def _cancel_edit(self):
        self._editing = False

    # Cursor blink (same pattern as TextInput)
    def _update_cursor_blink(self):
        now = time.monotonic()
        if now - self._cursor_blink_time >= 0.5:
            self._cursor_visible = not self._cursor_visible
            self._cursor_blink_time = now

    def _reset_cursor_blink(self):
        self._cursor_visible = True
        self._cursor_blink_time = time.monotonic()

    def _measure_text_width(self, renderer, text: str) -> float:
        w, _ = renderer.measure_text(text, self.font_size)
        return w

    # --- Geometry helpers ---

    def _button_rect(self) -> tuple[float, float, float, float]:
        """Return (x, y, w, h) of the button area."""
        bw = self.border_width
        bx = self.x + self.width - self.button_width - bw
        by = self.y + bw
        bh = self.height - bw * 2
        return bx, by, self.button_width, bh

    def _up_button_rect(self) -> tuple[float, float, float, float]:
        bx, by, bw, bh = self._button_rect()
        return bx, by, bw, bh / 2

    def _down_button_rect(self) -> tuple[float, float, float, float]:
        bx, by, bw, bh = self._button_rect()
        return bx, by + bh / 2, bw, bh / 2

    # --- Size ---

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 120
        h = self.font_size + self.padding * 2 + self.border_width * 2
        return (w, h)

    # --- Render ---

    def render(self, renderer: 'UIRenderer'):
        self._renderer = renderer
        bw = self.border_width

        # Border
        border_col = self.focused_border_color if self.focused else self.border_color
        renderer.draw_rect(self.x, self.y, self.width, self.height, border_col, self.border_radius)

        # Background
        bg_color = self.focused_background_color if self.focused else self.background_color
        renderer.draw_rect(
            self.x + bw, self.y + bw,
            self.width - bw * 2, self.height - bw * 2,
            bg_color, max(0, self.border_radius - bw)
        )

        # Button area
        bx, by, btn_w, bh = self._button_rect()

        # Up button
        ux, uy, uw, uh = self._up_button_rect()
        up_col = self.button_hover_color if self._hovered_button == "up" else self.button_color
        renderer.draw_rect(ux, uy, uw, uh, up_col, 0)
        renderer.draw_text_centered(ux + uw / 2, uy + uh / 2, "\u25B2", self.arrow_color, self.font_size * 0.5)

        # Down button
        dx, dy, dw, dh = self._down_button_rect()
        down_col = self.button_hover_color if self._hovered_button == "down" else self.button_color
        renderer.draw_rect(dx, dy, dw, dh, down_col, 0)
        renderer.draw_text_centered(dx + dw / 2, dy + dh / 2, "\u25BC", self.arrow_color, self.font_size * 0.5)

        # Text area
        text_x = self.x + self.padding + bw
        text_area_width = self.width - (self.padding + bw) * 2 - self.button_width
        text_area_height = self.height - bw * 2
        baseline_y = self.y + bw + self.padding + self.font_size

        renderer.begin_clip(text_x, self.y + bw, text_area_width, text_area_height)

        display_text = self._edit_text if self._editing else self._format_value()
        renderer.draw_text(text_x, baseline_y, display_text, self.text_color, self.font_size)

        # Cursor
        if self.focused and self._editing:
            self._update_cursor_blink()
            if self._cursor_visible:
                cursor_px = self._measure_text_width(renderer, self._edit_text[:self._cursor_pos])
                cursor_screen_x = text_x + cursor_px
                cursor_y = self.y + bw + self.padding
                renderer.draw_rect(cursor_screen_x, cursor_y, 1.5, self.font_size, self.cursor_color)

        renderer.end_clip()

    # --- Mouse events ---

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False
        self._hovered_button = ""

    def on_mouse_move(self, event: MouseEvent):
        ux, uy, uw, uh = self._up_button_rect()
        dx, dy, dw, dh = self._down_button_rect()
        if ux <= event.x < ux + uw and uy <= event.y < uy + uh:
            self._hovered_button = "up"
        elif dx <= event.x < dx + dw and dy <= event.y < dy + dh:
            self._hovered_button = "down"
        else:
            self._hovered_button = ""

    def on_mouse_down(self, event: MouseEvent) -> bool:
        # Check buttons
        ux, uy, uw, uh = self._up_button_rect()
        if ux <= event.x < ux + uw and uy <= event.y < uy + uh:
            self._increment()
            if self._editing:
                self._edit_text = self._format_value()
                self._cursor_pos = len(self._edit_text)
            return True

        dx, dy, dw, dh = self._down_button_rect()
        if dx <= event.x < dx + dw and dy <= event.y < dy + dh:
            self._decrement()
            if self._editing:
                self._edit_text = self._format_value()
                self._cursor_pos = len(self._edit_text)
            return True

        # Click on text area — begin editing
        if not self._editing:
            self._begin_edit()
        # Position cursor
        if self._renderer is not None:
            text_start_x = self.x + self.padding + self.border_width
            relative_x = event.x - text_start_x
            x_acc = 0.0
            for i, ch in enumerate(self._edit_text):
                char_w = self._measure_text_width(self._renderer, ch)
                if relative_x < x_acc + char_w / 2:
                    self._cursor_pos = i
                    break
                x_acc += char_w
            else:
                self._cursor_pos = len(self._edit_text)
        self._reset_cursor_blink()
        return True

    # --- Focus events ---

    def on_focus(self):
        self.focused = True
        self._reset_cursor_blink()

    def on_blur(self):
        self.focused = False
        self._commit_edit()

    # --- Keyboard events ---

    def on_key_down(self, event: KeyEvent) -> bool:
        from tcbase import Key

        key = event.key
        if key == Key.UP:
            self._increment()
            if self._editing:
                self._edit_text = self._format_value()
                self._cursor_pos = len(self._edit_text)
            self._reset_cursor_blink()
            return True

        if key == Key.DOWN:
            self._decrement()
            if self._editing:
                self._edit_text = self._format_value()
                self._cursor_pos = len(self._edit_text)
            self._reset_cursor_blink()
            return True

        if not self._editing:
            return False

        if key == Key.LEFT:
            if self._cursor_pos > 0:
                self._cursor_pos -= 1
            self._reset_cursor_blink()
            return True

        if key == Key.RIGHT:
            if self._cursor_pos < len(self._edit_text):
                self._cursor_pos += 1
            self._reset_cursor_blink()
            return True

        if key == Key.HOME:
            self._cursor_pos = 0
            self._reset_cursor_blink()
            return True

        if key == Key.END:
            self._cursor_pos = len(self._edit_text)
            self._reset_cursor_blink()
            return True

        if key == Key.BACKSPACE:
            if self._cursor_pos > 0:
                self._edit_text = self._edit_text[:self._cursor_pos - 1] + self._edit_text[self._cursor_pos:]
                self._cursor_pos -= 1
            self._reset_cursor_blink()
            return True

        if key == Key.DELETE:
            if self._cursor_pos < len(self._edit_text):
                self._edit_text = self._edit_text[:self._cursor_pos] + self._edit_text[self._cursor_pos + 1:]
            self._reset_cursor_blink()
            return True

        if key == Key.ENTER:
            self._commit_edit()
            return True

        if key == Key.ESCAPE:
            self._cancel_edit()
            return True

        return False

    def on_text_input(self, event: TextEvent) -> bool:
        if not self._editing:
            self._begin_edit()
        # Filter: only digits, dot, minus
        filtered = "".join(ch for ch in event.text if ch in "0123456789.-")
        if not filtered:
            return True
        self._edit_text = self._edit_text[:self._cursor_pos] + filtered + self._edit_text[self._cursor_pos:]
        self._cursor_pos += len(filtered)
        self._reset_cursor_blink()
        return True


class SliderEdit(Widget):
    """Composite widget: Slider + SpinBox side by side."""

    def __init__(self):
        super().__init__()

        # Numeric parameters
        self.value: float = 0.0
        self.min_value: float = 0.0
        self.max_value: float = 1.0
        self.step: float = 0.0
        self.decimals: int = 2

        # Layout
        self.spacing: float = 4
        self.spinbox_width: float = 80

        # Internal widgets
        self._slider = Slider()
        self._spinbox = SpinBox()
        self.add_child(self._slider)
        self.add_child(self._spinbox)

        self._updating: bool = False

        # Callback
        self.on_change: Callable[[float], None] | None = None

        # Sync parameters to children
        self._sync_params()
        self._slider.on_change = self._on_slider_change
        self._spinbox.on_change = self._on_spinbox_change

    def _sync_params(self):
        """Push numeric params to child widgets."""
        self._slider.min_value = self.min_value
        self._slider.max_value = self.max_value
        self._slider.step = self.step
        self._slider.value = self.value
        self._spinbox.min_value = self.min_value
        self._spinbox.max_value = self.max_value
        self._spinbox.step = self.step if self.step > 0 else 0.01
        self._spinbox.value = self.value
        self._spinbox.decimals = self.decimals

    def _on_slider_change(self, val: float):
        if self._updating:
            return
        self._updating = True
        self._spinbox.value = val
        if self._spinbox._editing:
            self._spinbox._edit_text = self._spinbox._format_value()
            self._spinbox._cursor_pos = len(self._spinbox._edit_text)
        self.value = val
        if self.on_change:
            self.on_change(val)
        self._updating = False

    def _on_spinbox_change(self, val: float):
        if self._updating:
            return
        self._updating = True
        self._slider.value = val
        self.value = val
        if self.on_change:
            self.on_change(val)
        self._updating = False

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 300
        h = self._slider.compute_size(viewport_w, viewport_h)[1]
        return (w, h)

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        super().layout(x, y, width, height, viewport_w, viewport_h)
        self._sync_params()
        slider_w = width - self.spinbox_width - self.spacing
        self._slider.layout(x, y, slider_w, height, viewport_w, viewport_h)
        self._spinbox.layout(x + slider_w + self.spacing, y, self.spinbox_width, height, viewport_w, viewport_h)


class TextArea(Widget):
    """Multi-line text editor with scrollbar."""

    def __init__(self):
        super().__init__()
        self.focusable: bool = True

        # Content
        self._lines: list[str] = [""]
        self.placeholder: str = ""
        self.cursor_line: int = 0
        self.cursor_col: int = 0
        self.max_lines: int = 0  # 0 = unlimited
        self.read_only: bool = False

        # Visual configuration
        self.font_size: float = _t.font_size
        self.padding: float = 6
        self.border_width: float = 1
        self.border_radius: float = _t.border_radius
        self.line_height: float = 0  # 0 = auto

        # Colors
        self.background_color: tuple[float, float, float, float] = _t.bg_input
        self.focused_background_color: tuple[float, float, float, float] = _t.bg_input_focus
        self.border_color: tuple[float, float, float, float] = _t.border
        self.focused_border_color: tuple[float, float, float, float] = _t.border_focus
        self.text_color: tuple[float, float, float, float] = _t.text_primary
        self.placeholder_color: tuple[float, float, float, float] = _t.text_muted
        self.cursor_color: tuple[float, float, float, float] = _t.text_primary

        # Scrollbar
        self.show_scrollbar: bool = True
        self.scrollbar_width: float = 8.0
        self.scrollbar_color: tuple[float, float, float, float] = _t.scrollbar
        self.scrollbar_hover_color: tuple[float, float, float, float] = _t.scrollbar_hover

        # State
        self.focused: bool = False
        self.hovered: bool = False
        self._scroll_y: float = 0.0
        self._scroll_x: float = 0.0
        self._cursor_blink_time: float = 0.0
        self._cursor_visible: bool = True
        self._dragging_scrollbar: bool = False
        self._scrollbar_hovered: bool = False
        self._drag_start_y: float = 0.0
        self._drag_start_scroll: float = 0.0
        self._renderer: 'UIRenderer | None' = None

        # Callback
        self.on_change: Callable[[str], None] | None = None

    # --- Text property ---

    @property
    def text(self) -> str:
        return "\n".join(self._lines)

    @text.setter
    def text(self, value: str):
        self._lines = value.split("\n") if value else [""]
        self.cursor_line = min(self.cursor_line, len(self._lines) - 1)
        self.cursor_col = min(self.cursor_col, len(self._lines[self.cursor_line]))

    # --- Helpers ---

    def _effective_line_height(self) -> float:
        return self.line_height if self.line_height > 0 else self.font_size * 1.4

    def _content_height(self) -> float:
        return len(self._lines) * self._effective_line_height()

    def _visible_height(self) -> float:
        bw = self.border_width
        return self.height - self.padding * 2 - bw * 2

    def _max_scroll_y(self) -> float:
        return max(0.0, self._content_height() - self._visible_height())

    def _ensure_cursor_visible(self):
        lh = self._effective_line_height()
        cursor_top = self.cursor_line * lh
        cursor_bottom = cursor_top + lh
        visible_h = self._visible_height()
        if cursor_top < self._scroll_y:
            self._scroll_y = cursor_top
        if cursor_bottom > self._scroll_y + visible_h:
            self._scroll_y = cursor_bottom - visible_h
        self._scroll_y = max(0.0, min(self._scroll_y, self._max_scroll_y()))

    def _measure_text_width(self, renderer, text: str) -> float:
        w, _ = renderer.measure_text(text, self.font_size)
        return w

    def _cursor_pos_from_xy(self, renderer, x: float, y: float) -> tuple[int, int]:
        bw = self.border_width
        content_x = self.x + self.padding + bw
        content_y = self.y + self.padding + bw
        lh = self._effective_line_height()

        rel_y = y - content_y + self._scroll_y
        line = int(rel_y / lh)
        line = max(0, min(line, len(self._lines) - 1))

        rel_x = x - content_x + self._scroll_x
        line_text = self._lines[line]
        x_acc = 0.0
        col = len(line_text)
        for i, ch in enumerate(line_text):
            char_w = self._measure_text_width(renderer, ch)
            if rel_x < x_acc + char_w / 2:
                col = i
                break
            x_acc += char_w

        return line, col

    # --- Cursor blink ---

    def _update_cursor_blink(self):
        now = time.monotonic()
        if now - self._cursor_blink_time >= 0.5:
            self._cursor_visible = not self._cursor_visible
            self._cursor_blink_time = now

    def _reset_cursor_blink(self):
        self._cursor_visible = True
        self._cursor_blink_time = time.monotonic()

    # --- Size ---

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 300
        h = self.preferred_height.to_pixels(viewport_h) if self.preferred_height else 150
        return (w, h)

    # --- Render ---

    def render(self, renderer: 'UIRenderer'):
        self._renderer = renderer
        bw = self.border_width
        lh = self._effective_line_height()

        # Border
        border_col = self.focused_border_color if self.focused else self.border_color
        renderer.draw_rect(self.x, self.y, self.width, self.height, border_col, self.border_radius)

        # Background
        bg_color = self.focused_background_color if self.focused else self.background_color
        renderer.draw_rect(
            self.x + bw, self.y + bw,
            self.width - bw * 2, self.height - bw * 2,
            bg_color, max(0, self.border_radius - bw)
        )

        content_x = self.x + self.padding + bw
        content_y = self.y + self.padding + bw
        content_w = self.width - (self.padding + bw) * 2
        content_h = self._visible_height()

        # Reduce content width for scrollbar
        has_scrollbar = self.show_scrollbar and self._content_height() > content_h
        if has_scrollbar:
            content_w -= self.scrollbar_width

        renderer.begin_clip(content_x, content_y, content_w, content_h)

        if not self._lines or (len(self._lines) == 1 and not self._lines[0]):
            # Placeholder
            if not self.focused and self.placeholder:
                renderer.draw_text(
                    content_x, content_y + self.font_size,
                    self.placeholder, self.placeholder_color, self.font_size
                )
        else:
            # Draw visible lines
            first_line = max(0, int(self._scroll_y / lh))
            last_line = min(len(self._lines), int((self._scroll_y + content_h) / lh) + 1)
            for i in range(first_line, last_line):
                line_y = content_y + i * lh - self._scroll_y + self.font_size
                renderer.draw_text(
                    content_x - self._scroll_x, line_y,
                    self._lines[i], self.text_color, self.font_size
                )

        # Cursor
        if self.focused:
            self._update_cursor_blink()
            if self._cursor_visible:
                cursor_x_px = self._measure_text_width(renderer, self._lines[self.cursor_line][:self.cursor_col])
                cx = content_x + cursor_x_px - self._scroll_x
                cy = content_y + self.cursor_line * lh - self._scroll_y
                renderer.draw_rect(cx, cy, 1.5, lh, self.cursor_color)

        renderer.end_clip()

        # Scrollbar
        if has_scrollbar:
            max_sy = self._max_scroll_y()
            viewport_ratio = content_h / self._content_height()
            thumb_h = max(20.0, content_h * viewport_ratio)
            track_h = content_h - thumb_h
            thumb_y = content_y + (track_h * (self._scroll_y / max_sy) if max_sy > 0 else 0)
            sb_x = self.x + self.width - self.scrollbar_width - bw

            color = self.scrollbar_hover_color if (self._scrollbar_hovered or self._dragging_scrollbar) else self.scrollbar_color
            renderer.draw_rect(sb_x, thumb_y, self.scrollbar_width, thumb_h, color, self.scrollbar_width / 2)

    # --- Mouse events ---

    def on_mouse_enter(self):
        self.hovered = True

    def on_mouse_leave(self):
        self.hovered = False
        self._scrollbar_hovered = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        bw = self.border_width
        # Check scrollbar
        if self.show_scrollbar and self._content_height() > self._visible_height():
            sb_x = self.x + self.width - self.scrollbar_width - bw
            if event.x >= sb_x:
                self._dragging_scrollbar = True
                self._drag_start_y = event.y
                self._drag_start_scroll = self._scroll_y
                return True

        # Position cursor
        if self._renderer is not None:
            self.cursor_line, self.cursor_col = self._cursor_pos_from_xy(self._renderer, event.x, event.y)
        self._reset_cursor_blink()
        return True

    def on_mouse_move(self, event: MouseEvent):
        if self._dragging_scrollbar:
            delta_y = event.y - self._drag_start_y
            content_h = self._visible_height()
            viewport_ratio = content_h / self._content_height()
            thumb_h = max(20.0, content_h * viewport_ratio)
            track_h = content_h - thumb_h
            max_sy = self._max_scroll_y()
            if track_h > 0:
                self._scroll_y = self._drag_start_scroll + delta_y * (max_sy / track_h)
                self._scroll_y = max(0.0, min(self._scroll_y, max_sy))
        else:
            # Track scrollbar hover
            bw = self.border_width
            if self.show_scrollbar and self._content_height() > self._visible_height():
                sb_x = self.x + self.width - self.scrollbar_width - bw
                self._scrollbar_hovered = event.x >= sb_x
            else:
                self._scrollbar_hovered = False

    def on_mouse_up(self, event: MouseEvent):
        self._dragging_scrollbar = False

    def on_mouse_wheel(self, event: MouseWheelEvent) -> bool:
        max_sy = self._max_scroll_y()
        if max_sy <= 0:
            return False
        self._scroll_y -= event.dy * 30
        self._scroll_y = max(0.0, min(self._scroll_y, max_sy))
        return True

    # --- Focus events ---

    def on_focus(self):
        self.focused = True
        self._reset_cursor_blink()

    def on_blur(self):
        self.focused = False

    # --- Keyboard events ---

    def on_key_down(self, event: KeyEvent) -> bool:
        if self.read_only:
            return False
        from tcbase import Key

        key = event.key
        if key == Key.LEFT:
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_col = len(self._lines[self.cursor_line])
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.RIGHT:
            if self.cursor_col < len(self._lines[self.cursor_line]):
                self.cursor_col += 1
            elif self.cursor_line < len(self._lines) - 1:
                self.cursor_line += 1
                self.cursor_col = 0
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.UP:
            if self.cursor_line > 0:
                self.cursor_line -= 1
                self.cursor_col = min(self.cursor_col, len(self._lines[self.cursor_line]))
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.DOWN:
            if self.cursor_line < len(self._lines) - 1:
                self.cursor_line += 1
                self.cursor_col = min(self.cursor_col, len(self._lines[self.cursor_line]))
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.HOME:
            self.cursor_col = 0
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.END:
            self.cursor_col = len(self._lines[self.cursor_line])
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.ENTER:
            if self.max_lines > 0 and len(self._lines) >= self.max_lines:
                return True
            line = self._lines[self.cursor_line]
            self._lines[self.cursor_line] = line[:self.cursor_col]
            self._lines.insert(self.cursor_line + 1, line[self.cursor_col:])
            self.cursor_line += 1
            self.cursor_col = 0
            self._fire_on_change()
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.BACKSPACE:
            if self.cursor_col > 0:
                line = self._lines[self.cursor_line]
                self._lines[self.cursor_line] = line[:self.cursor_col - 1] + line[self.cursor_col:]
                self.cursor_col -= 1
                self._fire_on_change()
            elif self.cursor_line > 0:
                # Merge with previous line
                prev_len = len(self._lines[self.cursor_line - 1])
                self._lines[self.cursor_line - 1] += self._lines[self.cursor_line]
                del self._lines[self.cursor_line]
                self.cursor_line -= 1
                self.cursor_col = prev_len
                self._fire_on_change()
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        if key == Key.DELETE:
            line = self._lines[self.cursor_line]
            if self.cursor_col < len(line):
                self._lines[self.cursor_line] = line[:self.cursor_col] + line[self.cursor_col + 1:]
                self._fire_on_change()
            elif self.cursor_line < len(self._lines) - 1:
                # Merge with next line
                self._lines[self.cursor_line] += self._lines[self.cursor_line + 1]
                del self._lines[self.cursor_line + 1]
                self._fire_on_change()
            self._reset_cursor_blink()
            self._ensure_cursor_visible()
            return True

        return False

    def on_text_input(self, event: TextEvent) -> bool:
        if self.read_only:
            return False
        line = self._lines[self.cursor_line]
        self._lines[self.cursor_line] = line[:self.cursor_col] + event.text + line[self.cursor_col:]
        self.cursor_col += len(event.text)
        self._fire_on_change()
        self._reset_cursor_blink()
        self._ensure_cursor_visible()
        return True

    def _fire_on_change(self):
        if self.on_change is not None:
            self.on_change(self.text)


class _DropdownList(Widget):
    """Internal dropdown list widget for ComboBox overlay."""

    def __init__(self, combo: ComboBox):
        super().__init__()
        self._combo = combo
        self._hovered_index: int = -1
        self._scroll_offset: float = 0.0

    def render(self, renderer: 'UIRenderer'):
        c = self._combo
        # Background
        renderer.draw_rect(self.x, self.y, self.width, self.height,
                           c.dropdown_background, c.border_radius)

        renderer.begin_clip(self.x, self.y, self.width, self.height)

        item_h = c.dropdown_item_height
        for i, text in enumerate(c.items):
            iy = self.y + i * item_h - self._scroll_offset
            if iy + item_h < self.y or iy > self.y + self.height:
                continue

            # Hover/selected highlight
            if i == self._hovered_index:
                renderer.draw_rect(self.x, iy, self.width, item_h,
                                   c.dropdown_item_hover, 0)
            elif i == c.selected_index:
                renderer.draw_rect(self.x, iy, self.width, item_h,
                                   (c.dropdown_item_hover[0], c.dropdown_item_hover[1],
                                    c.dropdown_item_hover[2], 0.5), 0)

            renderer.draw_text(
                self.x + c.padding,
                iy + item_h / 2 + c.font_size * 0.35,
                text, c.text_color, c.font_size
            )

        renderer.end_clip()

    def _index_at(self, y: float) -> int:
        rel_y = y - self.y + self._scroll_offset
        idx = int(rel_y / self._combo.dropdown_item_height)
        if 0 <= idx < len(self._combo.items):
            return idx
        return -1

    def on_mouse_move(self, event: MouseEvent):
        self._hovered_index = self._index_at(event.y)

    def on_mouse_leave(self):
        self._hovered_index = -1

    def on_mouse_down(self, event: MouseEvent) -> bool:
        if event.button != MouseButton.LEFT:
            return False
        idx = self._index_at(event.y)
        if idx >= 0:
            self._combo._select_item(idx)
        return True

    def on_mouse_wheel(self, event: MouseWheelEvent) -> bool:
        c = self._combo
        total = len(c.items) * c.dropdown_item_height
        max_scroll = max(0.0, total - self.height)
        if max_scroll <= 0:
            return False
        self._scroll_offset -= event.dy * 30
        self._scroll_offset = max(0.0, min(self._scroll_offset, max_scroll))
        return True

    def hit_test(self, px: float, py: float):
        if not self.visible:
            return None
        if not self.contains(px, py):
            return None
        return self
