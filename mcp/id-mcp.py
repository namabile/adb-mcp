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

#logger.log(f"Python path: {sys.executable}")
#logger.log(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
#logger.log(f"Current working directory: {os.getcwd()}")
#logger.log(f"Sys.path: {sys.path}")


# Create an MCP server
mcp_name = "Adobe InDesign MCP Server"
mcp = FastMCP(mcp_name, log_level="ERROR")
print(f"{mcp_name} running on stdio", file=sys.stderr)

APPLICATION = "indesign"
PROXY_URL = 'http://localhost:3001'
PROXY_TIMEOUT = 20

socket_client.configure(
    app=APPLICATION, 
    url=PROXY_URL,
    timeout=PROXY_TIMEOUT
)

init(APPLICATION, socket_client)

@mcp.tool()
def create_document(
   width: int,
   height: int,
   pages: int = 1,
   pages_facing: bool = False,
   columns: dict = {"count": 1, "gutter": 12},
   margins: dict = {"top": 36, "bottom": 36, "left": 36, "right": 36}
):
   """
   Creates a new InDesign document with specified dimensions and layout settings.

   Args:
       width (int): Document width in points (1 point = 1/72 inch)
       height (int): Document height in points
       pages (int, optional): Number of pages in the document. Defaults to 1.
       pages_facing (bool, optional): Whether to create facing pages (spread layout).
           Defaults to False.
       columns (dict, optional): Column layout configuration with keys:
           - count (int): Number of columns per page
           - gutter (int): Space between columns in points
           Defaults to {"count": 1, "gutter": 12}.
       margins (dict, optional): Page margin settings in points with keys:
           - top (int): Top margin
           - bottom (int): Bottom margin
           - left (int): Left margin
           - right (int): Right margin
           Defaults to {"top": 36, "bottom": 36, "left": 36, "right": 36}.

   Returns:
       dict: Result of the command execution from the InDesign UXP plugin
   """
   command = createCommand("createDocument", {
       "intent": "WEB_INTENT",
       "pageWidth": width,
       "pageHeight": height,
       "margins": margins,
       "columns": columns,
       "pagesPerDocument": pages,
       "pagesFacing": pages_facing
   })

   return sendCommand(command)


# =============================================================================
# TEXT FRAME TOOLS
# =============================================================================

@mcp.tool()
def create_text_frame(
    x: float,
    y: float,
    width: float,
    height: float,
    content: str = "",
    page_index: int = 0
):
    """
    Creates a text frame at the specified position on a page.

    Args:
        x (float): X position from left edge in points
        y (float): Y position from top edge in points
        width (float): Width of the text frame in points
        height (float): Height of the text frame in points
        content (str, optional): Initial text content. Defaults to empty string.
        page_index (int, optional): Page index (0-based). Defaults to 0.

    Returns:
        dict: Contains 'frameId' for referencing the created frame
    """
    command = createCommand("createTextFrame", {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "content": content,
        "pageIndex": page_index
    })
    return sendCommand(command)


@mcp.tool()
def set_text_frame_content(frame_id: int, content: str):
    """
    Sets or replaces the text content in an existing text frame.

    Args:
        frame_id (int): The ID of the text frame to modify
        content (str): The new text content

    Returns:
        dict: Result of the operation
    """
    command = createCommand("setTextFrameContent", {
        "frameId": frame_id,
        "content": content
    })
    return sendCommand(command)


@mcp.tool()
def apply_paragraph_style(frame_id: int, style_name: str):
    """
    Applies a paragraph style to all text in a text frame.

    Args:
        frame_id (int): The ID of the text frame
        style_name (str): Name of the paragraph style to apply

    Returns:
        dict: Result of the operation
    """
    command = createCommand("applyParagraphStyle", {
        "frameId": frame_id,
        "styleName": style_name
    })
    return sendCommand(command)


@mcp.tool()
def apply_character_style(
    frame_id: int,
    style_name: str,
    start_index: int = 0,
    end_index: int = -1
):
    """
    Applies a character style to a range of text within a text frame.

    Args:
        frame_id (int): The ID of the text frame
        style_name (str): Name of the character style to apply
        start_index (int, optional): Start character index. Defaults to 0.
        end_index (int, optional): End character index. -1 means end of text. Defaults to -1.

    Returns:
        dict: Result of the operation
    """
    command = createCommand("applyCharacterStyle", {
        "frameId": frame_id,
        "styleName": style_name,
        "startIndex": start_index,
        "endIndex": end_index
    })
    return sendCommand(command)


# =============================================================================
# COLOR SWATCH TOOLS
# =============================================================================

@mcp.tool()
def create_color_swatch(
    name: str,
    color_value: str,
    color_space: str = "RGB"
):
    """
    Creates a named color swatch in the document.

    Args:
        name (str): Name for the color swatch (e.g., "Synaptic Blue")
        color_value (str): Hex color value (e.g., "#0D1B2A")
        color_space (str, optional): Color space - "RGB" or "CMYK". Defaults to "RGB".

    Returns:
        dict: Contains 'swatchName' of the created swatch
    """
    command = createCommand("createColorSwatch", {
        "name": name,
        "colorValue": color_value,
        "colorSpace": color_space
    })
    return sendCommand(command)


@mcp.tool()
def list_swatches():
    """
    Lists all color swatches in the active document.

    Returns:
        dict: Contains 'swatches' array with swatch names and values
    """
    command = createCommand("listSwatches", {})
    return sendCommand(command)


# =============================================================================
# STYLE MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def create_paragraph_style(
    name: str,
    font_family: str,
    font_size: float,
    leading: float = None,
    color: str = None,
    alignment: str = "LEFT_ALIGN",
    space_before: float = 0,
    space_after: float = 0
):
    """
    Creates a named paragraph style for consistent text formatting.

    Args:
        name (str): Name for the paragraph style (e.g., "Body Text")
        font_family (str): Font family name (e.g., "IBM Plex Serif")
        font_size (float): Font size in points
        leading (float, optional): Line spacing in points. Defaults to auto.
        color (str, optional): Text color as swatch name or hex value
        alignment (str, optional): Text alignment - LEFT_ALIGN, CENTER_ALIGN,
            RIGHT_ALIGN, JUSTIFY_ALIGN. Defaults to "LEFT_ALIGN".
        space_before (float, optional): Space before paragraph in points. Defaults to 0.
        space_after (float, optional): Space after paragraph in points. Defaults to 0.

    Returns:
        dict: Contains 'styleName' of the created style
    """
    command = createCommand("createParagraphStyle", {
        "name": name,
        "fontFamily": font_family,
        "fontSize": font_size,
        "leading": leading,
        "color": color,
        "alignment": alignment,
        "spaceBefore": space_before,
        "spaceAfter": space_after
    })
    return sendCommand(command)


@mcp.tool()
def create_character_style(
    name: str,
    font_family: str = None,
    font_size: float = None,
    font_style: str = None,
    color: str = None
):
    """
    Creates a named character style for inline text formatting.

    Args:
        name (str): Name for the character style (e.g., "Bold Accent")
        font_family (str, optional): Font family name
        font_size (float, optional): Font size in points
        font_style (str, optional): Font style - "Regular", "Bold", "Italic", "Bold Italic"
        color (str, optional): Text color as swatch name or hex value

    Returns:
        dict: Contains 'styleName' of the created style
    """
    command = createCommand("createCharacterStyle", {
        "name": name,
        "fontFamily": font_family,
        "fontSize": font_size,
        "fontStyle": font_style,
        "color": color
    })
    return sendCommand(command)


@mcp.tool()
def list_styles():
    """
    Lists all paragraph and character styles in the document.

    Returns:
        dict: Contains 'paragraphStyles' and 'characterStyles' arrays
    """
    command = createCommand("listStyles", {})
    return sendCommand(command)


# =============================================================================
# IMAGE AND SHAPE TOOLS
# =============================================================================

@mcp.tool()
def place_image(
    file_path: str,
    x: float,
    y: float,
    width: float = None,
    height: float = None,
    page_index: int = 0,
    fit_option: str = "PROPORTIONALLY"
):
    """
    Places an image file into the document.

    Args:
        file_path (str): Absolute path to the image file
        x (float): X position from left edge in points
        y (float): Y position from top edge in points
        width (float, optional): Desired width in points. If omitted, uses original size.
        height (float, optional): Desired height in points. If omitted, uses original size.
        page_index (int, optional): Page index (0-based). Defaults to 0.
        fit_option (str, optional): How to fit content - PROPORTIONALLY,
            FILL_PROPORTIONALLY, CONTENT_TO_FRAME. Defaults to "PROPORTIONALLY".

    Returns:
        dict: Contains 'frameId' of the created image frame
    """
    command = createCommand("placeImage", {
        "filePath": file_path,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "pageIndex": page_index,
        "fitOption": fit_option
    })
    return sendCommand(command)


@mcp.tool()
def create_rectangle(
    x: float,
    y: float,
    width: float,
    height: float,
    fill_color: str = None,
    stroke_color: str = None,
    stroke_weight: float = 0,
    page_index: int = 0
):
    """
    Creates a rectangle shape, useful for backgrounds and containers.

    Args:
        x (float): X position from left edge in points
        y (float): Y position from top edge in points
        width (float): Width in points
        height (float): Height in points
        fill_color (str, optional): Fill color as swatch name or hex value
        stroke_color (str, optional): Stroke color as swatch name or hex value
        stroke_weight (float, optional): Stroke weight in points. Defaults to 0.
        page_index (int, optional): Page index (0-based). Defaults to 0.

    Returns:
        dict: Contains 'frameId' of the created rectangle
    """
    command = createCommand("createRectangle", {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "fillColor": fill_color,
        "strokeColor": stroke_color,
        "strokeWeight": stroke_weight,
        "pageIndex": page_index
    })
    return sendCommand(command)


# =============================================================================
# PAGE MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
def add_page(at_index: int = -1, based_on_master: str = None):
    """
    Adds a new page to the document.

    Args:
        at_index (int, optional): Position to insert page. -1 adds at end. Defaults to -1.
        based_on_master (str, optional): Name of master page to base on.

    Returns:
        dict: Contains 'pageIndex' of the new page
    """
    command = createCommand("addPage", {
        "atIndex": at_index,
        "basedOnMaster": based_on_master
    })
    return sendCommand(command)


@mcp.tool()
def get_page_count():
    """
    Gets the total number of pages in the document.

    Returns:
        dict: Contains 'pageCount' number
    """
    command = createCommand("getPageCount", {})
    return sendCommand(command)


@mcp.tool()
def delete_page(page_index: int):
    """
    Deletes a page from the document.

    Args:
        page_index (int): Index of the page to delete (0-based)

    Returns:
        dict: Result of the operation
    """
    command = createCommand("deletePage", {
        "pageIndex": page_index
    })
    return sendCommand(command)


# =============================================================================
# TABLE TOOLS
# =============================================================================

@mcp.tool()
def create_table(
    x: float,
    y: float,
    width: float,
    height: float,
    rows: int,
    columns: int,
    page_index: int = 0
):
    """
    Creates a table at the specified position.

    Args:
        x (float): X position from left edge in points
        y (float): Y position from top edge in points
        width (float): Total table width in points
        height (float): Total table height in points
        rows (int): Number of rows
        columns (int): Number of columns
        page_index (int, optional): Page index (0-based). Defaults to 0.

    Returns:
        dict: Contains 'tableId' and 'frameId' for referencing the table
    """
    command = createCommand("createTable", {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "rows": rows,
        "columns": columns,
        "pageIndex": page_index
    })
    return sendCommand(command)


@mcp.tool()
def set_table_cell(
    frame_id: int,
    row: int,
    column: int,
    content: str
):
    """
    Sets content in a specific table cell.

    Args:
        frame_id (int): The ID of the text frame containing the table
        row (int): Row index (0-based)
        column (int): Column index (0-based)
        content (str): Text content for the cell

    Returns:
        dict: Result of the operation
    """
    command = createCommand("setTableCell", {
        "frameId": frame_id,
        "row": row,
        "column": column,
        "content": content
    })
    return sendCommand(command)


@mcp.tool()
def style_table_row(
    frame_id: int,
    row: int,
    fill_color: str = None,
    text_color: str = None
):
    """
    Styles a row in a table (useful for headers).

    Args:
        frame_id (int): The ID of the text frame containing the table
        row (int): Row index (0-based)
        fill_color (str, optional): Background color as swatch name or hex
        text_color (str, optional): Text color as swatch name or hex

    Returns:
        dict: Result of the operation
    """
    command = createCommand("styleTableRow", {
        "frameId": frame_id,
        "row": row,
        "fillColor": fill_color,
        "textColor": text_color
    })
    return sendCommand(command)


# =============================================================================
# EXPORT TOOLS
# =============================================================================

@mcp.tool()
def export_pdf(
    output_path: str,
    preset: str = "HIGH_QUALITY_PRINT",
    page_range: str = "ALL"
):
    """
    Exports the document to PDF.

    Args:
        output_path (str): Absolute path for the output PDF file
        preset (str, optional): PDF preset - HIGH_QUALITY_PRINT, SMALLEST_FILE_SIZE,
            PRESS_QUALITY, PDF_X1A_2001. Defaults to "HIGH_QUALITY_PRINT".
        page_range (str, optional): Pages to export - "ALL" or range like "1-5" or "1,3,5".
            Defaults to "ALL".

    Returns:
        dict: Contains 'outputPath' of the exported file
    """
    command = createCommand("exportPDF", {
        "outputPath": output_path,
        "preset": preset,
        "pageRange": page_range
    })
    return sendCommand(command)


@mcp.tool()
def export_jpeg(
    output_path: str,
    page_index: int = 0,
    quality: int = 80,
    resolution: int = 300
):
    """
    Exports a page as a JPEG image.

    Args:
        output_path (str): Absolute path for the output JPEG file
        page_index (int, optional): Page to export (0-based). Defaults to 0.
        quality (int, optional): JPEG quality 0-100. Defaults to 80.
        resolution (int, optional): Resolution in DPI. Defaults to 300.

    Returns:
        dict: Contains 'outputPath' of the exported file
    """
    command = createCommand("exportJPEG", {
        "outputPath": output_path,
        "pageIndex": page_index,
        "quality": quality,
        "resolution": resolution
    })
    return sendCommand(command)


# =============================================================================
# DOCUMENT INSPECTION TOOLS
# =============================================================================

@mcp.tool()
def get_document_info():
    """
    Gets information about the active document.

    Returns:
        dict: Contains document properties (size, pages, margins, etc.)
    """
    command = createCommand("getDocumentInfo", {})
    return sendCommand(command)


@mcp.tool()
def list_text_frames(page_index: int = None):
    """
    Lists all text frames in the document or on a specific page.

    Args:
        page_index (int, optional): Filter to specific page. None returns all frames.

    Returns:
        dict: Contains 'textFrames' array with frame IDs and bounds
    """
    command = createCommand("listTextFrames", {
        "pageIndex": page_index
    })
    return sendCommand(command)


@mcp.tool()
def list_images(page_index: int = None):
    """
    Lists all placed images in the document or on a specific page.

    Args:
        page_index (int, optional): Filter to specific page. None returns all images.

    Returns:
        dict: Contains 'images' array with frame IDs and file paths
    """
    command = createCommand("listImages", {
        "pageIndex": page_index
    })
    return sendCommand(command)


@mcp.tool()
def get_selection():
    """
    Gets information about the currently selected object(s).

    Returns:
        dict: Contains 'selection' array with selected object IDs and types
    """
    command = createCommand("getSelection", {})
    return sendCommand(command)


# =============================================================================
# ADVANCED LAYOUT TOOLS
# =============================================================================

@mcp.tool()
def create_master_page(
    name: str,
    prefix: str = "A",
    based_on: str = None
):
    """
    Creates a new master page (master spread) for consistent layouts.

    Master pages contain elements that appear on all pages using that master,
    such as headers, footers, page numbers, and background elements.

    Args:
        name: Name for the master page (e.g., "Chapter Opener")
        prefix: Single letter prefix shown in Pages panel (default: "A")
        based_on: Name of existing master to base this on (optional)

    Returns:
        dict: Contains 'masterName' of the created master spread
    """
    command = createCommand("createMasterPage", {
        "name": name,
        "prefix": prefix,
        "basedOn": based_on
    })
    return sendCommand(command)


@mcp.tool()
def link_text_frames(
    source_frame_id: int,
    target_frame_id: int
):
    """
    Links two text frames so text flows from source to target.

    When text overflows the source frame, it continues in the target frame.
    This is essential for multi-page documents like whitepapers.

    Args:
        source_frame_id: ID of the frame where text starts
        target_frame_id: ID of the frame where overflow text continues

    Returns:
        dict: Contains success status
    """
    command = createCommand("linkTextFrames", {
        "sourceFrameId": source_frame_id,
        "targetFrameId": target_frame_id
    })
    return sendCommand(command)


@mcp.tool()
def set_text_wrap(
    frame_id: int,
    wrap_mode: str = "BOUNDING_BOX",
    offset_top: float = 12,
    offset_left: float = 12,
    offset_bottom: float = 12,
    offset_right: float = 12
):
    """
    Sets text wrap preferences for an object so text flows around it.

    Essential for placing images in text-heavy layouts.

    Args:
        frame_id: ID of the frame (rectangle, image frame) to wrap text around
        wrap_mode: Type of wrap - "NONE", "BOUNDING_BOX", "CONTOUR", "JUMP_OBJECT"
        offset_top: Space above object in points (default: 12)
        offset_left: Space left of object in points (default: 12)
        offset_bottom: Space below object in points (default: 12)
        offset_right: Space right of object in points (default: 12)

    Returns:
        dict: Contains success status
    """
    command = createCommand("setTextWrap", {
        "frameId": frame_id,
        "wrapMode": wrap_mode,
        "offsetTop": offset_top,
        "offsetLeft": offset_left,
        "offsetBottom": offset_bottom,
        "offsetRight": offset_right
    })
    return sendCommand(command)


@mcp.tool()
def save_document(
    file_path: str = None
):
    """
    Saves the active InDesign document.

    If no path is provided and the document has been saved before,
    it saves to the existing location. For new documents, a path is required.

    Args:
        file_path: Full path where to save the document (e.g., "/Users/name/Documents/whitepaper.indd")
                   If None, saves to existing location for previously saved documents.

    Returns:
        dict: Contains 'filePath' of the saved document
    """
    command = createCommand("saveDocument", {
        "filePath": file_path
    })
    return sendCommand(command)


@mcp.tool()
def close_document(
    save: bool = False
):
    """
    Closes the active InDesign document.

    Args:
        save: If True, saves the document before closing. If False, closes without saving
              (discarding any unsaved changes). Defaults to False.

    Returns:
        dict: Contains 'success' status and 'documentName' of the closed document
    """
    command = createCommand("closeDocument", {
        "save": save
    })
    return sendCommand(command)


@mcp.resource("config://get_instructions")
def get_instructions() -> str:
    """Read this first! Returns information and instructions on how to use Photoshop and this API"""

    return f"""
    You are an InDesign and design expert who is creative and loves to help other people learn to use InDesign and create.

    Rules to follow:

    1. Think deeply about how to solve the task
    2. Always check your work
    3. Read the info for the API calls to make sure you understand the requirements and arguments
    """


"""
BLEND_MODES = [
    "COLOR",
    "COLORBURN",
    "COLORDODGE",
    "DARKEN",
    "DARKERCOLOR",
    "DIFFERENCE",
    "DISSOLVE",
    "EXCLUSION",
    "HARDLIGHT",
    "HARDMIX",
    "HUE",
    "LIGHTEN",
    "LIGHTERCOLOR",
    "LINEARBURN",
    "LINEARDODGE",
    "LINEARLIGHT",
    "LUMINOSITY",
    "MULTIPLY",
    "NORMAL",
    "OVERLAY",
    "PINLIGHT",
    "SATURATION",
    "SCREEN",
    "SOFTLIGHT",
    "VIVIDLIGHT",
    "SUBTRACT",
    "DIVIDE"
]
"""