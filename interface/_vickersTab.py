import dearpygui.dearpygui as dpg
from config import get_config, get_preference, hex_to_rgba
from config.user_preferences import save_preference


def showVickersTab(callbacks, fonts):
    """
    Create and configure the image processing tab UI.
    This function sets up the processing tab interface with two main sections:
    1. A control panel (left side) containing file selection, processing mode options,
        and Vickers hardness test parameters.
    2. A plot area (right side) for displaying and interacting with images.
    Args:
         callbacks: Object containing callback functions for UI interactions, including:
              - callbacks.imageProcessing.openFile: Handle file selection
              - callbacks.imageProcessing.cancelImportImage: Handle file dialog cancellation
              - callbacks.imageProcessing.onProcessingModeChange: Handle processing mode changes
              - callbacks.imageProcessing.onCalibrationChange: Handle calibration value changes
              - callbacks.imageProcessing.onPlotClick: Handle mouse clicks on the plot
         fonts: Dictionary containing font objects for UI text styling, including:
              - fonts["bold"]: Bold font for headers and labels
    The control panel includes:
         - File dialog for image import (supports .jpg, .png, .jpeg, .bmp formats)
         - Image file name and path display
         - Processing mode radio buttons ("Marcar Puntos", "Mover Imagen")
         - Vickers hardness test parameters (calibration and load inputs)
    The plot area provides:
         - Interactive plot with pan and zoom capabilities
         - Equal aspect ratio for accurate measurements
         - Axis labels in micrometers (µm)
         - Mouse click handler for placing measurement points
    Configuration is loaded from the application's config file using get_config().
    User preferences for Vickers parameters are persisted using get_preference() and
    save_preference() functions.
    """
    config = get_config()
    
    # Use last project folder or fallback to current directory
    default_image_path = get_preference("last_project_folder", default=".")

    with dpg.group(horizontal=True):

        # ============ Child Window #1: CONTROLS ============
        with dpg.child_window(width=config["UI.ProcessingTab"]["controls_width"], tag="ProcessingControlsChild"):

            with dpg.file_dialog(
                directory_selector=False,
                min_size=[config["UI.FileDialog"]["min_width"], config["UI.FileDialog"]["min_height"]],
                show=False,
                tag="file_dialog_id",
                callback=callbacks.imageProcessing.openFile,
                cancel_callback=callbacks.imageProcessing.cancelImportImage,
                default_path=default_image_path,
            ):
                dpg.add_file_extension("", color=hex_to_rgba(config["UI.FileDialog.Colors"]["default_file"]))
                dpg.add_file_extension(".*")
                dpg.add_file_extension(".jpg", color=hex_to_rgba(config["UI.FileDialog.Colors"]["jpg_file"]))
                dpg.add_file_extension(".png", color=hex_to_rgba(config["UI.FileDialog.Colors"]["png_file"]))
                dpg.add_file_extension(".jpeg", color=hex_to_rgba(config["UI.FileDialog.Colors"]["jpeg_file"]))
                dpg.add_file_extension(".bmp", color=hex_to_rgba(config["UI.FileDialog.Colors"]["bmp_file"]))

            dpg.add_text(config["UI.Labels"]["select_image_prompt"], tag="select_image_prompt_text", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("select_image_prompt_text", fonts["bold"])

            dpg.add_button(
                tag="import_image", width=-1, label=config["UI.Labels"]["import_button"], callback=lambda: dpg.show_item("file_dialog_id")
            )
            dpg.add_text("Archivo: ", tag="file_name_text")
            dpg.add_text("Ruta: ", tag="file_path_text")

            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            dpg.add_text("Botón Izquierdo:", tag="title1_text", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("title1_text", fonts["bold"])
            dpg.add_radio_button(
                items=["Marcar Puntos", "Mover Imagen"],
                tag="processing_mode_radio",
                horizontal=True,
                default_value="Marcar Puntos",
                callback=callbacks.imageProcessing.onProcessingModeChange,
            )

            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            dpg.add_text("Parámetros Vickers", tag="title2_text", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("title2_text", fonts["bold"])

            # input text (float): Calibración (µm/pixel)
            dpg.add_input_float(
                label="Escala (µm/pixel)",
                tag="vickers_calibration_input",
                default_value=get_preference("vickers_calibration", default=1.0),
                min_value=0.0001,
                min_clamped=True,
                width=200,
                format="%.6f",
                callback=callbacks.imageProcessing.onCalibrationChange,
            )

            # input text (float): Carga aplicada (g)
            dpg.add_input_float(
                label="Carga Aplicada (g)",
                tag="vickers_load_input",
                default_value=get_preference("vickers_load", default=500.0),
                min_value=0.1,
                min_clamped=True,
                width=200,
                format="%.2f",
                callback=lambda s, v: save_preference("vickers_load", v),
            )

            # input int: Número de mediciones
            dpg.add_input_int(
                label="Mediciones [1-10]",
                tag="vickers_n_measurements_input",
                default_value=get_preference("vickers_n_measurements", default=2),
                min_value=1,
                max_value=10,
                min_clamped=True,
                max_clamped=True,
                width=200,
                callback=callbacks.imageProcessing.onNMeasurementsChange,
            )

            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            with dpg.group(horizontal=True):
                dpg.add_text("Mediciones", tag="title3_text", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
                dpg.bind_item_font("title3_text", fonts["bold"])

                dpg.add_spacer(width=20)

                dpg.add_spacer(height=5)
                dpg.add_button(
                    tag="reset_measurements_button",
                    # width=-1,
                    label="Reiniciar",
                    callback=callbacks.imageProcessing.resetMeasurementsButton
                )

            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_text("Medición Actual:")
                dpg.add_text("0/1", tag="vickers_current_measurement", color=hex_to_rgba(config["UI.Colors"]["green_text"]))
            dpg.bind_item_font("vickers_current_measurement", fonts["bold"])

            with dpg.group(horizontal=True, horizontal_spacing=20):
                dpg.add_text("Puntos:")
                dpg.add_text("0/4", tag="vickers_npoints", color=hex_to_rgba(config["UI.Colors"]["green_text"]))
            dpg.bind_item_font("vickers_npoints", fonts["bold"])
            
            # Child window with scroll for measurements table
            with dpg.child_window(height=120, border=True, tag="measurements_scroll"):
                with dpg.table(tag="measurements_table", header_row=True, borders_innerH=True, borders_outerH=True,
                              borders_innerV=True, borders_outerV=True, row_background=True):
                    dpg.add_table_column(label="Med", width_fixed=True, init_width_or_weight=40)
                    dpg.add_table_column(label="Puntos", width_fixed=True, init_width_or_weight=60)
                    dpg.add_table_column(label="D1 (µm)")
                    dpg.add_table_column(label="D2 (µm)")
                    dpg.add_table_column(label="Dprom (µm)")
            
            dpg.add_spacer(height=5)
            
            # Summary section with averages
            with dpg.group(tag="measurements_summary"):
                # Title for completed measurements - yellow text, h1 font
                dpg.add_text("PROMEDIOS FINALES", tag="promedios_finales_text", show=False, color=hex_to_rgba(config["UI.Colors"]["yellow_text"]))
                dpg.bind_item_font("promedios_finales_text", fonts["h1"])
                
                dpg.add_text("D1 promedio: N/A", tag="vickers_d1_avg_text")
                dpg.add_text("D2 promedio: N/A", tag="vickers_d2_avg_text")
                dpg.add_text("D final: N/A", tag="vickers_diagonal_avg_text")
            
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            dpg.add_text("Resultados", tag="title4_text", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("title4_text", fonts["bold"])

            # Result display with border
            with dpg.child_window(height=100, border=True):
                # dpg.add_spacer(height=5)
                with dpg.group():
                    with dpg.group(horizontal=True, horizontal_spacing=20):
                        dpg.add_text("Dureza Vickers:", tag="vickers_hardness_label")
                        dpg.bind_item_font("vickers_hardness_label", fonts["bold"])
                        dpg.add_text("N/A", tag="vickers_hardness_value", color=hex_to_rgba(config["UI.Colors"]["green_text"]))
                        dpg.bind_item_font("vickers_hardness_value", fonts["h1"])
                    # dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True, horizontal_spacing=20):
                        dpg.add_text("Desviación Estándar:", tag="vickers_std_label")
                        dpg.bind_item_font("vickers_std_label", fonts["bold"])
                        dpg.add_text("N/A", tag="vickers_std_value", color=hex_to_rgba(config["UI.Colors"]["green_text"]))
            
            dpg.add_spacer(height=10)
            
            # Navigation buttons for data table points
            with dpg.group(horizontal=True, horizontal_spacing=10):
                dpg.add_button(
                    tag="prev_point_button",
                    width=185,
                    label="PREVIO",
                    callback=callbacks.imageProcessing.loadPreviousPoint
                )
                dpg.add_button(
                    tag="next_point_button",
                    width=185,
                    label="SIGUIENTE",
                    callback=callbacks.imageProcessing.loadNextPoint
                )
            
            

            

        # ============ Child Window #2: PLOT AREA ============
        with dpg.group():
            with dpg.child_window(tag="ProcessingParent", height=-50, width=-1):
                # Create theme for plot styling (thicker lines and larger markers)
                with dpg.theme(tag="plot_theme"):
                    with dpg.theme_component(dpg.mvLineSeries):
                        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 3, category=dpg.mvThemeCat_Plots)
                    with dpg.theme_component(dpg.mvScatterSeries):
                        dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                        dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 8, category=dpg.mvThemeCat_Plots)
                
                with dpg.plot(
                    tag="ProcessingPlotParent",
                    label=config["UI.Labels"]["plot_title"],
                    height=-1,
                    width=-1,
                    equal_aspects=True,
                    pan_button=dpg.mvMouseButton_Left,
                    query=True,
                ):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Ancho (µm)", tag="Processing_x_axis", no_gridlines=False)
                    dpg.add_plot_axis(dpg.mvYAxis, label="Alto (µm)", tag="Processing_y_axis", no_gridlines=False)
                    
                    # Apply theme to plot
                    dpg.bind_item_theme("ProcessingPlotParent", "plot_theme")
            
            # ============ Image Controls Area ============
            with dpg.group(horizontal=True, horizontal_spacing=10):
                with dpg.child_window(tag="image_buttons", height=-1, width=-120, border=False):
                    with dpg.group(horizontal=True, horizontal_spacing=10, indent=10):
                        dpg.add_button(label="B/W", tag="bw_button", width=100, height=40, callback=callbacks.imageProcessing.convertToBlackAndWhite)
                        dpg.add_button(label="Invert", tag="invert_button", width=100, height=40, callback=callbacks.imageProcessing.invertImage)
                        dpg.add_button(label="Reset", tag="reset_image_button", width=100, height=40, callback=callbacks.imageProcessing.resetImageToOriginal)

                with dpg.child_window(tag="exit_button", height=-1, width=-1, border=False):
                    # Create theme for exit button (red background)
                    with dpg.theme(tag="exit_button_theme"):
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_color(dpg.mvThemeCol_Button, (180, 0, 0, 255))
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (220, 0, 0, 255))
                            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (140, 0, 0, 255))
                    
                    dpg.add_button(label="Exit", tag="btnExit", width=100, height=40, callback=lambda: dpg.stop_dearpygui())
                    dpg.bind_item_theme("btnExit", "exit_button_theme")
                    dpg.bind_item_font("btnExit", fonts["bold"])
                

    # Create modal popup for waiting message between measurements
    with dpg.window(label="", modal=True, show=False, tag="waiting_popup", no_title_bar=True, 
                    no_resize=True, no_move=True, no_close=True, pos=[400, 300]):
        with dpg.group(horizontal=False):
            dpg.add_spacer(height=20)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                dpg.add_text("", tag="waiting_popup_text", wrap=0, color=hex_to_rgba(config["UI.Colors"]["green_text"]))
                dpg.bind_item_font("waiting_popup_text", fonts["h1"])
            dpg.add_spacer(height=20)

    # Register global mouse click handler for Vickers measurement (outside the group context)
    with dpg.handler_registry():
        dpg.add_mouse_click_handler(button=0, callback=callbacks.imageProcessing.onPlotClick)
