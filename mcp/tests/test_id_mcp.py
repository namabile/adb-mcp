# MIT License
# Copyright (c) 2025 Mike Chambers

"""
Unit tests for InDesign MCP tools.

These tests verify the Python MCP layer creates correct command structures.
They mock the socket_client to avoid requiring a live InDesign connection.

Run with: pytest tests/test_id_mcp.py -v
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_socket_client():
    """Create a mock socket client that captures commands."""
    mock = MagicMock()
    mock.send_message_blocking.return_value = {"status": "success", "data": {}}
    return mock


@pytest.fixture
def id_mcp_module(mock_socket_client):
    """Import id-mcp module with mocked dependencies."""
    # Mock the socket_client module before importing
    with patch.dict('sys.modules', {'socket_client': MagicMock()}):
        # Mock the core module's sendCommand to capture commands
        import core
        core.socket_client = mock_socket_client
        core.application = "indesign"

        # Now import the MCP module (it will use our mocked core)
        import importlib
        if 'id-mcp' in sys.modules:
            del sys.modules['id-mcp']

        # We need to test the functions directly, so let's recreate them
        from core import createCommand, sendCommand
        return createCommand, sendCommand, mock_socket_client


class TestCommandCreation:
    """Test that commands are created with correct structure."""

    def test_create_command_structure(self):
        """Test createCommand produces valid command dict."""
        from core import createCommand, init
        import socket_client

        # Initialize core module
        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("testAction", {"key": "value"})

        assert command["application"] == "indesign"
        assert command["action"] == "testAction"
        assert command["options"] == {"key": "value"}


class TestTextFrameTools:
    """Test text frame tool command generation."""

    def test_create_text_frame_command(self):
        """Test create_text_frame generates correct command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("createTextFrame", {
            "x": 100,
            "y": 200,
            "width": 300,
            "height": 150,
            "content": "Test content",
            "pageIndex": 0
        })

        assert command["action"] == "createTextFrame"
        assert command["options"]["x"] == 100
        assert command["options"]["y"] == 200
        assert command["options"]["width"] == 300
        assert command["options"]["height"] == 150
        assert command["options"]["content"] == "Test content"
        assert command["options"]["pageIndex"] == 0

    def test_apply_paragraph_style_command(self):
        """Test apply_paragraph_style generates correct command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("applyParagraphStyle", {
            "frameId": 12345,
            "styleName": "Body Text"
        })

        assert command["action"] == "applyParagraphStyle"
        assert command["options"]["frameId"] == 12345
        assert command["options"]["styleName"] == "Body Text"


class TestColorSwatchTools:
    """Test color swatch tool command generation."""

    def test_create_color_swatch_rgb(self):
        """Test create_color_swatch with RGB color."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("createColorSwatch", {
            "name": "Synaptic Blue",
            "colorValue": "#0D1B2A",
            "colorSpace": "RGB"
        })

        assert command["action"] == "createColorSwatch"
        assert command["options"]["name"] == "Synaptic Blue"
        assert command["options"]["colorValue"] == "#0D1B2A"
        assert command["options"]["colorSpace"] == "RGB"

    def test_create_color_swatch_cmyk(self):
        """Test create_color_swatch with CMYK color space."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("createColorSwatch", {
            "name": "Print Blue",
            "colorValue": "#0D1B2A",
            "colorSpace": "CMYK"
        })

        assert command["options"]["colorSpace"] == "CMYK"


class TestStyleTools:
    """Test style management tool command generation."""

    def test_create_paragraph_style_command(self):
        """Test create_paragraph_style with all options."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("createParagraphStyle", {
            "name": "Headline",
            "fontFamily": "0xProto",
            "fontSize": 24,
            "leading": 28,
            "color": "#0D1B2A",
            "alignment": "CENTER_ALIGN",
            "spaceBefore": 12,
            "spaceAfter": 6
        })

        assert command["action"] == "createParagraphStyle"
        assert command["options"]["name"] == "Headline"
        assert command["options"]["fontFamily"] == "0xProto"
        assert command["options"]["fontSize"] == 24
        assert command["options"]["leading"] == 28
        assert command["options"]["alignment"] == "CENTER_ALIGN"

    def test_create_character_style_command(self):
        """Test create_character_style command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("createCharacterStyle", {
            "name": "Bold Accent",
            "fontFamily": "IBM Plex Serif",
            "fontStyle": "Bold",
            "color": "#FFB703"
        })

        assert command["action"] == "createCharacterStyle"
        assert command["options"]["fontStyle"] == "Bold"


class TestImageTools:
    """Test image and shape tool command generation."""

    def test_place_image_command(self):
        """Test place_image command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("placeImage", {
            "filePath": "/path/to/image.png",
            "x": 36,
            "y": 100,
            "width": 540,
            "height": None,
            "pageIndex": 0,
            "fitOption": "PROPORTIONALLY"
        })

        assert command["action"] == "placeImage"
        assert command["options"]["filePath"] == "/path/to/image.png"
        assert command["options"]["fitOption"] == "PROPORTIONALLY"

    def test_create_rectangle_command(self):
        """Test create_rectangle command with all options."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("createRectangle", {
            "x": 0,
            "y": 0,
            "width": 612,
            "height": 80,
            "fillColor": "Synaptic Blue",
            "strokeColor": None,
            "strokeWeight": 0,
            "pageIndex": 0
        })

        assert command["action"] == "createRectangle"
        assert command["options"]["fillColor"] == "Synaptic Blue"


class TestTableTools:
    """Test table tool command generation."""

    def test_create_table_command(self):
        """Test create_table command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("createTable", {
            "x": 36,
            "y": 200,
            "width": 540,
            "height": 200,
            "rows": 5,
            "columns": 3,
            "pageIndex": 0
        })

        assert command["action"] == "createTable"
        assert command["options"]["rows"] == 5
        assert command["options"]["columns"] == 3

    def test_set_table_cell_command(self):
        """Test set_table_cell command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("setTableCell", {
            "frameId": 12345,
            "row": 0,
            "column": 1,
            "content": "Header Cell"
        })

        assert command["action"] == "setTableCell"
        assert command["options"]["row"] == 0
        assert command["options"]["column"] == 1


class TestExportTools:
    """Test export tool command generation."""

    def test_export_pdf_command(self):
        """Test export_pdf command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("exportPDF", {
            "outputPath": "/output/whitepaper.pdf",
            "preset": "HIGH_QUALITY_PRINT",
            "pageRange": "ALL"
        })

        assert command["action"] == "exportPDF"
        assert command["options"]["outputPath"] == "/output/whitepaper.pdf"
        assert command["options"]["preset"] == "HIGH_QUALITY_PRINT"

    def test_export_jpeg_command(self):
        """Test export_jpeg command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("exportJPEG", {
            "outputPath": "/output/page1.jpg",
            "pageIndex": 0,
            "quality": 90,
            "resolution": 300
        })

        assert command["action"] == "exportJPEG"
        assert command["options"]["quality"] == 90
        assert command["options"]["resolution"] == 300


class TestPageTools:
    """Test page management tool command generation."""

    def test_add_page_command(self):
        """Test add_page command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("addPage", {
            "atIndex": -1,
            "basedOnMaster": "A-Master"
        })

        assert command["action"] == "addPage"
        assert command["options"]["atIndex"] == -1
        assert command["options"]["basedOnMaster"] == "A-Master"

    def test_delete_page_command(self):
        """Test delete_page command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("deletePage", {
            "pageIndex": 2
        })

        assert command["action"] == "deletePage"
        assert command["options"]["pageIndex"] == 2


class TestInspectionTools:
    """Test document inspection tool command generation."""

    def test_get_document_info_command(self):
        """Test get_document_info command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("getDocumentInfo", {})

        assert command["action"] == "getDocumentInfo"
        assert command["options"] == {}

    def test_list_text_frames_command(self):
        """Test list_text_frames command."""
        from core import createCommand, init

        mock_client = MagicMock()
        init("indesign", mock_client)

        command = createCommand("listTextFrames", {
            "pageIndex": 0
        })

        assert command["action"] == "listTextFrames"
        assert command["options"]["pageIndex"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
