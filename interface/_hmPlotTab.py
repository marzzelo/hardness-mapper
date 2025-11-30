import dearpygui.dearpygui as dpg
from config import get_config, hex_to_rgba


def showHMPlotTab(callbacks, fonts):
    """
    Create and configure the Heat Map Plot tab UI.
    This tab displays a heat map visualization of hardness values
    at the marked points from the Heat Map and Data Table.
    
    Args:
        callbacks: Object containing callback functions for UI interactions.
        fonts: Dictionary containing font objects for UI text styling.
    
    Configuration is loaded from the application's config file using get_config().
    """
    config = get_config()

    with dpg.group(horizontal=True):
        
        # ============ Child Window: LEFT PANEL (Controls) ============
        with dpg.child_window(width=400, height=-1, tag="HMPlotControlsChild"):
            
            dpg.add_text("Mapa de Calor de Durezas", tag="hm_plot_title", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("hm_plot_title", fonts["h1"])
            
            dpg.add_spacer(height=10)
            
            dpg.add_text("Controles del Mapa de Calor", tag="hm_plot_controls_title", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("hm_plot_controls_title", fonts["bold"])
            
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Generate Heat Map buttons
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Mapa Web",
                    tag="generate_web_heatmap_button",
                    width=190,
                    callback=callbacks.hmPlot.generateWebHeatMap
                )
                dpg.add_button(
                    label="Mapa Local",
                    tag="generate_local_heatmap_button",
                    width=190,
                    callback=callbacks.hmPlot.generateLocalHeatMap
                )
            
            dpg.add_spacer(height=5)
            
            # Progress bar (hidden by default)
            dpg.add_progress_bar(
                tag="hm_progress_bar",
                default_value=0.0,
                width=-1,
                show=False
            )
            dpg.add_text(
                "Generando mapa de calor...",
                tag="hm_progress_text",
                show=False,
                color=(150, 200, 255)
            )
            
            dpg.add_spacer(height=10)
            
            # Color scale selector
            dpg.add_text("Escala de Color:")
            dpg.add_combo(
                items=["viridis", "plasma", "inferno", "magma", "cividis", "hot", "cool", "rainbow"],
                default_value="viridis",
                tag="hm_colorscale_combo",
                width=-1,
                callback=callbacks.hmPlot.onColorScaleChange
            )
            
            dpg.add_spacer(height=10)
            
            # Interpolation method
            dpg.add_text("Método de Interpolación:")
            dpg.add_combo(
                items=["linear", "cubic", "nearest"],
                default_value="cubic",
                tag="hm_interpolation_combo",
                width=-1,
                callback=callbacks.hmPlot.onInterpolationChange
            )
            
            dpg.add_spacer(height=10)
            
            # Show points and lines toggles (horizontal)
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label="Mostrar Puntos",
                    tag="hm_show_points_checkbox",
                    default_value=False,
                    callback=callbacks.hmPlot.onShowPointsChange
                )
                dpg.add_spacer(width=20)
                dpg.add_checkbox(
                    label="Líneas",
                    tag="hm_show_lines_checkbox",
                    default_value=False,
                    callback=callbacks.hmPlot.onShowLinesChange
                )
            
            dpg.add_spacer(height=5)
            
            # Surface overlay checkbox
            dpg.add_checkbox(
                label="Img. Overlay",
                tag="hm_show_overlay_checkbox",
                default_value=False,
                callback=callbacks.hmPlot.onShowSurfaceOverlayChange
            )
            
            dpg.add_spacer(height=10)
            
            # Resolution/Smoothness slider
            dpg.add_text("Resolución del Mapa (Suavidad):")
            dpg.add_slider_int(
                default_value=500,
                min_value=50,
                max_value=1000,
                tag="hm_resolution_slider",
                width=-1,
                callback=callbacks.hmPlot.onResolutionChange
            )
            
            dpg.add_spacer(height=10)
            
            # Contour levels slider
            dpg.add_text("Número de Niveles de Color:")
            dpg.add_slider_int(
                default_value=40,
                min_value=5,
                max_value=200,
                tag="hm_levels_slider",
                width=-1,
                callback=callbacks.hmPlot.onLevelsChange
            )
            
            dpg.add_spacer(height=10)
            
            # Figure size slider
            dpg.add_text("Tamaño de la Figura:")
            dpg.add_slider_float(
                default_value=callbacks.hmPlot.figure_scale,
                min_value=0.5,
                max_value=2.0,
                format="%.1fx",
                tag="hm_figsize_slider",
                width=-1,
                callback=callbacks.hmPlot.onFigureSizeChange
            )
            
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            
            # Export button
            dpg.add_button(
                label="Exportar Imagen PNG",
                tag="export_heatmap_button",
                width=-1,
                callback=callbacks.hmPlot.exportHeatMap
            )
            
            dpg.add_spacer(height=10)
            
            # Info text
            dpg.add_text("Información:", tag="hm_plot_info_label", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("hm_plot_info_label", fonts["bold"])
            dpg.add_text("", tag="hm_plot_info_text", wrap=380)
        
        # ============ Child Window: RIGHT PANEL (Heat Map Plot) ============
        with dpg.child_window(width=-1, height=-1, tag="HMPlotDisplayChild"):
            
            # Heat map plot will be added here dynamically
            dpg.add_text("Genere el mapa de calor usando el botón en el panel izquierdo.", 
                        tag="hm_plot_placeholder",
                        wrap=-1)
