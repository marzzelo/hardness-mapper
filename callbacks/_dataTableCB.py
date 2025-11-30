import os
import dearpygui.dearpygui as dpg
from rich import print
from config import get_preference, get_config


class DataTableCB:
    def __init__(self, callbacks) -> None:
        self.callbacks = callbacks  # Reference to main callbacks to access heatMap data
        self.table_data = []  # List of dicts: {id, x, y, hv, std_dev, image_path}
        self.image_textures = {}  # Store texture tags for cleanup
    
    def updateFromHeatMap(self, sender=None, app_data=None):
        """Synchronize table data with Heat Map points (Mapeado tab).
        Updates existing points and adds new ones while preserving image paths and HV values.
        """
        # Get points from heat map
        if not hasattr(self.callbacks, 'heatMap'):
            print("[red]Heat Map callback no disponible[/red]")
            return
        
        heatmap_points = self.callbacks.heatMap.points
        
        if len(heatmap_points) == 0:
            print("[yellow]No hay puntos marcados en el Mapeado[/yellow]")
            return
        
        # Get default paths
        config = get_config()
        default_image_import_path = config['Paths'].get('default_image_import_path', 'images/')
        last_project_folder = get_preference("last_project_folder", default=".")
        
        # Create a map of existing points by ID for quick lookup
        existing_points = {point['id']: point for point in self.table_data}
        
        # Update or add points
        new_table_data = []
        for i, (x, y) in enumerate(heatmap_points):
            point_number = i + 1
            point_id = f"P{point_number}"
            
            if point_id in existing_points:
                # Point exists - update coordinates, keep image path and HV
                existing_point = existing_points[point_id]
                new_table_data.append({
                    'id': point_id,
                    'x': x,
                    'y': y,
                    'hv': existing_point.get('hv'),  # Preserve existing HV
                    'std_dev': existing_point.get('std_dev'),  # Preserve existing std_dev
                    'image_path': existing_point.get('image_path')  # Preserve existing image path
                })
            else:
                # New point - create with defaults
                default_image_path = os.path.join(last_project_folder, default_image_import_path, f"{point_number} 400x.jpg")
                new_table_data.append({
                    'id': point_id,
                    'x': x,
                    'y': y,
                    'hv': None,  # Null HV for new points
                    'std_dev': None,  # Null std_dev for new points
                    'image_path': default_image_path
                })
        
        # Replace table data
        self.table_data = new_table_data
        
        # Rebuild table
        self.rebuildTable()
        
        print(f"[green]Tabla sincronizada con {len(self.table_data)} puntos del Mapeado[/green]")
    
    def rebuildTable(self):
        """Rebuild the entire table with current data."""
        if not dpg.does_item_exist("data_table"):
            return
        
        # Clear existing rows
        children = dpg.get_item_children("data_table", slot=1)
        if children:
            for child in children:
                dpg.delete_item(child)
        
        # Clear existing textures
        for texture_tag in self.image_textures.values():
            if dpg.does_item_exist(texture_tag):
                dpg.delete_item(texture_tag)
        self.image_textures.clear()
        
        # Add rows for each data point
        for i, data in enumerate(self.table_data):
            with dpg.table_row(parent="data_table", tag=f"table_row_{i}"):
                # Column 1: ID (read-only)
                dpg.add_text(data['id'])
                
                # Column 2: X (read-only)
                dpg.add_text(f"{data['x']:.3f}")
                
                # Column 3: Y (read-only)
                dpg.add_text(f"{data['y']:.3f}")
                
                # Column 4: HV (editable)
                dpg.add_input_float(
                    default_value=data['hv'] if data['hv'] is not None else 0.0,
                    width=100,
                    format="%.1f",
                    tag=f"table_hv_{i}",
                    callback=lambda s, v, u: self.onValueChange(u, 'hv', v),
                    user_data=i,
                    step=0,
                    step_fast=0
                )
                
                # Column 5: Std Dev (read-only display)
                std_dev_text = f"±{data['std_dev']:.2f}" if data.get('std_dev') is not None else "-"
                dpg.add_text(std_dev_text, tag=f"table_stddev_{i}")
                
                # Column 6: Image Path (file selector)
                dpg.add_button(
                    label=data['image_path'] if data['image_path'] else "Seleccionar...",
                    width=-1,
                    tag=f"table_path_{i}",
                    callback=lambda s, a, u: self.selectImageFile(u),
                    user_data=i
                )
                
                # Column 7: Image thumbnail
                self.addImageThumbnail(i, data['image_path'])
    
    def addImageThumbnail(self, index, image_path):
        """Add image thumbnail to table cell."""
        # Check if file exists
        if not os.path.isfile(image_path):
            dpg.add_text("(Sin imagen)", tag=f"table_thumb_{index}")
            return
        
        try:
            # Load image
            width, height, channels, data = dpg.load_image(image_path)
            
            # Calculate thumbnail size (max 140x140)
            max_size = 140
            if width > height:
                thumb_width = max_size
                thumb_height = int(height * max_size / width)
            else:
                thumb_height = max_size
                thumb_width = int(width * max_size / height)
            
            # Create texture
            texture_tag = f"table_texture_{index}"
            if dpg.does_item_exist(texture_tag):
                dpg.delete_item(texture_tag)
            
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, data, tag=texture_tag)
            
            self.image_textures[index] = texture_tag
            
            # Add image button (clickable thumbnail)
            dpg.add_image_button(
                texture_tag, 
                width=thumb_width, 
                height=thumb_height, 
                tag=f"table_thumb_{index}",
                callback=lambda s, a, u: self.goToVickersWithImage(u),
                user_data=index
            )
            
        except Exception as e:
            dpg.add_text(f"(Error: {str(e)[:20]})", tag=f"table_thumb_{index}")
            print(f"[red]Error cargando imagen {image_path}: {e}[/red]")
    
    def onValueChange(self, row_index, field, new_value):
        """Handle changes to editable fields."""
        if row_index < len(self.table_data):
            self.table_data[row_index][field] = new_value
            print(f"[cyan]Fila {row_index + 1}, {field} actualizado: {new_value}[/cyan]")
    
    def selectImageFile(self, row_index):
        """Open file dialog to select image file for a specific row."""
        def file_callback(sender, app_data):
            if app_data and 'file_path_name' in app_data:
                file_path = app_data['file_path_name']
                # Update table data
                self.table_data[row_index]['image_path'] = file_path
                print(f"[cyan]Fila {row_index + 1}, imagen actualizada: {file_path}[/cyan]")
                
                # Update button label to show new path
                if dpg.does_item_exist(f"table_path_{row_index}"):
                    dpg.set_item_label(f"table_path_{row_index}", file_path)
                
                # Rebuild the entire table to update thumbnail properly
                self.rebuildTable()
        
        # Create file dialog if not exists
        if not dpg.does_item_exist("table_file_dialog"):
            from config import get_preference
            
            # Use last project folder or current directory as default
            default_path = get_preference("last_project_folder") or "."
            
            with dpg.file_dialog(
                directory_selector=False,
                show=False,
                callback=file_callback,
                tag="table_file_dialog",
                width=700,
                height=400,
                modal=True,
                default_path=default_path
            ):
                dpg.add_file_extension(".jpg")
                dpg.add_file_extension(".jpeg")
                dpg.add_file_extension(".png")
                dpg.add_file_extension(".bmp")
                dpg.add_file_extension(".tif")
                dpg.add_file_extension(".tiff")
        else:
            # Update default path if dialog already exists
            from config import get_preference
            default_path = get_preference("last_project_folder") or "."
            dpg.configure_item("table_file_dialog", default_path=default_path)
        
        # Update callback with current row index
        dpg.set_item_callback("table_file_dialog", file_callback)
        dpg.show_item("table_file_dialog")
    
    def goToVickers(self, row_index):
        """Switch to Vickers tab for hardness calculation."""
        # Switch to first tab (Vickers)
        if dpg.does_item_exist("tab_bar"):
            dpg.set_value("tab_bar", "tab_vickers")
        
        point_id = self.table_data[row_index]['id']
        print(f"[green]Cambiando a tab Vickers para calcular dureza del punto {point_id}[/green]")
    
    def goToVickersWithImage(self, row_index):
        """Switch to Vickers tab and load the image for this point."""
        if row_index >= len(self.table_data):
            return
        
        image_path = self.table_data[row_index]['image_path']
        
        # Check if file exists
        if not os.path.isfile(image_path):
            print(f"[yellow]Imagen no encontrada: {image_path}[/yellow]")
            self.goToVickers(row_index)
            return
        
        # Switch to Vickers tab
        if dpg.does_item_exist("tab_bar"):
            dpg.set_value("tab_bar", "tab_vickers")
        
        point_id = self.table_data[row_index]['id']
        print(f"[green]Cambiando a tab Vickers y cargando imagen para punto {point_id}[/green]")
        
        # Load image in Vickers tab
        self.loadImageInVickers(image_path)
        
        # Reset Vickers measurements to start fresh
        vickers = self.callbacks.imageProcessing
        vickers.resetVickersMeasurement()
        
        # Set current index in Vickers callback
        vickers.current_table_index = row_index
        
        print(f"[cyan]Mediciones reiniciadas para punto {point_id}[/cyan]")
    
    def loadImageInVickers(self, image_path):
        """Load an image directly into the Vickers tab plot."""
        # Access Vickers callback (stored as imageProcessing)
        vickers = self.callbacks.imageProcessing
        
        # Split path into directory and filename
        file_dir = os.path.dirname(image_path)
        file_name = os.path.basename(image_path)
        
        # Set file path and name
        vickers.filePath = file_dir
        vickers.fileName = file_name
        
        # Update UI text elements (these are text items, need to configure, not set_value)
        if dpg.does_item_exist("file_name_text"):
            dpg.configure_item("file_name_text", default_value="Archivo: " + file_name)
        if dpg.does_item_exist("file_path_text"):
            dpg.configure_item("file_path_text", default_value="Ruta: " + file_dir)
        
        try:
            # Load image
            width, height, channels, data = dpg.load_image(image_path)
            
            # Store image dimensions
            vickers.image_width = width
            vickers.image_height = height
            vickers.current_image_path = image_path
            
            # Store original and current image data
            vickers.original_image_data = [data[i] for i in range(len(data))]
            vickers.current_image_data = vickers.original_image_data
            
            # Get calibration
            from config import get_preference
            calibration = get_preference("vickers_calibration", default=1.0)
            real_width = int(width * calibration)
            real_height = int(height * calibration)
            
            # Delete existing image series
            if dpg.does_item_exist("image_series"):
                dpg.delete_item("image_series")
            
            # Delete existing texture
            if dpg.does_item_exist("loaded_image_texture"):
                dpg.delete_item("loaded_image_texture")
            
            # Create texture
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, data, tag="loaded_image_texture")
            
            # Add image series to plot (using correct axis tag and bounds format)
            if dpg.does_item_exist("Processing_y_axis"):
                dpg.add_image_series(
                    "loaded_image_texture",
                    bounds_min=(0, 0),
                    bounds_max=(real_width, real_height),
                    parent="Processing_y_axis",
                    tag="image_series",
                    label=file_name[-34:-4] if len(file_name) > 34 else file_name[:-4]
                )
            
            # Fit plot axes (using correct axis tags)
            if dpg.does_item_exist("Processing_x_axis"):
                dpg.fit_axis_data("Processing_x_axis")
            if dpg.does_item_exist("Processing_y_axis"):
                dpg.fit_axis_data("Processing_y_axis")
            
            print(f"[green]Imagen cargada: {file_name} ({width}x{height})[/green]")
            
        except Exception as e:
            print(f"[red]Error cargando imagen en Vickers: {e}[/red]")
    
    def loadDefaultImages(self, sender=None, app_data=None):
        """Load default images for each point from <last_project_folder>/<default_image_import_path>/<n> 400x.(jpg|png)."""
        if len(self.table_data) == 0:
            print("[yellow]No hay puntos en la tabla. Cargue o actualice la tabla primero.[/yellow]")
            return
        
        # Get last project folder (or current directory as fallback)
        last_project_folder = get_preference("last_project_folder", default=".")
        
        # Get default image import path from config
        config = get_config()
        default_image_import_path = config['Paths'].get('default_image_import_path', 'images/')
        
        # Construct full images folder path
        images_folder = os.path.join(last_project_folder, default_image_import_path)
        
        print(f"[cyan]Cargando imágenes default desde: {images_folder}[/cyan]")
        
        updated_count = 0
        for i, data in enumerate(self.table_data):
            # Extract point number from ID (e.g., "P1" -> 1)
            point_id = data['id']
            if point_id.startswith('P'):
                try:
                    point_number = int(point_id[1:])
                except ValueError:
                    print(f"[yellow]ID inválido: {point_id}[/yellow]")
                    continue
            else:
                continue
            
            # Try to find image with extensions .jpg or .png
            base_name = f"{point_number} 400x"
            image_path = None
            
            for ext in ['.jpg', '.png', '.jpeg', '.JPG', '.PNG', '.JPEG']:
                potential_path = os.path.join(images_folder, base_name + ext)
                if os.path.isfile(potential_path):
                    image_path = potential_path
                    break
            
            if image_path:
                # Update table data
                self.table_data[i]['image_path'] = image_path
                updated_count += 1
                print(f"[green]  {point_id}: {image_path}[/green]")
            else:
                print(f"[yellow]  {point_id}: No se encontró imagen '{ base_name}.jpg/.png'[/yellow]")
        
        # Rebuild table to update UI and thumbnails
        self.rebuildTable()
        
        print(f"[green]Imágenes default cargadas: {updated_count}/{len(self.table_data)} puntos[/green]")
            
