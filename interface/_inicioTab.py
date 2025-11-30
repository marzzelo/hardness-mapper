import dearpygui.dearpygui as dpg
from config import get_config, hex_to_rgba
from datetime import datetime
import os


def get_app_version():
    """Read version from version.txt file."""
    version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.txt")
    try:
        with open(version_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Unknown"


def showInicioTab(callbacks, fonts):
    """
    Create and configure the Inicio (Home) tab UI.
    This tab contains project information and quick navigation buttons.
    
    Args:
        callbacks: Object containing callback functions for UI interactions.
        fonts: Dictionary containing font objects for UI text styling.
    """
    config = get_config()

    with dpg.group(horizontal=True):
        
        # ============ Left Panel: Project Data ============
        with dpg.child_window(width=500, height=-1, tag="InicioLeftPanel"):
            
            dpg.add_text("Gestión de Proyecto", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font(dpg.last_item(), fonts["h1"])
            
            dpg.add_spacer(height=10)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            # Load/Save/New buttons
            with dpg.group(horizontal=True, horizontal_spacing=10):
                dpg.add_button(
                    label="Nuevo Proyecto",
                    width=150,
                    height=40,
                    callback=callbacks.proyecto.newProject
                )
                dpg.add_button(
                    label="Cargar Proyecto",
                    width=150,
                    height=40,
                    callback=callbacks.proyecto.loadProject
                )
            
            dpg.add_spacer(height=10)
            
            with dpg.group(horizontal=True, horizontal_spacing=10):
                dpg.add_button(
                    label="Guardar Proyecto",
                    width=150,
                    height=40,
                    callback=callbacks.proyecto.saveProject
                )
                dpg.add_button(
                    label="Reporte HTML",
                    width=150,
                    height=40,
                    callback=callbacks.proyecto.generateHTMLReport
                )
            
            dpg.add_spacer(height=20)
            dpg.add_separator()
            dpg.add_spacer(height=20)
            
            # Project Data Section
            dpg.add_text("Datos del Proyecto", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font(dpg.last_item(), fonts["bold"])
            
            dpg.add_spacer(height=10)
            
            # Project Name
            dpg.add_text("Nombre del Proyecto:")
            dpg.add_input_text(
                tag="proyecto_nombre",
                width=-1,
                hint="Ingrese el nombre del proyecto"
            )
            
            dpg.add_spacer(height=10)
            
            # Project Description
            dpg.add_text("Descripción del Proyecto:")
            dpg.add_input_text(
                tag="proyecto_descripcion",
                width=-1,
                height=80,
                multiline=True,
                hint="Ingrese una descripción detallada"
            )
            
            dpg.add_spacer(height=10)
            
            # Request Number
            dpg.add_text("N° de Requerimiento:")
            dpg.add_input_text(
                tag="proyecto_requerimiento",
                width=-1,
                hint="Ej: REQ-2025-001"
            )
            
            dpg.add_spacer(height=10)
            
            # Responsible Technician
            dpg.add_text("Técnico Responsable:")
            dpg.add_input_text(
                tag="proyecto_tecnico",
                width=-1,
                hint="Nombre del técnico"
            )
            
            dpg.add_spacer(height=10)
            
            # Date
            dpg.add_text("Fecha de Realización:")
            default_date = datetime.now().strftime("%Y-%m-%d")
            dpg.add_input_text(
                tag="proyecto_fecha",
                width=-1,
                default_value=default_date,
                hint="YYYY-MM-DD"
            )
        
        # ============ Right Panel: Navigation Buttons ============
        with dpg.child_window(height=-1, width=-1, tag="InicioRightPanel"):
            
            dpg.add_spacer(height=20)
            
            # Main application title with version
            app_version = get_app_version()
            title_item = dpg.add_text(f"VICKERS MAPPING PRO - Versión {app_version}", tag="app_title", 
                                     color=hex_to_rgba(config["UI.Colors"]["yellow_text"]))
            dpg.bind_item_font(title_item, fonts["title"])
            
            dpg.add_spacer(height=10)
            
            # Subtitle - Developer name (will be centered dynamically)
            subtitle_item = dpg.add_text("Laboratorio de Ensayos Estructurales e Investigación de Materiales", 
                                        tag="app_subtitle", color=(255, 255, 255, 255), wrap=-1)
            dpg.bind_item_font(subtitle_item, fonts["bold"])
            
            dpg.add_spacer(height=20)
            dpg.add_separator()
            dpg.add_spacer(height=20)
            
            dpg.add_text("Navegación Rápida", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font(dpg.last_item(), fonts["h1"])
            
            dpg.add_spacer(height=20)
            
            # Create themes for colored buttons
            with dpg.theme(tag="button_theme_mapeado"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (70, 130, 180, 255))  # Steel blue
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (100, 150, 200, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (50, 110, 160, 255))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            
            with dpg.theme(tag="button_theme_tabla"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 179, 113, 255))  # Medium sea green
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (90, 200, 140, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (40, 160, 95, 255))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            
            with dpg.theme(tag="button_theme_vickers"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 140, 0, 255))  # Dark orange
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 165, 50, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (230, 120, 0, 255))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            
            with dpg.theme(tag="button_theme_hmplot"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (148, 0, 211, 255))  # Dark violet
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (170, 50, 230, 255))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (130, 0, 190, 255))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
            
            # Navigation buttons with spacing
            dpg.add_text("1. Mapeado de Superficie", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font(dpg.last_item(), fonts["bold"])
            btn1 = dpg.add_button(
                label="Ir a Mapeado",
                width=-1,
                height=80,
                callback=lambda: dpg.set_value("tab_bar", "tab_mapping")
            )
            dpg.bind_item_theme(btn1, "button_theme_mapeado")
            dpg.add_text("Cargue la imagen de la superficie y marque los puntos de medición", wrap=-1)
            
            dpg.add_spacer(height=20)
            
            dpg.add_text("2. Tabla de Puntos", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font(dpg.last_item(), fonts["bold"])
            btn2 = dpg.add_button(
                label="Ir a HM Tabla",
                width=-1,
                height=80,
                callback=lambda: dpg.set_value("tab_bar", "tab_tabla")
            )
            dpg.bind_item_theme(btn2, "button_theme_tabla")
            dpg.add_text("Gestione los puntos marcados y asigne imágenes para medición", wrap=-1)
            
            dpg.add_spacer(height=20)
            
            dpg.add_text("3. Medición Vickers", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font(dpg.last_item(), fonts["bold"])
            btn3 = dpg.add_button(
                label="Ir a Vickers",
                width=-1,
                height=80,
                callback=lambda: dpg.set_value("tab_bar", "tab_vickers")
            )
            dpg.bind_item_theme(btn3, "button_theme_vickers")
            dpg.add_text("Realice las mediciones de dureza Vickers en cada punto", wrap=-1)
            
            dpg.add_spacer(height=20)
            
            dpg.add_text("4. Visualización de Resultados", color=hex_to_rgba(config["UI.Colors"]["section_title"]))
            dpg.bind_item_font(dpg.last_item(), fonts["bold"])
            btn4 = dpg.add_button(
                label="Ir a HM Plot",
                width=-1,
                height=80,
                callback=lambda: dpg.set_value("tab_bar", "tab_hmplot")
            )
            dpg.bind_item_theme(btn4, "button_theme_hmplot")
            dpg.add_text("Genere mapas de calor y visualice los resultados completos", wrap=-1)
