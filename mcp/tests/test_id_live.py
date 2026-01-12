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
        ("Page Management", TestLivePageManagement()),
        ("Tables", TestLiveTables()),
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

    return failed == 0


if __name__ == "__main__":
    success = run_all_live_tests()
    sys.exit(0 if success else 1)
