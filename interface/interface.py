import dearpygui.dearpygui as dpg
from ._inicioTab import showInicioTab
from ._vickersTab import showVickersTab
from ._mappingTab import showMappingTab
from ._dataTableTab import showDataTableTab
from ._hmPlotTab import showHMPlotTab
from ._theme import applyTheme
from .utils import center_viewport
from config import get_config, get_preference, save_preference


class Interface:
    def __init__(self, callbacks) -> None:
        self.callbacks = callbacks
        self.config = get_config()
        self.show()
    
    def center_title_elements(self):
        """Center the title and subtitle elements in the Inicio tab"""
        try:
            if dpg.does_item_exist("InicioRightPanel") and dpg.does_item_exist("app_title"):
                # Get parent window width
                parent_width = dpg.get_item_rect_size("InicioRightPanel")[0]
                
                # Center title
                if dpg.does_item_exist("app_title"):
                    title_width = dpg.get_item_rect_size("app_title")[0]
                    title_pos = [(parent_width - title_width) / 2, dpg.get_item_pos("app_title")[1]]
                    dpg.set_item_pos("app_title", title_pos)
                
                # Center subtitle
                if dpg.does_item_exist("app_subtitle"):
                    subtitle_width = dpg.get_item_rect_size("app_subtitle")[0]
                    subtitle_pos = [(parent_width - subtitle_width) / 2, dpg.get_item_pos("app_subtitle")[1]]
                    dpg.set_item_pos("app_subtitle", subtitle_pos)
        except Exception as e:
            pass  # Silently fail if items don't exist yet

    def show(self):
        dpg.create_context()
        dpg.configure_app(init_file=self.config["Paths"]["dpg_ini_file"])  # enable ini file to save window positions and sizes

        # ============ MAIN VIEWPORT ============
        with dpg.window(label="Main", tag="Main"):
            self.fonts = applyTheme()
            self.showTabBar()
        # =======================================

        dpg.set_primary_window("Main", True)
        
        # Get viewport dimensions from preferences or use config defaults
        viewport_width = get_preference("viewport_width", default=None) or self.config["Window"]["width"]
        viewport_height = get_preference("viewport_height", default=None) or self.config["Window"]["height"]
        
        dpg.create_viewport(
            title=self.config["Window"]["title"],
            width=viewport_width,
            height=viewport_height,
            min_width=self.config["Window"]["min_width"],
            min_height=self.config["Window"]["min_height"],
        )

        dpg.set_viewport_small_icon(self.config["Paths"]["icon_small"])
        dpg.set_viewport_large_icon(self.config["Paths"]["icon_large"])

        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        # Restore maximized state from preferences
        if get_preference("viewport_maximized", default=False):
            dpg.maximize_viewport()
        else:
            center_viewport()
        
        # Center title and subtitle after first render
        frame_count = 0
        
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            
            # Center text elements after a few frames (when sizes are available)
            if frame_count == 3:
                self.center_title_elements()
            frame_count += 1

        # Save viewport state before closing
        import ctypes
        try:
            user32 = ctypes.windll.user32
            # Get screen and viewport dimensions
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            vp_width = dpg.get_viewport_width()
            vp_height = dpg.get_viewport_height()
            
            # Check if maximized
            is_maximized = (vp_width >= screen_width - 20 and vp_height >= screen_height - 100)
            save_preference("viewport_maximized", is_maximized)
            
            # Save dimensions only if not maximized
            if not is_maximized:
                save_preference("viewport_width", vp_width)
                save_preference("viewport_height", vp_height)
        except:
            # If detection fails, try to save dimensions anyway
            try:
                vp_width = dpg.get_viewport_width()
                vp_height = dpg.get_viewport_height()
                save_preference("viewport_width", vp_width)
                save_preference("viewport_height", vp_height)
            except:
                pass
        
        dpg.destroy_context()

    def showTabBar(self):
        with dpg.tab_bar(tag="tab_bar"):
            with dpg.tab(label="Inicio", tag="tab_inicio"):
                showInicioTab(self.callbacks, self.fonts)
            
            with dpg.tab(label="Vickers", tag="tab_vickers"):
                showVickersTab(self.callbacks, self.fonts)
            
            with dpg.tab(label="Mapeado", tag="tab_mapping"):
                showMappingTab(self.callbacks, self.fonts)
            
            with dpg.tab(label="Tabla", tag="tab_tabla"):
                showDataTableTab(self.callbacks, self.fonts)
            
            with dpg.tab(label="Mapa de Calor", tag="tab_hmplot"):
                showHMPlotTab(self.callbacks, self.fonts)


