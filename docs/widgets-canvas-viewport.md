# Canvas и Viewport3D

## Canvas

`Canvas` — zoom/pan виджет для RGBA numpy-изображений + overlay-слоя.

API:
- данные:
  - `set_image(np_rgba_or_none)`
  - `set_overlay(np_rgba_or_none)`
  - `set_overlay_ref(np_rgba_or_none)`
  - `mark_overlay_dirty(x0, y0, x1, y1)`
- viewport:
  - `zoom` (property)
  - `set_zoom(value, anchor_wx=None, anchor_wy=None)`
  - `fit_in_view()`
  - `center_on(ix, iy)`
  - `widget_to_image(wx, wy)`, `image_to_widget(ix, iy)`
- callbacks:
  - `on_canvas_mouse_down(ix, iy, button, mods)`
  - `on_canvas_mouse_move(ix, iy)`
  - `on_canvas_mouse_up(ix, iy)`
  - `on_zoom_changed(zoom)`
  - `on_render_overlay(canvas, renderer)`

Поведение:
- middle mouse drag = pan;
- wheel = zoom around cursor;
- `min_zoom`, `max_zoom`, `zoom_factor` настраиваемы.

## Viewport3D

`Viewport3D` показывает FBO-сцену от `termin` и пересылает input в 3D input manager.

API:
- `set_surface(surface, display=None)`
- callback: `on_before_resize(new_w, new_h)`

Особенности:
- получает цветовую текстуру FBO и blit-ит ее в область виджета;
- при resize вызывает `surface.resize(new_w, new_h)`;
- обрабатывает `on_mouse_*`, `on_key_down`, `on_key_up` как прокси в native input.

## Пример Canvas

```python
canvas = Canvas()
canvas.set_image(image_rgba)
canvas.fit_in_view()

canvas.on_canvas_mouse_down = lambda ix, iy, btn, mods: print(ix, iy)
canvas.on_zoom_changed = lambda z: print("zoom", z)
```
