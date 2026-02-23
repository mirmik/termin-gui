"""HStack container."""

from __future__ import annotations

from tcgui.widgets.widget import Widget


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
