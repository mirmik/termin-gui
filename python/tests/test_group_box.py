"""GroupBox layout tests."""

from tcgui.widgets.group_box import GroupBox
from tcgui.widgets.units import px
from tests.conftest import make_widget, VIEWPORT_W, VIEWPORT_H


def test_collapsed_height():
    gb = GroupBox()
    gb.expanded = False
    gb.title_height = 28
    w, h = gb.compute_size(VIEWPORT_W, VIEWPORT_H)
    assert h == 28


def test_expanded_height():
    gb = GroupBox()
    gb.expanded = True
    gb.title_height = 28
    gb.content_padding = 8
    child = make_widget(100, 200)
    gb.add_child(child)
    w, h = gb.compute_size(VIEWPORT_W, VIEWPORT_H)
    # h = title_height + child_h + padding*2 = 28 + 200 + 16 = 244
    assert abs(h - 244) <= 0.5


def test_child_positioned_below_title():
    gb = GroupBox()
    gb.expanded = True
    gb.title_height = 28
    gb.content_padding = 8
    child = make_widget(100, 200)
    gb.add_child(child)

    gb.layout(10, 20, 300, 244, VIEWPORT_W, VIEWPORT_H)
    # child.y = gb.y + title_height + content_padding = 20 + 28 + 8 = 56
    assert abs(child.y - 56) <= 0.5
    # child.x = gb.x + content_padding = 10 + 8 = 18
    assert abs(child.x - 18) <= 0.5


def test_child_width_reduced_by_padding():
    gb = GroupBox()
    gb.expanded = True
    gb.content_padding = 8
    child = make_widget(100, 200)
    gb.add_child(child)

    gb.layout(0, 0, 300, 244, VIEWPORT_W, VIEWPORT_H)
    # child.width = 300 - 8*2 = 284
    assert abs(child.width - 284) <= 0.5
