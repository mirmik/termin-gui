"""Base dialog widget for modal dialogs."""

from __future__ import annotations

from typing import Callable

from tcbase import Key
from tcgui.widgets.widget import Widget
from tcgui.widgets.events import KeyEvent
from tcgui.widgets.theme import current_theme as _t


class Dialog(Widget):
    """Base modal dialog with title bar, content area, and button bar.

    Not placed in the normal widget tree — shown as a modal overlay
    via :meth:`show`.

    Usage::

        dlg = Dialog()
        dlg.title = "New Project"
        dlg.content = my_form_widget
        dlg.buttons = ["OK", "Cancel"]
        dlg.default_button = "OK"
        dlg.on_result = lambda btn: print(btn)
        dlg.show(ui)
    """

    def __init__(self):
        super().__init__()

        # Configuration
        self.title: str = ""
        self.content: Widget | None = None
        self.buttons: list[str] = ["OK"]
        self.default_button: str | None = None
        self.cancel_button: str | None = None
        self.on_result: Callable[[str], None] | None = None
        self.min_width: float = 300

        # Style
        self.background_color: tuple[float, float, float, float] = _t.bg_surface
        self.title_background_color: tuple[float, float, float, float] = (0.18, 0.18, 0.22, 1.0)
        self.title_text_color: tuple[float, float, float, float] = _t.text_primary
        self.title_font_size: float = _t.font_size + 2
        self.border_radius: float = _t.border_radius + 2
        self.padding: float = 16
        self.button_spacing: float = 8
        self.title_height: float = 36
        self.button_bar_height: float = 44

        # Internal
        self._button_widgets: list = []
        self._built: bool = False

    # ------------------------------------------------------------------
    # Build internal widgets
    # ------------------------------------------------------------------

    def _build(self):
        """Create button widgets from configuration."""
        from tcgui.widgets.button import Button

        for btn in self._button_widgets:
            self.remove_child(btn)
        self._button_widgets.clear()

        for btn_text in self.buttons:
            btn = Button()
            btn.text = btn_text
            btn.font_size = _t.font_size
            btn.padding = 8
            if btn_text == self.default_button:
                btn.background_color = _t.accent
            btn.on_click = (lambda t: lambda: self._on_button_click(t))(btn_text)
            self._button_widgets.append(btn)

        self._built = True

    def _on_button_click(self, button_name: str):
        if self.on_result:
            self.on_result(button_name)
        self.close()

    # ------------------------------------------------------------------
    # Show / close
    # ------------------------------------------------------------------

    def show(self, ui) -> None:
        """Show this dialog as a centered modal overlay."""
        self._ui = ui
        if not self._built:
            self._build()
        self._ensure_children()

        vw = ui._viewport_w
        vh = ui._viewport_h
        w, h = self.compute_size(vw, vh)

        x = (vw - w) / 2
        y = (vh - h) / 2
        self.layout(x, y, w, h, vw, vh)

        ui.show_overlay(self, modal=True, dismiss_on_outside=False,
                        on_dismiss=self._on_overlay_dismissed)

    def close(self) -> None:
        """Remove this dialog from the overlay stack."""
        if self._ui is not None:
            self._ui.hide_overlay(self)

    def _on_overlay_dismissed(self):
        """Called when ESC closes this overlay."""
        if self.cancel_button and self.on_result:
            self.on_result(self.cancel_button)

    # ------------------------------------------------------------------
    # Sizing
    # ------------------------------------------------------------------

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        content_w, content_h = 0.0, 0.0
        if self.content is not None:
            content_w, content_h = self.content.compute_size(viewport_w, viewport_h)

        btn_total_w = 0.0
        for btn in self._button_widgets:
            bw, _ = btn.compute_size(viewport_w, viewport_h)
            btn_total_w += bw
        if self._button_widgets:
            btn_total_w += self.button_spacing * (len(self._button_widgets) - 1)

        w = max(self.min_width, content_w + self.padding * 2,
                btn_total_w + self.padding * 2)
        h = self.title_height + content_h + self.padding + self.button_bar_height

        if self.preferred_width:
            w = self.preferred_width.to_pixels(viewport_w)
        if self.preferred_height:
            h = self.preferred_height.to_pixels(viewport_h)

        return (w, h)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        super().layout(x, y, width, height, viewport_w, viewport_h)
        self._ensure_children()

        # Content area
        if self.content is not None:
            cx = x + self.padding
            cy = y + self.title_height
            cw = width - self.padding * 2
            _, ch = self.content.compute_size(viewport_w, viewport_h)
            self.content.layout(cx, cy, cw, ch, viewport_w, viewport_h)

        # Buttons: right-aligned at bottom
        btn_y = y + height - self.button_bar_height
        btn_sizes = []
        total_btn_w = 0.0
        for btn in self._button_widgets:
            bw, bh = btn.compute_size(viewport_w, viewport_h)
            btn_sizes.append((bw, bh))
            total_btn_w += bw
        if self._button_widgets:
            total_btn_w += self.button_spacing * (len(self._button_widgets) - 1)

        btn_x = x + width - self.padding - total_btn_w
        for btn, (bw, bh) in zip(self._button_widgets, btn_sizes):
            by = btn_y + (self.button_bar_height - bh) / 2
            btn.layout(btn_x, by, bw, bh, viewport_w, viewport_h)
            btn_x += bw + self.button_spacing

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self, renderer: 'UIRenderer'):
        # Background
        renderer.draw_rect(self.x, self.y, self.width, self.height,
                           self.background_color, self.border_radius)

        # Title bar
        renderer.draw_rect(self.x, self.y, self.width, self.title_height,
                           self.title_background_color, self.border_radius)
        # Cover bottom corners of title bar so they don't round
        if self.title_height < self.height:
            renderer.draw_rect(
                self.x, self.y + self.title_height - self.border_radius,
                self.width, self.border_radius,
                self.title_background_color,
            )

        # Title text
        if self.title:
            renderer.draw_text(
                self.x + self.padding,
                self.y + self.title_height / 2 + self.title_font_size * 0.35,
                self.title, self.title_text_color, self.title_font_size,
            )

        # Content
        if self.content is not None:
            self.content.render(renderer)

        # Buttons
        for btn in self._button_widgets:
            btn.render(renderer)

    def _ensure_children(self):
        if self.content is not None:
            if self.content.parent is not self:
                if self.content.parent is not None:
                    self.content.parent.remove_child(self.content)
                self.add_child(self.content)
        for btn in self._button_widgets:
            if btn.parent is not self:
                if btn.parent is not None:
                    btn.parent.remove_child(btn)
                self.add_child(btn)

    # ------------------------------------------------------------------
    # Hit testing
    # ------------------------------------------------------------------

    def hit_test(self, px: float, py: float) -> Widget | None:
        if not self.visible:
            return None
        if not self.contains(px, py):
            return None

        # Buttons
        for btn in self._button_widgets:
            hit = btn.hit_test(px, py)
            if hit:
                return hit

        # Content (may have interactive children)
        if self.content is not None:
            hit = self.content.hit_test(px, py)
            if hit:
                return hit

        return self

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    def on_key_down(self, event: KeyEvent) -> bool:
        if event.key == Key.ENTER and self.default_button:
            self._on_button_click(self.default_button)
            return True
        return False
