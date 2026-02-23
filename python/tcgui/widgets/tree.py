"""Tree widgets: TreeNode, TreeWidget."""

from __future__ import annotations

import time
from typing import Any, Callable

from tcgui.widgets.widget import Widget
from tcgui.widgets.events import MouseEvent, MouseWheelEvent, KeyEvent
from tcgui.widgets.theme import current_theme as _t


class TreeNode(Widget):
    """A single node in a tree. Contains an arbitrary content widget."""

    def __init__(self, content: Widget | None = None):
        super().__init__()
        self.subnodes: list[TreeNode] = []
        self.expanded: bool = False
        self.data: Any = None

        # Internal state (managed by TreeWidget)
        self._depth: int = 0
        self._selected: bool = False
        self._hovered: bool = False
        self._tree: TreeWidget | None = None

        # Content widget
        self._content: Widget | None = None
        if content is not None:
            self.content = content

    @property
    def content(self) -> Widget | None:
        return self._content

    @content.setter
    def content(self, widget: Widget | None):
        if self._content is not None:
            self.remove_child(self._content)
        self._content = widget
        if widget is not None:
            self.add_child(widget)

    @property
    def has_subnodes(self) -> bool:
        return len(self.subnodes) > 0

    def add_node(self, node: TreeNode) -> TreeNode:
        """Add a child tree node."""
        node._tree = self._tree
        self.subnodes.append(node)
        if self._tree is not None:
            self._tree._dirty = True
        return node

    def remove_node(self, node: TreeNode):
        """Remove a child tree node."""
        if node in self.subnodes:
            node._tree = None
            self.subnodes.remove(node)
            if self._tree is not None:
                self._tree._dirty = True

    def toggle(self):
        """Toggle expanded/collapsed state."""
        if not self.has_subnodes:
            return
        self.expanded = not self.expanded
        if self._tree is not None:
            self._tree._dirty = True
            if self.expanded and self._tree.on_expand:
                self._tree.on_expand(self)
            elif not self.expanded and self._tree.on_collapse:
                self._tree.on_collapse(self)

    def _set_tree_recursive(self, tree: TreeWidget | None):
        """Set back-reference to owning TreeWidget for this node and all descendants."""
        self._tree = tree
        for child in self.subnodes:
            child._set_tree_recursive(tree)


class TreeWidget(Widget):
    """Tree view widget. Displays a hierarchy of TreeNode items."""

    def __init__(self):
        super().__init__()
        self.focusable = True

        self.root_nodes: list[TreeNode] = []

        # Configuration
        self.indent_size: float = 20
        self.toggle_size: float = 16
        self.row_height: float = 28
        self.row_spacing: float = 0
        self.toggle_font_size: float = 10

        # Colors
        self.selected_background: tuple[float, float, float, float] = _t.selected
        self.hover_background: tuple[float, float, float, float] = _t.hover_subtle
        self.toggle_color: tuple[float, float, float, float] = _t.text_secondary

        # Callbacks
        self.on_select: Callable[[TreeNode], None] | None = None
        self.on_activate: Callable[[TreeNode], None] | None = None
        self.on_expand: Callable[[TreeNode], None] | None = None
        self.on_collapse: Callable[[TreeNode], None] | None = None

        # State
        self.selected_node: TreeNode | None = None
        self._visible_nodes: list[TreeNode] = []
        self._hovered_node: TreeNode | None = None
        self._scroll_offset: float = 0.0
        self._dirty: bool = True

        # Cached viewport for re-layout on dirty
        self._viewport_w: float = 0
        self._viewport_h: float = 0

        # Double-click
        self._last_click_node: TreeNode | None = None
        self._last_click_time: float = 0.0
        self._DOUBLE_CLICK_INTERVAL: float = 0.4

    def add_root(self, node: TreeNode) -> TreeNode:
        """Add a top-level tree node."""
        node._set_tree_recursive(self)
        self.root_nodes.append(node)
        self._dirty = True
        return node

    def remove_root(self, node: TreeNode):
        """Remove a top-level tree node."""
        if node in self.root_nodes:
            node._set_tree_recursive(None)
            self.root_nodes.remove(node)
            if self.selected_node is node:
                self.selected_node = None
            self._dirty = True

    def clear(self):
        """Remove all nodes."""
        for node in self.root_nodes:
            node._set_tree_recursive(None)
        self.root_nodes.clear()
        self.selected_node = None
        self._dirty = True

    # --- Visible nodes ---

    def _rebuild_visible(self):
        """Flatten the tree into a list of visible nodes."""
        self._visible_nodes = []
        for node in self.root_nodes:
            self._collect_visible(node, 0)
        self._dirty = False

    def _collect_visible(self, node: TreeNode, depth: int):
        node._depth = depth
        self._visible_nodes.append(node)
        if node.expanded:
            for child in node.subnodes:
                self._collect_visible(child, depth + 1)

    def _node_at_y(self, y: float) -> TreeNode | None:
        """Find the node at a given y coordinate."""
        rel_y = y - self.y + self._scroll_offset
        stride = self.row_height + self.row_spacing
        if stride <= 0:
            return None
        idx = int(rel_y / stride)
        if 0 <= idx < len(self._visible_nodes):
            # Check we're within the row, not in spacing
            if rel_y - idx * stride <= self.row_height:
                return self._visible_nodes[idx]
        return None

    def _node_y(self, node: TreeNode) -> float:
        """Get the y position of a node (relative to widget top, before scroll)."""
        try:
            idx = self._visible_nodes.index(node)
        except ValueError:
            return 0.0
        stride = self.row_height + self.row_spacing
        return self.y + idx * stride - self._scroll_offset

    def _select_node(self, node: TreeNode | None):
        """Set the selected node."""
        if self.selected_node is not None:
            self.selected_node._selected = False
        self.selected_node = node
        if node is not None:
            node._selected = True
            if self.on_select:
                self.on_select(node)

    def _ensure_visible(self, node: TreeNode):
        """Scroll to make node visible if needed."""
        try:
            idx = self._visible_nodes.index(node)
        except ValueError:
            return
        stride = self.row_height + self.row_spacing
        node_top = idx * stride
        node_bottom = node_top + self.row_height

        if node_top < self._scroll_offset:
            self._scroll_offset = node_top
        elif node_bottom > self._scroll_offset + self.height:
            self._scroll_offset = node_bottom - self.height

    def _find_parent(self, target: TreeNode) -> TreeNode | None:
        """Find the parent TreeNode of target."""
        def _search(nodes: list[TreeNode]) -> TreeNode | None:
            for node in nodes:
                if target in node.subnodes:
                    return node
                found = _search(node.subnodes)
                if found:
                    return found
            return None
        return _search(self.root_nodes)

    # --- Widget overrides ---

    def compute_size(self, viewport_w: float, viewport_h: float) -> tuple[float, float]:
        if self.preferred_width and self.preferred_height:
            return (
                self.preferred_width.to_pixels(viewport_w),
                self.preferred_height.to_pixels(viewport_h),
            )
        if self._dirty:
            self._rebuild_visible()
        n = len(self._visible_nodes)
        h = n * self.row_height + max(0, n - 1) * self.row_spacing if n else self.row_height
        w = self.preferred_width.to_pixels(viewport_w) if self.preferred_width else 300
        if self.preferred_height:
            h = self.preferred_height.to_pixels(viewport_h)
        return (w, h)

    def layout(self, x: float, y: float, width: float, height: float,
               viewport_w: float, viewport_h: float):
        super().layout(x, y, width, height, viewport_w, viewport_h)
        self._viewport_w = viewport_w
        self._viewport_h = viewport_h

        if self._dirty:
            self._rebuild_visible()

        self._layout_nodes()

    def _layout_nodes(self):
        """Position all visible nodes and their content widgets."""
        stride = self.row_height + self.row_spacing
        for i, node in enumerate(self._visible_nodes):
            node.x = self.x
            node.y = self.y + i * stride - self._scroll_offset
            node.width = self.width
            node.height = self.row_height

            if node._content is not None:
                indent = node._depth * self.indent_size + self.toggle_size
                cw, ch = node._content.compute_size(self._viewport_w, self._viewport_h)
                node._content.layout(
                    node.x + indent,
                    node.y + (node.height - ch) / 2,
                    node.width - indent, ch,
                    self._viewport_w, self._viewport_h,
                )

    def render(self, renderer: 'UIRenderer'):
        if self._dirty:
            self._rebuild_visible()
            self._layout_nodes()

        renderer.begin_clip(self.x, self.y, self.width, self.height)

        stride = self.row_height + self.row_spacing
        for i, node in enumerate(self._visible_nodes):
            row_y = self.y + i * stride - self._scroll_offset

            # Skip rows outside visible area
            if row_y + self.row_height < self.y or row_y > self.y + self.height:
                continue

            # Row background
            if node._selected:
                renderer.draw_rect(self.x, row_y, self.width, self.row_height,
                                   self.selected_background)
            elif node._hovered:
                renderer.draw_rect(self.x, row_y, self.width, self.row_height,
                                   self.hover_background)

            # Expand/collapse toggle
            if node.has_subnodes:
                toggle_x = self.x + node._depth * self.indent_size
                toggle_cy = row_y + self.row_height / 2
                symbol = "\u25BC" if node.expanded else "\u25B6"
                renderer.draw_text_centered(
                    toggle_x + self.toggle_size / 2,
                    toggle_cy,
                    symbol,
                    self.toggle_color,
                    self.toggle_font_size,
                )

            # Render content widget
            if node._content is not None:
                node._content.render(renderer)

        renderer.end_clip()

    def hit_test(self, px: float, py: float) -> Widget | None:
        if not self.visible:
            return None
        if not self.contains(px, py):
            return None
        return self

    # --- Mouse events ---

    def on_mouse_wheel(self, event: MouseWheelEvent) -> bool:
        """Scroll tree view with mouse wheel."""
        stride = self.row_height + self.row_spacing
        total_content = len(self._visible_nodes) * stride
        max_scroll = max(0.0, total_content - self.height)
        if max_scroll <= 0:
            return False
        self._scroll_offset -= event.dy * 30
        self._scroll_offset = max(0.0, min(self._scroll_offset, max_scroll))
        self._layout_nodes()
        return True

    def on_mouse_move(self, event: MouseEvent):
        node = self._node_at_y(event.y)
        if node is not self._hovered_node:
            if self._hovered_node is not None:
                self._hovered_node._hovered = False
            if node is not None:
                node._hovered = True
            self._hovered_node = node

    def on_mouse_leave(self):
        if self._hovered_node is not None:
            self._hovered_node._hovered = False
            self._hovered_node = None

    def on_mouse_down(self, event: MouseEvent) -> bool:
        node = self._node_at_y(event.y)
        if node is None:
            return False

        now = time.monotonic()

        # Check if click is on the toggle area
        toggle_x = self.x + node._depth * self.indent_size
        if node.has_subnodes and toggle_x <= event.x < toggle_x + self.toggle_size:
            node.toggle()
            return True

        # Double-click detection
        if (node is self._last_click_node
                and now - self._last_click_time < self._DOUBLE_CLICK_INTERVAL):
            if self.on_activate:
                self.on_activate(node)
            self._last_click_node = None
            self._last_click_time = 0.0
            return True

        # Single click — select
        self._last_click_node = node
        self._last_click_time = now
        self._select_node(node)
        return True

    # --- Keyboard events ---

    def on_key_down(self, event: KeyEvent) -> bool:
        from tcbase import Key

        if not self._visible_nodes:
            return False

        key = event.key
        if key == Key.DOWN:
            return self._navigate(1)

        if key == Key.UP:
            return self._navigate(-1)

        if key == Key.RIGHT:
            if self.selected_node is not None:
                if self.selected_node.has_subnodes and not self.selected_node.expanded:
                    self.selected_node.toggle()
                elif self.selected_node.expanded and self.selected_node.subnodes:
                    # Move to first child
                    self._select_node(self.selected_node.subnodes[0])
                    self._ensure_visible(self.selected_node)
            return True

        if key == Key.LEFT:
            if self.selected_node is not None:
                if self.selected_node.expanded and self.selected_node.has_subnodes:
                    self.selected_node.toggle()
                else:
                    # Move to parent
                    parent = self._find_parent(self.selected_node)
                    if parent is not None:
                        self._select_node(parent)
                        self._ensure_visible(parent)
            return True

        if key == Key.ENTER:
            if self.selected_node is not None and self.on_activate:
                self.on_activate(self.selected_node)
            return True

        return False

    def _navigate(self, delta: int) -> bool:
        """Move selection by delta positions in the visible list."""
        if self.selected_node is None:
            if self._visible_nodes:
                self._select_node(self._visible_nodes[0])
                self._ensure_visible(self._visible_nodes[0])
            return True

        try:
            idx = self._visible_nodes.index(self.selected_node)
        except ValueError:
            return True

        new_idx = max(0, min(len(self._visible_nodes) - 1, idx + delta))
        node = self._visible_nodes[new_idx]
        self._select_node(node)
        self._ensure_visible(node)
        return True
