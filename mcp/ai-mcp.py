# MIT License
#
# Copyright (c) 2025 Mike Chambers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from mcp.server.fastmcp import FastMCP
from core import init, sendCommand, createCommand
import socket_client
import sys

# Create an MCP server
mcp_name = "Adobe Illustrator MCP Server"
mcp = FastMCP(mcp_name, log_level="ERROR")
print(f"{mcp_name} running on stdio", file=sys.stderr)

APPLICATION = "illustrator"
PROXY_URL = 'http://localhost:3001'
PROXY_TIMEOUT = 60  # Export operations can take longer

socket_client.configure(
    app=APPLICATION, 
    url=PROXY_URL,
    timeout=PROXY_TIMEOUT
)

init(APPLICATION, socket_client)

@mcp.tool()
def get_documents():
    """
    Returns information about all currently open documents in Illustrator.

    """
    command = createCommand("getDocuments", {})
    return sendCommand(command)

@mcp.tool()
def get_active_document_info():
    """
    Returns information about the current active document.

    """
    command = createCommand("getActiveDocumentInfo", {})
    return sendCommand(command)

@mcp.tool()
def open_file(
    path: str
):
    """
    Opens an Illustrator (.ai) file in Adobe Illustrator.
    
    Args:
        path (str): The absolute file path to the Illustrator file to open.
            Example: "/Users/username/Documents/my_artwork.ai"
    
    Returns:
        dict: Result containing:
            - success (bool): Whether the file was opened successfully
            - error (str): Error message if opening failed
    
    """
    
    command_params = {
        "path": path
    }
    
    command = createCommand("openFile", command_params)
    return sendCommand(command)

@mcp.tool()
def export_png(
    path: str,
    transparency: bool = True,
    anti_aliasing: bool = True,
    artboard_clipping: bool = True,
    horizontal_scale: int = 100,
    vertical_scale: int = 100,
    export_type: str = "PNG24",
    matte: bool = None,
    matte_color: dict = {"red": 255, "green": 255, "blue": 255}
):
    """
    Exports the active Illustrator document as a PNG file.
    
    Args:
        path (str): The absolute file path where the PNG will be saved.
            Example: "/Users/username/Documents/my_export.png"
        transparency (bool, optional): Enable/disable transparency. Defaults to True.
        anti_aliasing (bool, optional): Enable/disable anti-aliasing for smooth edges. Defaults to True.
        artboard_clipping (bool, optional): Clip export to artboard bounds. Defaults to True.
        horizontal_scale (int, optional): Horizontal scale percentage (1-1000). Defaults to 100.
        vertical_scale (int, optional): Vertical scale percentage (1-1000). Defaults to 100.
        export_type (str, optional): PNG format type. "PNG24" (24-bit) or "PNG8" (8-bit). Defaults to "PNG24".
        matte (bool, optional): Enable matte background color for transparency preview. 
            If None, uses Illustrator's default behavior.
        matte_color (dict, optional): RGB color for matte background. Defaults to {"red": 255, "green": 255, "blue": 255}.
            Dict with keys "red", "green", "blue" with values 0-255.
    
    Returns:
        dict: Export result containing:
            - success (bool): Whether the export succeeded
            - filePath (str): The actual file path where the PNG was saved
            - fileExists (bool): Whether the exported file exists
            - options (dict): The export options that were used
            - documentName (str): Name of the exported document
            - error (str): Error message if export failed
    
    Example:
        # Basic PNG export
        result = export_png("/Users/username/Desktop/my_artwork.png")
        
        # High-resolution export with transparency
        result = export_png(
            path="/Users/username/Desktop/high_res.png",
            horizontal_scale=300,
            vertical_scale=300,
            transparency=True
        )
        
        # PNG8 export with red matte background
        result = export_png(
            path="/Users/username/Desktop/small_file.png",
            export_type="PNG8",
            matte=True,
            matte_color={"red": 255, "green": 0, "blue": 0}
        )
        
        # Blue matte background
        result = export_png(
            path="/Users/username/Desktop/blue_bg.png",
            matte=True,
            matte_color={"red": 0, "green": 100, "blue": 255}
        )
    """


    # Only include matte and matteColor if needed
    command_params = {
        "path": path,
        "transparency": transparency,
        "antiAliasing": anti_aliasing,
        "artBoardClipping": artboard_clipping,
        "horizontalScale": horizontal_scale,
        "verticalScale": vertical_scale,
        "exportType": export_type
    }

    # Only include matte if explicitly set
    if matte is not None:
        command_params["matte"] = matte
        
    # Include matte color if matte is enabled or custom colors provided
    if matte or matte_color != {"red": 255, "green": 255, "blue": 255}:
        command_params["matteColor"] = matte_color

    command = createCommand("exportPNG", command_params)
    return sendCommand(command)



@mcp.tool()
def execute_extend_script(script_string: str):
    """
    Executes arbitrary ExtendScript code in Illustrator and returns the result.

    The script should use 'return' to send data back. The result will be automatically
    JSON stringified. If the script throws an error, it will be caught and returned
    as an error object.

    Args:
        script_string (str): The ExtendScript code to execute. Must use 'return' to
                           send results back.

    Returns:
        any: The result returned from the ExtendScript, or an error object containing:
            - error (str): Error message
            - line (str): Line number where error occurred

    Example:
        script = '''
            var comp = app.project.activeItem;
            return {
                name: comp.name,
                layers: comp.numLayers
            };
        '''
        result = execute_extend_script(script)
    """
    command = createCommand("executeExtendScript", {
        "scriptString": script_string
    })
    return sendCommand(command)


# ============================================================
# Document Management Tools
# ============================================================

@mcp.tool()
def create_document(
    width: float = 612,
    height: float = 792,
    name: str = "Untitled",
    color_mode: str = "RGB",
    num_artboards: int = 1
):
    """
    Creates a new Illustrator document with specified dimensions.

    Args:
        width: Document width in points (72 points = 1 inch). Default is 612 (Letter width).
        height: Document height in points. Default is 792 (Letter height).
        name: Document name/title.
        color_mode: Color mode - "RGB" or "CMYK". Default is "RGB".
        num_artboards: Number of artboards (1-100). Default is 1.

    Returns:
        dict: Contains 'success', 'name', 'width', 'height', 'colorSpace', 'numArtboards'

    Example:
        # Create a 1200x800 social media graphic
        result = create_document(width=1200, height=800, name="Social Graphic")
    """
    command = createCommand("createDocument", {
        "width": width,
        "height": height,
        "name": name,
        "colorMode": color_mode,
        "numArtboards": num_artboards
    })
    return sendCommand(command)


@mcp.tool()
def save_document(file_path: str = None):
    """
    Saves the active Illustrator document.

    Args:
        file_path: Optional file path for "Save As". If not provided, saves in place.
                   Must be an absolute path ending in .ai

    Returns:
        dict: Contains 'success', 'name', 'path', 'saved'

    Example:
        # Save to a new location
        result = save_document("/Users/me/Documents/artwork.ai")

        # Save in place (document must have been saved before)
        result = save_document()
    """
    command = createCommand("saveDocument", {
        "filePath": file_path
    })
    return sendCommand(command)


@mcp.tool()
def close_document(save: bool = False):
    """
    Closes the active Illustrator document.

    Args:
        save: If True, saves the document before closing. Default is False.

    Returns:
        dict: Contains 'success', 'documentName', 'saved'
    """
    command = createCommand("closeDocument", {
        "save": save
    })
    return sendCommand(command)


# ============================================================
# Color and Swatch Management Tools
# ============================================================

@mcp.tool()
def create_color_swatch(
    name: str,
    color_value: str
):
    """
    Creates a named color swatch in the active document.

    Args:
        name: The name for the swatch (e.g., "Brand Blue")
        color_value: Hex color value (e.g., "#0D1B2A")

    Returns:
        dict: Contains 'success', 'swatchName', 'colorValue', 'alreadyExisted'

    Example:
        result = create_color_swatch("Synaptic Blue", "#0D1B2A")
    """
    command = createCommand("createColorSwatch", {
        "name": name,
        "colorValue": color_value
    })
    return sendCommand(command)


@mcp.tool()
def create_brand_swatches():
    """
    Creates all Ultrathink Solutions brand color swatches in the active document.

    Creates the following swatches:
        - Synaptic Blue (#0D1B2A) - Primary dark
        - Void Black (#0B090A) - Text/accents
        - Axon White (#F5F5F5) - Backgrounds
        - Neural Gold (#FFB703) - Accent
        - Spark Yellow (#FFD000) - Highlight
        - Electric Orange (#FB8500) - CTA/emphasis

    Returns:
        dict: Contains 'success', 'createdSwatches' (list of newly created),
              'brandColors' (all brand color definitions)
    """
    command = createCommand("createBrandSwatches", {})
    return sendCommand(command)


@mcp.tool()
def list_swatches():
    """
    Lists all color swatches in the active document.

    Returns:
        dict: Contains 'success', 'count', 'swatches' (array of swatch info)
              Each swatch has: name, index, colorType, and color values
    """
    command = createCommand("listSwatches", {})
    return sendCommand(command)


# ============================================================
# Shape Tools
# ============================================================

@mcp.tool()
def create_rectangle(
    x: float,
    y: float,
    width: float,
    height: float,
    fill_color: str = None,
    stroke_color: str = None,
    stroke_weight: float = 1,
    corner_radius: float = 0,
    layer_name: str = None,
    name: str = None
):
    """
    Creates a rectangle shape on the active artboard.

    Args:
        x: X position from left edge in points
        y: Y position from top edge in points
        width: Rectangle width in points
        height: Rectangle height in points
        fill_color: Fill color as hex "#0D1B2A" or swatch name. None for no fill.
        stroke_color: Stroke color as hex or swatch name. None for no stroke.
        stroke_weight: Stroke weight in points. Default is 1.
        corner_radius: Corner radius for rounded rectangles. Default is 0.
        layer_name: Target layer name. Creates if doesn't exist. None for active layer.
        name: Item name for referencing later. Auto-generated if not provided.

    Returns:
        dict: Contains 'success', 'itemName', 'layer', 'bounds'

    Example:
        # Create a blue rectangle with rounded corners
        result = create_rectangle(
            x=50, y=50, width=200, height=100,
            fill_color="#0D1B2A", corner_radius=10
        )
    """
    command = createCommand("createRectangle", {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "fillColor": fill_color,
        "strokeColor": stroke_color,
        "strokeWeight": stroke_weight,
        "cornerRadius": corner_radius,
        "layerName": layer_name,
        "name": name
    })
    return sendCommand(command)


@mcp.tool()
def create_ellipse(
    x: float,
    y: float,
    width: float,
    height: float,
    fill_color: str = None,
    stroke_color: str = None,
    stroke_weight: float = 1,
    layer_name: str = None,
    name: str = None
):
    """
    Creates an ellipse/circle shape on the active artboard.

    Args:
        x: X position from left edge in points
        y: Y position from top edge in points
        width: Ellipse width in points (same as height for circle)
        height: Ellipse height in points
        fill_color: Fill color as hex "#FFB703" or swatch name. None for no fill.
        stroke_color: Stroke color as hex or swatch name. None for no stroke.
        stroke_weight: Stroke weight in points. Default is 1.
        layer_name: Target layer name. Creates if doesn't exist.
        name: Item name for referencing later.

    Returns:
        dict: Contains 'success', 'itemName', 'layer', 'bounds'

    Example:
        # Create a gold circle
        result = create_ellipse(
            x=100, y=100, width=80, height=80,
            fill_color="Neural Gold"
        )
    """
    command = createCommand("createEllipse", {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "fillColor": fill_color,
        "strokeColor": stroke_color,
        "strokeWeight": stroke_weight,
        "layerName": layer_name,
        "name": name
    })
    return sendCommand(command)


@mcp.tool()
def create_line(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    stroke_color: str = "#000000",
    stroke_weight: float = 1,
    stroke_cap: str = "BUTTENDCAP",
    layer_name: str = None,
    name: str = None
):
    """
    Creates a line between two points.

    Args:
        start_x: Starting X position in points
        start_y: Starting Y position in points
        end_x: Ending X position in points
        end_y: Ending Y position in points
        stroke_color: Stroke color as hex. Default is black.
        stroke_weight: Stroke weight in points. Default is 1.
        stroke_cap: Line cap style - "BUTTENDCAP", "ROUNDENDCAP", "PROJECTINGENDCAP"
        layer_name: Target layer name.
        name: Item name for referencing later.

    Returns:
        dict: Contains 'success', 'itemName', 'layer', 'start', 'end'
    """
    command = createCommand("createLine", {
        "startX": start_x,
        "startY": start_y,
        "endX": end_x,
        "endY": end_y,
        "strokeColor": stroke_color,
        "strokeWeight": stroke_weight,
        "strokeCap": stroke_cap,
        "layerName": layer_name,
        "name": name
    })
    return sendCommand(command)


# ============================================================
# Text Tools
# ============================================================

@mcp.tool()
def create_point_text(
    x: float,
    y: float,
    content: str,
    font_family: str = "Arial",
    font_style: str = "Regular",
    font_size: float = 24,
    text_color: str = "#000000",
    alignment: str = "LEFT",
    tracking: float = 0,
    layer_name: str = None,
    name: str = None
):
    """
    Creates single-line point text (ideal for headlines and labels).

    Args:
        x: X position from left edge in points
        y: Y position from top edge in points
        content: The text content
        font_family: Font family name (e.g., "0xProto", "Arial")
        font_style: Font style (e.g., "Regular", "Bold", "Italic")
        font_size: Font size in points. Default is 24.
        text_color: Text color as hex. Default is black.
        alignment: Text alignment - "LEFT", "CENTER", "RIGHT"
        tracking: Letter spacing adjustment. Default is 0.
        layer_name: Target layer name.
        name: Item name for referencing later.

    Returns:
        dict: Contains 'success', 'itemName', 'layer', 'bounds', 'content'

    Example:
        # Create a headline with brand font
        result = create_point_text(
            x=50, y=60,
            content="AI Adoption Metrics",
            font_family="0xProto",
            font_size=36,
            text_color="#0D1B2A"
        )
    """
    command = createCommand("createPointText", {
        "x": x,
        "y": y,
        "content": content,
        "fontFamily": font_family,
        "fontStyle": font_style,
        "fontSize": font_size,
        "textColor": text_color,
        "alignment": alignment,
        "tracking": tracking,
        "layerName": layer_name,
        "name": name
    })
    return sendCommand(command)


@mcp.tool()
def create_area_text(
    x: float,
    y: float,
    width: float,
    height: float,
    content: str,
    font_family: str = "Arial",
    font_style: str = "Regular",
    font_size: float = 12,
    text_color: str = "#000000",
    alignment: str = "LEFT",
    layer_name: str = None,
    name: str = None
):
    """
    Creates multi-line area text within a bounding box (ideal for body text).

    Args:
        x: X position from left edge in points
        y: Y position from top edge in points
        width: Text area width in points
        height: Text area height in points
        content: The text content (can include newlines with \\n)
        font_family: Font family name (e.g., "IBMPlexSerif", "Arial")
        font_style: Font style (e.g., "Regular", "Bold")
        font_size: Font size in points. Default is 12.
        text_color: Text color as hex. Default is black.
        alignment: Text alignment - "LEFT", "CENTER", "RIGHT", "FULLJUSTIFY"
        layer_name: Target layer name.
        name: Item name for referencing later.

    Returns:
        dict: Contains 'success', 'itemName', 'layer', 'bounds', 'content'

    Example:
        # Create body text with serif font
        result = create_area_text(
            x=50, y=150, width=500, height=400,
            content="Organizations adopting AI see 40% efficiency gains...",
            font_family="IBMPlexSerif",
            font_size=14,
            text_color="#F5F5F5"
        )
    """
    command = createCommand("createAreaText", {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "content": content,
        "fontFamily": font_family,
        "fontStyle": font_style,
        "fontSize": font_size,
        "textColor": text_color,
        "alignment": alignment,
        "layerName": layer_name,
        "name": name
    })
    return sendCommand(command)

# ============================================================
# Layer Management Tools
# ============================================================

@mcp.tool()
def create_layer(
    name: str = "New Layer",
    above_layer: str = None,
    visible: bool = True,
    locked: bool = False
):
    """
    Creates a new layer in the active document.

    Args:
        name: Name for the new layer. Default is "New Layer".
        above_layer: Name of layer to position above. None places at top.
        visible: Whether layer is visible. Default is True.
        locked: Whether layer is locked. Default is False.

    Returns:
        dict: Contains 'success', 'layerName', 'visible', 'locked',
              'zOrderPosition', 'totalLayers'

    Example:
        # Create a new layer for icons
        result = create_layer(name="Icons", visible=True)

        # Create hidden layer for guides
        result = create_layer(name="Guides", visible=False, locked=True)
    """
    command = createCommand("createLayer", {
        "name": name,
        "aboveLayer": above_layer,
        "visible": visible,
        "locked": locked
    })
    return sendCommand(command)


@mcp.tool()
def delete_layer(name: str):
    """
    Deletes a layer from the active document.

    Args:
        name: Name of the layer to delete.

    Returns:
        dict: Contains 'success', 'deletedLayer', 'remainingLayers'

    Note:
        Cannot delete the last remaining layer in a document.
    """
    command = createCommand("deleteLayer", {
        "name": name
    })
    return sendCommand(command)


@mcp.tool()
def rename_layer(current_name: str, new_name: str):
    """
    Renames an existing layer.

    Args:
        current_name: Current name of the layer.
        new_name: New name for the layer.

    Returns:
        dict: Contains 'success', 'oldName', 'newName'
    """
    command = createCommand("renameLayer", {
        "currentName": current_name,
        "newName": new_name
    })
    return sendCommand(command)


@mcp.tool()
def set_layer_visibility(name: str, visible: bool):
    """
    Shows or hides a layer.

    Args:
        name: Name of the layer.
        visible: True to show, False to hide.

    Returns:
        dict: Contains 'success', 'layerName', 'visible'

    Example:
        # Hide the background layer
        result = set_layer_visibility("Background", False)
    """
    command = createCommand("setLayerVisibility", {
        "name": name,
        "visible": visible
    })
    return sendCommand(command)


@mcp.tool()
def set_layer_lock(name: str, locked: bool):
    """
    Locks or unlocks a layer.

    Args:
        name: Name of the layer.
        locked: True to lock, False to unlock.

    Returns:
        dict: Contains 'success', 'layerName', 'locked'

    Example:
        # Lock the background to prevent accidental edits
        result = set_layer_lock("Background", True)
    """
    command = createCommand("setLayerLock", {
        "name": name,
        "locked": locked
    })
    return sendCommand(command)


@mcp.tool()
def reorder_layer(name: str, position: str):
    """
    Changes a layer's position in the layer stack.

    Args:
        name: Name of the layer to move.
        position: New position - "front", "back", "forward", "backward",
                  or a numeric index (0 = top).

    Returns:
        dict: Contains 'success', 'layerName', 'newZOrderPosition', 'totalLayers'

    Example:
        # Move layer to front (top)
        result = reorder_layer("Header", "front")

        # Move layer back one position
        result = reorder_layer("Content", "backward")

        # Move to specific index
        result = reorder_layer("Footer", "2")
    """
    command = createCommand("reorderLayer", {
        "name": name,
        "position": str(position)
    })
    return sendCommand(command)


@mcp.tool()
def get_layers():
    """
    Gets detailed information about all layers in the active document.

    Returns:
        dict: Contains 'totalLayers' and 'layers' array with each layer's:
              - name, visible, locked, opacity, zOrderPosition
              - itemCounts (pathItems, textFrames, etc.)
              - subLayers (if any)
    """
    command = createCommand("getLayers", {})
    return sendCommand(command)


# ============================================================
# Export Tools
# ============================================================

@mcp.tool()
def export_svg(
    output_path: str,
    artboard_index: int = 0,
    embed_fonts: bool = True,
    embed_raster_images: bool = True,
    css_properties: str = "STYLEATTRIBUTES",
    font_subsetting: str = "GLYPHSUSED"
):
    """
    Exports the active document as SVG.

    Args:
        output_path: Absolute path for the SVG file (e.g., "/path/to/export.svg")
        artboard_index: Index of artboard to export (0-based). Default is 0.
        embed_fonts: Embed fonts as outlines. Default is True.
        embed_raster_images: Embed raster images in SVG. Default is True.
        css_properties: CSS output method:
            - "STYLEATTRIBUTES" (default): Inline style attributes
            - "PRESENTATIONATTRIBUTES": Presentation attributes
            - "STYLEELEMENTS": Style elements
        font_subsetting: Font subsetting method:
            - "GLYPHSUSED" (default): Only used glyphs
            - "NONE": No subsetting
            - "ALLGLYPHS": All glyphs

    Returns:
        dict: Contains 'success', 'filePath', 'fileExists', 'documentName', 'artboardIndex'

    Example:
        result = export_svg("/Users/me/Desktop/infographic.svg")
    """
    command = createCommand("exportSVG", {
        "outputPath": output_path,
        "artboardIndex": artboard_index,
        "embedFonts": embed_fonts,
        "embedRasterImages": embed_raster_images,
        "cssProperties": css_properties,
        "fontSubsetting": font_subsetting
    })
    return sendCommand(command)


@mcp.tool()
def export_pdf(
    output_path: str,
    preset: str = "[High Quality Print]",
    preserve_editability: bool = True,
    optimize_for_fast_web_view: bool = False,
    view_after_saving: bool = False,
    artboard_range: str = None
):
    """
    Exports the active document as PDF.

    Args:
        output_path: Absolute path for the PDF file (e.g., "/path/to/export.pdf")
        preset: PDF preset name. Default is "[High Quality Print]".
                Common presets: "[Smallest File Size]", "[Press Quality]"
        preserve_editability: Keep Illustrator editing capability. Default is True.
        optimize_for_fast_web_view: Optimize for web viewing. Default is False.
        view_after_saving: Open PDF after saving. Default is False.
        artboard_range: Which artboards to export (e.g., "1-3" or "1,3,5").
                       None exports all.

    Returns:
        dict: Contains 'success', 'filePath', 'fileExists', 'documentName', 'preset'

    Example:
        # High quality print PDF
        result = export_pdf("/Users/me/Desktop/print.pdf")

        # Small web PDF
        result = export_pdf(
            "/Users/me/Desktop/web.pdf",
            preset="[Smallest File Size]",
            optimize_for_fast_web_view=True
        )
    """
    command = createCommand("exportPDF", {
        "outputPath": output_path,
        "preset": preset,
        "preserveEditability": preserve_editability,
        "optimizeForFastWebView": optimize_for_fast_web_view,
        "viewAfterSaving": view_after_saving,
        "artboardRange": artboard_range
    })
    return sendCommand(command)


@mcp.tool()
def export_jpeg(
    output_path: str,
    artboard_index: int = 0,
    quality: int = 80,
    horizontal_scale: int = 100,
    vertical_scale: int = 100,
    anti_aliasing: bool = True,
    artboard_clipping: bool = True,
    blur_amount: float = 0
):
    """
    Exports the active document as JPEG.

    Args:
        output_path: Absolute path for the JPEG file (e.g., "/path/to/export.jpg")
        artboard_index: Index of artboard to export (0-based). Default is 0.
        quality: JPEG quality (0-100). Default is 80.
        horizontal_scale: Horizontal scale percentage. Default is 100.
        vertical_scale: Vertical scale percentage. Default is 100.
        anti_aliasing: Enable anti-aliasing. Default is True.
        artboard_clipping: Clip to artboard bounds. Default is True.
        blur_amount: Blur amount (0-2). Default is 0.

    Returns:
        dict: Contains 'success', 'filePath', 'fileExists', 'documentName',
              'quality', 'artboardIndex'

    Example:
        # Standard quality export
        result = export_jpeg("/Users/me/Desktop/preview.jpg", quality=80)

        # High-res export at 2x scale
        result = export_jpeg(
            "/Users/me/Desktop/highres.jpg",
            quality=100,
            horizontal_scale=200,
            vertical_scale=200
        )
    """
    command = createCommand("exportJPEG", {
        "outputPath": output_path,
        "artboardIndex": artboard_index,
        "quality": quality,
        "horizontalScale": horizontal_scale,
        "verticalScale": vertical_scale,
        "antiAliasing": anti_aliasing,
        "artBoardClipping": artboard_clipping,
        "blurAmount": blur_amount
    })
    return sendCommand(command)


@mcp.resource("config://get_instructions")
def get_instructions() -> str:
    """Read this first! Returns information and instructions on how to use Illustrator and this API"""

    return f"""
    You are an Illustrator export who is creative and loves to help other people learn to use Illustrator.

    Rules to follow:

    1. Think deeply about how to solve the task
    2. Always check your work before responding
    3. Read the info for the API calls to make sure you understand the requirements and arguments

    """


# Illustrator Blend Modes (for future use)
BLEND_MODES = [
    "ADD",
    "ALPHA_ADD",
    "CLASSIC_COLOR_BURN",
    "CLASSIC_COLOR_DODGE",
    "CLASSIC_DIFFERENCE",
    "COLOR",
    "COLOR_BURN",
    "COLOR_DODGE",
    "DANCING_DISSOLVE",
    "DARKEN",
    "DARKER_COLOR",
    "DIFFERENCE",
    "DISSOLVE",
    "EXCLUSION",
    "HARD_LIGHT",
    "HARD_MIX",
    "HUE",
    "LIGHTEN",
    "LIGHTER_COLOR",
    "LINEAR_BURN",
    "LINEAR_DODGE",
    "LINEAR_LIGHT",
    "LUMINESCENT_PREMUL",
    "LUMINOSITY",
    "MULTIPLY",
    "NORMAL",
    "OVERLAY",
    "PIN_LIGHT",
    "SATURATION",
    "SCREEN",
    "SILHOUETE_ALPHA",
    "SILHOUETTE_LUMA",
    "SOFT_LIGHT",
    "STENCIL_ALPHA",
    "STENCIL_LUMA",
    "SUBTRACT",
    "VIVID_LIGHT"
]