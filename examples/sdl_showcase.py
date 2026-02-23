"""Showcase example with all new tcgui widgets.

Demonstrates: ScrollArea, ProgressBar, Slider, TabBar/TabView, mouse wheel.

Requirements: tcbase, tgfx, tcgui, PySDL2
Run: python3 examples/sdl_showcase.py
"""

import ctypes
import sdl2
from sdl2 import video

from tgfx import OpenGLGraphicsBackend
from tcbase import Key, MouseButton, Mods

from tcgui.widgets.ui import UI
from tcgui.widgets.basic import Label, Button, ProgressBar, Slider, SpinBox, SliderEdit, TextArea
from tcgui.widgets.containers import VStack, HStack, Panel, ScrollArea, GroupBox
from tcgui.widgets.tabs import TabView
from tcgui.widgets.units import px, pct


# --- SDL helpers ---

def create_window(title: str, width: int, height: int):
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
        raise RuntimeError(f"SDL_Init failed: {sdl2.SDL_GetError()}")

    video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MAJOR_VERSION, 3)
    video.SDL_GL_SetAttribute(video.SDL_GL_CONTEXT_MINOR_VERSION, 3)
    video.SDL_GL_SetAttribute(
        video.SDL_GL_CONTEXT_PROFILE_MASK,
        video.SDL_GL_CONTEXT_PROFILE_CORE,
    )
    video.SDL_GL_SetAttribute(video.SDL_GL_DOUBLEBUFFER, 1)
    video.SDL_GL_SetAttribute(video.SDL_GL_DEPTH_SIZE, 24)

    flags = video.SDL_WINDOW_OPENGL | video.SDL_WINDOW_RESIZABLE | video.SDL_WINDOW_SHOWN
    window = video.SDL_CreateWindow(
        title.encode("utf-8"),
        video.SDL_WINDOWPOS_CENTERED,
        video.SDL_WINDOWPOS_CENTERED,
        width, height, flags,
    )
    if not window:
        raise RuntimeError(f"SDL_CreateWindow failed: {sdl2.SDL_GetError()}")

    gl_ctx = video.SDL_GL_CreateContext(window)
    if not gl_ctx:
        video.SDL_DestroyWindow(window)
        raise RuntimeError(f"SDL_GL_CreateContext failed: {sdl2.SDL_GetError()}")

    video.SDL_GL_MakeCurrent(window, gl_ctx)
    video.SDL_GL_SetSwapInterval(1)
    return window, gl_ctx


def get_drawable_size(window):
    w, h = ctypes.c_int(), ctypes.c_int()
    video.SDL_GL_GetDrawableSize(window, ctypes.byref(w), ctypes.byref(h))
    return w.value, h.value


_KEY_MAP = {
    sdl2.SDL_SCANCODE_BACKSPACE: Key.BACKSPACE,
    sdl2.SDL_SCANCODE_DELETE: Key.DELETE,
    sdl2.SDL_SCANCODE_LEFT: Key.LEFT,
    sdl2.SDL_SCANCODE_RIGHT: Key.RIGHT,
    sdl2.SDL_SCANCODE_UP: Key.UP,
    sdl2.SDL_SCANCODE_DOWN: Key.DOWN,
    sdl2.SDL_SCANCODE_HOME: Key.HOME,
    sdl2.SDL_SCANCODE_END: Key.END,
    sdl2.SDL_SCANCODE_RETURN: Key.ENTER,
    sdl2.SDL_SCANCODE_ESCAPE: Key.ESCAPE,
    sdl2.SDL_SCANCODE_TAB: Key.TAB,
    sdl2.SDL_SCANCODE_SPACE: Key.SPACE,
}


def translate_key(scancode: int) -> int:
    if scancode in _KEY_MAP:
        return _KEY_MAP[scancode]
    keycode = sdl2.SDL_GetKeyFromScancode(scancode)
    if 0 <= keycode < 128:
        try:
            return Key(keycode)
        except ValueError:
            pass
    return Key.UNKNOWN


def translate_mods(sdl_mods: int) -> int:
    result = 0
    if sdl_mods & (sdl2.KMOD_LSHIFT | sdl2.KMOD_RSHIFT):
        result |= Mods.SHIFT.value
    if sdl_mods & (sdl2.KMOD_LCTRL | sdl2.KMOD_RCTRL):
        result |= Mods.CTRL.value
    if sdl_mods & (sdl2.KMOD_LALT | sdl2.KMOD_RALT):
        result |= Mods.ALT.value
    return result


_SDL_BUTTON_MAP = {
    1: MouseButton.LEFT,
    2: MouseButton.MIDDLE,
    3: MouseButton.RIGHT,
}


def translate_button(sdl_button: int) -> MouseButton:
    return _SDL_BUTTON_MAP.get(sdl_button, MouseButton.LEFT)


# --- Tab pages ---

def make_progress_page():
    """Page with ProgressBar widgets."""
    page = VStack()
    page.spacing = 12
    page.alignment = "left"

    title = Label()
    title.text = "ProgressBar"
    title.font_size = 18
    title.color = (1, 1, 1, 1)
    page.add_child(title)

    # Basic progress bar
    pb1 = ProgressBar()
    pb1.value = 0.65
    pb1.preferred_width = px(350)
    pb1.preferred_height = px(20)
    page.add_child(pb1)

    # Progress bar with text
    pb2 = ProgressBar()
    pb2.value = 0.42
    pb2.show_text = True
    pb2.preferred_width = px(350)
    pb2.preferred_height = px(24)
    pb2.fill_color = (0.2, 0.8, 0.4, 1.0)
    page.add_child(pb2)

    # Slider to control progress
    info = Label()
    info.text = "Drag the slider to change progress:"
    info.font_size = 13
    info.color = (0.6, 0.6, 0.6, 1.0)
    page.add_child(info)

    slider = Slider()
    slider.preferred_width = px(350)
    slider.value = 0.65
    page.add_child(slider)

    def on_slider(val):
        pb1.value = val
        pb2.value = val

    slider.on_change = on_slider

    return page


def make_slider_page():
    """Page with Slider widgets."""
    page = VStack()
    page.spacing = 14
    page.alignment = "left"

    title = Label()
    title.text = "Slider"
    title.font_size = 18
    title.color = (1, 1, 1, 1)
    page.add_child(title)

    # Continuous slider
    lbl1 = Label()
    lbl1.text = "Continuous: 0.50"
    lbl1.font_size = 13
    lbl1.color = (0.8, 0.8, 0.8, 1.0)
    page.add_child(lbl1)

    s1 = Slider()
    s1.value = 0.5
    s1.preferred_width = px(350)
    s1.on_change = lambda v: setattr(lbl1, 'text', f"Continuous: {v:.2f}")
    page.add_child(s1)

    # Stepped slider (0-100, step 10)
    lbl2 = Label()
    lbl2.text = "Stepped (0-100, step 10): 50"
    lbl2.font_size = 13
    lbl2.color = (0.8, 0.8, 0.8, 1.0)
    page.add_child(lbl2)

    s2 = Slider()
    s2.min_value = 0
    s2.max_value = 100
    s2.step = 10
    s2.value = 50
    s2.preferred_width = px(350)
    s2.fill_color = (0.9, 0.5, 0.2, 1.0)
    s2.on_change = lambda v: setattr(lbl2, 'text', f"Stepped (0-100, step 10): {int(v)}")
    page.add_child(s2)

    # Color slider
    lbl3 = Label()
    lbl3.text = "Color mix slider"
    lbl3.font_size = 13
    lbl3.color = (0.8, 0.8, 0.8, 1.0)
    page.add_child(lbl3)

    s3 = Slider()
    s3.preferred_width = px(350)
    s3.fill_color = (0.8, 0.2, 0.2, 1.0)
    s3.thumb_color = (1.0, 0.4, 0.4, 1.0)
    page.add_child(s3)

    return page


def make_scroll_page():
    """Page with ScrollArea demonstration."""
    page = VStack()
    page.spacing = 12
    page.alignment = "left"

    title = Label()
    title.text = "ScrollArea"
    title.font_size = 18
    title.color = (1, 1, 1, 1)
    page.add_child(title)

    info = Label()
    info.text = "Scroll with mouse wheel or drag scrollbar:"
    info.font_size = 13
    info.color = (0.6, 0.6, 0.6, 1.0)
    page.add_child(info)

    # ScrollArea wrapping a tall VStack
    scroll = ScrollArea()
    scroll.preferred_width = px(380)
    scroll.preferred_height = px(250)

    content = VStack()
    content.spacing = 6
    content.alignment = "left"

    for i in range(30):
        lbl = Label()
        lbl.text = f"  Item {i + 1} — scrollable content line"
        lbl.font_size = 14
        lbl.color = (0.85, 0.85, 0.9, 1.0)
        content.add_child(lbl)

    scroll.add_child(content)
    page.add_child(scroll)

    return page


def make_spinbox_page():
    """Page with SpinBox and SliderEdit widgets."""
    page = VStack()
    page.spacing = 14
    page.alignment = "left"

    title = Label()
    title.text = "SpinBox & SliderEdit"
    title.font_size = 18
    title.color = (1, 1, 1, 1)
    page.add_child(title)

    # SpinBox: integer
    lbl1 = Label()
    lbl1.text = "Integer SpinBox (0-100, step 1):"
    lbl1.font_size = 13
    lbl1.color = (0.8, 0.8, 0.8, 1.0)
    page.add_child(lbl1)

    sb1 = SpinBox()
    sb1.value = 42
    sb1.min_value = 0
    sb1.max_value = 100
    sb1.step = 1
    sb1.decimals = 0
    sb1.preferred_width = px(150)
    page.add_child(sb1)

    # SpinBox: float
    lbl2 = Label()
    lbl2.text = "Float SpinBox (0.0-1.0, step 0.05):"
    lbl2.font_size = 13
    lbl2.color = (0.8, 0.8, 0.8, 1.0)
    page.add_child(lbl2)

    sb2 = SpinBox()
    sb2.value = 0.5
    sb2.min_value = 0.0
    sb2.max_value = 1.0
    sb2.step = 0.05
    sb2.decimals = 2
    sb2.preferred_width = px(150)
    page.add_child(sb2)

    # SliderEdit
    lbl3 = Label()
    lbl3.text = "SliderEdit (0-100):"
    lbl3.font_size = 13
    lbl3.color = (0.8, 0.8, 0.8, 1.0)
    page.add_child(lbl3)

    se = SliderEdit()
    se.value = 42
    se.min_value = 0
    se.max_value = 100
    se.step = 1
    se.decimals = 0
    se.preferred_width = px(380)
    page.add_child(se)

    # Status label
    status = Label()
    status.text = "SpinBox: 42 | SliderEdit: 42"
    status.font_size = 12
    status.color = (0.6, 0.6, 0.6, 1.0)
    page.add_child(status)

    def update_status(*_):
        status.text = f"SpinBox: {sb1._format_value()} | SliderEdit: {se.value:.0f}"

    sb1.on_change = update_status
    se.on_change = update_status

    return page


def make_textarea_page():
    """Page with TextArea widget."""
    page = VStack()
    page.spacing = 14
    page.alignment = "left"

    title = Label()
    title.text = "TextArea"
    title.font_size = 18
    title.color = (1, 1, 1, 1)
    page.add_child(title)

    info = Label()
    info.text = "Multi-line text editor:"
    info.font_size = 13
    info.color = (0.6, 0.6, 0.6, 1.0)
    page.add_child(info)

    ta = TextArea()
    ta.preferred_width = px(400)
    ta.preferred_height = px(200)
    ta.placeholder = "Type here..."
    ta.text = "Line 1: Hello, TextArea!\nLine 2: Multi-line editing.\nLine 3: Arrow keys, Enter, Backspace.\nLine 4: Scroll with mouse wheel."
    page.add_child(ta)

    # Line counter
    counter = Label()
    counter.text = f"Lines: {len(ta._lines)} | Chars: {len(ta.text)}"
    counter.font_size = 12
    counter.color = (0.6, 0.6, 0.6, 1.0)
    page.add_child(counter)

    def on_text_change(text):
        counter.text = f"Lines: {len(ta._lines)} | Chars: {len(text)}"

    ta.on_change = on_text_change

    return page


def make_groupbox_page():
    """Page with GroupBox widgets."""
    page = VStack()
    page.spacing = 14
    page.alignment = "left"

    title = Label()
    title.text = "GroupBox"
    title.font_size = 18
    title.color = (1, 1, 1, 1)
    page.add_child(title)

    info = Label()
    info.text = "Collapsible sections (click title to toggle):"
    info.font_size = 13
    info.color = (0.6, 0.6, 0.6, 1.0)
    page.add_child(info)

    # GroupBox 1
    gb1 = GroupBox()
    gb1.title = "Model Parameters"
    gb1.preferred_width = px(400)

    content1 = VStack()
    content1.spacing = 8
    content1.alignment = "left"
    for name, val in [("Learning rate", "0.001"), ("Batch size", "32"), ("Epochs", "100")]:
        row = HStack()
        row.spacing = 8
        row.alignment = "center"
        lbl = Label()
        lbl.text = f"{name}:"
        lbl.font_size = 13
        lbl.color = (0.8, 0.8, 0.8, 1.0)
        row.add_child(lbl)
        val_lbl = Label()
        val_lbl.text = val
        val_lbl.font_size = 13
        val_lbl.color = (0.5, 0.8, 1.0, 1.0)
        row.add_child(val_lbl)
        content1.add_child(row)
    gb1.add_child(content1)
    page.add_child(gb1)

    # GroupBox 2 (collapsed by default)
    gb2 = GroupBox()
    gb2.title = "Advanced Settings"
    gb2.expanded = False
    gb2.preferred_width = px(400)

    content2 = VStack()
    content2.spacing = 8
    content2.alignment = "left"
    adv_lbl = Label()
    adv_lbl.text = "Advanced options would go here."
    adv_lbl.font_size = 13
    adv_lbl.color = (0.7, 0.7, 0.7, 1.0)
    content2.add_child(adv_lbl)
    gb2.add_child(content2)
    page.add_child(gb2)

    return page


# --- UI ---

def build_ui(graphics):
    root = Panel()
    root.preferred_width = pct(100)
    root.preferred_height = pct(100)
    root.background_color = (0.12, 0.12, 0.14, 1.0)
    root.padding = 20

    layout = VStack()
    layout.spacing = 16
    layout.alignment = "left"

    # Title
    title = Label()
    title.text = "tcgui Widget Showcase"
    title.font_size = 24
    title.color = (1, 1, 1, 1)
    layout.add_child(title)

    # TabView with all demos
    tabs = TabView()
    tabs.preferred_width = px(550)
    tabs.preferred_height = px(450)

    tabs.add_tab("Progress", make_progress_page())
    tabs.add_tab("Slider", make_slider_page())
    tabs.add_tab("Scroll", make_scroll_page())
    tabs.add_tab("SpinBox", make_spinbox_page())
    tabs.add_tab("TextArea", make_textarea_page())
    tabs.add_tab("GroupBox", make_groupbox_page())

    layout.add_child(tabs)
    root.add_child(layout)

    ui = UI(graphics)
    ui.root = root
    return ui


# --- Main ---

def main():
    window, gl_ctx = create_window("tcgui — Widget Showcase", 700, 600)

    graphics = OpenGLGraphicsBackend.get_instance()
    graphics.ensure_ready()

    ui = build_ui(graphics)

    sdl2.SDL_StartTextInput()
    event = sdl2.SDL_Event()
    running = True

    def dispatch(ev):
        nonlocal running
        t = ev.type
        if t == sdl2.SDL_QUIT:
            running = False
        elif t == sdl2.SDL_WINDOWEVENT:
            if ev.window.event == video.SDL_WINDOWEVENT_CLOSE:
                running = False
        elif t == sdl2.SDL_MOUSEMOTION:
            ui.mouse_move(float(ev.motion.x), float(ev.motion.y))
        elif t == sdl2.SDL_MOUSEBUTTONDOWN:
            ui.mouse_down(float(ev.button.x), float(ev.button.y), translate_button(ev.button.button))
        elif t == sdl2.SDL_MOUSEBUTTONUP:
            ui.mouse_up(float(ev.button.x), float(ev.button.y))
        elif t == sdl2.SDL_MOUSEWHEEL:
            mx, my = ctypes.c_int(), ctypes.c_int()
            sdl2.SDL_GetMouseState(ctypes.byref(mx), ctypes.byref(my))
            ui.mouse_wheel(float(ev.wheel.x), float(ev.wheel.y), float(mx.value), float(my.value))
        elif t == sdl2.SDL_KEYDOWN:
            key = translate_key(ev.key.keysym.scancode)
            mods = translate_mods(sdl2.SDL_GetModState())
            ui.key_down(key, mods)
        elif t == sdl2.SDL_TEXTINPUT:
            ui.text_input(ev.text.text.decode("utf-8"))

    while running:
        if sdl2.SDL_WaitEventTimeout(ctypes.byref(event), 500):
            dispatch(event)
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                dispatch(event)

        if not running:
            break

        vw, vh = get_drawable_size(window)
        graphics.bind_framebuffer(None)
        graphics.set_viewport(0, 0, vw, vh)
        graphics.clear_color_depth(0.12, 0.12, 0.14, 1.0)

        ui.render(vw, vh)

        video.SDL_GL_SwapWindow(window)

    video.SDL_GL_DeleteContext(gl_ctx)
    video.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()


if __name__ == "__main__":
    main()
