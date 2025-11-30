import os
import io
import time
import threading
import numpy as np
import dearpygui.dearpygui as dpg
from rich import print
from config import get_preference, save_preference

try:
    import plotly.graph_objects as go
    import plotly.io as pio
    from scipy.interpolate import griddata
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("[yellow]plotly/scipy no disponibles. Instale con: pip install plotly scipy[/yellow]")

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[yellow]matplotlib no disponible. Instale con: pip install matplotlib[/yellow]")


class HMPlotCB:
    def __init__(self, callbacks) -> None:
        self.callbacks = callbacks  # Reference to main callbacks to access data table
        self.colorscale = "Viridis"
        self.interpolation = "cubic"
        self.show_points = False
        self.show_lines = False  # Show contour lines
        self.show_surface_overlay = False  # Show surface image overlay
        self.grid_resolution = 500  # Grid resolution for interpolation
        self.contour_levels = 40  # Number of contour levels
        self.figure_scale = get_preference("heatmap_figure_scale", default=1.0)  # Figure size multiplier
        self.last_figure = None
        self.heatmap_texture = None
        self.last_heatmap_image_path = None  # Store path to last generated heatmap image
        self.surface_texture = None  # Texture for surface image overlay

    def _hide_progress(self):
        """Hide progress bar and text."""
        if dpg.does_item_exist("hm_progress_bar"):
            dpg.configure_item("hm_progress_bar", show=False)
        if dpg.does_item_exist("hm_progress_text"):
            dpg.configure_item("hm_progress_text", show=False)

    def _prepare_data(self):
        """Helper to prepare data for plotting."""
        if not hasattr(self.callbacks, 'dataTable'):
            print("[red]Data Table callback no disponible[/red]")
            return None

        table_data = self.callbacks.dataTable.table_data
        
        if len(table_data) == 0:
            print("[yellow]No hay datos en la tabla para generar el mapa de calor[/yellow]")
            if dpg.does_item_exist("hm_plot_info_text"):
                dpg.set_value("hm_plot_info_text", "No hay datos disponibles. Agregue puntos en la Tabla.")
            return None
        
        # Filter points with HV values
        points_with_hv = [(row['x'], row['y'], row['hv']) for row in table_data if row['hv'] is not None and row['hv'] > 0]
        
        if len(points_with_hv) < 3:
            print(f"[yellow]Se necesitan al menos 3 puntos con valores HV. Actuales: {len(points_with_hv)}[/yellow]")
            if dpg.does_item_exist("hm_plot_info_text"):
                dpg.set_value("hm_plot_info_text", f"Se necesitan al menos 3 puntos con HV. Actuales: {len(points_with_hv)}")
            return None
        
        print(f"[green]Generando mapa de calor con {len(points_with_hv)} puntos...[/green]")
        
        # Extract x, y, z data
        x_data = np.array([p[0] for p in points_with_hv])
        y_data = np.array([p[1] for p in points_with_hv])
        z_data = np.array([p[2] for p in points_with_hv])
        
        # Create grid for interpolation
        x_min, x_max = x_data.min(), x_data.max()
        y_min, y_max = y_data.min(), y_data.max()
        
        # Add padding
        x_range = x_max - x_min
        y_range = y_max - y_min
        padding = 0.1
        x_min -= x_range * padding
        x_max += x_range * padding
        y_min -= y_range * padding
        y_max += y_range * padding
        
        # Create grid
        xi = np.linspace(x_min, x_max, self.grid_resolution)
        yi = np.linspace(y_min, y_max, self.grid_resolution)
        xi_grid, yi_grid = np.meshgrid(xi, yi)
        
        # Interpolate
        method = self.interpolation if self.interpolation != 'linear' else 'linear'
        zi_grid = griddata((x_data, y_data), z_data, (xi_grid, yi_grid), method=method)

        return {
            'x_data': x_data, 'y_data': y_data, 'z_data': z_data,
            'xi': xi, 'yi': yi, 'zi_grid': zi_grid,
            'bounds': (x_min, x_max, y_min, y_max)
        }

    def generateWebHeatMap(self, sender=None, app_data=None):
        """Generate heat map visualization in browser using Plotly."""
        if not PLOTLY_AVAILABLE:
            print("[red]plotly/scipy no disponibles[/red]")
            return

        # Show progress bar
        if dpg.does_item_exist("hm_progress_bar"):
            dpg.configure_item("hm_progress_bar", show=True)
            dpg.set_value("hm_progress_bar", 0.0)
        if dpg.does_item_exist("hm_progress_text"):
            dpg.configure_item("hm_progress_text", show=True)
        
        # Run generation in thread
        thread = threading.Thread(target=self._generateWebHeatMapThread)
        thread.start()
    
    def _generateWebHeatMapThread(self):
        """Thread function for web heat map generation."""
        try:
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.1)
            
            data = self._prepare_data()
            if not data:
                self._hide_progress()
                return
            
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.3)

            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.5)
            
            # Create Plotly figure
            fig = go.Figure()

            # Add Contour trace
            fig.add_trace(go.Contour(
                z=data['zi_grid'],
                x=data['xi'],
                y=data['yi'],
                colorscale=self.colorscale,
                ncontours=self.contour_levels,
                contours=dict(
                    coloring='heatmap',
                    showlines=self.show_lines,
                ),
                colorbar=dict(
                    title=dict(
                        text='Dureza Vickers (HV)',
                        side='right'
                    )
                ),
                hoverinfo='x+y+z',
                hovertemplate='X: %{x:.2f} mm<br>Y: %{y:.2f} mm<br>HV: %{z:.1f}<extra></extra>'
            ))
            
            # Plot measurement points if enabled
            if self.show_points:
                fig.add_trace(go.Scatter(
                    x=data['x_data'],
                    y=data['y_data'],
                    mode='markers+text',
                    marker=dict(
                        color='black',
                        size=6,
                        line=dict(width=2, color='white')
                    ),
                    text=[f"P{i+1}<br>{z:.1f}HV" for i, z in enumerate(data['z_data'])],
                    textposition="top center",
                    textfont=dict(color='white'),
                    name='Puntos de Medición',
                    hoverinfo='text+x+y',
                    hovertemplate='<b>%{text}</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>'
                ))
            
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.7)
        
            # Update layout
            fig.update_layout(
                title='Mapa de Calor de Durezas Vickers',
                xaxis_title='X (mm)',
                yaxis_title='Y (mm)',
                template='plotly_dark',
                autosize=True,
                margin=dict(l=50, r=50, b=50, t=80),
                yaxis=dict(
                    scaleanchor="x",
                    scaleratio=1
                )
            )
            
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.9)
            
            self.last_figure = fig
            fig.show() # <-- ¡Esto inicia el servidor y abre el navegador!
            
            if dpg.does_item_exist("hm_plot_info_text"):
                self._update_info_text(data['z_data'], len(data['x_data']))
                current_text = dpg.get_value("hm_plot_info_text")
                dpg.set_value("hm_plot_info_text", current_text + "\n\nEl gráfico interactivo se ha abierto en su navegador web.")
            
            if dpg.does_item_exist("hm_plot_placeholder"):
                dpg.set_value("hm_plot_placeholder", "El gráfico interactivo se está mostrando en una ventana externa (navegador).")
            
            # Update progress to complete
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 1.0)
            
            # Hide progress after delay
            time.sleep(0.5)
            self._hide_progress()
        
        except Exception as e:
            print(f"[red]Error generando mapa web: {e}[/red]")
            self._hide_progress()

    def generateLocalHeatMap(self, sender=None, app_data=None):
        """Generate heat map visualization inside Dear PyGui using Matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            print("[red]matplotlib no disponible[/red]")
            return

        # Show progress bar
        if dpg.does_item_exist("hm_progress_bar"):
            dpg.configure_item("hm_progress_bar", show=True)
            dpg.set_value("hm_progress_bar", 0.0)
        if dpg.does_item_exist("hm_progress_text"):
            dpg.configure_item("hm_progress_text", show=True)
        
        # Run generation in thread
        thread = threading.Thread(target=self._generateLocalHeatMapThread)
        thread.start()
    
    def _generateLocalHeatMapThread(self):
        """Thread function for local heat map generation."""
        try:
            # Read checkbox state at generation time
            if dpg.does_item_exist("hm_show_overlay_checkbox"):
                self.show_surface_overlay = dpg.get_value("hm_show_overlay_checkbox")
                print(f"[cyan]Estado del overlay al generar: {self.show_surface_overlay}[/cyan]")
            
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.1)
            
            data = self._prepare_data()
            if not data:
                self._hide_progress()
                return
            
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.3)
            
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.5)
            
            x_min, x_max, y_min, y_max = data['bounds']
            width_data = x_max - x_min
            height_data = y_max - y_min
            aspect_ratio = height_data / width_data
            
            # Create matplotlib figure with high DPI for better resolution
            # Set figure size to match aspect ratio to avoid distortion when filling axes
            base_width = 10
            fig_width = base_width
            fig_height = base_width * aspect_ratio
            
            # Use transparent background if overlay is enabled
            fig_bg = 'none' if self.show_surface_overlay else 'white'
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300, facecolor=fig_bg)
            
            # Ensure axes fill the figure completely
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            ax.axis('off')
            ax.patch.set_alpha(0.0 if self.show_surface_overlay else 1.0)
            
            # Plot filled contours with transparency if overlay is enabled
            # Map plotly colorscale names to matplotlib colormaps if possible
            cmap = self.colorscale.lower()
            if cmap == 'bluered': cmap = 'coolwarm' # Approximation
            
            # Adjust alpha based on overlay mode
            contour_alpha = 0.5 if self.show_surface_overlay else 1.0
            
            try:
                im = ax.contourf(data['xi'], data['yi'], data['zi_grid'], levels=self.contour_levels, cmap=cmap, alpha=contour_alpha)
            except ValueError:
                # Fallback if colormap not found
                im = ax.contourf(data['xi'], data['yi'], data['zi_grid'], levels=self.contour_levels, cmap='viridis', alpha=contour_alpha)
            
            # Optionally add contour lines
            if self.show_lines:
                ax.contour(data['xi'], data['yi'], data['zi_grid'], levels=self.contour_levels, colors='black', linewidths=0.5, alpha=0.5)
            
            # Add points and labels directly to the matplotlib plot
            if self.show_points:
                ax.scatter(data['x_data'], data['y_data'], c='black', s=40, edgecolors='white', linewidths=1, zorder=10)
                for i, (x, y, z) in enumerate(zip(data['x_data'], data['y_data'], data['z_data'])):
                    ax.annotate(f"P{i+1}\n{z:.1f}HV", (x, y), 
                               xytext=(0, 8), textcoords='offset points', 
                               ha='center', va='bottom',
                               fontsize=7, color='black', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.1', fc='white', alpha=0.3, ec='none')
                    )

            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', transparent=True)
            buf.seek(0)
            
            # Save to project maps folder
            from config import get_preference
            last_project_folder = get_preference("last_project_folder", default=".")
            maps_folder = os.path.join(last_project_folder, "maps")
            os.makedirs(maps_folder, exist_ok=True)
            project_heatmap_path = os.path.join(maps_folder, "heatmap.png")
            fig.savefig(project_heatmap_path, format='png', transparent=False, facecolor='white', bbox_inches='tight', dpi=300)
            self.last_heatmap_image_path = project_heatmap_path
            print(f"[cyan]Mapa de calor guardado en: {project_heatmap_path}[/cyan]")
            
            # Store figure for export (keep reference before closing)
            self.last_figure = fig
            
            # Don't close fig immediately, keep it for export
            # plt.close(fig)
            
            from PIL import Image
            img = Image.open(buf)
            img_array = np.array(img)
            
            # Convert RGBA to flat array normalized to 0-1
            height, width = img_array.shape[:2]
            img_flat = (img_array.flatten() / 255.0).tolist()
            
            # Delete old texture if exists
            if self.heatmap_texture and dpg.does_item_exist(self.heatmap_texture):
                dpg.delete_item(self.heatmap_texture)
                self.heatmap_texture = None
            
            # Create texture with unique tag
            import time
            texture_tag = f"hm_texture_{int(time.time() * 1000000)}"
            with dpg.texture_registry():
                self.heatmap_texture = dpg.add_static_texture(width, height, img_flat, tag=texture_tag)
            
            # Update progress
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 0.8)
            
            # Clear previous plot/image
            dpg.delete_item("HMPlotDisplayChild", children_only=True)
            
            # Create Plot
            with dpg.plot(parent="HMPlotDisplayChild", label="Mapa de Calor Local (Matplotlib)", height=-1, width=-1, equal_aspects=True):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="X (mm)")
                with dpg.plot_axis(dpg.mvYAxis, label="Y (mm)") as y_axis:
                    # Add surface image overlay if enabled
                    if self.show_surface_overlay and hasattr(self.callbacks, 'heatMap'):
                        try:
                            surface_image_path = self.callbacks.heatMap.current_image_path
                            if surface_image_path and os.path.exists(surface_image_path):
                                print(f"[cyan]Cargando imagen de superficie: {surface_image_path}[/cyan]")
                                # Load surface image and get its bounds
                                from PIL import Image as PILImage
                                surface_img = PILImage.open(surface_image_path)
                                surf_width, surf_height = surface_img.size
                                
                                # Get calibration and origin offset from heatMap
                                from config import get_preference
                                calibration = get_preference("heatmap_calibration", default=0.001)  # mm/pixel
                                origin_offset = self.callbacks.heatMap.origin_offset  # [x_offset, y_offset] in mm
                                
                                print(f"[cyan]Calibración: {calibration} mm/px, Origen: {origin_offset}[/cyan]")
                                
                                # Calculate bounds of surface image in mm coordinates
                                # The origin_offset shifts the coordinate system, so we need to subtract it
                                # from the image position (same logic as in _heatMapCB.py updateImageBounds)
                                surf_x_min = -origin_offset[0]
                                surf_y_min = -origin_offset[1]
                                surf_x_max = surf_x_min + surf_width * calibration
                                surf_y_max = surf_y_min + surf_height * calibration
                                
                                print(f"[cyan]Límites superficie: X[{surf_x_min:.2f}, {surf_x_max:.2f}] Y[{surf_y_min:.2f}, {surf_y_max:.2f}][/cyan]")
                                
                                # Convert surface image to texture
                                surf_img_array = np.array(surface_img.convert('RGBA'))
                                surf_height_px, surf_width_px = surf_img_array.shape[:2]
                                surf_img_flat = (surf_img_array.flatten() / 255.0).tolist()
                                
                                # Delete old surface texture if exists
                                if self.surface_texture and dpg.does_item_exist(self.surface_texture):
                                    dpg.delete_item(self.surface_texture)
                                    self.surface_texture = None
                                
                                # Create texture
                                import time
                                surf_texture_tag = f"surface_texture_{int(time.time() * 1000000)}"
                                with dpg.texture_registry():
                                    self.surface_texture = dpg.add_static_texture(surf_width_px, surf_height_px, surf_img_flat, tag=surf_texture_tag)
                                
                                print(f"[green]Textura de superficie creada: {surf_width_px}x{surf_height_px}[/green]")
                                
                                # Add surface image with lower opacity
                                dpg.add_image_series(self.surface_texture, [surf_x_min, surf_y_min], [surf_x_max, surf_y_max], 
                                                   label="Imagen de Superficie", uv_min=(0, 1), uv_max=(1, 0))
                                print(f"[green]Imagen de superficie agregada al plot[/green]")
                            else:
                                print(f"[yellow]No se encontró imagen de superficie: {surface_image_path}[/yellow]")
                        except Exception as surf_error:
                            print(f"[yellow]Error cargando imagen de superficie: {surf_error}[/yellow]")
                            import traceback
                            traceback.print_exc()
                    
                    # Add the heatmap image series on top
                    dpg.add_image_series(self.heatmap_texture, [x_min, y_min], [x_max, y_max], label="Mapa de Calor")
            
            # Update info text
            if dpg.does_item_exist("hm_plot_info_text"):
                self._update_info_text(data['z_data'], len(data['x_data']))
                        
            # Update progress to complete
            if dpg.does_item_exist("hm_progress_bar"):
                dpg.set_value("hm_progress_bar", 1.0)
            
            # Hide progress after delay
            time.sleep(0.5)
            self._hide_progress()

        except Exception as e:
            print(f"[red]Error generando mapa local: {e}[/red]")
            if dpg.does_item_exist("hm_plot_info_text"):
                dpg.set_value("hm_plot_info_text", f"Error generando mapa local: {e}")
            self._hide_progress()

    def _update_info_text(self, z_data, num_points):
        hv_min, hv_max = z_data.min(), z_data.max()
        hv_avg = z_data.mean()
        dpg.set_value("hm_plot_info_text", 
                        f"Puntos: {num_points}\n"
                        f"HV mín: {hv_min:.1f}\n"
                        f"HV máx: {hv_max:.1f}\n"
                        f"HV promedio: {hv_avg:.1f}\n"
                        f"Escala: {self.colorscale}\n"
                        f"Interpolación: {self.interpolation}")

    def generateHeatMap(self, sender=None, app_data=None):
        # Legacy wrapper
        self.generateWebHeatMap(sender, app_data)


    def onColorScaleChange(self, sender, app_data):
        """Handle color scale change."""
        # Map matplotlib names to plotly if needed, or just use capitalized
        self.colorscale = app_data
        # Simple mapping for common names
        if self.colorscale.lower() == 'viridis': self.colorscale = 'Viridis'
        elif self.colorscale.lower() == 'plasma': self.colorscale = 'Plasma'
        elif self.colorscale.lower() == 'inferno': self.colorscale = 'Inferno'
        elif self.colorscale.lower() == 'magma': self.colorscale = 'Magma'
        elif self.colorscale.lower() == 'cividis': self.colorscale = 'Cividis'
        elif self.colorscale.lower() == 'hot': self.colorscale = 'Hot'
        elif self.colorscale.lower() == 'cool': self.colorscale = 'Bluered' # Approx
        elif self.colorscale.lower() == 'rainbow': self.colorscale = 'Rainbow'
        
        print(f"[cyan]Escala de color cambiada a: {self.colorscale}[/cyan]")
        # Regenerate if we have data (optional, maybe user wants to click generate)
        # self.generateHeatMap()
    
    def onInterpolationChange(self, sender, app_data):
        """Handle interpolation method change."""
        self.interpolation = app_data
        # self.generateHeatMap()
    
    def onShowPointsChange(self, sender, app_data):
        """Handle show points toggle."""
        self.show_points = app_data
        print(f"[cyan]Mostrar puntos: {self.show_points}[/cyan]")
        # self.generateHeatMap()
    
    def onShowLinesChange(self, sender, app_data):
        """Handle show contour lines toggle."""
        self.show_lines = app_data
        print(f"[cyan]Mostrar líneas: {self.show_lines}[/cyan]")
        # self.generateHeatMap()
    
    def onShowSurfaceOverlayChange(self, sender, app_data):
        """Handle show surface overlay toggle."""
        self.show_surface_overlay = dpg.get_value(sender)
        print(f"[cyan]Mostrar imagen de superficie: {self.show_surface_overlay}[/cyan]")
        # Note: Don't auto-regenerate, let user click generate button again
        # This avoids issues with threading and losing the current map
    
    def onResolutionChange(self, sender, app_data):
        """Handle resolution/smoothness change."""
        self.grid_resolution = app_data
    
    def onLevelsChange(self, sender, app_data):
        """Handle contour levels change."""
        self.contour_levels = app_data
    
    def onFigureSizeChange(self, sender, app_data):
        """Handle figure size scale change."""
        self.figure_scale = app_data
        save_preference("heatmap_figure_scale", self.figure_scale)
    
    def exportHeatMap(self, sender=None, app_data=None):
        """Export heat map."""
        if self.last_figure is None:
            print("[yellow]Primero genere el mapa de calor[/yellow]")
            return

        # Create file dialog for export
        if not dpg.does_item_exist("hm_export_dialog"):
            from config import get_preference
            default_path = get_preference("last_project_folder") or "."
            
            with dpg.file_dialog(
                directory_selector=False,
                show=False,
                callback=self.saveHeatMapFile,
                tag="hm_export_dialog",
                width=700,
                height=400,
                default_filename="heatmap.png",
                default_path=default_path,
                modal=True
            ):
                dpg.add_file_extension(".png")
                dpg.add_file_extension(".html")
                dpg.add_file_extension(".pdf")
                dpg.add_file_extension(".svg")
        else:
            # Update default path if dialog already exists
            from config import get_preference
            default_path = get_preference("last_project_folder") or "."
            dpg.configure_item("hm_export_dialog", default_path=default_path)
        
        dpg.show_item("hm_export_dialog")
    
    def saveHeatMapFile(self, sender, app_data):
        """Save heat map to file."""
        if app_data and 'file_path_name' in app_data:
            file_path = app_data['file_path_name']
            
            if self.last_figure is None:
                print("[red]No hay gráfico para exportar[/red]")
                return
            
            try:
                # Check if it's a Plotly figure or Matplotlib figure
                if hasattr(self.last_figure, 'write_html'):
                    # Plotly figure
                    if file_path.endswith('.html'):
                        self.last_figure.write_html(file_path)
                    else:
                        # Requires kaleido
                        self.last_figure.write_image(file_path)
                    print(f"[green]Mapa de calor exportado: {file_path}[/green]")
                else:
                    # Matplotlib figure
                    if file_path.endswith('.html'):
                        print("[yellow]HTML no soportado para mapas Matplotlib. Use PNG, PDF o SVG[/yellow]")
                        return
                    
                    # Save matplotlib figure
                    self.last_figure.savefig(file_path, format=file_path.split('.')[-1], 
                                            transparent=False, facecolor='white', 
                                            bbox_inches='tight', dpi=300)
                    print(f"[green]Mapa de calor exportado: {file_path}[/green]")
                    
            except Exception as e:
                print(f"[red]Error al exportar: {e}[/red]")
                if 'kaleido' in str(e).lower():
                    print("[yellow]Para exportar imágenes estáticas de Plotly instale kaleido: pip install -U kaleido[/yellow]")
