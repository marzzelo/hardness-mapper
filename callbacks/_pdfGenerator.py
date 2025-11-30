"""
PDF and HTML Report Generator for Vickers Hardness Testing

This module provides functionality to generate comprehensive reports with:
- Project information (name, description, technician, date)
- Measurement point data table (coordinates, hardness values)
- Vickers measurement data with annotated images
- Heat map visualization (if available)
- Mapping surface image with marked points (if available)

Supports both PDF (using reportlab) and HTML (standalone) formats.
Includes LaTeX formula rendering using matplotlib for PDF reports.
"""

import os
import io
from datetime import datetime
from typing import List, Tuple, Optional, Dict

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from PIL import Image
import base64
import webbrowser


def generate_html_report(
    file_path: str,
    project_data: Optional[Dict],
    heatmap_data: Optional[Dict],
    table_data: Optional[List[Dict]],
    heatmap_html_path: Optional[str] = None,
    grid_columns: int = 4,
) -> None:
    """
    Generate a comprehensive multi-page HTML report for Vickers hardness testing project.
    
    Args:
        file_path: Path where the HTML will be saved
        project_data: Dict with project info (nombre, descripcion, requerimiento, tecnico, fecha)
        heatmap_data: Dict with mapping info (calibration, points, origin_offset, image_path)
        table_data: List of point data dicts with id, x, y, hv, std_dev, image_path
        heatmap_html_path: Optional path to generated heat map HTML file
        grid_columns: Number of columns for hardness points grid (default 4)
    """
    # Ensure .html extension
    if not file_path.endswith(".html"):
        file_path += ".html"
    
    # Build HTML content
    html_content = _build_html_report(
        project_data,
        heatmap_data,
        table_data,
        heatmap_html_path,
        grid_columns
    )
    
    # Save HTML file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[green]Reporte HTML generado: {file_path}[/green]")
    
    # Open in default browser
    webbrowser.open(f"file://{os.path.abspath(file_path)}")


def _build_html_report(
    project_data: Optional[Dict],
    heatmap_data: Optional[Dict],
    table_data: Optional[List[Dict]],
    heatmap_html_path: Optional[str],
    grid_columns: int
) -> str:
    """Build complete HTML report with embedded CSS and JavaScript."""
    
    # Load and encode logo
    logo_base64 = _get_logo_base64()
    
    # Generate sections
    project_section = _generate_project_info_section(project_data)
    mapping_section = _generate_mapping_section(heatmap_data)
    points_section = _generate_hardness_points_section(table_data, grid_columns)
    heatmap_section = _generate_heatmap_section(heatmap_html_path)
    
    # Build complete HTML
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Dureza Vickers - {project_data.get('nombre', 'Proyecto') if project_data else 'Proyecto'}</title>
    <style>
        {_get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header class="page-header">
            {logo_base64}
            <h1>REPORTE DE ENSAYO DE DUREZA VICKERS</h1>
            <p class="subtitle">Laboratorio de Ensayos Estructurales e Investigación de Materiales</p>
            <p class="date">Fecha de generación: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </header>
        
        <nav class="navigation">
            <a href="#project">Datos del Proyecto</a>
            <a href="#mapping">Mapeado de Superficie</a>
            <a href="#hardness">Puntos de Dureza</a>
            <a href="#heatmap">Mapa de Calor</a>
        </nav>
        
        {project_section}
        {mapping_section}
        {points_section}
        {heatmap_section}
        
        <footer class="page-footer">
            <p>&copy; {datetime.now().year} Laboratorio de Ensayos Estructurales e Investigación de Materiales</p>
            <p>Este documento fue generado automáticamente por Vickers Mapping Pro</p>
        </footer>
    </div>
    
    <script>
        {_get_javascript()}
    </script>
</body>
</html>"""
    
    return html


def _get_logo_base64() -> str:
    """Load logo from resources and encode as base64 for embedding in HTML."""
    logo_path = os.path.join("resources", "logo_blue.jpg")
    
    if not os.path.exists(logo_path):
        print(f"[yellow]Logo no encontrado en: {logo_path}[/yellow]")
        return ""  # Return empty string if logo not found
    
    try:
        with open(logo_path, 'rb') as logo_file:
            logo_data = base64.b64encode(logo_file.read()).decode('utf-8')
            return f'<img src="data:image/jpeg;base64,{logo_data}" alt="Logo" class="logo">'
    except Exception as e:
        print(f"[yellow]Error cargando logo: {e}[/yellow]")
        return ""


def _get_css_styles() -> str:
    """
    Load and return CSS styles from external file for the HTML report.
    Falls back to inline styles if file is not found.
    """
    css_file_path = os.path.join(os.path.dirname(__file__), "_reportStyles.css")
    
    try:
        with open(css_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[yellow]Warning: CSS file not found at {css_file_path}, using fallback styles[/yellow]")
        # Minimal fallback styles
        return """
        body { font-family: Arial, sans-serif; padding: 20px; background: #f0f0f0; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; }
        .section { padding: 20px; margin-bottom: 20px; }
        .section-title { font-size: 2em; color: #1e3c72; border-bottom: 2px solid #2a5298; }
        .no-data { text-align: center; color: #999; font-style: italic; }
        """
    except Exception as e:
        print(f"[yellow]Warning: Error loading CSS file: {e}[/yellow]")
        return ""


def _get_javascript() -> str:
    """Return embedded JavaScript for the HTML report."""
    return """
        // Smooth scrolling for navigation links
        document.querySelectorAll('.navigation a').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Add fade-in animation on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        document.querySelectorAll('.section').forEach(section => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(20px)';
            section.style.transition = 'opacity 0.6s, transform 0.6s';
            observer.observe(section);
        });
    """


def _generate_project_info_section(project_data: Optional[Dict]) -> str:
    """Generate project information section HTML."""
    if not project_data:
        return '<section id="project" class="section"><p class="no-data">No hay datos del proyecto disponibles</p></section>'
    
    nombre = project_data.get('nombre', 'N/A')
    descripcion = project_data.get('descripcion', 'N/A')
    requerimiento = project_data.get('requerimiento', 'N/A')
    tecnico = project_data.get('tecnico', 'N/A')
    fecha = project_data.get('fecha', 'N/A')
    
    return f"""
    <section id="project" class="section">
        <h2 class="section-title">Datos del Proyecto</h2>
        <p class="section-description">Información general del proyecto de ensayo de dureza Vickers.</p>
        
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Nombre del Proyecto</div>
                <div class="info-value">{nombre}</div>
            </div>
            <div class="info-item">
                <div class="info-label">N° de Requerimiento</div>
                <div class="info-value">{requerimiento}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Técnico Responsable</div>
                <div class="info-value">{tecnico}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Fecha de Realización</div>
                <div class="info-value">{fecha}</div>
            </div>
        </div>
        
        <div class="description-box">
            <div class="info-label">Descripción</div>
            <div class="info-value">{descripcion}</div>
        </div>
    </section>
    """


def _generate_mapping_section(heatmap_data: Optional[Dict]) -> str:
    """Generate mapping section HTML with surface image and points."""
    if not heatmap_data:
        return '<section id="mapping" class="section"><p class="no-data">No hay datos de mapeado disponibles</p></section>'
    
    calibration = heatmap_data.get('calibration', 0.0)
    points = heatmap_data.get('points', [])
    origin_offset = heatmap_data.get('origin_offset', (0, 0))
    mapping_image_path = heatmap_data.get('mapping_image_path', None)
    
    # Use the saved mapping image with points already overlaid
    image_html = ""
    if mapping_image_path and os.path.exists(mapping_image_path):
        try:
            with open(mapping_image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                image_html = f'<img src="data:image/png;base64,{img_data}" alt="Superficie mapeada con puntos">'
        except Exception as e:
            image_html = f'<p class="no-data">Error cargando imagen: {str(e)}</p>'
    else:
        image_html = '<p class="no-data">Sin imagen de superficie. Genere el mapeado en la pestaña Mapeado.</p>'
    
    points_list = ""
    for i, (x, y) in enumerate(points):
        points_list += f"<li>P{i+1}: ({x:.3f}, {y:.3f}) mm</li>"
    
    return f"""
    <section id="mapping" class="section">
        <h2 class="section-title">Mapeado de Superficie</h2>
        <p class="section-description">Imagen de la superficie ensayada con los puntos de medición marcados.</p>
        
        <div class="mapping-container">
            <div class="mapping-image">
                {image_html}
            </div>
            <div class="mapping-info">
                <div class="info-item">
                    <div class="info-label">Calibración</div>
                    <div class="info-value">{calibration:.6f} mm/pixel</div>
                </div>
                <div class="info-item" style="margin-top: 15px;">
                    <div class="info-label">Offset del Origen</div>
                    <div class="info-value">X: {origin_offset[0]:.3f} mm, Y: {origin_offset[1]:.3f} mm</div>
                </div>
                <div class="info-item" style="margin-top: 15px;">
                    <div class="info-label">Puntos Marcados ({len(points)})</div>
                    <div class="info-value">
                        <ul style="margin-top: 10px; margin-left: 20px; max-height: 300px; overflow-y: auto;">
                            {points_list}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """


def _generate_hardness_points_section(table_data: Optional[List[Dict]], grid_columns: int) -> str:
    """Generate hardness points section HTML with grid layout."""
    if not table_data or len(table_data) == 0:
        return '<section id="hardness" class="section"><p class="no-data">No hay datos de puntos de dureza disponibles</p></section>'
    
    # Calculate statistics
    hv_values = [p.get('hv', 0) for p in table_data if p.get('hv') is not None]
    if hv_values:
        hv_avg = sum(hv_values) / len(hv_values)
        hv_min = min(hv_values)
        hv_max = max(hv_values)
        hv_range = hv_max - hv_min
    else:
        hv_avg = hv_min = hv_max = hv_range = 0
    
    stats_html = f"""
    <div class="statistics">
        <div class="stat-card">
            <div class="stat-label">Total de Puntos</div>
            <div class="stat-value">{len(table_data)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Dureza Promedio</div>
            <div class="stat-value">{hv_avg:.1f} HV</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Dureza Mínima</div>
            <div class="stat-value">{hv_min:.1f} HV</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Dureza Máxima</div>
            <div class="stat-value">{hv_max:.1f} HV</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Rango</div>
            <div class="stat-value">{hv_range:.1f} HV</div>
        </div>
    </div>
    """
    
    # Generate grid of point cards
    points_html = ""
    for point in table_data:
        point_id = point.get('id', 'N/A')
        x = point.get('x', 0)
        y = point.get('y', 0)
        hv = point.get('hv', 0)
        std_dev = point.get('std_dev', None)
        image_path = point.get('image_path', None)
        filename = os.path.basename(image_path) if image_path else "N/A"
        
        # Convert image to base64
        img_html = ""
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    ext = os.path.splitext(image_path)[1].lower()
                    mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
                    img_html = f'<img src="data:{mime_type};base64,{img_data}" alt="{point_id}">'
            except:
                img_html = '<div style="height:200px;background:#ddd;display:flex;align-items:center;justify-content:center;">Sin imagen</div>'
        else:
            img_html = '<div style="height:200px;background:#ddd;display:flex;align-items:center;justify-content:center;">Sin imagen</div>'
        
        std_dev_text = f"±{std_dev:.2f}" if std_dev is not None else "N/A"
        hv_text = f"{hv:.1f} HV" if hv is not None else "N/A"
        
        points_html += f"""
        <div class="point-card">
            <div class="point-header">{point_id}</div>
            {img_html}
            <div class="point-info">
                <div class="point-detail"><strong>X:</strong> {x:.3f} mm</div>
                <div class="point-detail"><strong>Y:</strong> {y:.3f} mm</div>
                <div class="point-detail"><strong>Dureza:</strong> {hv_text}</div>
                <div class="point-detail"><strong>Std Dev:</strong> {std_dev_text}</div>
            </div>
            <div class="point-filename">{filename}</div>
        </div>
        """
    
    return f"""
    <section id="hardness" class="section">
        <h2 class="section-title">Puntos de Dureza Vickers</h2>
        <p class="section-description">Resultados de las mediciones de dureza para cada punto marcado en la superficie.</p>
        
        {stats_html}
        
        <div class="points-grid" style="grid-template-columns: repeat({grid_columns}, 1fr);">
            {points_html}
        </div>
    </section>
    """


def _generate_heatmap_section(heatmap_html_path: Optional[str]) -> str:
    """Generate heatmap section HTML."""
    if not heatmap_html_path or not os.path.exists(heatmap_html_path):
        return '<section id="heatmap" class="section"><p class="no-data">No hay mapa de calor disponible. Genere el mapa de calor en la pestaña HM Plot.</p></section>'
    
    # Check if it's an HTML file or image file
    try:
        if heatmap_html_path.endswith('.html'):
            # Read the heatmap HTML content to embed it
            with open(heatmap_html_path, 'r', encoding='utf-8') as f:
                heatmap_content = f.read()
            
            # Encode as base64 for iframe src
            heatmap_b64 = base64.b64encode(heatmap_content.encode('utf-8')).decode('utf-8')
            
            return f"""
            <section id="heatmap" class="section">
                <h2 class="section-title">Mapa de Calor</h2>
                <p class="section-description">Visualización gráfica de la distribución de dureza en la superficie ensayada.</p>
                
                <div class="heatmap-container">
                    <iframe src="data:text/html;base64,{heatmap_b64}"></iframe>
                </div>
            </section>
            """
        else:
            # It's an image file (PNG, JPG, etc.)
            with open(heatmap_html_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                ext = os.path.splitext(heatmap_html_path)[1].lower()
                mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
                
            return f"""
            <section id="heatmap" class="section">
                <h2 class="section-title">Mapa de Calor</h2>
                <p class="section-description">Visualización gráfica de la distribución de dureza en la superficie ensayada.</p>
                
                <div class="heatmap-container" style="padding: 20px; background: white;">
                    <img src="data:{mime_type};base64,{img_data}" alt="Mapa de Calor" style="width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                </div>
            </section>
            """
    except Exception as e:
        return f'<section id="heatmap" class="section"><p class="no-data">Error cargando mapa de calor: {str(e)}</p></section>'


# def _render_latex_formula(latex_string: str, fontsize: int = 14, dpi: int = 40) -> Optional[ImageReader]:
#     """
#     Render a LaTeX formula as an image using matplotlib.
    
#     Args:
#         latex_string: LaTeX formula string (without $ delimiters)
#         fontsize: Font size for the formula
#         dpi: DPI for the rendered image
        
#     Returns:
#         ImageReader object or None if matplotlib is not available
#     """
#     try:
#         import matplotlib
#         matplotlib.use('Agg')  # Use non-interactive backend
#         import matplotlib.pyplot as plt
        
#         # Create figure with transparent background
#         fig = plt.figure(figsize=(4, 0.6))
#         fig.patch.set_alpha(0.0)
        
#         # Render LaTeX text
#         plt.text(0.5, 0.5, f'${latex_string}$', 
#                 fontsize=fontsize, 
#                 ha='center', 
#                 va='center',
#                 transform=fig.transFigure)
#         plt.axis('off')
        
#         # Save to buffer
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=dpi, 
#                    bbox_inches='tight', 
#                    transparent=True,
#                    pad_inches=0.1)
#         buf.seek(0)
#         plt.close(fig)
        
#         return ImageReader(buf)
#     except ImportError:
#         print("[yellow]Warning: matplotlib not available, LaTeX formulas will not be rendered[/yellow]")
#         return None
#     except Exception as e:
#         print(f"[yellow]Warning: Could not render LaTeX formula: {e}[/yellow]")
#         return None
