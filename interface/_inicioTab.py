import dearpygui.dearpygui as dpg
from config import get_config, hex_to_rgba
from datetime import datetime
import os


# Store texture IDs for navigation cards
_nav_textures = {}


def _load_nav_textures():
    """Load textures for navigation cards from resources folder."""
    global _nav_textures
    
    if _nav_textures:  # Already loaded
        return _nav_textures
    
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
    
    images = {
        "mapeado": "mapeado.png",
        "tabla": "tabla.png",
        "vickers": "vickers.png",
        "heatmap": "mapa de calor.png"
    }
    
    for key, filename in images.items():
        filepath = os.path.join(resources_dir, filename)
        if os.path.exists(filepath):
            width, height, channels, data = dpg.load_image(filepath)
            
            with dpg.texture_registry():
                texture_id = dpg.add_static_texture(
                    width=width,
                    height=height,
                    default_value=data,
                    tag=f"nav_texture_{key}"
                )
            _nav_textures[key] = {
                "id": texture_id,
                "width": width,
                "height": height
            }
    
    return _nav_textures


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
            
            # Load navigation textures
            nav_textures = _load_nav_textures()
            
            # Card size - square buttons that fit 2 per row
            # Based on typical right panel width (~600px), with spacing
            card_size = 270  # Square size for each card
            card_spacing = 15
            
            # Create theme for card buttons with image
            def create_card_themes(name, base_color):
                """Create normal and hover themes for a card."""
                r, g, b = base_color
                
                with dpg.theme(tag=f"card_btn_theme_{name}"):
                    with dpg.theme_component(dpg.mvButton):
                        dpg.add_theme_color(dpg.mvThemeCol_Button, (r, g, b, 40))
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (r, g, b, 100))
                        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (r, g, b, 150))
                        dpg.add_theme_color(dpg.mvThemeCol_Border, (r, g, b, 255))
                        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15)
                        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)
            
            # Create themes for each card
            create_card_themes("mapeado", (70, 130, 180))
            create_card_themes("tabla", (60, 179, 113))
            create_card_themes("vickers", (255, 140, 0))
            create_card_themes("heatmap", (148, 0, 211))
            
            # Card data configuration
            cards = [
                {
                    "key": "mapeado",
                    "title": "1. Mapeado",
                    "description": "Cargar imagen y marcar puntos",
                    "tab": "tab_mapping",
                    "color": (70, 130, 180)
                },
                {
                    "key": "tabla",
                    "title": "2. Tabla de Puntos",
                    "description": "Gestionar puntos y asignar imágenes",
                    "tab": "tab_tabla",
                    "color": (60, 179, 113)
                },
                {
                    "key": "vickers",
                    "title": "3. Medición Vickers",
                    "description": "Medir dureza en cada punto",
                    "tab": "tab_vickers",
                    "color": (255, 140, 0)
                },
                {
                    "key": "heatmap",
                    "title": "4. Mapa de Calor",
                    "description": "Visualizar resultados y generar mapas",
                    "tab": "tab_hmplot",
                    "color": (148, 0, 211)
                }
            ]
            
            def nav_callback(sender, app_data, user_data):
                dpg.set_value("tab_bar", user_data)
            
            # Row 1: Mapeado and Tabla  
            with dpg.group(horizontal=True, horizontal_spacing=card_spacing):
                for card in cards[:2]:
                    with dpg.group():
                        # Square card button with texture
                        if card["key"] in nav_textures:
                            btn = dpg.add_image_button(
                                nav_textures[card["key"]]["id"],
                                width=card_size,
                                height=card_size,
                                callback=nav_callback,
                                user_data=card["tab"],
                                tag=f"nav_btn_{card['key']}"
                            )
                            dpg.bind_item_theme(btn, f"card_btn_theme_{card['key']}")
                        
                        # Title below image
                        r, g, b = card["color"]
                        title = dpg.add_text(card["title"], color=(r, g, b, 255))
                        dpg.bind_item_font(title, fonts["bold"])
                        
                        # Description
                        dpg.add_text(card["description"], color=(180, 180, 180, 255), wrap=card_size)
            
            dpg.add_spacer(height=15)
            
            # Row 2: Vickers and HM Plot
            with dpg.group(horizontal=True, horizontal_spacing=card_spacing):
                for card in cards[2:]:
                    with dpg.group():
                        # Square card button with texture
                        if card["key"] in nav_textures:
                            btn = dpg.add_image_button(
                                nav_textures[card["key"]]["id"],
                                width=card_size,
                                height=card_size,
                                callback=nav_callback,
                                user_data=card["tab"],
                                tag=f"nav_btn_{card['key']}"
                            )
                            dpg.bind_item_theme(btn, f"card_btn_theme_{card['key']}")
                        
                        # Title below image
                        r, g, b = card["color"]
                        title = dpg.add_text(card["title"], color=(r, g, b, 255))
                        dpg.bind_item_font(title, fonts["bold"])
                        
                        # Description
                        dpg.add_text(card["description"], color=(180, 180, 180, 255), wrap=card_size)
