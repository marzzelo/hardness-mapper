import dearpygui.dearpygui as dpg
from config import get_config, hex_to_rgba


def showDataTableTab(callbacks, fonts):
    """
    Create and configure the data table tab UI.
    This tab displays an editable table with measurement point data including:
    - Point ID, X, Y coordinates (from Heat Map)
    - Hardness HV values
    - Image file paths
    - Links to Vickers tab for calculations
    - Thumbnail images
    
    Args:
        callbacks: Object containing callback functions for UI interactions.
        fonts: Dictionary containing font objects for UI text styling.
    
    Configuration is loaded from the application's config file using get_config().
    """
    config = get_config()

    with dpg.group(horizontal=True):
        
        # ============ Child Window: DATA TABLE ============
        with dpg.child_window(width=-1, height=-1, tag="DataTableChild"):
            
            dpg.add_text("Tabla de Datos de Medición", tag="data_table_title", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font("data_table_title", fonts["h1"])
            
            dpg.add_spacer(height=10)
            
            with dpg.group(horizontal=True, horizontal_spacing=10):
                dpg.add_button(
                    label="Actualizar desde Mapeado",
                    tag="update_from_heatmap_button",
                    callback=callbacks.dataTable.updateFromHeatMap
                )
                dpg.add_button(
                    label="Cargar imágenes default",
                    tag="load_default_images_button",
                    callback=callbacks.dataTable.loadDefaultImages
                )
                            
            dpg.add_spacer(height=10)
            
            # Main data table with scroll
            with dpg.child_window(height=-1, border=True, tag="data_table_scroll"):
                with dpg.table(
                    tag="data_table",
                    header_row=True,
                    borders_innerH=True,
                    borders_outerH=True,
                    borders_innerV=True,
                    borders_outerV=True,
                    row_background=False,
                    scrollY=True,
                    scrollX=True,
                    policy=dpg.mvTable_SizingStretchProp
                ):
                    # Column definitions
                    dpg.add_table_column(label="ID", width_fixed=True, init_width_or_weight=50)
                    dpg.add_table_column(label="X (mm)", width_fixed=True, init_width_or_weight=80)
                    dpg.add_table_column(label="Y (mm)", width_fixed=True, init_width_or_weight=80)
                    dpg.add_table_column(label="HV", width_fixed=True, init_width_or_weight=120)
                    dpg.add_table_column(label="Std Dev", width_fixed=True, init_width_or_weight=100)
                    dpg.add_table_column(label="Ruta Imagen", width_fixed=False, init_width_or_weight=500)
                    dpg.add_table_column(label="Vista Previa", width_fixed=True, init_width_or_weight=180)

