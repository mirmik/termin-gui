"""Draggable splitter between panels in HStack."""

from __future__ import annotations

from tcgui.widgets.widget import Widget
from tcgui.widgets.events import MouseEvent
from tcgui.widgets.units import px
from tcgui.widgets.theme import current_theme as _t


class Splitter(Widget):
    """Vertical splitter bar. Drag to resize the panel on the given side.

    Usage::

        splitter = Splitter(target=left_panel, side="left")
        hstack.add_child(left_panel)
        hstack.add_child(splitter)
        hstack.add_child(canvas)
    """

    def __init__(self, target: Widget, side: str = "left"):
        super().__init__()
        self._target = target
        self._side = side  # "left" or "right"
        self.preferred_width = px(5)
        self.cursor = "move"

        self.color: tuple[float, float, float, float] = _t.text_muted
        self.hover_color: tuple[float, float, float, float] = _t.accent
        self.bar_width: float = 1.0

        self._dragging = False
        self._drag_start_x: float = 0
        self._drag_start_width: float = 0
        self._hovered = False
        self._min_width: float = 100
        self._max_width: float = 600

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 5
        return (w, 0)

    def render(self, renderer):
        c = self.hover_color if (self._hovered or self._dragging) else self.color
        cx = self.x + self.width / 2 - self.bar_width / 2
        renderer.draw_rect(cx, self.y, self.bar_width, self.height, c)

    def hit_test(self, px: float, py: float) -> Widget | None:
        if not self.visible:
            return None
        if not self.contains(px, py):
            return None
        return self

    def on_mouse_move(self, event: MouseEvent):
        if self._dragging:
            dx = event.x - self._drag_start_x
            if self._side == "right":
                dx = -dx
            new_w = max(self._min_width, min(self._max_width, self._drag_start_width + dx))
            self._target.preferred_width = px(new_w)
            if self._ui:
                self._ui.request_layout()
        else:
            self._hovered = True

    def on_mouse_leave(self):
        self._hovered = False

    def on_mouse_down(self, event: MouseEvent) -> bool:
        self._dragging = True
        self._drag_start_x = event.x
        tw = self._target.preferred_width
        self._drag_start_width = tw.to_pixels(1000) if tw else self._target.width
        return True

    def on_mouse_up(self, event: MouseEvent):
        self._dragging = False
