"""Graphics item primitives for scene-based interaction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SceneTransform:
    """World-to-screen transform parameters."""

    origin_x: float
    origin_y: float
    zoom: float

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        return (
            self.origin_x + wx * self.zoom,
            self.origin_y + wy * self.zoom,
        )


class GraphicsItem:
    """Base retained item for a lightweight scene graph."""

    def __init__(self) -> None:
        self.parent: GraphicsItem | None = None
        self.children: list[GraphicsItem] = []

        self.x: float = 0.0
        self.y: float = 0.0
        self.width: float = 100.0
        self.height: float = 60.0
        self.z_index: float = 0.0

        self.visible: bool = True
        self.enabled: bool = True
        self.selectable: bool = True
        self.draggable: bool = False
        self.selected: bool = False
        self.hovered: bool = False

        self.data: dict[str, Any] = {}

    def add_child(self, child: "GraphicsItem") -> "GraphicsItem":
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child: "GraphicsItem") -> None:
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def world_position(self) -> tuple[float, float]:
        if self.parent is None:
            return (self.x, self.y)
        px, py = self.parent.world_position()
        return (px + self.x, py + self.y)

    def world_bounds(self) -> tuple[float, float, float, float]:
        wx, wy = self.world_position()
        return (wx, wy, self.width, self.height)

    def contains_local(self, lx: float, ly: float) -> bool:
        return 0.0 <= lx <= self.width and 0.0 <= ly <= self.height

    def hit_test(self, wx: float, wy: float) -> "GraphicsItem | None":
        if not self.visible or not self.enabled:
            return None

        x, y = self.world_position()
        lx = wx - x
        ly = wy - y
        if not self.contains_local(lx, ly):
            return None

        for child in sorted(self.children, key=lambda i: i.z_index, reverse=True):
            hit = child.hit_test(wx, wy)
            if hit is not None:
                return hit
        return self

    def paint(self, renderer, transform: SceneTransform) -> None:
        """Draw item body. Override in subclasses."""
        del renderer, transform

    def render(self, renderer, transform: SceneTransform) -> None:
        if not self.visible:
            return
        self.paint(renderer, transform)
        for child in sorted(self.children, key=lambda i: i.z_index):
            child.render(renderer, transform)


class RectItem(GraphicsItem):
    """Simple rectangle item with optional text label."""

    def __init__(self, label: str = "") -> None:
        super().__init__()
        self.label = label
        self.fill_color = (0.22, 0.24, 0.30, 1.0)
        self.border_color = (0.36, 0.40, 0.50, 1.0)
        self.border_selected_color = (0.95, 0.72, 0.20, 1.0)
        self.text_color = (0.90, 0.92, 0.96, 1.0)
        self.font_size = 13.0
        self.border_width = 1.0

    def paint(self, renderer, transform: SceneTransform) -> None:
        wx, wy, ww, wh = self.world_bounds()
        sx, sy = transform.world_to_screen(wx, wy)
        sw = ww * transform.zoom
        sh = wh * transform.zoom

        renderer.draw_rect(sx, sy, sw, sh, self.fill_color)
        border = self.border_selected_color if self.selected else self.border_color
        renderer.draw_rect_outline(sx, sy, sw, sh, border, self.border_width)

        if self.label:
            renderer.draw_text(
                sx + 8.0,
                sy + min(sh - 6.0, self.font_size + 8.0),
                self.label,
                self.text_color,
                self.font_size,
            )
