import dearpygui.dearpygui as dpg
from config import get_config


def applyTheme():
    config = get_config()

    with dpg.theme() as global_theme:
        with dpg.theme_component(0):
            # Main Styles
            dpg.add_theme_style(
                dpg.mvStyleVar_WindowPadding, config["Theme.Padding"]["window_padding_x"], config["Theme.Padding"]["window_padding_y"]
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FramePadding, config["Theme.Padding"]["frame_padding_x"], config["Theme.Padding"]["frame_padding_y"]
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_CellPadding, config["Theme.Padding"]["cell_padding_x"], config["Theme.Padding"]["cell_padding_y"]
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_ItemSpacing, config["Theme.Spacing"]["item_spacing_x"], config["Theme.Spacing"]["item_spacing_y"]
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_ItemInnerSpacing,
                config["Theme.Spacing"]["item_inner_spacing_x"],
                config["Theme.Spacing"]["item_inner_spacing_y"],
            )
            dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing, config["Theme.Spacing"]["indent_spacing"])
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, config["Theme.Sizes"]["scrollbar_size"])
            dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, config["Theme.Sizes"]["grab_min_size"])

            # Border Styles
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, config["Theme.Borders"]["window_border_size"])
            dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, config["Theme.Borders"]["popup_border_size"])
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, config["Theme.Borders"]["frame_border_size"])

            # Rounding Style
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, config["Theme.Rounding"]["window_rounding"])
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, config["Theme.Rounding"]["child_rounding"])
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, config["Theme.Rounding"]["frame_rounding"])
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, config["Theme.Rounding"]["popup_rounding"])
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, config["Theme.Rounding"]["scrollbar_rounding"])
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, config["Theme.Rounding"]["grab_rounding"])
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, config["Theme.Rounding"]["tab_rounding"])

    dpg.bind_theme(global_theme)

    # add font to registry
    with dpg.font_registry():
        # first argument ids the path to the .ttf or .otf file
        default_font = dpg.add_font(config["Fonts"]["default_font_path"], config["Fonts"]["default_font_size"])
        italic_font = dpg.add_font(config["Fonts"]["italic_font_path"], config["Fonts"]["italic_font_size"])
        bold_font = dpg.add_font(config["Fonts"]["bold_font_path"], config["Fonts"]["bold_font_size"])
        h1_font = dpg.add_font(config["Fonts"]["h1_font_path"], config["Fonts"]["h1_font_size"])
        # Use h1_font as title_font for now (safe fallback)
        title_font = h1_font
        # dpg.show_font_manager()

    # set global font
    dpg.bind_font(default_font)

    return {"default": default_font, "italic": italic_font, "bold": bold_font, "h1": h1_font, "title": title_font}
