"""VStack container."""

from __future__ import annotations

from tcgui.widgets.widget import Widget


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
