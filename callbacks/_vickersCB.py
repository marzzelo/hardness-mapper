import os
import math
import threading
from datetime import datetime
from time import time
import dearpygui.dearpygui as dpg
from rich import print
from config import get_preference, save_preference

class VickersCB:
    def __init__(self, callbacks=None) -> None:

        self.callbacks = callbacks  # Reference to parent callbacks
        self.filePath = None
        self.fileName = None
        self.exportImageFilePath = None
        self.currentTab = None
        self.image_width = None
        self.image_height = None
        self.current_table_index = None  # Track current point from data table
        
        # Multi-measurement structure
        self.n_measurements = get_preference("vickers_n_measurements", default=2)  # Number of measurements to perform
        self.current_measurement = 0  # Current measurement index (0-based)
        self.measurements = []  # List of measurements, each with {points: [(x,y)...], d1: float, d2: float, d_avg: float, hv: float}
        self.current_points = []  # Points for current measurement being marked
        
        self.vickers_series_tags = []  # List of series tags for cleanup
        self.processing_mode = "Marcar Puntos"  # Current mode: "Mover Imagen" or "Marcar Puntos"
        self.original_image_data = None  # Store original image data for reset
        self.current_image_data = None  # Store current working image data
        self.current_image_path = None  # Store current image path for reload

    def openFile(self, sender, app_data):
        # Debug info
        print("OK was clicked.")
        print("Sender: ", sender)
        print("App Data: ", app_data)

        self.filePath = app_data["current_path"]
        self.fileName = list(app_data["selections"].keys())[0]  # Get the first selected file name
        full_path = os.path.join(self.filePath, self.fileName)

        if os.path.isfile(full_path) is False:
            print(f"[red]The selected file does not exist: {full_path}[/red]")
            return

        dpg.set_value("file_name_text", "Archivo: " + self.fileName)
        dpg.set_value("file_path_text", "Ruta: " + self.filePath)

        # Load and display the image
        try:
            width, height, channels, data = dpg.load_image(full_path)

            # Store image dimensions
            self.image_width = width
            self.image_height = height
            
            # Store current image path for reload
            self.current_image_path = full_path
            
            # Store original and current image data (convert to list for consistency)
            self.original_image_data = [data[i] for i in range(len(data))]
            self.current_image_data = self.original_image_data

            # Get calibration value to convert pixels to µm
            calibration = get_preference("vickers_calibration", default=1.0)
            real_width = int(width * calibration)
            real_height = int(height * calibration)

            # Delete existing image series first
            if dpg.does_item_exist("image_series"):
                dpg.delete_item("image_series")

            # Delete existing texture if it exists
            if dpg.does_item_exist("loaded_image_texture"):
                dpg.delete_item("loaded_image_texture")

            # Create texture for modifications
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, data, tag="loaded_image_texture")

            # Add image series to the plot with µm coordinates
            dpg.add_image_series(
                "loaded_image_texture",
                bounds_min=(0, 0),
                bounds_max=(real_width, real_height),
                parent="Processing_y_axis",
                tag="image_series",
                label=self.fileName[-34:-4],  # Remove file extension from label and limit to last 30 characters
            )

            # Reset axis to auto mode first
            dpg.set_axis_limits_auto("Processing_x_axis")
            dpg.set_axis_limits_auto("Processing_y_axis")

            # Then fit the data to show the full image
            dpg.fit_axis_data("Processing_x_axis")
            dpg.fit_axis_data("Processing_y_axis")

            # Clear previous Vickers measurement
            self.resetVickersMeasurement()

            print(f"[green]Image loaded successfully: {width}x{height}[/green]")

        except Exception as e:
            import traceback

            print(f"[red]Error loading image: {e}[/red]")
            traceback.print_exc()

    def cancelImportImage(self, sender=None, app_data=None):
        # Debug info
        print("CANCEL was clicked.")
        print("Sender: ", sender)
        print("App Data: ", app_data)

        dpg.hide_item("file_dialog_id")

    def updateImageScale(self):
        """
        Update the image series bounds when calibration changes.
        Recalculates µm coordinates based on stored pixel dimensions.
        """
        if self.image_width is None or self.image_height is None:
            return  # No image loaded

        if not dpg.does_item_exist("image_series"):
            return  # Image series doesn't exist

        # Get current calibration
        calibration = get_preference("vickers_calibration", default=1.0)

        # Calculate new bounds in µm (rounded to integers)
        real_width = int(self.image_width * calibration)
        real_height = int(self.image_height * calibration)

        # Update image series bounds
        dpg.configure_item("image_series", bounds_max=(real_width, real_height))

        # Re-fit axes to new bounds
        dpg.fit_axis_data("Processing_x_axis")
        dpg.fit_axis_data("Processing_y_axis")

        print(f"[green]Image scale updated: {real_width}x{real_height} µm (calibration: {calibration} µm/pixel)[/green]")

    def onCalibrationChange(self, sender, new_value):
        """
        Callback for calibration input changes.
        Saves the new value and updates the image scale.
        """
        save_preference("vickers_calibration", new_value)
        self.updateImageScale()

    def onNMeasurementsChange(self, sender, new_value):
        """
        Callback for n_measurements input changes.
        Saves the new value and resets measurements.
        """
        save_preference("vickers_n_measurements", new_value)
        self.n_measurements = new_value
        self.resetVickersMeasurement()
        print(f"[yellow]Número de mediciones configurado a: {new_value}[/yellow]")

    def onProcessingModeChange(self, sender, new_value):
        """
        Callback for processing mode radio button.
        Switches between "Mover Imagen" and "Marcar Puntos" modes.
        """
        self.processing_mode = new_value

        # Update plot pan button based on mode
        if new_value == "Mover Imagen":
            # Enable left-click pan
            dpg.configure_item("ProcessingPlotParent", pan_button=dpg.mvMouseButton_Left)
            print("[yellow]Modo: Mover Imagen (click izquierdo para pan)[/yellow]")
        else:  # "Marcar Puntos"
            # Disable left-click pan (use right-click instead)
            dpg.configure_item("ProcessingPlotParent", pan_button=dpg.mvMouseButton_Right)
            print("[yellow]Modo: Marcar Puntos (click izquierdo para marcar)[/yellow]")

    def onPlotClick(self, sender, app_data):
        """
        Handle mouse clicks on the plot for Vickers indentation measurement.
        Captures up to 4 points per measurement, then moves to next measurement.
        Only active when mode is "Marcar Puntos".
        """
        # Only process clicks in "Marcar Puntos" mode
        if self.processing_mode != "Marcar Puntos":
            return

        # Only process clicks when hovering over the plot
        if not dpg.is_item_hovered("ProcessingPlotParent"):
            return

        # Get plot coordinates
        plot_coords = dpg.get_plot_mouse_pos()

        if plot_coords is None:
            return

        # Block clicks if all measurements are complete
        if len(self.measurements) >= self.n_measurements:
            print(f"[yellow]⚠ Todas las mediciones completadas ({self.n_measurements}/{self.n_measurements}). Presione 'Reset Mediciones' para continuar.[/yellow]")
            return

        # Check if current measurement is complete (4 points)
        if len(self.current_points) >= 4:
            # Move to next measurement
            self.current_measurement += 1
            self.current_points = []
            
            # Check if all measurements are complete
            if self.current_measurement >= self.n_measurements:
                print(f"[green]═══ Todas las mediciones completadas ({self.n_measurements}) ═══[/green]")
                return
            

        # Add point to current measurement
        self.current_points.append(plot_coords)
        total_points = self.current_measurement * 4 + len(self.current_points)
        print(f"[cyan]Medición {self.current_measurement + 1}, Punto {len(self.current_points)}: ({plot_coords[0]:.1f}, {plot_coords[1]:.1f}) µm[/cyan]")

        # Update UI
        dpg.set_value("vickers_current_measurement", f"{self.current_measurement + 1}/{self.n_measurements}")
        dpg.set_value("vickers_npoints", f"{len(self.current_points)}/4")

        # Draw geometry
        self.drawVickersGeometry()
        
        # If 4 points complete, save measurement and calculate
        if len(self.current_points) == 4:
            self.saveMeasurement()

    def drawVickersGeometry(self):
        """
        Draw Vickers measurement geometry progressively for current measurement.
        - Circles at each vertex (different colors)
        - Lines connecting vertices
        - Diagonals with length annotations when 4 points complete
        """
        # Clear previous drawings for current measurement
        for tag in self.vickers_series_tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
        self.vickers_series_tags.clear()

        num_points = len(self.current_points)
        if num_points == 0:
            return

        # Draw circles at each vertex using scatter series
        for i, (x, y) in enumerate(self.current_points):
            tag = f"vickers_point_{self.current_measurement}_{i}"
            dpg.add_scatter_series([x], [y], parent="Processing_y_axis", tag=tag)
            self.vickers_series_tags.append(tag)

        # Draw lines connecting vertices
        if num_points >= 2:
            # Line from P1 to P2
            tag = f"vickers_line_{self.current_measurement}_1_2"
            x_data = [self.current_points[0][0], self.current_points[1][0]]
            y_data = [self.current_points[0][1], self.current_points[1][1]]
            dpg.add_line_series(x_data, y_data, parent="Processing_y_axis", tag=tag)
            self.vickers_series_tags.append(tag)

        if num_points >= 3:
            # Line from P2 to P3
            tag = f"vickers_line_{self.current_measurement}_2_3"
            x_data = [self.current_points[1][0], self.current_points[2][0]]
            y_data = [self.current_points[1][1], self.current_points[2][1]]
            dpg.add_line_series(x_data, y_data, parent="Processing_y_axis", tag=tag)
            self.vickers_series_tags.append(tag)

        if num_points >= 4:
            # Line from P3 to P4
            tag = f"vickers_line_{self.current_measurement}_3_4"
            x_data = [self.current_points[2][0], self.current_points[3][0]]
            y_data = [self.current_points[2][1], self.current_points[3][1]]
            dpg.add_line_series(x_data, y_data, parent="Processing_y_axis", tag=tag)
            self.vickers_series_tags.append(tag)

            # Line from P4 to P1 (close the quadrilateral)
            tag = f"vickers_line_{self.current_measurement}_4_1"
            x_data = [self.current_points[3][0], self.current_points[0][0]]
            y_data = [self.current_points[3][1], self.current_points[0][1]]
            dpg.add_line_series(x_data, y_data, parent="Processing_y_axis", tag=tag)
            self.vickers_series_tags.append(tag)

            # Draw diagonals
            p1 = self.current_points[0]
            p2 = self.current_points[1]
            p3 = self.current_points[2]
            p4 = self.current_points[3]

            d1_length = math.sqrt((p3[0] - p1[0]) ** 2 + (p3[1] - p1[1]) ** 2)
            tag = f"vickers_diagonal_{self.current_measurement}_1_3"
            x_data = [p1[0], p3[0]]
            y_data = [p1[1], p3[1]]
            dpg.add_line_series(x_data, y_data, label=f"M{self.current_measurement + 1} D1: {d1_length:.2f} µm", parent="Processing_y_axis", tag=tag)
            self.vickers_series_tags.append(tag)

            # Diagonal 2: P2 to P4
            d2_length = math.sqrt((p4[0] - p2[0]) ** 2 + (p4[1] - p2[1]) ** 2)
            tag = f"vickers_diagonal_{self.current_measurement}_2_4"
            x_data = [p2[0], p4[0]]
            y_data = [p2[1], p4[1]]
            dpg.add_line_series(x_data, y_data, label=f"M{self.current_measurement + 1} D2: {d2_length:.2f} µm", parent="Processing_y_axis", tag=tag)
            self.vickers_series_tags.append(tag)

    def saveMeasurement(self):
        """
        Save current measurement (4 points) and calculate its diagonals and hardness.
        Updates the measurements table and recalculates averages.
        """
        if len(self.current_points) != 4:
            return
        
        p1, p2, p3, p4 = self.current_points
        
        # Calculate diagonals
        d1 = math.sqrt((p3[0] - p1[0]) ** 2 + (p3[1] - p1[1]) ** 2)
        d2 = math.sqrt((p4[0] - p2[0]) ** 2 + (p4[1] - p2[1]) ** 2)
        d_avg = (d1 + d2) / 2
        
        # Calculate Vickers hardness for this measurement
        load_kgf = get_preference("vickers_load", default=500.0) / 1000.0  # g to kgf
        d_mm = d_avg / 1000.0  # µm to mm
        
        if d_mm > 0:
            hv = 1.854 * load_kgf / (d_mm ** 2)
        else:
            hv = 0
        
        # Store measurement
        measurement = {
            "points": self.current_points.copy(),
            "d1": d1,
            "d2": d2,
            "d_avg": d_avg,
            "hv": hv
        }
        self.measurements.append(measurement)
        
        # Add row to table
        self.updateMeasurementsTable()
        
        # Update summary with averages
        self.updateMeasurementsSummary()
        
        # Print results
        print(f"[green]═══ Medición {len(self.measurements)} Completa ═══[/green]")
        print(f"[green]D1: {d1:.2f} µm | D2: {d2:.2f} µm | D_avg: {d_avg:.2f} µm | HV: {hv:.1f}[/green]")
        
        # Check if all measurements are complete
        if len(self.measurements) >= self.n_measurements:
            print(f"[green]✓ Todas las mediciones completadas ({self.n_measurements}/{self.n_measurements})[/green]")
            print("[yellow]Puede exportar el informe PDF o presionar 'Reset Mediciones' para un nuevo conjunto.[/yellow]")
            
            # Update HV value in data table with final average
            hv_values = [m["hv"] for m in self.measurements]
            hv_avg = sum(hv_values) / len(hv_values)
            
            # Calculate standard deviation
            if len(hv_values) > 1:
                variance = sum((x - hv_avg) ** 2 for x in hv_values) / (len(hv_values) - 1)
                std_dev = math.sqrt(variance)
            else:
                std_dev = 0.0
            
            self.updateTableHV(hv_avg, std_dev)
        else:
            # If not the last measurement, show waiting popup and schedule geometry clearing after 2 seconds
            next_measurement = len(self.measurements) + 1
            waiting_msg = f"Iniciar medici\u00f3n {next_measurement} de {self.n_measurements}"
            if dpg.does_item_exist("waiting_popup_text"):
                dpg.set_value("waiting_popup_text", waiting_msg)
            if dpg.does_item_exist("waiting_popup"):
                # Center the popup in the viewport
                viewport_width = dpg.get_viewport_width()
                viewport_height = dpg.get_viewport_height()
                popup_width = 400
                popup_height = 100
                dpg.configure_item("waiting_popup", 
                                 pos=[(viewport_width - popup_width) // 2, (viewport_height - popup_height) // 2],
                                 width=popup_width, height=popup_height)
                dpg.configure_item("waiting_popup", show=True)
            print(f"[cyan]Esperando 2 segundos antes de preparar la siguiente medición...[/cyan]")
            threading.Timer(2.0, self.clearCurrentGeometry).start()

    def clearCurrentGeometry(self):
        """Clear the geometry drawn for the current measurement to prepare for the next one."""
        # Clear all drawn series for current measurement
        for tag in self.vickers_series_tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)
        self.vickers_series_tags.clear()
        
        # Hide waiting popup
        if dpg.does_item_exist("waiting_popup"):
            dpg.configure_item("waiting_popup", show=False)
        
        print(f"[yellow]Geometría borrada. Lista para medición {len(self.measurements) + 1}/{self.n_measurements}[/yellow]")
    
    def updateTableHV(self, hv_value, std_dev=None):
        """Update HV value and standard deviation in data table if current image matches a table entry."""
        if not self.callbacks or not hasattr(self.callbacks, 'dataTable'):
            return
        
        if not self.current_image_path:
            return
        
        # Get current image full path
        current_full_path = self.current_image_path
        
        # Search for matching entry in data table
        data_table = self.callbacks.dataTable
        for i, row in enumerate(data_table.table_data):
            row_path = row.get('image_path', '')
            
            # Compare paths (normalize for comparison)
            if os.path.normpath(row_path) == os.path.normpath(current_full_path):
                # Update HV value and std_dev
                row['hv'] = hv_value
                if std_dev is not None:
                    row['std_dev'] = std_dev
                    print(f"[cyan]Actualizado HV={hv_value:.1f} ±{std_dev:.2f} para punto {row['id']} en la tabla[/cyan]")
                else:
                    print(f"[cyan]Actualizado HV={hv_value:.1f} para punto {row['id']} en la tabla[/cyan]")
                
                # Rebuild table to show updated value
                data_table.rebuildTable()
                break

    def updateMeasurementsTable(self):
        """Update the measurements table with all completed measurements."""
        if not dpg.does_item_exist("measurements_table"):
            return
        
        # Clear existing rows (keep header)
        children = dpg.get_item_children("measurements_table", slot=1)
        if children:
            for child in children:
                dpg.delete_item(child)
        
        # Add rows for each measurement
        for i, meas in enumerate(self.measurements):
            with dpg.table_row(parent="measurements_table"):
                dpg.add_text(f"{i+1}")
                dpg.add_text(f"4")
                dpg.add_text(f"{meas['d1']:.2f}")
                dpg.add_text(f"{meas['d2']:.2f}")
                dpg.add_text(f"{meas['d_avg']:.2f}")

    def updateMeasurementsSummary(self):
        """Calculate and display averages and standard deviation for all measurements."""
        if len(self.measurements) == 0:
            dpg.set_value("vickers_d1_avg_text", "D1 promedio: N/A")
            dpg.set_value("vickers_d2_avg_text", "D2 promedio: N/A")
            dpg.set_value("vickers_diagonal_avg_text", "D final: N/A")
            dpg.set_value("vickers_hardness_value", "N/A")
            dpg.set_value("vickers_std_value", "N/A")
            # Hide promedios title when no measurements
            if dpg.does_item_exist("promedios_finales_text"):
                dpg.configure_item("promedios_finales_text", show=False)
            return
        
        # Calculate averages
        d1_values = [m["d1"] for m in self.measurements]
        d2_values = [m["d2"] for m in self.measurements]
        d_avg_values = [m["d_avg"] for m in self.measurements]
        hv_values = [m["hv"] for m in self.measurements]
        
        d1_avg = sum(d1_values) / len(d1_values)
        d2_avg = sum(d2_values) / len(d2_values)
        d_final = sum(d_avg_values) / len(d_avg_values)
        hv_avg = sum(hv_values) / len(hv_values)
        
        # Calculate standard deviation of hardness
        if len(hv_values) > 1:
            variance = sum((x - hv_avg) ** 2 for x in hv_values) / (len(hv_values) - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0
        
        # Update UI
        dpg.set_value("vickers_d1_avg_text", f"D1 promedio: {d1_avg:.2f} µm")
        dpg.set_value("vickers_d2_avg_text", f"D2 promedio: {d2_avg:.2f} µm")
        dpg.set_value("vickers_diagonal_avg_text", f"D final: {d_final:.2f} µm")
        dpg.set_value("vickers_hardness_value", f"{hv_avg:.1f} HV")
        dpg.set_value("vickers_std_value", f"±{std_dev:.2f} HV")
        
        # Show promedios title only when all measurements are complete
        if len(self.measurements) >= self.n_measurements:
            if dpg.does_item_exist("promedios_finales_text"):
                dpg.configure_item("promedios_finales_text", show=True)
        else:
            if dpg.does_item_exist("promedios_finales_text"):
                dpg.configure_item("promedios_finales_text", show=False)

    def resetVickersMeasurement(self):
        """
        Reset Vickers measurement state and clear all drawings.
        """
        # Clear all drawn series
        for tag in self.vickers_series_tags:
            if dpg.does_item_exist(tag):
                dpg.delete_item(tag)

        # Reset state
        self.measurements.clear()
        self.current_points.clear()
        self.current_measurement = 0
        self.vickers_series_tags.clear()
        self.n_measurements = dpg.get_value("vickers_n_measurements_input") if dpg.does_item_exist("vickers_n_measurements_input") else 1

        # Reset UI measurements
        dpg.set_value("vickers_current_measurement", f"0/{self.n_measurements}")
        dpg.set_value("vickers_npoints", "0/4")
        
        # Clear table
        self.updateMeasurementsTable()
        
        # Reset summary
        self.updateMeasurementsSummary()

        print("[yellow]Mediciones reseteadas[/yellow]")

    def resetMeasurementsButton(self, sender=None, app_data=None):
        """
        Callback for Reset button. Clears all measurements and resets the system
        to allow a new set of measurements on the same image.
        """
        self.resetVickersMeasurement()
        print("[green]Sistema reseteado. Listo para nuevo conjunto de mediciones.[/green]")

    def _recreateImageTexture(self, image_data):
        """
        Helper method to recreate image texture and series with new data.
        Deletes existing texture/series and creates new ones with updated data.
        """
        # Get calibration for bounds
        calibration = get_preference("vickers_calibration", default=1.0)
        real_width = int(self.image_width * calibration)
        real_height = int(self.image_height * calibration)
        
        # Delete and recreate image series
        if dpg.does_item_exist("image_series"):
            dpg.delete_item("image_series")
        
        # Delete and recreate texture
        if dpg.does_item_exist("loaded_image_texture"):
            dpg.delete_item("loaded_image_texture")
        with dpg.texture_registry():
            dpg.add_static_texture(self.image_width, self.image_height, image_data, tag="loaded_image_texture") # type: ignore
        
        # Recreate image series
        dpg.add_image_series(
            "loaded_image_texture",
            bounds_min=(0, 0),
            bounds_max=(real_width, real_height),
            parent="Processing_y_axis",
            tag="image_series",
            label=self.fileName[-34:-4] if self.fileName else "Image"
        )





    def convertToBlackAndWhite(self, sender=None, app_data=None):
        """Convert loaded image to black and white (grayscale)."""
        if self.current_image_data is None or self.image_width is None or self.image_height is None:
            print("[yellow]No image loaded to convert[/yellow]")
            return
        
        try:
            # Convert to grayscale using luminosity method: 0.299*R + 0.587*G + 0.114*B
            bw_data = []
            for i in range(0, len(self.current_image_data), 4):
                r = self.current_image_data[i]
                g = self.current_image_data[i+1]
                b = self.current_image_data[i+2]
                a = self.current_image_data[i+3]
                gray = 0.299 * r + 0.587 * g + 0.114 * b
                bw_data.extend([gray, gray, gray, a])
            
            # Update current data and recreate texture
            self.current_image_data = bw_data
            self._recreateImageTexture(bw_data)
            
            print("[green]Image converted to B/W[/green]")
            
        except Exception as e:
            print(f"[red]Error converting to B/W: {e}[/red]")
            import traceback
            traceback.print_exc()
    
    def invertImage(self, sender=None, app_data=None):
        """Invert colors of loaded image."""
        if self.current_image_data is None or self.image_width is None or self.image_height is None:
            print("[yellow]No image loaded to invert[/yellow]")
            return
        
        try:
            # Invert RGB values (keep alpha)
            inverted_data = []
            for i in range(0, len(self.current_image_data), 4):
                r = self.current_image_data[i]
                g = self.current_image_data[i+1]
                b = self.current_image_data[i+2]
                a = self.current_image_data[i+3]
                inverted_data.extend([1.0 - r, 1.0 - g, 1.0 - b, a])
            
            # Update current data and recreate texture
            self.current_image_data = inverted_data
            self._recreateImageTexture(inverted_data)
            
            print("[green]Image inverted[/green]")
            
        except Exception as e:
            print(f"[red]Error inverting image: {e}[/red]")
            import traceback
            traceback.print_exc()
    
    def resetImageToOriginal(self, sender=None, app_data=None):
        """Reset image to original state from stored data."""
        if self.original_image_data is None or self.image_width is None or self.image_height is None:
            print("[yellow]No image loaded to reset[/yellow]")
            return
        
        try:
            # Restore from original data and recreate texture
            self.current_image_data = self.original_image_data
            self._recreateImageTexture(self.original_image_data)
            
            print("[green]Image reset to original[/green]")
            
        except Exception as e:
            print(f"[red]Error resetting image: {e}[/red]")
            import traceback
            traceback.print_exc()
    
    def loadPreviousPoint(self, sender=None, app_data=None):
        """Load the previous point from the data table."""
        if not self.callbacks or not hasattr(self.callbacks, 'dataTable'):
            print("[red]Data Table callback no disponible[/red]")
            return
        
        data_table = self.callbacks.dataTable
        
        if len(data_table.table_data) == 0:
            print("[yellow]No hay puntos en la tabla de datos[/yellow]")
            return
        
        # Determine previous index
        if self.current_table_index is None:
            # Start from last point
            new_index = len(data_table.table_data) - 1
        else:
            new_index = self.current_table_index - 1
            if new_index < 0:
                new_index = len(data_table.table_data) - 1  # Wrap around to last
        
        # Load point
        self.loadPointByIndex(new_index)
    
    def loadNextPoint(self, sender=None, app_data=None):
        """Load the next point from the data table."""
        if not self.callbacks or not hasattr(self.callbacks, 'dataTable'):
            print("[red]Data Table callback no disponible[/red]")
            return
        
        data_table = self.callbacks.dataTable
        
        if len(data_table.table_data) == 0:
            print("[yellow]No hay puntos en la tabla de datos[/yellow]")
            return
        
        # Determine next index
        if self.current_table_index is None:
            # Start from first point
            new_index = 0
        else:
            new_index = self.current_table_index + 1
            if new_index >= len(data_table.table_data):
                new_index = 0  # Wrap around to first
        
        # Load point
        self.loadPointByIndex(new_index)
    
    def loadPointByIndex(self, index):
        """Load a specific point from the data table by index."""
        if not self.callbacks or not hasattr(self.callbacks, 'dataTable'):
            print("[red]Data Table callback no disponible[/red]")
            return
        
        data_table = self.callbacks.dataTable
        
        if index < 0 or index >= len(data_table.table_data):
            print(f"[red]Índice inválido: {index}[/red]")
            return
        
        point_data = data_table.table_data[index]
        image_path = point_data['image_path']
        
        # Check if file exists
        if not os.path.isfile(image_path):
            print(f"[yellow]Imagen no encontrada: {image_path}[/yellow]")
            print(f"[yellow]Punto {point_data['id']} cargado sin imagen[/yellow]")
            self.current_table_index = index
            return
        
        # Load image using data table's method
        data_table.loadImageInVickers(image_path)
        
        # Reset measurements for new point
        self.resetVickersMeasurement()
        
        # Update current index
        self.current_table_index = index
        
        print(f"[green]═══ Punto {point_data['id']} cargado (índice {index + 1}/{len(data_table.table_data)}) ═══[/green]")
        print(f"[cyan]Coordenadas: X={point_data['x']:.3f}, Y={point_data['y']:.3f}[/cyan]")
        if point_data['hv'] is not None:
            print(f"[cyan]HV existente: {point_data['hv']:.1f}[/cyan]")

