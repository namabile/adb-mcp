# MIT License
# Copyright (c) 2025 Mike Chambers

"""
Live integration tests for InDesign MCP tools.

These tests require:
1. InDesign to be running
2. The adb-mcp UXP plugin to be loaded in InDesign
3. The proxy server running on ws://localhost:3001

Run with: pytest tests/test_id_live.py -v --live
Or run directly: python tests/test_id_live.py

These tests will create actual documents in InDesign!
"""

import pytest
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if we should run live tests
def pytest_configure(config):
    config.addinivalue_line("markers", "live: mark test as requiring live InDesign connection")


def is_live_mode():
    """Check if --live flag was passed or running directly."""
    return "--live" in sys.argv or __name__ == "__main__"


# Only import MCP modules if running live tests
if is_live_mode():
    from core import init, sendCommand, createCommand
    import socket_client

    # Configure socket client
    APPLICATION = "indesign"
    PROXY_URL = 'http://localhost:3001'
    PROXY_TIMEOUT = 20

    socket_client.configure(
        app=APPLICATION,
        url=PROXY_URL,
        timeout=PROXY_TIMEOUT
    )
    init(APPLICATION, socket_client)


@pytest.mark.live
class TestLiveDocumentCreation:
    """Live tests for document creation."""

    def test_create_document(self):
        """Test creating a new InDesign document."""
        command = createCommand("createDocument", {
            "intent": "WEB_INTENT",
            "pageWidth": 612,  # Letter width in points
            "pageHeight": 792,  # Letter height in points
            "margins": {"top": 36, "bottom": 36, "left": 36, "right": 36},
            "columns": {"count": 1, "gutter": 12},
            "pagesPerDocument": 1,
            "pagesFacing": False
        })

        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Created document: {result}")

    def test_get_document_info(self):
        """Test getting document info."""
        command = createCommand("getDocumentInfo", {})
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Document info: {result}")


@pytest.mark.live
class TestLiveColorSwatches:
    """Live tests for color swatch creation."""

    def test_create_brand_colors(self):
        """Test creating Ultrathink brand color swatches."""
        brand_colors = [
            ("Synaptic Blue", "#0D1B2A"),
            ("Void Black", "#0B090A"),
            ("Axon White", "#F5F5F5"),
            ("Neural Gold", "#FFB703"),
            ("Spark Yellow", "#FFD000"),
            ("Electric Orange", "#FB8500"),
        ]

        for name, hex_value in brand_colors:
            command = createCommand("createColorSwatch", {
                "name": name,
                "colorValue": hex_value,
                "colorSpace": "RGB"
            })
            result = sendCommand(command)
            assert result["status"] == "SUCCESS", f"Failed to create {name}: {result}"
            print(f"✓ Created swatch: {name}")

    def test_list_swatches(self):
        """Test listing all swatches."""
        command = createCommand("listSwatches", {})
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Swatches: {result.get('response', {}).get('swatches', [])}")


@pytest.mark.live
class TestLiveTextFrames:
    """Live tests for text frame creation."""

    def test_create_text_frame(self):
        """Test creating a text frame with content."""
        command = createCommand("createTextFrame", {
            "x": 36,
            "y": 100,
            "width": 540,
            "height": 50,
            "content": "Test Headline - Ultrathink Solutions",
            "pageIndex": 0
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        frame_id = result.get("response", {}).get("frameId")
        print(f"✓ Created text frame with ID: {frame_id}")
        return frame_id

    def test_list_text_frames(self):
        """Test listing all text frames."""
        command = createCommand("listTextFrames", {"pageIndex": None})
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Text frames: {result.get('response', {}).get('textFrames', [])}")


@pytest.mark.live
class TestLiveStyles:
    """Live tests for style creation."""

    def test_create_paragraph_styles(self):
        """Test creating paragraph styles for whitepaper."""
        styles = [
            {
                "name": "WP Headline",
                "fontFamily": "Helvetica",  # Fallback if 0xProto not installed
                "fontSize": 24,
                "color": "#0D1B2A",
                "alignment": "LEFT_ALIGN",
                "spaceBefore": 0,
                "spaceAfter": 12
            },
            {
                "name": "WP Body",
                "fontFamily": "Georgia",  # Fallback if IBM Plex Serif not installed
                "fontSize": 11,
                "leading": 14,
                "color": "#0B090A",
                "alignment": "JUSTIFY_ALIGN",
                "spaceBefore": 0,
                "spaceAfter": 6
            }
        ]

        for style in styles:
            command = createCommand("createParagraphStyle", style)
            result = sendCommand(command)
            assert result["status"] == "SUCCESS", f"Failed to create style {style['name']}: {result}"
            print(f"✓ Created paragraph style: {style['name']}")

    def test_list_styles(self):
        """Test listing all styles."""
        command = createCommand("listStyles", {})
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        data = result.get("response", {})
        print(f"✓ Paragraph styles: {data.get('paragraphStyles', [])}")
        print(f"✓ Character styles: {data.get('characterStyles', [])}")


@pytest.mark.live
class TestLiveRectangles:
    """Live tests for rectangle/shape creation."""

    def test_create_header_bar(self):
        """Test creating a colored header bar."""
        command = createCommand("createRectangle", {
            "x": 0,
            "y": 0,
            "width": 612,
            "height": 80,
            "fillColor": "#0D1B2A",  # Synaptic Blue
            "strokeColor": None,
            "strokeWeight": 0,
            "pageIndex": 0
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Created header rectangle: {result.get('response', {}).get('frameId')}")


@pytest.mark.live
class TestLivePageManagement:
    """Live tests for page management."""

    def test_get_page_count(self):
        """Test getting page count."""
        command = createCommand("getPageCount", {})
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Page count: {result.get('response', {}).get('pageCount')}")

    def test_add_page(self):
        """Test adding a new page."""
        command = createCommand("addPage", {
            "atIndex": -1,
            "basedOnMaster": None
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Added page at index: {result.get('response', {}).get('pageIndex')}")


@pytest.mark.live
class TestLiveTables:
    """Live tests for table creation."""

    def test_create_table(self):
        """Test creating a table."""
        command = createCommand("createTable", {
            "x": 36,
            "y": 300,
            "width": 540,
            "height": 150,
            "rows": 4,
            "columns": 3,
            "pageIndex": 0
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        frame_id = result.get("response", {}).get("frameId")
        print(f"✓ Created table in frame: {frame_id}")
        return frame_id


@pytest.mark.live
class TestLiveImagePlacement:
    """Live tests for image placement."""

    def test_place_image(self):
        """Test placing an image file into the document."""
        # Use the test fixture image
        test_image_path = os.path.join(
            os.path.dirname(__file__), "fixtures", "test_image.png"
        )

        command = createCommand("placeImage", {
            "filePath": test_image_path,
            "x": 36,
            "y": 160,
            "width": 200,
            "height": 100,
            "pageIndex": 0,
            "fitOption": "PROPORTIONALLY"
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        frame_id = result.get("response", {}).get("frameId")
        print(f"✓ Placed image with frame ID: {frame_id}")
        return frame_id

    def test_list_images(self):
        """Test listing all placed images."""
        command = createCommand("listImages", {"pageIndex": 0})
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        images = result.get("response", {}).get("images", [])
        print(f"✓ Images on page: {len(images)} found")


@pytest.mark.live
class TestLiveStyleApplication:
    """Live tests for applying styles to content."""

    def test_apply_paragraph_style(self):
        """Test applying a paragraph style to a text frame."""
        # First create a text frame
        frame_cmd = createCommand("createTextFrame", {
            "x": 250, "y": 160, "width": 300, "height": 80,
            "content": "This text will have a style applied to it.",
            "pageIndex": 0
        })
        frame_result = sendCommand(frame_cmd)
        assert frame_result["status"] == "SUCCESS", f"Failed to create frame: {frame_result}"
        frame_id = frame_result.get("response", {}).get("frameId")

        # Apply the WP Body style (created in earlier test)
        style_cmd = createCommand("applyParagraphStyle", {
            "frameId": frame_id,
            "styleName": "WP Body"
        })
        result = sendCommand(style_cmd)
        assert result["status"] == "SUCCESS", f"Failed to apply style: {result}"
        print(f"✓ Applied 'WP Body' style to frame {frame_id}")

    def test_set_text_frame_content(self):
        """Test updating text content in an existing frame."""
        # Create a frame first
        frame_cmd = createCommand("createTextFrame", {
            "x": 250, "y": 250, "width": 300, "height": 40,
            "content": "Original content",
            "pageIndex": 0
        })
        frame_result = sendCommand(frame_cmd)
        assert frame_result["status"] == "SUCCESS", f"Failed to create frame: {frame_result}"
        frame_id = frame_result.get("response", {}).get("frameId")

        # Update the content
        update_cmd = createCommand("setTextFrameContent", {
            "frameId": frame_id,
            "content": "Updated content - Ultrathink Solutions"
        })
        result = sendCommand(update_cmd)
        assert result["status"] == "SUCCESS", f"Failed to update content: {result}"
        print(f"✓ Updated text content in frame {frame_id}")


@pytest.mark.live
class TestLiveTableOperations:
    """Live tests for table cell operations."""

    def test_set_table_cells(self):
        """Test setting content in table cells."""
        # Create a table first
        table_cmd = createCommand("createTable", {
            "x": 36, "y": 460,
            "width": 540, "height": 120,
            "rows": 3, "columns": 3,
            "pageIndex": 0
        })
        table_result = sendCommand(table_cmd)
        assert table_result["status"] == "SUCCESS", f"Failed to create table: {table_result}"
        table_id = table_result.get("response", {}).get("tableId")

        # Set header cells
        headers = ["Feature", "Standard", "Premium"]
        for col, header in enumerate(headers):
            cell_cmd = createCommand("setTableCell", {
                "tableId": table_id,
                "row": 0,
                "column": col,
                "content": header
            })
            result = sendCommand(cell_cmd)
            assert result["status"] == "SUCCESS", f"Failed to set cell [0,{col}]: {result}"

        # Set data cells
        data = [
            ["API Access", "Limited", "Unlimited"],
            ["Support", "Email", "24/7 Phone"]
        ]
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                cell_cmd = createCommand("setTableCell", {
                    "tableId": table_id,
                    "row": row_idx + 1,
                    "column": col_idx,
                    "content": value
                })
                result = sendCommand(cell_cmd)
                assert result["status"] == "SUCCESS", f"Failed to set cell [{row_idx+1},{col_idx}]: {result}"

        print(f"✓ Populated table {table_id} with 9 cells")

    def test_style_table_row(self):
        """Test styling a table row."""
        # Create another table for styling test
        table_cmd = createCommand("createTable", {
            "x": 36, "y": 600,
            "width": 540, "height": 80,
            "rows": 2, "columns": 3,
            "pageIndex": 0
        })
        table_result = sendCommand(table_cmd)
        assert table_result["status"] == "SUCCESS", f"Failed to create table: {table_result}"
        table_id = table_result.get("response", {}).get("tableId")

        # Style the header row with brand colors
        style_cmd = createCommand("styleTableRow", {
            "tableId": table_id,
            "rowIndex": 0,
            "fillColor": "#0D1B2A",  # Synaptic Blue
            "textColor": "#F5F5F5"   # Axon White
        })
        result = sendCommand(style_cmd)
        assert result["status"] == "SUCCESS", f"Failed to style row: {result}"
        print(f"✓ Styled header row of table {table_id} with brand colors")


@pytest.mark.live
class TestLiveExport:
    """Live tests for document export."""

    def test_export_pdf(self):
        """Test exporting document to PDF."""
        # Use user's home directory for better UXP compatibility
        home = os.path.expanduser("~")
        output_path = f"{home}/Desktop/ultrathink_test_whitepaper.pdf"

        command = createCommand("exportPDF", {
            "outputPath": output_path,
            "preset": "HIGH_QUALITY_PRINT",
            "pageRange": "ALL"
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Exported PDF to: {output_path}")

        # Verify file was created
        assert os.path.exists(output_path), f"PDF file not found at {output_path}"
        file_size = os.path.getsize(output_path)
        print(f"✓ PDF file size: {file_size:,} bytes")

        # Clean up
        os.remove(output_path)

    def test_export_jpeg(self):
        """Test exporting a page as JPEG."""
        home = os.path.expanduser("~")
        output_path = f"{home}/Desktop/ultrathink_test_page1.jpg"

        command = createCommand("exportJPEG", {
            "outputPath": output_path,
            "pageIndex": 0,
            "quality": 80,
            "resolution": 150
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Exported JPEG to: {output_path}")

        # Verify file was created
        assert os.path.exists(output_path), f"JPEG file not found at {output_path}"
        file_size = os.path.getsize(output_path)
        print(f"✓ JPEG file size: {file_size:,} bytes")

        # Clean up
        os.remove(output_path)


@pytest.mark.live
class TestLiveSaveDocument:
    """Live tests for saving documents."""

    def test_save_document(self):
        """Test saving the InDesign document."""
        home = os.path.expanduser("~")
        output_path = f"{home}/Desktop/ultrathink_test_document.indd"

        command = createCommand("saveDocument", {
            "filePath": output_path
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Saved document to: {output_path}")

        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)


@pytest.mark.live
class TestLiveAdvancedLayout:
    """Live tests for advanced layout tools."""

    def test_create_master_page(self):
        """Test creating a master page."""
        command = createCommand("createMasterPage", {
            "name": "Whitepaper Header",
            "prefix": "B",
            "basedOn": None
        })
        result = sendCommand(command)
        assert result["status"] == "SUCCESS", f"Failed: {result}"
        print(f"✓ Created master page: {result.get('response', {}).get('masterName')}")

    def test_link_text_frames(self):
        """Test linking two text frames for text flow."""
        # Create first frame
        cmd1 = createCommand("createTextFrame", {
            "x": 36, "y": 500, "width": 250, "height": 200,
            "content": "This is a long text that should overflow into the next frame. " * 10,
            "pageIndex": 0
        })
        result1 = sendCommand(cmd1)
        assert result1["status"] == "SUCCESS", f"Failed to create frame 1: {result1}"
        frame1_id = result1.get("response", {}).get("frameId")

        # Create second frame
        cmd2 = createCommand("createTextFrame", {
            "x": 320, "y": 500, "width": 250, "height": 200,
            "content": "",
            "pageIndex": 0
        })
        result2 = sendCommand(cmd2)
        assert result2["status"] == "SUCCESS", f"Failed to create frame 2: {result2}"
        frame2_id = result2.get("response", {}).get("frameId")

        # Link the frames
        link_cmd = createCommand("linkTextFrames", {
            "sourceFrameId": frame1_id,
            "targetFrameId": frame2_id
        })
        result = sendCommand(link_cmd)
        assert result["status"] == "SUCCESS", f"Failed to link frames: {result}"
        print(f"✓ Linked text frames: {frame1_id} -> {frame2_id}")

    def test_set_text_wrap(self):
        """Test setting text wrap on a rectangle."""
        # Create a rectangle
        cmd = createCommand("createRectangle", {
            "x": 200, "y": 200, "width": 150, "height": 100,
            "fillColor": "#FFB703",
            "pageIndex": 0
        })
        result = sendCommand(cmd)
        assert result["status"] == "SUCCESS", f"Failed to create rectangle: {result}"
        frame_id = result.get("response", {}).get("frameId")

        # Set text wrap
        wrap_cmd = createCommand("setTextWrap", {
            "frameId": frame_id,
            "wrapMode": "BOUNDING_BOX",
            "offsetTop": 24,
            "offsetLeft": 24,
            "offsetBottom": 24,
            "offsetRight": 24
        })
        result = sendCommand(wrap_cmd)
        assert result["status"] == "SUCCESS", f"Failed to set text wrap: {result}"
        print(f"✓ Set text wrap on frame: {frame_id}")


def run_all_live_tests():
    """Run all live tests in sequence."""
    print("\n" + "=" * 60)
    print("INDESIGN MCP LIVE INTEGRATION TESTS")
    print("=" * 60)
    print("\nMake sure InDesign is running with the adb-mcp plugin loaded!")
    print("-" * 60)

    tests = [
        ("Document Creation", TestLiveDocumentCreation()),
        ("Color Swatches", TestLiveColorSwatches()),
        ("Paragraph Styles", TestLiveStyles()),
        ("Rectangles", TestLiveRectangles()),
        ("Text Frames", TestLiveTextFrames()),
        ("Image Placement", TestLiveImagePlacement()),
        ("Style Application", TestLiveStyleApplication()),
        ("Page Management", TestLivePageManagement()),
        ("Tables", TestLiveTables()),
        ("Table Operations", TestLiveTableOperations()),
        ("Advanced Layout", TestLiveAdvancedLayout()),
        ("Save Document", TestLiveSaveDocument()),
        ("Export", TestLiveExport()),
    ]

    passed = 0
    failed = 0

    for name, test_class in tests:
        print(f"\n--- {name} ---")
        for method_name in dir(test_class):
            if method_name.startswith("test_"):
                method = getattr(test_class, method_name)
                try:
                    method()
                    passed += 1
                except Exception as e:
                    print(f"✗ {method_name}: {e}")
                    failed += 1
                time.sleep(0.5)  # Brief pause between tests

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    # Teardown: Close the test document without saving
    print("\n--- Teardown ---")
    try:
        close_cmd = createCommand("closeDocument", {"save": False})
        result = sendCommand(close_cmd)
        if result["status"] == "SUCCESS":
            doc_name = result.get("response", {}).get("documentName", "unknown")
            print(f"✓ Closed test document: {doc_name}")
        else:
            print(f"✗ Failed to close document: {result}")
    except Exception as e:
        print(f"✗ Error during teardown: {e}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_live_tests()
    sys.exit(0 if success else 1)
