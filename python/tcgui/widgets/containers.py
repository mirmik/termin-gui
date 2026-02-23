"""Container widgets: HStack, VStack, Panel, ScrollArea."""

from __future__ import annotations

from tcgui.widgets.widget import Widget
from tcgui.widgets.units import Value, px


class HStack(Widget):
    """Horizontal layout container."""

    def __init__(self):
        super().__init__()
        self.spacing: float = 0  # pixels
        self.alignment: str = "center"  # top, center, bottom (vertical)
        self.justify: str = "start"  # start, center, end (horizontal)

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )

        total_width = 0.0
        max_height = 0.0

        for child in self.children:
            cw, ch = child.compute_size(viewport_w, viewport_h)
            total_width += cw
            max_height = max(max_height, ch)

        if self.children:
            total_width += self.spacing * (len(self.children) - 1)

        # Allow override of individual dimensions
        if self.preferred_width:
            total_width = self.preferred_width.to_pixels(viewport_w)
        if self.preferred_height:
            max_height = self.preferred_height.to_pixels(viewport_h)

        return (total_width, max_height)

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        super().layout(x, y, width, height, viewport_w, viewport_h)

        # Calculate total content width
        total_content_width = 0.0
        for child in self.children:
            cw, _ = child.compute_size(viewport_w, viewport_h)
            total_content_width += cw
        if self.children:
            total_content_width += self.spacing * (len(self.children) - 1)

        # Horizontal justify
        if self.justify == "center":
            cx = x + (width - total_content_width) / 2
        elif self.justify == "end":
            cx = x + width - total_content_width
        else:  # start
            cx = x

        for child in self.children:
            cw, ch = child.compute_size(viewport_w, viewport_h)

            # Vertical alignment
            if self.alignment == "top":
                cy = y
            elif self.alignment == "bottom":
                cy = y + height - ch
            else:  # center
                cy = y + (height - ch) / 2

            child.layout(cx, cy, cw, ch, viewport_w, viewport_h)
            cx += cw + self.spacing


class VStack(Widget):
    """Vertical layout container."""

    def __init__(self):
        super().__init__()
        self.spacing: float = 0  # pixels
        self.alignment: str = "center"  # left, center, right (horizontal)
        self.justify: str = "start"  # start, center, end (vertical)

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )

        max_width = 0.0
        total_height = 0.0

        for child in self.children:
            cw, ch = child.compute_size(viewport_w, viewport_h)
            max_width = max(max_width, cw)
            total_height += ch

        if self.children:
            total_height += self.spacing * (len(self.children) - 1)

        if self.preferred_width:
            max_width = self.preferred_width.to_pixels(viewport_w)
        if self.preferred_height:
            total_height = self.preferred_height.to_pixels(viewport_h)

        return (max_width, total_height)

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        super().layout(x, y, width, height, viewport_w, viewport_h)

        # Calculate total content height
        total_content_height = 0.0
        for child in self.children:
            _, ch = child.compute_size(viewport_w, viewport_h)
            total_content_height += ch
        if self.children:
            total_content_height += self.spacing * (len(self.children) - 1)

        # Vertical justify
        if self.justify == "center":
            cy = y + (height - total_content_height) / 2
        elif self.justify == "end":
            cy = y + height - total_content_height
        else:  # start
            cy = y

        for child in self.children:
            cw, ch = child.compute_size(viewport_w, viewport_h)

            # Horizontal alignment
            if self.alignment == "left":
                cx = x
            elif self.alignment == "right":
                cx = x + width - cw
            else:  # center
                cx = x + (width - cw) / 2

            child.layout(cx, cy, cw, ch, viewport_w, viewport_h)
            cy += ch + self.spacing


class Panel(Widget):
    """Container with background and padding."""

    def __init__(self):
        super().__init__()
        self.padding: float = 0  # pixels
        self.background_color: tuple[float, float, float, float] = (0.2, 0.2, 0.2, 0.9)
        self.border_radius: float = 0
        self.background_image: str = ""  # path to background image
        self.background_tint: tuple[float, float, float, float] = (1, 1, 1, 1)
        self._bg_texture = None

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h)
            )

        if self.children:
            # Panel wraps first child
            cw, ch = self.children[0].compute_size(viewport_w, viewport_h)
            return (cw + self.padding * 2, ch + self.padding * 2)

        return (self.padding * 2, self.padding * 2)

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        super().layout(x, y, width, height, viewport_w, viewport_h)

        # Inner area after padding
        inner_x = x + self.padding
        inner_y = y + self.padding
        inner_w = width - self.padding * 2
        inner_h = height - self.padding * 2

        for child in self.children:
            cw, ch = child.compute_size(viewport_w, viewport_h)

            # Respect child's anchor within panel's inner area
            anchor = child.anchor
            cx, cy = inner_x, inner_y

            if anchor == "absolute":
                # Absolute positioning relative to panel
                if child.position_x is not None:
                    cx = inner_x + child.position_x.to_pixels(inner_w)
                if child.position_y is not None:
                    cy = inner_y + child.position_y.to_pixels(inner_h)
            else:
                # Anchor-based positioning
                if "left" in anchor:
                    cx = inner_x
                elif "right" in anchor:
                    cx = inner_x + inner_w - cw
                elif "center" in anchor or anchor in ("top", "bottom"):
                    cx = inner_x + (inner_w - cw) / 2

                if "top" in anchor:
                    cy = inner_y
                elif "bottom" in anchor:
                    cy = inner_y + inner_h - ch
                elif "center" in anchor or anchor in ("left", "right"):
                    cy = inner_y + (inner_h - ch) / 2

                # Apply offset
                cx += child.offset_x
                cy += child.offset_y

            child.layout(cx, cy, cw, ch, viewport_w, viewport_h)

    def _ensure_bg_texture(self, renderer: 'UIRenderer'):
        if self._bg_texture is None and self.background_image:
            self._bg_texture = renderer.load_image(self.background_image)

    def render(self, renderer: 'UIRenderer'):
        # Draw background only if not fully transparent
        if self.background_color[3] > 0:
            renderer.draw_rect(
                self.x, self.y, self.width, self.height,
                self.background_color,
                self.border_radius
            )
        # Draw background image on top of color
        if self.background_image:
            self._ensure_bg_texture(renderer)
            if self._bg_texture is not None:
                renderer.draw_image(
                    self.x, self.y, self.width, self.height,
                    self._bg_texture, self.background_tint
                )
        # Render children
        super().render(renderer)


class ScrollArea(Widget):
    """Scrollable container. Wraps a single child and provides vertical/horizontal scrolling."""

    def __init__(self):
        super().__init__()
        self.scroll_x: float = 0.0
        self.scroll_y: float = 0.0
        self.scroll_speed: float = 30.0
        self.show_scrollbar: bool = True
        self.scrollbar_width: float = 8.0
        self.scrollbar_color: tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.5)
        self.scrollbar_hover_color: tuple[float, float, float, float] = (0.7, 0.7, 0.7, 0.7)

        self._content_w: float = 0.0
        self._content_h: float = 0.0
        self._dragging_scrollbar: bool = False
        self._drag_start_y: float = 0.0
        self._drag_start_scroll: float = 0.0
        self._scrollbar_hovered: bool = False

        # Cached viewport
        self._viewport_w: float = 0
        self._viewport_h: float = 0

    @property
    def _max_scroll_y(self) -> float:
        return max(0.0, self._content_h - self.height)

    @property
    def _max_scroll_x(self) -> float:
        return max(0.0, self._content_w - self.width)

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h),
            )
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 200
        h = self.preferred_height.to_pixels(viewport_h) if self.preferred_height else 200
        return (w, h)

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        super().layout(x, y, width, height, viewport_w, viewport_h)
        self._viewport_w = viewport_w
        self._viewport_h = viewport_h

        if self.children:
            content = self.children[0]
            cw, ch = content.compute_size(viewport_w, viewport_h)
            self._content_w = cw
            self._content_h = ch

            # Clamp scroll
            self.scroll_y = max(0.0, min(self.scroll_y, self._max_scroll_y))
            self.scroll_x = max(0.0, min(self.scroll_x, self._max_scroll_x))

            content.layout(
                x - self.scroll_x,
                y - self.scroll_y,
                max(cw, width),
                max(ch, height),
                viewport_w, viewport_h,
            )

    def render(self, renderer: 'UIRenderer'):
        renderer.begin_clip(self.x, self.y, self.width, self.height)

        for child in self.children:
            if child.visible:
                child.render(renderer)

        renderer.end_clip()

        # Draw vertical scrollbar
        if self.show_scrollbar and self._content_h > self.height:
            viewport_ratio = self.height / self._content_h
            thumb_h = max(20.0, self.height * viewport_ratio)
            track_h = self.height - thumb_h
            thumb_y = self.y + (track_h * (self.scroll_y / self._max_scroll_y) if self._max_scroll_y > 0 else 0)
            sb_x = self.x + self.width - self.scrollbar_width

            color = self.scrollbar_hover_color if self._scrollbar_hovered or self._dragging_scrollbar else self.scrollbar_color
            renderer.draw_rect(sb_x, thumb_y, self.scrollbar_width, thumb_h, color, self.scrollbar_width / 2)

    def hit_test(self, px: float, py: float) -> Widget | None:
        if not self.visible:
            return None
        if not self.contains(px, py):
            return None

        # Scrollbar area belongs to ScrollArea itself
        if self.show_scrollbar and self._content_h > self.height:
            sb_x = self.x + self.width - self.scrollbar_width
            if px >= sb_x:
                return self

        # Check children
        for child in reversed(self.children):
            hit = child.hit_test(px, py)
            if hit and hit is not self:
                return hit

        return self

    def on_mouse_wheel(self, dx: float, dy: float) -> bool:
        if self._max_scroll_y <= 0:
            return False
        self.scroll_y -= dy * self.scroll_speed
        self.scroll_y = max(0.0, min(self.scroll_y, self._max_scroll_y))
        self._relayout_content()
        return True

    def on_mouse_down(self, x: float, y: float) -> bool:
        # Check if click is on scrollbar
        if self.show_scrollbar and self._content_h > self.height:
            sb_x = self.x + self.width - self.scrollbar_width
            if x >= sb_x:
                self._dragging_scrollbar = True
                self._drag_start_y = y
                self._drag_start_scroll = self.scroll_y
                return True
        return False

    def on_mouse_move(self, x: float, y: float):
        if self._dragging_scrollbar:
            delta_y = y - self._drag_start_y
            viewport_ratio = self.height / self._content_h
            thumb_h = max(20.0, self.height * viewport_ratio)
            track_h = self.height - thumb_h
            if track_h > 0:
                self.scroll_y = self._drag_start_scroll + delta_y * (self._max_scroll_y / track_h)
                self.scroll_y = max(0.0, min(self.scroll_y, self._max_scroll_y))
                self._relayout_content()
        else:
            # Track scrollbar hover
            if self.show_scrollbar and self._content_h > self.height:
                sb_x = self.x + self.width - self.scrollbar_width
                self._scrollbar_hovered = x >= sb_x
            else:
                self._scrollbar_hovered = False

    def on_mouse_up(self, x: float, y: float):
        self._dragging_scrollbar = False

    def on_mouse_leave(self):
        self._scrollbar_hovered = False

    def _relayout_content(self):
        """Re-position content after scroll change."""
        if self.children:
            content = self.children[0]
            cw, ch = content.compute_size(self._viewport_w, self._viewport_h)
            content.layout(
                self.x - self.scroll_x,
                self.y - self.scroll_y,
                max(cw, self.width),
                max(ch, self.height),
                self._viewport_w, self._viewport_h,
            )
