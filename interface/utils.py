import dearpygui.dearpygui as dpg
import ctypes


def center_viewport():
    # Center the viewport on screen after showing it
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()

    # Get primary monitor size
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    x_pos = (screen_width - viewport_width) // 2
    y_pos = (screen_height - viewport_height) // 2
    dpg.set_viewport_pos([x_pos, y_pos])
