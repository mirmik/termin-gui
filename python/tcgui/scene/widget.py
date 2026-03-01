"""Scene view widget with pan/zoom/selection/drag support."""

from __future__ import annotations

from tcbase import Key, MouseButton

from tcgui.scene.item import GraphicsItem, SceneTransform
from tcgui.scene.scene import GraphicsScene
from tcgui.widgets.events import MouseEvent, MouseWheelEvent, KeyEvent
from tcgui.widgets.widget import Widget


class SceneView(Widget):
    """Widget that displays a GraphicsScene."""

    def __init__(self, scene: GraphicsScene | None = None) -> None:
        super().__init__()
        self.focusable = True
        self.cursor = "move"

        self.scene = scene if scene is not None else GraphicsScene()

        self.background_color = (0.10, 0.11, 0.13, 1.0)
        self.grid_color = (0.17, 0.19, 0.24, 1.0)
        self.grid_axis_color = (0.30, 0.33, 0.42, 1.0)
        self.show_grid = True
        self.grid_step = 40.0

        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 4.0
        self.zoom_factor = 1.15
        self.offset_x = 0.0
        self.offset_y = 0.0

        self._panning = False
        self._pan_start_x = 0.0
        self._pan_start_y = 0.0
        self._pan_start_offset_x = 0.0
        self._pan_start_offset_y = 0.0

        self._drag_item: GraphicsItem | None = None
        self._drag_item_start_x = 0.0
        self._drag_item_start_y = 0.0
        self._drag_mouse_start_wx = 0.0
        self._drag_mouse_start_wy = 0.0

    def world_to_screen(self, wx: float, wy: float) -> tuple[float, float]:
        return (
            self.x + self.offset_x + wx * self.zoom,
            self.y + self.offset_y + wy * self.zoom,
        )

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        return (
            (sx - self.x - self.offset_x) / self.zoom,
            (sy - self.y - self.offset_y) / self.zoom,
        )

    def _make_transform(self) -> SceneTransform:
        return SceneTransform(
            origin_x=self.x + self.offset_x,
            origin_y=self.y + self.offset_y,
            zoom=self.zoom,
        )

    def _draw_grid(self, renderer) -> None:
        if not self.show_grid or self.grid_step <= 0.0:
            return

        world_left, world_top = self.screen_to_world(self.x, self.y)
        world_right, world_bottom = self.screen_to_world(
            self.x + self.width, self.y + self.height
        )

        step = self.grid_step
        start_x = int(world_left // step) * step
        end_x = int(world_right // step + 1) * step
        start_y = int(world_top // step) * step
        end_y = int(world_bottom // step + 1) * step

        for wx in range(int(start_x), int(end_x) + 1, int(step)):
            sx, _ = self.world_to_screen(float(wx), 0.0)
            color = self.grid_axis_color if wx == 0 else self.grid_color
            renderer.draw_line(sx, self.y, sx, self.y + self.height, color, 1.0)

        for wy in range(int(start_y), int(end_y) + 1, int(step)):
            _, sy = self.world_to_screen(0.0, float(wy))
            color = self.grid_axis_color if wy == 0 else self.grid_color
            renderer.draw_line(self.x, sy, self.x + self.width, sy, color, 1.0)

    def render(self, renderer) -> None:
        renderer.draw_rect(self.x, self.y, self.width, self.height, self.background_color)
        renderer.begin_clip(self.x, self.y, self.width, self.height)
        self._draw_grid(renderer)
        self.scene.render(renderer, self._make_transform())
        renderer.end_clip()

    def on_mouse_down(self, event: MouseEvent) -> bool:
        if event.button == MouseButton.MIDDLE:
            self._panning = True
            self._pan_start_x = event.x
            self._pan_start_y = event.y
            self._pan_start_offset_x = self.offset_x
            self._pan_start_offset_y = self.offset_y
            return True

        if event.button != MouseButton.LEFT:
            return False

        wx, wy = self.screen_to_world(event.x, event.y)
        hit = self.scene.hit_test(wx, wy)
        self.scene.set_selected(hit)

        if hit is not None and hit.draggable:
            self._drag_item = hit
            self._drag_item_start_x = hit.x
            self._drag_item_start_y = hit.y
            self._drag_mouse_start_wx = wx
            self._drag_mouse_start_wy = wy
        return True

    def on_mouse_move(self, event: MouseEvent) -> None:
        if self._panning:
            self.offset_x = self._pan_start_offset_x + (event.x - self._pan_start_x)
            self.offset_y = self._pan_start_offset_y + (event.y - self._pan_start_y)
            return

        if self._drag_item is not None:
            wx, wy = self.screen_to_world(event.x, event.y)
            self._drag_item.x = self._drag_item_start_x + (wx - self._drag_mouse_start_wx)
            self._drag_item.y = self._drag_item_start_y + (wy - self._drag_mouse_start_wy)

    def on_mouse_up(self, event: MouseEvent) -> None:
        del event
        self._panning = False
        self._drag_item = None

    def on_mouse_wheel(self, event: MouseWheelEvent) -> bool:
        before_wx, before_wy = self.screen_to_world(event.x, event.y)
        factor = self.zoom_factor if event.dy > 0 else 1.0 / self.zoom_factor
        self.zoom = max(self.min_zoom, min(self.zoom * factor, self.max_zoom))
        self.offset_x = (event.x - self.x) - before_wx * self.zoom
        self.offset_y = (event.y - self.y) - before_wy * self.zoom
        return True

    def on_key_down(self, event: KeyEvent) -> bool:
        if event.key == Key.DELETE:
            for item in self.scene.selected_items[:]:
                if item.parent is None:
                    self.scene.remove_item(item)
            self.scene.clear_selection()
            return True
        return False
