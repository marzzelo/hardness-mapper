import dearpygui.dearpygui as dpg
from config import get_config, get_preference, hex_to_rgba


def showMappingTab(callbacks, fonts):
    """
    Create and configure the heat map tab UI.
    This function sets up the heat map tab interface with two main sections:
    1. A control panel (left side) for heat map configuration and controls.
    2. A display area (right side) for visualizing the heat map.
    
    Args:
        callbacks: Object containing callback functions for UI interactions.
        fonts: Dictionary containing font objects for UI text styling.
    
    Configuration is loaded from the application's config file using get_config().
    """
    config = get_config()
    
    # Use last project folder or fallback to current directory
    default_image_path = get_preference("last_project_folder", default=".")

    with dpg.group(horizontal=True):
        
        # ============ Child Window #1: CONTROLS ============
        with dpg.child_window(width=config["UI.ProcessingTab"]["controls_width"], tag="HeatMapControlsChild"):
            
            with dpg.file_dialog(
                directory_selector=False,
                min_size=[config["UI.FileDialog"]["min_width"], config["UI.FileDialog"]["min_height"]],
                show=False,
                tag="heatmap_file_dialog_id",
                callback=callbacks.heatMap.openFile,
                cancel_callback=callbacks.heatMap.cancelImportImage,
                default_path=default_image_path,
            ):
                dpg.add_file_extension("", color=hex_to_rgba(config["UI.FileDialog.Colors"]["default_file"]))
                dpg.add_file_extension(".*")
                dpg.add_file_extension(".jpg", color=hex_to_rgba(config["UI.FileDialog.Colors"]["jpg_file"]))
                dpg.add_file_extension(".png", color=hex_to_rgba(config["UI.FileDialog.Colors"]["png_file"]))
                dpg.add_file_extension(".jpeg", color=hex_to_rgba(config["UI.FileDialog.Colors"]["jpeg_file"]))
                dpg.add_file_extension(".bmp", color=hex_to_rgba(config["UI.FileDialog.Colors"]["bmp_file"]))

            dpg.add_text("Seleccionar Imagen de Superficie", tag="heatmap_select_image_text", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("heatmap_select_image_text", fonts["bold"])

            dpg.add_button(
                tag="heatmap_import_image", 
                width=-1, 
                label="Importar Imagen", 
                callback=lambda: dpg.show_item("heatmap_file_dialog_id")
            )
            dpg.add_text("Archivo: ", tag="heatmap_file_name_text")
            dpg.add_text("Ruta: ", tag="heatmap_file_path_text")

            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            dpg.add_text("Parámetros", tag="heatmap_params_title", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("heatmap_params_title", fonts["bold"])

            # Calibration input
            dpg.add_input_float(
                label="Escala (mm/pixel)",
                tag="heatmap_calibration_input",
                default_value=get_preference("heatmap_calibration", default=0.001),
                min_value=0.000001,
                min_clamped=True,
                width=200,
                format="%.6f",
                callback=callbacks.heatMap.onCalibrationChange,
            )
            
            # Calibrate and Set Origin buttons
            with dpg.group(horizontal=True, horizontal_spacing=5):
                dpg.add_button(
                    label="Calibrar Escala",
                    tag="heatmap_calibrate_button",
                    width=185,
                    callback=callbacks.heatMap.startCalibration
                )
                dpg.add_button(
                    label="Set (0,0)",
                    tag="heatmap_set_origin_button",
                    width=185,
                    callback=callbacks.heatMap.startSetOrigin
                )

            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Botón Izquierdo section
            dpg.add_text("Botón Izquierdo", color=hex_to_rgba(config["UI.Colors"]["green_text"]))
            dpg.bind_item_font(dpg.last_item(), fonts["bold"])
            
            dpg.add_radio_button(
                items=["Marcar Puntos", "Mover Imagen"],
                tag="heatmap_mode_radio",
                horizontal=True,
                default_value="Marcar Puntos",
                callback=callbacks.heatMap.onModeChange,
            )
            
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            dpg.add_text("Puntos de Medición", tag="heatmap_points_title", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("heatmap_points_title", fonts["bold"])

            with dpg.group(horizontal=True):
                dpg.add_button(
                    tag="heatmap_reset_points_button",
                    label="Reset Points",
                    callback=callbacks.heatMap.resetPoints
                )
                dpg.add_spacer(width=5)
                dpg.add_button(
                    tag="heatmap_restart_button",
                    label="Reset All",
                    callback=callbacks.heatMap.restartHeatMap
                )

            dpg.add_text("Total: 0 puntos", tag="heatmap_point_count", color=hex_to_rgba(config["UI.Colors"]["green_text"]))
            dpg.bind_item_font("heatmap_point_count", fonts["bold"])

            dpg.add_spacer(height=5)

            # Points table with scroll
            with dpg.child_window(height=400, border=True, tag="heatmap_points_scroll"):
                with dpg.table(tag="heatmap_points_table", header_row=True, borders_innerH=True, borders_outerH=True,
                              borders_innerV=True, borders_outerV=True, row_background=True):
                    dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=60)
                    dpg.add_table_column(label="X (mm)")
                    dpg.add_table_column(label="Y (mm)")

            dpg.add_spacer(height=10)

            dpg.add_text("Instrucciones:", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.add_text("- Modo Marcar Puntos: Click para marcar", wrap=250)
            dpg.add_text("- Modo Mover Imagen: Click para hacer pan", wrap=250)
            dpg.add_text("- Los puntos se identifican como P1, P2, etc.", wrap=250)
            
            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Save mapping image button
            dpg.add_button(
                label="Guardar Imagen del Mapeado",
                tag="heatmap_save_image_button",
                width=-1,
                callback=callbacks.heatMap.saveMappingImageManual
            )

        # ============ Child Window #2: PLOT AREA ============
        with dpg.group():
            with dpg.child_window(tag="HeatMapParent", height=-50, width=-1):
                # Create theme for plot styling
                with dpg.theme(tag="heatmap_plot_theme"):
                    with dpg.theme_component(dpg.mvLineSeries):
                        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 3, category=dpg.mvThemeCat_Plots)
                    with dpg.theme_component(dpg.mvScatterSeries):
                        dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                        dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 8, category=dpg.mvThemeCat_Plots)
                
                with dpg.plot(
                    tag="HeatMapPlotParent",
                    label="Mapa de Calor - Superficie",
                    height=-1,
                    width=-1,
                    equal_aspects=True,
                    pan_button=dpg.mvMouseButton_Right,  # Right button for pan by default
                    query=True,  # Enable query for click detection
                ):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Ancho (mm)", tag="HeatMap_x_axis", no_gridlines=False)
                    dpg.add_plot_axis(dpg.mvYAxis, label="Alto (mm)", tag="HeatMap_y_axis", no_gridlines=False)
                    
                    # Apply theme to plot
                    dpg.bind_item_theme("HeatMapPlotParent", "heatmap_plot_theme")
            
            # ============ Image Controls Area ============
            with dpg.group(horizontal=True, horizontal_spacing=10):
                with dpg.child_window(tag="heatmap_controls_area", height=-1, width=-1, border=False):
                    with dpg.group(horizontal=True, horizontal_spacing=10, indent=10):
                        dpg.add_text("Haga click izquierdo sobre la imagen para marcar los puntos de medición")

    # Create modal popup for calibration
    with dpg.window(label="Calibración de Escala", modal=True, show=False, tag="calibration_popup",
                    no_resize=True, no_move=True, pos=[400, 300], width=450, height=200):
        dpg.add_text("Ingrese la distancia real entre los dos puntos marcados:")
        dpg.add_spacer(height=10)
        
        dpg.add_input_float(
            label="Distancia (mm)",
            tag="calibration_distance_input",
            default_value=10.0,
            min_value=0.001,
            min_clamped=True,
            width=200,
            format="%.3f"
        )
        
        dpg.add_spacer(height=20)
        
        with dpg.group(horizontal=True, horizontal_spacing=10):
            dpg.add_button(
                label="Calcular",
                width=100,
                callback=callbacks.heatMap.calculateCalibration
            )
            dpg.add_button(
                label="Cancelar",
                width=100,
                callback=callbacks.heatMap.cancelCalibration
            )

    # Register global mouse click handler for heat map
    with dpg.handler_registry():
        dpg.add_mouse_click_handler(button=0, callback=callbacks.heatMap.onPlotClick)
