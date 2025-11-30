import os
import math
import dearpygui.dearpygui as dpg
from rich import print
from config import get_preference, save_preference


class HeatMapCB:
    def __init__(self, callbacks=None) -> None:
        self.callbacks = callbacks
        self.filePath = None
        self.fileName = None
        self.image_width = None
        self.image_height = None
        self.current_image_path = None
        self.original_image_data = None
        self.current_image_data = None
        
        # Heat map points
        self.points = []  # List of (x, y) coordinates
        self.point_series_tags = []  # List of series tags for cleanup
        
        # Calibration mode
        self.calibration_mode = False  # True when calibrating
        self.calibration_points = []  # Two points for calibration
        self.calibration_series_tags = []  # Tags for calibration visual elements
        
        # Origin offset
        self.origin_offset = (0, 0)  # Offset to apply to image position
        self.set_origin_mode = False  # True when setting origin
        self.axis_series_tags = []  # Tags for coordinate axes lines
        
        # Mouse mode
        self.mode = "Marcar Puntos"  # "Marcar Puntos" or "Mover Imagen"
        
        # Saved mapping image path
        self.saved_mapping_image_path = None  # Path to saved mapping image with points

    def openFile(self, sender, app_data):
        """Handle file selection for heat map image."""
        print("Heat Map - File selected")
        print("Sender: ", sender)
        print("App Data: ", app_data)

        self.filePath = app_data["current_path"]
        self.fileName = list(app_data["selections"].keys())[0]
        full_path = os.path.join(self.filePath, self.fileName)

        if not os.path.isfile(full_path):
            print(f"[red]The selected file does not exist: {full_path}[/red]")
            return

        dpg.set_value("heatmap_file_name_text", "Archivo: " + self.fileName)
        dpg.set_value("heatmap_file_path_text", "Ruta: " + self.filePath)

        # Load and display the image
        try:
            width, height, channels, data = dpg.load_image(full_path)

            self.image_width = width
            self.image_height = height
            self.current_image_path = full_path
            
            # Store original and current image data
            self.original_image_data = [data[i] for i in range(len(data))]
            self.current_image_data = self.original_image_data

            # Get calibration value
            calibration = get_preference("heatmap_calibration", default=0.001)
            real_width = width * calibration
            real_height = height * calibration

            # Delete existing image series
            if dpg.does_item_exist("heatmap_image_series"):
                dpg.delete_item("heatmap_image_series")

            # Delete existing texture
            if dpg.does_item_exist("heatmap_image_texture"):
                dpg.delete_item("heatmap_image_texture")

            # Create texture
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, data, tag="heatmap_image_texture")

            # Add image series to plot
            dpg.add_image_series(
                "heatmap_image_texture",
                bounds_min=(0, 0),
                bounds_max=(real_width, real_height),
                parent="HeatMap_y_axis",
                tag="heatmap_image_series",
                label=self.fileName[-34:-4],
            )

            # Reset axis
            dpg.set_axis_limits_auto("HeatMap_x_axis")
            dpg.set_axis_limits_auto("HeatMap_y_axis")
            dpg.fit_axis_data("HeatMap_x_axis")
            dpg.fit_axis_data("HeatMap_y_axis")

            # Clear previous points
            self.resetPoints()
            
            # Reset origin offset and clear axes
            self.origin_offset = (0, 0)
            self.clearCoordinateAxes()

            print(f"[green]Imagen del mapa de calor cargada: {width}x{height} pixels[/green]")

        except Exception as e:
            import traceback
            print(f"[red]Error loading image: {e}[/red]")
            traceback.print_exc()

    def cancelImportImage(self, sender=None, app_data=None):
        """Handle file dialog cancellation."""
        print("Heat Map - CANCEL was clicked.")
        dpg.hide_item("heatmap_file_dialog_id")
    
    def loadImageFromPath(self, full_path):
        """Load and display image from a given file path."""
        if not os.path.isfile(full_path):
            print(f"[red]El archivo no existe: {full_path}[/red]")
            return False
        
        self.filePath = os.path.dirname(full_path)
        self.fileName = os.path.basename(full_path)
        
        # Update UI text
        dpg.set_value("heatmap_file_name_text", "Archivo: " + self.fileName)
        dpg.set_value("heatmap_file_path_text", "Ruta: " + self.filePath)
        
        # Load and display the image
        try:
            width, height, channels, data = dpg.load_image(full_path)

            self.image_width = width
            self.image_height = height
            self.current_image_path = full_path
            
            # Store original and current image data
            self.original_image_data = [data[i] for i in range(len(data))]
            self.current_image_data = self.original_image_data

            # Get calibration value
            calibration = get_preference("heatmap_calibration", default=0.001)
            real_width = width * calibration
            real_height = height * calibration

            # Delete existing image series
            if dpg.does_item_exist("heatmap_image_series"):
                dpg.delete_item("heatmap_image_series")

            # Delete existing texture
            if dpg.does_item_exist("heatmap_image_texture"):
                dpg.delete_item("heatmap_image_texture")

            # Create texture
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, data, tag="heatmap_image_texture")

            # Add image series to plot
            dpg.add_image_series(
                "heatmap_image_texture",
                bounds_min=(0, 0),
                bounds_max=(real_width, real_height),
                parent="HeatMap_y_axis",
                tag="heatmap_image_series",
                label=self.fileName[-34:-4],
            )

            # Reset axis
            dpg.set_axis_limits_auto("HeatMap_x_axis")
            dpg.set_axis_limits_auto("HeatMap_y_axis")
            dpg.fit_axis_data("HeatMap_x_axis")
            dpg.fit_axis_data("HeatMap_y_axis")

            print(f"[green]Imagen del mapa de calor cargada: {width}x{height} pixels[/green]")
            return True

        except Exception as e:
            import traceback
            print(f"[red]Error cargando imagen: {e}[/red]")
            traceback.print_exc()
            return False

    def onCalibrationChange(self, sender, new_value):
        """Handle calibration changes."""
        save_preference("heatmap_calibration", new_value)
        self.updateImageScale()

    def updateImageScale(self):
        """Update image series bounds when calibration changes."""
        if self.image_width is None or self.image_height is None:
            return

        if not dpg.does_item_exist("heatmap_image_series"):
            return

        calibration = get_preference("heatmap_calibration", default=0.001)
        real_width = self.image_width * calibration
        real_height = self.image_height * calibration
        
        # Apply origin offset
        x_offset, y_offset = self.origin_offset
        bounds_min = (-x_offset, -y_offset)
        bounds_max = (real_width - x_offset, real_height - y_offset)

        dpg.configure_item("heatmap_image_series", bounds_min=bounds_min, bounds_max=bounds_max)
        dpg.fit_axis_data("HeatMap_x_axis")
        dpg.fit_axis_data("HeatMap_y_axis")

        print(f"[green]Heat Map scale updated: {real_width:.2f}x{real_height:.2f} mm (calibration: {calibration} mm/pixel)[/green]")

    def onPlotClick(self, sender, app_data):
        """Handle mouse clicks on the plot to mark measurement points."""
        # Only process clicks when hovering over the heat map plot
        if not dpg.is_item_hovered("HeatMapPlotParent"):
            return

        # Get plot coordinates
        plot_coords = dpg.get_plot_mouse_pos()

        if plot_coords is None:
            return
        
        # Check current mode
        if self.mode == "Mover Imagen":
            # Pan mode - DearPyGUI handles this automatically
            return

        # Handle set origin mode
        if self.set_origin_mode:
            self.handleSetOriginClick(plot_coords)
            return

        # Handle calibration mode
        if self.calibration_mode:
            self.handleCalibrationClick(plot_coords)
            return

        # Add point in Marcar Puntos mode
        self.points.append(plot_coords)
        point_index = len(self.points)
        
        print(f"[cyan]Punto P{point_index}: ({plot_coords[0]:.3f}, {plot_coords[1]:.3f}) mm[/cyan]")

        # Draw point and update table
        self.drawPoint(point_index - 1, plot_coords)
        self.updatePointsTable()
        
        # Add point to Data Table tab
        self.addPointToDataTable(point_index, plot_coords)

    def drawPoint(self, index, coords):
        """Draw a diamond (rombo) at the specified coordinates."""
        x, y = coords
        
        # Create diamond vertices (rombo)
        # Diamond size in mm
        size = 2
        
        # Diamond vertices: top, right, bottom, left
        diamond_x = [x, x + size, x, x - size, x]
        diamond_y = [y + size, y, y - size, y, y + size]
        
        # Draw diamond outline
        tag = f"heatmap_point_{index}_diamond"
        dpg.add_line_series(diamond_x, diamond_y, parent="HeatMap_y_axis", tag=tag, label=f"P{index + 1}")
        self.point_series_tags.append(tag)
        
        # Draw center point
        tag_center = f"heatmap_point_{index}_center"
        dpg.add_scatter_series([x], [y], parent="HeatMap_y_axis", tag=tag_center)
        self.point_series_tags.append(tag_center)

    def updatePointsTable(self):
        """Update the points table with all marked points."""
        if not dpg.does_item_exist("heatmap_points_table"):
            return
        
        # Clear existing rows
        children = dpg.get_item_children("heatmap_points_table", slot=1)
        if children:
            for child in children:
                dpg.delete_item(child)
        
        # Add rows for each point
        for i, (x, y) in enumerate(self.points):
            with dpg.table_row(parent="heatmap_points_table"):
                dpg.add_text(f"P{i + 1}")
                dpg.add_text(f"{x:.2f}")
                dpg.add_text(f"{y:.2f}")
        
        # Update point count
        if dpg.does_item_exist("heatmap_point_count"):
            dpg.set_value("heatmap_point_count", f"Total: {len(self.points)} puntos")
        
        # Save mapping image with points
        self.saveMappingImage()

    def saveMappingImage(self):
        """Save the mapping image with points overlaid to project folder."""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            return
        
        if len(self.points) == 0:
            return
        
        try:
            from PIL import Image as PILImage, ImageDraw, ImageFont
            
            # Open the image
            original_img = PILImage.open(self.current_image_path)
            
            # Add margin to prevent clipping of points and labels
            margin = 50  # pixels
            img_width, img_height = original_img.size
            new_width = img_width + 2 * margin
            new_height = img_height + 2 * margin
            
            # Create new image with margin (white background)
            img = PILImage.new('RGB', (new_width, new_height), (255, 255, 255))
            # Paste original image in the center
            img.paste(original_img, (margin, margin))
            
            draw = ImageDraw.Draw(img)
            
            # Get calibration
            calibration = get_preference("heatmap_calibration", default=0.001)
            
            # Draw each point
            for i, (x_mm, y_mm) in enumerate(self.points):
                # Convert mm coordinates to pixel coordinates
                # The points are stored in the transformed coordinate system (with origin_offset applied)
                # To draw on the original image, we need to add back the origin_offset
                # calibration is in mm/pixel, so pixels = mm / calibration
                x_px = (x_mm + self.origin_offset[0]) / calibration
                y_px = img_height - (y_mm + self.origin_offset[1]) / calibration  # Flip Y axis
                
                # Apply margin offset
                x_px += margin
                y_px += margin
                
                # Draw point marker (circle)
                point_radius = 8
                color = (255, 0, 0)  # Red
                draw.ellipse(
                    [x_px - point_radius, y_px - point_radius, 
                     x_px + point_radius, y_px + point_radius],
                    outline=color,
                    width=3
                )
                
                # Draw point label
                label = f"P{i+1}"
                try:
                    # Try to use a better font if available
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    # Fallback to default font
                    font = ImageFont.load_default()
                
                # Add background to text for better visibility
                bbox = draw.textbbox((x_px + 12, y_px - 8), label, font=font)
                draw.rectangle(bbox, fill=(0, 0, 0, 180))
                draw.text((x_px + 12, y_px - 8), label, fill=(255, 255, 0), font=font)
            
            # Save to project maps folder
            last_project_folder = get_preference("last_project_folder", default=".")
            maps_folder = os.path.join(last_project_folder, "maps")
            os.makedirs(maps_folder, exist_ok=True)
            save_path = os.path.join(maps_folder, "mapping_with_points.png")
            
            img.save(save_path, format='PNG')
            self.saved_mapping_image_path = save_path
            print(f"[cyan]Imagen de mapeado guardada en: {save_path}[/cyan]")
            
        except Exception as e:
            print(f"[yellow]Error guardando imagen de mapeado: {e}[/yellow]")
    
    def saveMappingImageManual(self, sender=None, app_data=None):
        """Manually save the mapping image with points overlaid when button is clicked."""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            print("[yellow]No hay imagen cargada para guardar[/yellow]")
            return
        
        if len(self.points) == 0:
            print("[yellow]No hay puntos marcados para guardar[/yellow]")
            return
        
        # Call the automatic save method
        self.saveMappingImage()
        
        # Show confirmation message
        print("[green]✓ Imagen del mapeado guardada exitosamente[/green]")
    
    def resetPoints(self):
        """Clear all marked points."""
        # Clear all drawn series
        for tag in self.point_series_tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
        
        self.point_series_tags.clear()
        self.points.clear()
        
        # Update table and count
        self.updatePointsTable()
        
        print("[yellow]Puntos de mapa de calor reseteados[/yellow]")

    def resetPointsButton(self, sender=None, app_data=None):
        """Callback for Reset Points button."""
        self.resetPoints()
        print("[green]Sistema de mapa de calor reseteado.[/green]")

    def onModeChange(self, sender, app_data):
        """Handle mode change between Marcar Puntos and Mover Imagen."""
        self.mode = app_data
        print(f"[cyan]Modo cambiado a: {self.mode}[/cyan]")
        
        # Update plot behavior based on mode
        if self.mode == "Mover Imagen":
            # Enable pan with left button
            if dpg.does_item_exist("HeatMapPlotParent"):
                dpg.configure_item("HeatMapPlotParent", 
                                   pan_button=dpg.mvMouseButton_Left,
                                   query=False)  # Disable query to allow pan
            print("[cyan]Modo: Mover Imagen - Use el botón izquierdo para hacer pan/zoom[/cyan]")
        else:
            # Restore right-click pan for marking points
            if dpg.does_item_exist("HeatMapPlotParent"):
                dpg.configure_item("HeatMapPlotParent", 
                                   pan_button=dpg.mvMouseButton_Right,
                                   query=True)  # Enable query for click detection
            print("[cyan]Modo: Marcar Puntos - Haga clic izquierdo para marcar puntos[/cyan]")

    def restartHeatMap(self, sender=None, app_data=None):
        """Restart the entire heat map - clear all points and reset to initial state."""
        # Clear all points
        self.resetPoints()
        
        # Clear calibration if any
        self.clearCalibrationVisuals()
        self.calibration_mode = False
        self.calibration_points.clear()
        
        # Clear origin setting
        self.clearCoordinateAxes()
        self.origin_offset = (0, 0)
        self.set_origin_mode = False
        
        # Reset mode to Marcar Puntos
        self.mode = "Marcar Puntos"
        if dpg.does_item_exist("heatmap_mode_radio"):
            dpg.set_value("heatmap_mode_radio", "Marcar Puntos")
        
        # Reset plot configuration
        if dpg.does_item_exist("HeatMapPlotParent"):
            dpg.configure_item("HeatMapPlotParent", 
                               pan_button=dpg.mvMouseButton_Right,
                               query=True)
        
        print("[green]Mapa de Calor reiniciado completamente[/green]")

    def startCalibration(self, sender=None, app_data=None):
        """Start calibration mode - user will mark two points."""
        if self.image_width is None:
            print("[red]Debe cargar una imagen primero[/red]")
            return
        
        # Toggle calibration mode
        if self.calibration_mode:
            self.cancelCalibration()
            return
        
        self.calibration_mode = True
        self.calibration_points = []
        self.clearCalibrationVisuals()
        
        # Update button text
        if dpg.does_item_exist("heatmap_calibrate_button"):
            dpg.configure_item("heatmap_calibrate_button", label="Cancelar Calibración")
        
        print("[yellow]Modo calibración activado. Marque dos puntos sobre la imagen.[/yellow]")

    def handleCalibrationClick(self, coords):
        """Handle clicks during calibration mode."""
        self.calibration_points.append(coords)
        
        # Draw calibration point
        index = len(self.calibration_points) - 1
        tag = f"calibration_point_{index}"
        dpg.add_scatter_series([coords[0]], [coords[1]], parent="HeatMap_y_axis", tag=tag)
        self.calibration_series_tags.append(tag)
        
        print(f"[cyan]Punto de calibración {index + 1}: ({coords[0]:.3f}, {coords[1]:.3f})[/cyan]")
        
        # If two points marked, draw line and show popup
        if len(self.calibration_points) == 2:
            # Draw line between points
            p1, p2 = self.calibration_points
            tag = "calibration_line"
            dpg.add_line_series([p1[0], p2[0]], [p1[1], p2[1]], parent="HeatMap_y_axis", tag=tag)
            self.calibration_series_tags.append(tag)
            
            # Calculate pixel distance
            calibration = get_preference("heatmap_calibration", default=0.001)
            pixel_dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2) / calibration
            
            print(f"[yellow]Distancia en pixels: {pixel_dist:.2f}[/yellow]")
            
            # Show popup to enter real distance
            self.showCalibrationPopup(pixel_dist)

    def showCalibrationPopup(self, pixel_distance):
        """Show popup to enter real distance between calibration points."""
        # Store pixel distance for later calculation
        self.calibration_pixel_distance = pixel_distance
        
        # Show popup
        if dpg.does_item_exist("calibration_popup"):
            dpg.configure_item("calibration_popup", show=True)
            # Reset input value
            if dpg.does_item_exist("calibration_distance_input"):
                dpg.set_value("calibration_distance_input", 10.0)

    def calculateCalibration(self, sender=None, app_data=None):
        """Calculate calibration from entered real distance."""
        # Get real distance from input
        if not dpg.does_item_exist("calibration_distance_input"):
            return
        
        real_distance = dpg.get_value("calibration_distance_input")
        
        if real_distance <= 0:
            print("[red]La distancia debe ser mayor a 0[/red]")
            return
        
        # Calculate calibration: mm/pixel
        calibration = real_distance / self.calibration_pixel_distance
        
        # Update calibration input and save
        if dpg.does_item_exist("heatmap_calibration_input"):
            dpg.set_value("heatmap_calibration_input", calibration)
        
        save_preference("heatmap_calibration", calibration)
        self.updateImageScale()
        
        print(f"[green]Calibración calculada: {calibration:.6f} mm/pixel[/green]")
        print(f"[green]Distancia real: {real_distance:.3f} mm = {self.calibration_pixel_distance:.2f} pixels[/green]")
        
        # Close popup and exit calibration mode
        self.cancelCalibration()
        if dpg.does_item_exist("calibration_popup"):
            dpg.configure_item("calibration_popup", show=False)

    def cancelCalibration(self, sender=None, app_data=None):
        """Cancel calibration mode."""
        self.calibration_mode = False
        self.calibration_points = []
        self.clearCalibrationVisuals()
        
        # Update button text
        if dpg.does_item_exist("heatmap_calibrate_button"):
            dpg.configure_item("heatmap_calibrate_button", label="Calibrar Escala")
        
        # Hide popup if open
        if dpg.does_item_exist("calibration_popup"):
            dpg.configure_item("calibration_popup", show=False)
        
        print("[yellow]Modo calibración cancelado[/yellow]")

    def clearCalibrationVisuals(self):
        """Clear all calibration visual elements."""
        for tag in self.calibration_series_tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
        self.calibration_series_tags.clear()

    def startSetOrigin(self, sender=None, app_data=None):
        """Start set origin mode - user will mark one point as (0,0)."""
        if self.image_width is None:
            print("[red]Debe cargar una imagen primero[/red]")
            return
        
        # Toggle set origin mode
        if self.set_origin_mode:
            self.cancelSetOrigin()
            return
        
        self.set_origin_mode = True
        
        # Update button text
        if dpg.does_item_exist("heatmap_set_origin_button"):
            dpg.configure_item("heatmap_set_origin_button", label="Cancelar")
        
        print("[yellow]Modo establecer origen activado. Marque un punto que será el nuevo (0,0).[/yellow]")

    def handleSetOriginClick(self, coords):
        """Handle click to set new origin point."""
        # Store the offset (the clicked point becomes the new origin)
        self.origin_offset = coords
        
        print(f"[green]Nuevo origen establecido en: ({coords[0]:.3f}, {coords[1]:.3f}) mm[/green]")
        
        # Update image position
        self.updateImagePosition()
        
        # Draw coordinate axes at origin
        self.drawCoordinateAxes()
        
        # Exit set origin mode
        self.set_origin_mode = False
        if dpg.does_item_exist("heatmap_set_origin_button"):
            dpg.configure_item("heatmap_set_origin_button", label="Set (0,0)")

    def updateImagePosition(self):
        """Update image series position based on origin offset."""
        if self.image_width is None or self.image_height is None:
            return

        if not dpg.does_item_exist("heatmap_image_series"):
            return

        calibration = get_preference("heatmap_calibration", default=0.001)
        real_width = self.image_width * calibration
        real_height = self.image_height * calibration
        
        # Apply offset to image bounds
        x_offset, y_offset = self.origin_offset
        bounds_min = (-x_offset, -y_offset)
        bounds_max = (real_width - x_offset, real_height - y_offset)

        dpg.configure_item("heatmap_image_series", bounds_min=bounds_min, bounds_max=bounds_max)
        dpg.fit_axis_data("HeatMap_x_axis")
        dpg.fit_axis_data("HeatMap_y_axis")
        
        print(f"[green]Imagen reposicionada. Origen desplazado: ({-x_offset:.3f}, {-y_offset:.3f}) mm[/green]")

    def drawCoordinateAxes(self):
        """Draw thin blue coordinate axes at the origin (0,0)."""
        # Clear previous axes
        self.clearCoordinateAxes()
        
        if not dpg.does_item_exist("HeatMap_y_axis"):
            return
        
        # Get current axis limits to draw axes across the visible area
        x_limits = dpg.get_axis_limits("HeatMap_x_axis")
        y_limits = dpg.get_axis_limits("HeatMap_y_axis")
        
        # Draw X-axis (horizontal line at y=0)
        tag_x = "heatmap_x_axis_line"
        dpg.add_line_series(
            [x_limits[0], x_limits[1]], 
            [0, 0], 
            parent="HeatMap_y_axis", 
            tag=tag_x
        )
        # Set color to blue and don't show in legend
        with dpg.theme(tag=f"{tag_x}_theme"):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 100, 255, 255), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)
        dpg.bind_item_theme(tag_x, f"{tag_x}_theme")
        self.axis_series_tags.append(tag_x)
        self.axis_series_tags.append(f"{tag_x}_theme")
        
        # Draw Y-axis (vertical line at x=0)
        tag_y = "heatmap_y_axis_line"
        dpg.add_line_series(
            [0, 0], 
            [y_limits[0], y_limits[1]], 
            parent="HeatMap_y_axis", 
            tag=tag_y
        )
        # Set color to blue and don't show in legend
        with dpg.theme(tag=f"{tag_y}_theme"):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 100, 255, 255), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1, category=dpg.mvThemeCat_Plots)
        dpg.bind_item_theme(tag_y, f"{tag_y}_theme")
        self.axis_series_tags.append(tag_y)
        self.axis_series_tags.append(f"{tag_y}_theme")
        
        print("[green]Ejes de coordenadas dibujados en el origen (0,0)[/green]")

    def clearCoordinateAxes(self):
        """Clear coordinate axes lines."""
        for tag in self.axis_series_tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
        self.axis_series_tags.clear()

    def cancelSetOrigin(self, sender=None, app_data=None):
        """Cancel set origin mode."""
        self.set_origin_mode = False
        
        # Update button text
        if dpg.does_item_exist("heatmap_set_origin_button"):
            dpg.configure_item("heatmap_set_origin_button", label="Set (0,0)")
        
        print("[yellow]Modo establecer origen cancelado[/yellow]")
    
    def addPointToDataTable(self, point_index, coords):
        """Add the point to the Data Table tab."""
        if self.callbacks is None or not hasattr(self.callbacks, 'dataTable'):
            print("[yellow]Data Table callback no disponible[/yellow]")
            return
        
        x, y = coords
        point_id = f"P{point_index}"
        
        # Get default image import path from config
        from config import get_config
        config = get_config()
        default_path = config['Paths'].get('default_image_import_path', 'images/')
        
        # Get last project folder
        last_project_folder = get_preference("last_project_folder", default=".")
        
        # Construct default image path
        default_image_path = os.path.join(last_project_folder, default_path, f"{point_index} 400x.jpg")
        
        # Add to data table
        self.callbacks.dataTable.table_data.append({
            'id': point_id,
            'x': x,
            'y': y,
            'hv': None,  # To be filled by user or Vickers calculation
            'image_path': default_image_path
        })
        
        # Rebuild the data table to show the new point
        self.callbacks.dataTable.rebuildTable()
        
        print(f"[green]Punto {point_id} agregado a la tabla de datos[/green]")
