# Быстрый старт

Минимальный рабочий поток:

1. создать `UI(graphics)`;
2. собрать дерево виджетов;
3. назначить `ui.root`;
4. прокинуть события (`mouse_*`, `key_down`, `text_input`);
5. рендерить `ui.render(viewport_w, viewport_h)` каждый кадр.

## Минимальный пример

```python
from tgfx import OpenGLGraphicsBackend
from tcgui.widgets.ui import UI
from tcgui.widgets.basic import Label, Button
from tcgui.widgets.containers import Panel, VStack
from tcgui.widgets.units import pct, px

graphics = OpenGLGraphicsBackend.get_instance()
graphics.ensure_ready()

root = Panel()
root.preferred_width = pct(100)
root.preferred_height = pct(100)
root.padding = 24

stack = VStack()
stack.spacing = 12

label = Label()
label.text = "Hello tcgui"

button = Button()
button.text = "Click"
button.preferred_width = px(120)
button.on_click = lambda: print("clicked")

stack.add_child(label)
stack.add_child(button)
root.add_child(stack)

ui = UI(graphics)
ui.root = root

# В цикле кадра:
# ui.render(width, height)
```

## События, которые нужно прокинуть из платформы

- `ui.mouse_move(x, y)`
- `ui.mouse_down(x, y, button, mods=0)`
- `ui.mouse_up(x, y, button=MouseButton.LEFT, mods=0)`
- `ui.mouse_wheel(dx, dy, x, y)`
- `ui.key_down(key, mods=0)`
- `ui.text_input(text)`

См. полный SDL wiring в `examples/sdl_hello.py`.
