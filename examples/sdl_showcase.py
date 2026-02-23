"""Showcase example with all new tcgui widgets.

Demonstrates: ScrollArea, ProgressBar, Slider, TabBar/TabView, mouse wheel.

Requirements: tcbase, tgfx, tcgui, PySDL2
Run: python3 examples/sdl_showcase.py
"""

import ctypes
import sdl2
from sdl2 import video

from tgfx import OpenGLGraphicsBackend
from tcbase import Key

from tcgui.widgets.ui import UI
from tcgui.widgets.basic import Label, Button, ProgressBar, Slider
from tcgui.widgets.containers import VStack, HStack, Panel, ScrollArea
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
        result |= 0x0001
    if sdl_mods & (sdl2.KMOD_LCTRL | sdl2.KMOD_RCTRL):
        result |= 0x0002
    if sdl_mods & (sdl2.KMOD_LALT | sdl2.KMOD_RALT):
        result |= 0x0004
    return result


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
    tabs.preferred_width = px(500)
    tabs.preferred_height = px(400)

    tabs.add_tab("Progress", make_progress_page())
    tabs.add_tab("Slider", make_slider_page())
    tabs.add_tab("Scroll", make_scroll_page())

    layout.add_child(tabs)
    root.add_child(layout)

    ui = UI(graphics)
    ui.root = root
    return ui


# --- Main ---

def main():
    window, gl_ctx = create_window("tcgui — Widget Showcase", 600, 550)

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
            ui.mouse_down(float(ev.button.x), float(ev.button.y))
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
