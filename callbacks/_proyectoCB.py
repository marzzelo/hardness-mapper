import json
import dearpygui.dearpygui as dpg
from rich import print
from datetime import datetime
from config import get_preference, save_preference, get_config
import os


class ProyectoCB:
    def __init__(self, callbacks=None) -> None:
        self.callbacks = callbacks
        self.project_file = None
    
    def newProject(self, sender=None, app_data=None):
        """Create a new project by clearing all data and resetting to initial state."""
        try:
            print("[cyan]Iniciando nuevo proyecto...[/cyan]")
            
            # Clear project info fields
            if dpg.does_item_exist("proyecto_nombre"):
                dpg.set_value("proyecto_nombre", "")
            if dpg.does_item_exist("proyecto_descripcion"):
                dpg.set_value("proyecto_descripcion", "")
            if dpg.does_item_exist("proyecto_requerimiento"):
                dpg.set_value("proyecto_requerimiento", "")
            if dpg.does_item_exist("proyecto_tecnico"):
                dpg.set_value("proyecto_tecnico", "")
            if dpg.does_item_exist("proyecto_fecha"):
                dpg.set_value("proyecto_fecha", datetime.now().strftime("%Y-%m-%d"))
            
            # Clear Vickers tab
            if hasattr(self.callbacks, 'imageProcessing'):
                self.callbacks.imageProcessing.measurements = []
                self.callbacks.imageProcessing.current_measurement = 0
                self.callbacks.imageProcessing.current_points = []
                
                # Reset UI
                if dpg.does_item_exist("vickers_current_measurement"):
                    n_meas = self.callbacks.imageProcessing.n_measurements
                    dpg.set_value("vickers_current_measurement", f"0/{n_meas}")
                if dpg.does_item_exist("vickers_npoints"):
                    dpg.set_value("vickers_npoints", "0/4")
                
                # Clear measurements table
                self.callbacks.imageProcessing.updateMeasurementsTable()
                self.callbacks.imageProcessing.updateMeasurementsSummary()
                
                # Clear plot - remove all series
                if dpg.does_item_exist("Processing_y_axis"):
                    if hasattr(self.callbacks.imageProcessing, 'vickers_series_tags'):
                        for tag in self.callbacks.imageProcessing.vickers_series_tags:
                            if dpg.does_item_exist(tag):
                                dpg.delete_item(tag)
                        self.callbacks.imageProcessing.vickers_series_tags.clear()
                    
                    # Clear image if exists
                    if dpg.does_item_exist("image_series"):
                        dpg.delete_item("image_series")
                    if dpg.does_item_exist("loaded_image_texture"):
                        dpg.delete_item("loaded_image_texture")
                
                # Reset image data
                self.callbacks.imageProcessing.current_image_path = None
                self.callbacks.imageProcessing.original_image_data = None
                self.callbacks.imageProcessing.current_image_data = None
                self.callbacks.imageProcessing.image_width = None
                self.callbacks.imageProcessing.image_height = None
                self.callbacks.imageProcessing.filePath = None
                self.callbacks.imageProcessing.fileName = None
                
                # Reset file display
                if dpg.does_item_exist("file_name_text"):
                    dpg.set_value("file_name_text", "Archivo: ")
                if dpg.does_item_exist("file_path_text"):
                    dpg.set_value("file_path_text", "Ruta: ")
                
                print("[green]✓ Pestaña Vickers limpiada[/green]")
            
            # Clear HeatMap (Mapeado) tab - COMPLETE CLEANUP
            if hasattr(self.callbacks, 'heatMap'):
                # Clear all point markers from plot
                for tag in self.callbacks.heatMap.point_series_tags:
                    if dpg.does_item_exist(tag):
                        dpg.delete_item(tag)
                self.callbacks.heatMap.point_series_tags.clear()
                
                # Clear calibration visuals
                for tag in self.callbacks.heatMap.calibration_series_tags:
                    if dpg.does_item_exist(tag):
                        dpg.delete_item(tag)
                self.callbacks.heatMap.calibration_series_tags.clear()
                
                # Clear coordinate axes
                for tag in self.callbacks.heatMap.axis_series_tags:
                    if dpg.does_item_exist(tag):
                        dpg.delete_item(tag)
                self.callbacks.heatMap.axis_series_tags.clear()
                
                # Clear image series and texture
                if dpg.does_item_exist("heatmap_image_series"):
                    dpg.delete_item("heatmap_image_series")
                if dpg.does_item_exist("heatmap_image_texture"):
                    dpg.delete_item("heatmap_image_texture")
                
                # Reset all data variables
                self.callbacks.heatMap.points = []
                self.callbacks.heatMap.calibration_points = []
                self.callbacks.heatMap.origin_offset = (0, 0)
                self.callbacks.heatMap.calibration_mode = False
                self.callbacks.heatMap.set_origin_mode = False
                self.callbacks.heatMap.mode = "Marcar Puntos"
                self.callbacks.heatMap.current_image_path = None
                self.callbacks.heatMap.original_image_data = None
                self.callbacks.heatMap.current_image_data = None
                self.callbacks.heatMap.image_width = None
                self.callbacks.heatMap.image_height = None
                self.callbacks.heatMap.saved_mapping_image_path = None
                self.callbacks.heatMap.filePath = None
                self.callbacks.heatMap.fileName = None
                
                # Reset UI elements
                if dpg.does_item_exist("heatmap_mode_radio"):
                    dpg.set_value("heatmap_mode_radio", "Marcar Puntos")
                
                if dpg.does_item_exist("heatmap_file_name_text"):
                    dpg.set_value("heatmap_file_name_text", "Archivo: ")
                if dpg.does_item_exist("heatmap_file_path_text"):
                    dpg.set_value("heatmap_file_path_text", "Ruta: ")
                
                # Clear points table
                if dpg.does_item_exist("heatmap_points_table"):
                    children = dpg.get_item_children("heatmap_points_table", slot=1)
                    if children:
                        for child in children:
                            dpg.delete_item(child)
                
                # Reset point count
                if dpg.does_item_exist("heatmap_point_count"):
                    dpg.set_value("heatmap_point_count", "Total: 0 puntos")
                
                # Reset plot configuration
                if dpg.does_item_exist("HeatMapPlotParent"):
                    dpg.configure_item("HeatMapPlotParent", 
                                       pan_button=dpg.mvMouseButton_Right,
                                       query=True)
                
                # Reset axis limits
                if dpg.does_item_exist("HeatMap_x_axis"):
                    dpg.set_axis_limits_auto("HeatMap_x_axis")
                if dpg.does_item_exist("HeatMap_y_axis"):
                    dpg.set_axis_limits_auto("HeatMap_y_axis")
                
                print("[green]✓ Pestaña Mapeado limpiada completamente[/green]")
            
            # Clear Data Table tab - COMPLETE CLEANUP
            if hasattr(self.callbacks, 'dataTable'):
                # Clear table data
                self.callbacks.dataTable.table_data = []
                
                # Clear UI table
                if dpg.does_item_exist("data_table"):
                    children = dpg.get_item_children("data_table", slot=1)
                    if children:
                        for child in children:
                            dpg.delete_item(child)
                
                # Clear thumbnails if they exist
                if hasattr(self.callbacks.dataTable, 'thumbnail_textures'):
                    for texture_tag in self.callbacks.dataTable.thumbnail_textures.values():
                        if dpg.does_item_exist(texture_tag):
                            dpg.delete_item(texture_tag)
                    self.callbacks.dataTable.thumbnail_textures = {}
                
                # Rebuild empty table to show headers
                self.callbacks.dataTable.rebuildTable()
                
                print("[green]✓ Tabla de datos limpiada completamente[/green]")
            
            # Clear HM Plot tab
            if hasattr(self.callbacks, 'hmPlot'):
                self.callbacks.hmPlot.last_figure = None
                self.callbacks.hmPlot.last_heatmap_image_path = None
                self.callbacks.hmPlot.heatmap_texture = None
                
                # Clear plot display completely
                if dpg.does_item_exist("HMPlotDisplayChild"):
                    dpg.delete_item("HMPlotDisplayChild", children_only=True)
                    # Add placeholder text
                    dpg.add_text("Genere el mapa de calor usando los botones de la izquierda",
                                parent="HMPlotDisplayChild",
                                tag="hm_plot_placeholder")
                
                # Reset info text
                if dpg.does_item_exist("hm_plot_info_text"):
                    dpg.set_value("hm_plot_info_text", "No hay datos disponibles")
                
                print("[green]✓ Pestaña HM Plot limpiada[/green]")
            
            # Reset project file reference
            self.project_file = None
            
            print("[green]✓✓✓ Nuevo proyecto creado exitosamente ✓✓✓[/green]")
            print("[yellow]Todas las pestañas, imágenes, tablas y gráficos han sido limpiados[/yellow]")
            
        except Exception as e:
            print(f"[red]Error creando nuevo proyecto: {e}[/red]")
            import traceback
            traceback.print_exc()
    
    def getProjectData(self):
        """Get current project data from UI fields."""
        return {
            "nombre": dpg.get_value("proyecto_nombre") if dpg.does_item_exist("proyecto_nombre") else "",
            "descripcion": dpg.get_value("proyecto_descripcion") if dpg.does_item_exist("proyecto_descripcion") else "",
            "requerimiento": dpg.get_value("proyecto_requerimiento") if dpg.does_item_exist("proyecto_requerimiento") else "",
            "tecnico": dpg.get_value("proyecto_tecnico") if dpg.does_item_exist("proyecto_tecnico") else "",
            "fecha": dpg.get_value("proyecto_fecha") if dpg.does_item_exist("proyecto_fecha") else datetime.now().strftime("%Y-%m-%d"),
        }
    
    def setProjectData(self, data):
        """Set project data to UI fields."""
        if dpg.does_item_exist("proyecto_nombre"):
            dpg.set_value("proyecto_nombre", data.get("nombre", ""))
        if dpg.does_item_exist("proyecto_descripcion"):
            dpg.set_value("proyecto_descripcion", data.get("descripcion", ""))
        if dpg.does_item_exist("proyecto_requerimiento"):
            dpg.set_value("proyecto_requerimiento", data.get("requerimiento", ""))
        if dpg.does_item_exist("proyecto_tecnico"):
            dpg.set_value("proyecto_tecnico", data.get("tecnico", ""))
        if dpg.does_item_exist("proyecto_fecha"):
            dpg.set_value("proyecto_fecha", data.get("fecha", datetime.now().strftime("%Y-%m-%d")))
    
    def saveProject(self, sender=None, app_data=None):
        """Save project data and all related information to a JSON file."""
        # Get project name and sanitize for filename
        project_name = dpg.get_value("proyecto_nombre") if dpg.does_item_exist("proyecto_nombre") else "proyecto"
        
        # Clean filename: remove/replace invalid characters
        import re
        if project_name:
            # Replace invalid filename characters with underscore
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', project_name)
            # Remove leading/trailing spaces and dots
            clean_name = clean_name.strip('. ')
            # If empty after cleaning, use default
            if not clean_name:
                clean_name = "proyecto"
        else:
            clean_name = "proyecto"
        
        default_filename = f"{clean_name}.json"
        
        # Show file dialog
        if dpg.does_item_exist("save_project_dialog"):
            # Update default filename
            dpg.set_item_user_data("save_project_dialog", default_filename)
            dpg.show_item("save_project_dialog")
        else:
            self._createSaveDialog(default_filename)
            dpg.show_item("save_project_dialog")
    
    def _createSaveDialog(self, default_filename="proyecto.json"):
        """Create save project file dialog."""
        from config import get_config
        config = get_config()
        
        # Use last project folder or fallback to config default
        default_path = get_preference("last_project_folder") or config["Paths"].get("default_project_path", ".")
        
        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            tag="save_project_dialog",
            callback=self._saveProjectCallback,
            default_filename=default_filename,
            width=900,
            height=600,
            default_path=default_path,
        ):
            dpg.add_file_extension(".json", color=(0, 255, 0, 255))
            dpg.add_file_extension(".*")
    
    def _saveProjectCallback(self, sender, app_data):
        """Callback for save project dialog."""
        import os
        
        file_path = app_data["file_path_name"]
        
        # Ensure .json extension
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        print(f"[cyan]Intentando guardar proyecto en: {file_path}[/cyan]")
        
        try:
            # Get preferences for values not stored in objects
            from config import get_preference
            
            # Check if callbacks exist
            if self.callbacks is None:
                print("[yellow]Advertencia: callbacks es None[/yellow]")
            
            # Get project directory for relative paths
            project_dir = os.path.dirname(file_path)
            
            # Convert image path to relative path
            heatmap_image_relative = None
            if self.callbacks and hasattr(self.callbacks, 'heatMap') and self.callbacks.heatMap.current_image_path:
                try:
                    heatmap_image_relative = os.path.relpath(self.callbacks.heatMap.current_image_path, project_dir)
                    print(f"[cyan]Ruta relativa de imagen: {heatmap_image_relative}[/cyan]")
                except ValueError:
                    # If on different drives, use absolute path
                    heatmap_image_relative = self.callbacks.heatMap.current_image_path
                    print(f"[yellow]Usando ruta absoluta (diferentes unidades): {heatmap_image_relative}[/yellow]")
            
            # Gather all project data
            project_data = {
                # Project Info
                "info": self.getProjectData(),
                
                # Vickers Tab
                "vickers": {
                    "calibration": get_preference("vickers_calibration", default=1.0),
                    "load": get_preference("vickers_load", default=500.0),
                    "measurements": self.callbacks.imageProcessing.measurements if (self.callbacks and hasattr(self.callbacks, 'imageProcessing')) else [],
                    "n_measurements": self.callbacks.imageProcessing.n_measurements if (self.callbacks and hasattr(self.callbacks, 'imageProcessing')) else 2,
                },
                
                # Mapeado (HeatMap) Tab
                "heatmap": {
                    "calibration": get_preference("heatmap_calibration", default=0.001),
                    "points": self.callbacks.heatMap.points if (self.callbacks and hasattr(self.callbacks, 'heatMap')) else [],
                    "origin_offset": self.callbacks.heatMap.origin_offset if (self.callbacks and hasattr(self.callbacks, 'heatMap')) else (0, 0),
                    "image_path": heatmap_image_relative,
                },
                
                # HM Tabla Tab
                "table": {
                    "data": self.callbacks.dataTable.table_data if (self.callbacks and hasattr(self.callbacks, 'dataTable')) else []
                },
                
                # HM Plot Tab
                "hmplot": {
                    "colorscale": self.callbacks.hmPlot.colorscale if (self.callbacks and hasattr(self.callbacks, 'hmPlot')) else "Viridis",
                    "interpolation": self.callbacks.hmPlot.interpolation if (self.callbacks and hasattr(self.callbacks, 'hmPlot')) else "cubic",
                    "show_points": self.callbacks.hmPlot.show_points if (self.callbacks and hasattr(self.callbacks, 'hmPlot')) else False,
                    "show_lines": self.callbacks.hmPlot.show_lines if (self.callbacks and hasattr(self.callbacks, 'hmPlot')) else False,
                    "grid_resolution": self.callbacks.hmPlot.grid_resolution if (self.callbacks and hasattr(self.callbacks, 'hmPlot')) else 500,
                    "contour_levels": self.callbacks.hmPlot.contour_levels if (self.callbacks and hasattr(self.callbacks, 'hmPlot')) else 40,
                    "figure_scale": self.callbacks.hmPlot.figure_scale if (self.callbacks and hasattr(self.callbacks, 'hmPlot')) else 1.0,
                },
                
                # Metadata
                "saved_at": datetime.now().isoformat()
            }
            
            print(f"[cyan]Datos del proyecto preparados, guardando...[/cyan]")
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            self.project_file = file_path
            print(f"[green]✓ Proyecto guardado exitosamente en: {file_path}[/green]")
            
            # Save project folder to preferences
            project_folder = os.path.dirname(file_path)
            save_preference("last_project_folder", project_folder)
            print(f"[cyan]Carpeta del proyecto guardada en preferencias: {project_folder}[/cyan]")
            
            # Verify file was created
            import os
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"[green]✓ Archivo verificado: {file_size} bytes[/green]")
            else:
                print(f"[red]✗ ERROR: El archivo no existe después de guardar[/red]")
            
            # Show confirmation popup
            if dpg.does_item_exist("save_project_popup"):
                dpg.show_item("save_project_popup")
            else:
                self._createSavePopup()
                dpg.show_item("save_project_popup")
            
        except Exception as e:
            print(f"[red]Error guardando proyecto: {e}[/red]")
    
    def _createSavePopup(self):
        """Create save confirmation popup."""
        with dpg.window(
            label="Proyecto Guardado",
            modal=True,
            show=False,
            tag="save_project_popup",
            no_resize=True,
            width=400,
            height=150,
            pos=[400, 300]
        ):
            dpg.add_text("Proyecto guardado exitosamente", color=(0, 255, 0))
            dpg.add_spacer(height=10)
            dpg.add_button(
                label="OK",
                width=-1,
                callback=lambda: dpg.hide_item("save_project_popup")
            )
    
    def loadProject(self, sender=None, app_data=None):
        """Load project data from a JSON file."""
        # Show file dialog
        if dpg.does_item_exist("load_project_dialog"):
            dpg.show_item("load_project_dialog")
        else:
            self._createLoadDialog()
            dpg.show_item("load_project_dialog")
    
    def _createLoadDialog(self):
        """Create load project file dialog."""
        from config import get_config
        config = get_config()
        
        # Use last project folder or fallback to config default
        default_path = get_preference("last_project_folder") or config["Paths"].get("default_project_path", ".")
        
        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            tag="load_project_dialog",
            callback=self._loadProjectCallback,
            width=700,
            height=400,
            default_path=default_path,
        ):
            dpg.add_file_extension(".json", color=(0, 255, 0, 255))
            dpg.add_file_extension(".*")
    
    def _loadProjectCallback(self, sender, app_data):
        """Callback for load project dialog."""
        import os
        
        file_path = app_data["file_path_name"]
        
        if not os.path.isfile(file_path):
            print(f"[red]Archivo no encontrado: {file_path}[/red]")
            return
        
        try:
            # Load from file
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            from config import save_preference
            
            # Restore project info
            if "info" in project_data:
                self.setProjectData(project_data["info"])
            
            # Restore Vickers data
            if "vickers" in project_data:
                vickers_data = project_data["vickers"]
                
                # Save to preferences
                save_preference("vickers_calibration", vickers_data.get("calibration", 1.0))
                save_preference("vickers_load", vickers_data.get("load", 500.0))
                
                # Update UI
                if dpg.does_item_exist("vickers_calibration_input"):
                    dpg.set_value("vickers_calibration_input", vickers_data.get("calibration", 1.0))
                if dpg.does_item_exist("vickers_load_input"):
                    dpg.set_value("vickers_load_input", vickers_data.get("load", 500.0))
                
                # Restore measurements if available
                if hasattr(self.callbacks, 'imageProcessing'):
                    measurements_list = vickers_data.get("measurements", [])
                    self.callbacks.imageProcessing.measurements = measurements_list
                    self.callbacks.imageProcessing.n_measurements = vickers_data.get("n_measurements", 2)
                    
                    if dpg.does_item_exist("vickers_n_measurements_input"):
                        dpg.set_value("vickers_n_measurements_input", vickers_data.get("n_measurements", 2))
                    
                    # Update measurements table and summary
                    self.callbacks.imageProcessing.updateMeasurementsTable()
                    self.callbacks.imageProcessing.updateMeasurementsSummary()
                    
                    # Update current measurement counter
                    num_measurements = len(measurements_list)
                    if dpg.does_item_exist("vickers_current_measurement"):
                        if num_measurements >= self.callbacks.imageProcessing.n_measurements:
                            dpg.set_value("vickers_current_measurement", f"{self.callbacks.imageProcessing.n_measurements}/{self.callbacks.imageProcessing.n_measurements}")
                        else:
                            dpg.set_value("vickers_current_measurement", f"0/{self.callbacks.imageProcessing.n_measurements}")
                    
                    if num_measurements > 0:
                        print(f"[green]Mediciones Vickers restauradas: {num_measurements} mediciones[/green]")
            
            # Restore heat map data
            if "heatmap" in project_data and hasattr(self.callbacks, 'heatMap'):
                hm_data = project_data["heatmap"]
                
                # Restore calibration first
                calibration = hm_data.get("calibration", 0.001)
                save_preference("heatmap_calibration", calibration)
                if dpg.does_item_exist("heatmap_calibration_input"):
                    dpg.set_value("heatmap_calibration_input", calibration)
                
                # Load surface image if available
                # Check for new format (image_path) or old format (current_image_path)
                image_path_relative = hm_data.get("image_path") or hm_data.get("current_image_path")
                if image_path_relative:
                    # Resolve relative path from project directory
                    project_dir = os.path.dirname(file_path)
                    if not os.path.isabs(image_path_relative):
                        image_path = os.path.normpath(os.path.join(project_dir, image_path_relative))
                        print(f"[cyan]Resolviendo ruta relativa: {image_path_relative} -> {image_path}[/cyan]")
                    else:
                        image_path = image_path_relative
                    
                    if os.path.isfile(image_path):
                        # Load image without resetting points
                        self.callbacks.heatMap.loadImageFromPath(image_path)
                    else:
                        print(f"[yellow]Advertencia: Imagen no encontrada: {image_path}[/yellow]")
                
                # Restore points and origin
                self.callbacks.heatMap.points = hm_data.get("points", [])
                self.callbacks.heatMap.origin_offset = tuple(hm_data.get("origin_offset", (0, 0)))
                
                # Apply origin offset to image position
                if self.callbacks.heatMap.origin_offset != (0, 0):
                    self.callbacks.heatMap.updateImagePosition()
                    self.callbacks.heatMap.drawCoordinateAxes()
                
                # Redraw all points
                for i, point in enumerate(self.callbacks.heatMap.points):
                    self.callbacks.heatMap.drawPoint(i, point)
                
                # Update table
                self.callbacks.heatMap.updatePointsTable()
                
                print(f"[green]Mapa de calor restaurado: {len(self.callbacks.heatMap.points)} puntos[/green]")
            
            # Restore table data
            if "table" in project_data and hasattr(self.callbacks, 'dataTable'):
                self.callbacks.dataTable.table_data = project_data["table"].get("data", [])
                self.callbacks.dataTable.rebuildTable()
            
            # Restore HM Plot settings
            if "hmplot" in project_data and hasattr(self.callbacks, 'hmPlot'):
                hmplot_data = project_data["hmplot"]
                
                self.callbacks.hmPlot.colorscale = hmplot_data.get("colorscale", "Viridis")
                self.callbacks.hmPlot.interpolation = hmplot_data.get("interpolation", "cubic")
                self.callbacks.hmPlot.show_points = hmplot_data.get("show_points", False)
                self.callbacks.hmPlot.show_lines = hmplot_data.get("show_lines", False)
                self.callbacks.hmPlot.grid_resolution = hmplot_data.get("grid_resolution", 500)
                self.callbacks.hmPlot.contour_levels = hmplot_data.get("contour_levels", 40)
                self.callbacks.hmPlot.figure_scale = hmplot_data.get("figure_scale", 1.0)
                
                # Update UI
                if dpg.does_item_exist("hm_colorscale_combo"):
                    dpg.set_value("hm_colorscale_combo", hmplot_data.get("colorscale", "viridis").lower())
                if dpg.does_item_exist("hm_interpolation_combo"):
                    dpg.set_value("hm_interpolation_combo", hmplot_data.get("interpolation", "cubic"))
                if dpg.does_item_exist("hm_show_points_checkbox"):
                    dpg.set_value("hm_show_points_checkbox", hmplot_data.get("show_points", False))
                if dpg.does_item_exist("hm_show_lines_checkbox"):
                    dpg.set_value("hm_show_lines_checkbox", hmplot_data.get("show_lines", False))
                if dpg.does_item_exist("hm_resolution_slider"):
                    dpg.set_value("hm_resolution_slider", hmplot_data.get("grid_resolution", 500))
                if dpg.does_item_exist("hm_levels_slider"):
                    dpg.set_value("hm_levels_slider", hmplot_data.get("contour_levels", 40))
                if dpg.does_item_exist("hm_figsize_slider"):
                    dpg.set_value("hm_figsize_slider", hmplot_data.get("figure_scale", 1.0))
                
                # Save figure scale to preferences
                save_preference("heatmap_figure_scale", hmplot_data.get("figure_scale", 1.0))
            
            self.project_file = file_path
            print(f"[green]Proyecto cargado exitosamente: {file_path}[/green]")
            
            # Save project folder to preferences
            project_folder = os.path.dirname(file_path)
            save_preference("last_project_folder", project_folder)
            print(f"[cyan]Carpeta del proyecto guardada en preferencias: {project_folder}[/cyan]")
            
        except Exception as e:
            print(f"[red]Error cargando proyecto: {e}[/red]")
    
    def generateHTMLReport(self, sender=None, app_data=None):
        """Generate comprehensive HTML report with all project data."""
        try:
            from callbacks._pdfGenerator import generate_html_report
            
            # Get project name for filename
            project_name = dpg.get_value("proyecto_nombre") if dpg.does_item_exist("proyecto_nombre") else "reporte"
            if not project_name:
                project_name = "reporte"
            
            # Clean filename
            import re
            clean_name = re.sub(r'[<>:"/\\|?*]', '_', project_name)
            clean_name = clean_name.strip('. ')
            if not clean_name:
                clean_name = "reporte"
            
            # Get last project folder or use current directory
            last_project_folder = get_preference("last_project_folder", default=".")
            file_path = os.path.join(last_project_folder, f"{clean_name}_reporte.html")
            
            # Gather all project data
            project_data = self.getProjectData()
            
            # Get heatmap data (mapping)
            heatmap_data = None
            mapping_image_path = None
            if hasattr(self.callbacks, 'heatMap'):
                # Get absolute path for image
                image_path = self.callbacks.heatMap.current_image_path
                if image_path and not os.path.isabs(image_path):
                    image_path = os.path.join(last_project_folder, image_path)
                
                # Get saved mapping image with points
                if self.callbacks.heatMap.saved_mapping_image_path and os.path.exists(self.callbacks.heatMap.saved_mapping_image_path):
                    mapping_image_path = self.callbacks.heatMap.saved_mapping_image_path
                else:
                    # Fallback to maps folder
                    maps_img = os.path.join(last_project_folder, "maps", "mapping_with_points.png")
                    if os.path.exists(maps_img):
                        mapping_image_path = maps_img
                
                heatmap_data = {
                    'calibration': get_preference("heatmap_calibration", default=0.001),
                    'points': self.callbacks.heatMap.points,
                    'origin_offset': self.callbacks.heatMap.origin_offset,
                    'image_path': image_path,
                    'mapping_image_path': mapping_image_path
                }
            
            # Get table data
            table_data = None
            if hasattr(self.callbacks, 'dataTable'):
                # Make absolute paths for images
                table_data = []
                for point in self.callbacks.dataTable.table_data:
                    point_copy = point.copy()
                    img_path = point_copy.get('image_path')
                    if img_path and not os.path.isabs(img_path):
                        point_copy['image_path'] = os.path.join(last_project_folder, img_path)
                    table_data.append(point_copy)
            
            # Get heatmap image path (if exists)
            heatmap_html_path = None
            if hasattr(self.callbacks, 'hmPlot'):
                # Check if there's a saved heatmap image
                hm_image = os.path.join(last_project_folder, "maps", "heatmap.png")
                if os.path.exists(hm_image):
                    heatmap_html_path = hm_image
                elif self.callbacks.hmPlot.last_heatmap_image_path and os.path.exists(self.callbacks.hmPlot.last_heatmap_image_path):
                    heatmap_html_path = self.callbacks.hmPlot.last_heatmap_image_path
            
            # Get grid columns from config
            config = get_config()
            grid_columns = int(config.get('Report', {}).get('grid_columns', 4))
            
            print(f"[cyan]Generando reporte HTML...[/cyan]")
            
            # Generate HTML report
            generate_html_report(
                file_path=file_path,
                project_data=project_data,
                heatmap_data=heatmap_data,
                table_data=table_data,
                heatmap_html_path=heatmap_html_path,
                grid_columns=grid_columns
            )
            
            print(f"[green]✓ Reporte HTML generado exitosamente[/green]")
            
        except Exception as e:
            print(f"[red]Error generando reporte HTML: {e}[/red]")
            import traceback
            traceback.print_exc()
