#!/usr/bin/env python3
"""
Test Sprint 3: Layer Management and Export Tools

Tests:
1. Layer operations: create, rename, visibility, lock, reorder, delete
2. Export operations: SVG, PDF, JPEG
"""

import sys
import os
import tempfile

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from ai-mcp.py (has hyphen)
import importlib.util
spec = importlib.util.spec_from_file_location("ai_mcp",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai-mcp.py"))
ai_mcp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_mcp)

# Extract functions from the loaded module
create_document = ai_mcp.create_document
close_document = ai_mcp.close_document
create_brand_swatches = ai_mcp.create_brand_swatches
create_rectangle = ai_mcp.create_rectangle
create_point_text = ai_mcp.create_point_text
# Layer tools
create_layer = ai_mcp.create_layer
delete_layer = ai_mcp.delete_layer
rename_layer = ai_mcp.rename_layer
set_layer_visibility = ai_mcp.set_layer_visibility
set_layer_lock = ai_mcp.set_layer_lock
reorder_layer = ai_mcp.reorder_layer
get_layers = ai_mcp.get_layers
# Export tools
export_svg = ai_mcp.export_svg
export_pdf = ai_mcp.export_pdf
export_jpeg = ai_mcp.export_jpeg


def parse_result(result):
    """Parse the MCP result content from socket response"""
    import json

    # Handle the full socket response format: {senderId, response, status, document}
    if isinstance(result, dict):
        # Check for response.content[0].text structure (from socket client)
        if 'response' in result and 'content' in result['response']:
            text = result['response']['content'][0]['text']
            return json.loads(text)
        # Check for direct content[0].text structure
        elif 'content' in result:
            text = result['content'][0]['text']
            return json.loads(text)

    return result


def test_layer_management():
    """Test layer creation, modification, and deletion"""
    print("\n=== Testing Layer Management ===")

    # Create test document
    print("\n1. Creating test document...")
    result = parse_result(create_document(width=800, height=600, name="LayerTest"))
    assert result.get('success'), f"Failed to create document: {result}"
    print(f"   ✓ Created document: {result.get('name')}")

    # Create layers
    print("\n2. Creating layers...")

    # Create Background layer
    result = parse_result(create_layer(name="Background", visible=True, locked=False))
    assert result.get('success'), f"Failed to create Background layer: {result}"
    print(f"   ✓ Created layer: {result.get('layerName')}")

    # Create Content layer
    result = parse_result(create_layer(name="Content", visible=True, locked=False))
    assert result.get('success'), f"Failed to create Content layer: {result}"
    print(f"   ✓ Created layer: {result.get('layerName')}")

    # Create Header layer
    result = parse_result(create_layer(name="Header", visible=True, locked=False))
    assert result.get('success'), f"Failed to create Header layer: {result}"
    print(f"   ✓ Created layer: {result.get('layerName')}")

    # Get layers to verify
    print("\n3. Getting layer list...")
    result = parse_result(get_layers())
    assert result.get('totalLayers') >= 3, f"Expected at least 3 layers: {result}"
    layer_names = [l['name'] for l in result.get('layers', [])]
    print(f"   ✓ Total layers: {result.get('totalLayers')}")
    print(f"   ✓ Layer names: {layer_names}")

    # Rename layer
    print("\n4. Testing rename_layer...")
    result = parse_result(rename_layer(current_name="Content", new_name="MainContent"))
    assert result.get('success'), f"Failed to rename layer: {result}"
    print(f"   ✓ Renamed '{result.get('oldName')}' to '{result.get('newName')}'")

    # Set visibility
    print("\n5. Testing set_layer_visibility...")
    result = parse_result(set_layer_visibility(name="Background", visible=False))
    assert result.get('success'), f"Failed to set visibility: {result}"
    print(f"   ✓ Set {result.get('layerName')} visible={result.get('visible')}")

    # Set lock
    print("\n6. Testing set_layer_lock...")
    result = parse_result(set_layer_lock(name="Header", locked=True))
    assert result.get('success'), f"Failed to set lock: {result}"
    print(f"   ✓ Set {result.get('layerName')} locked={result.get('locked')}")

    # Unlock for later operations
    result = parse_result(set_layer_lock(name="Header", locked=False))

    # Reorder layer (use MainContent which we know exists from rename)
    print("\n7. Testing reorder_layer...")
    result = parse_result(reorder_layer(name="MainContent", position="front"))
    assert result.get('success'), f"Failed to reorder layer: {result}"
    print(f"   ✓ Moved {result.get('layerName')} to position {result.get('newZOrderPosition')}")

    # Delete layer (delete the unlocked Header layer)
    print("\n8. Testing delete_layer...")
    result = parse_result(delete_layer(name="Header"))
    assert result.get('success'), f"Failed to delete layer: {result}"
    print(f"   ✓ Deleted layer: {result.get('deletedLayer')}, remaining: {result.get('remainingLayers')}")

    # Make Background visible again for export tests (it was hidden in step 5)
    result = parse_result(set_layer_visibility(name="Background", visible=True))
    if result.get('success'):
        print("   ✓ Made Background visible again for export tests")

    print("\n✅ Layer management tests PASSED")
    return True


def test_export_tools():
    """Test SVG, PDF, and JPEG export"""
    print("\n=== Testing Export Tools ===")

    # Create a simple infographic for export testing
    print("\n1. Setting up content for export...")

    # Add brand swatches and some content
    create_brand_swatches()
    create_rectangle(x=0, y=0, width=800, height=600, fill_color="Synaptic Blue")
    create_rectangle(x=50, y=50, width=700, height=100, fill_color="Neural Gold")
    create_point_text(x=100, y=100, content="Export Test", font_size=36, text_color="#FFFFFF")
    print("   ✓ Created test content")

    # Use Desktop for exports (more accessible and avoids permission issues)
    temp_dir = os.path.expanduser("~/Desktop/illustrator_export_test")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"   ✓ Export directory: {temp_dir}")

    # Test SVG export
    print("\n2. Testing export_svg...")
    svg_path = os.path.join(temp_dir, "test_export.svg")
    result = parse_result(export_svg(output_path=svg_path, embed_fonts=True))
    assert result.get('success'), f"SVG export failed: {result}"
    assert os.path.exists(svg_path), f"SVG file not created at {svg_path}"
    svg_size = os.path.getsize(svg_path)
    print(f"   ✓ Exported SVG: {svg_path} ({svg_size} bytes)")

    # Test PDF export
    print("\n3. Testing export_pdf...")
    pdf_path = os.path.join(temp_dir, "test_export.pdf")
    result = parse_result(export_pdf(output_path=pdf_path, preserve_editability=True))
    assert result.get('success'), f"PDF export failed: {result}"
    assert os.path.exists(pdf_path), f"PDF file not created at {pdf_path}"
    pdf_size = os.path.getsize(pdf_path)
    print(f"   ✓ Exported PDF: {pdf_path} ({pdf_size} bytes)")

    # Test JPEG export
    print("\n4. Testing export_jpeg...")
    jpg_path = os.path.join(temp_dir, "test_export.jpg")
    result = parse_result(export_jpeg(output_path=jpg_path, quality=90))
    assert result.get('success'), f"JPEG export failed: {result}"
    assert os.path.exists(jpg_path), f"JPEG file not created at {jpg_path}"
    jpg_size = os.path.getsize(jpg_path)
    print(f"   ✓ Exported JPEG: {jpg_path} ({jpg_size} bytes)")

    # Clean up export files
    print("\n5. Cleaning up...")
    for f in [svg_path, pdf_path, jpg_path]:
        if os.path.exists(f):
            os.remove(f)
            print(f"   ✓ Removed {os.path.basename(f)}")
    try:
        os.rmdir(temp_dir)
        print(f"   ✓ Removed export directory")
    except OSError:
        print(f"   ⚠ Could not remove directory (may contain other files)")

    print("\n✅ Export tests PASSED")
    return True


def main():
    """Run all Sprint 3 tests"""
    print("=" * 60)
    print("SPRINT 3 TEST SUITE: Layer Management & Export Tools")
    print("=" * 60)

    try:
        # Test layer management
        test_layer_management()

        # Test export tools (uses document from layer test)
        test_export_tools()

        # Clean up
        print("\n=== Cleanup ===")
        result = parse_result(close_document(save=False))
        assert result.get('success'), f"Failed to close document: {result}"
        print(f"✓ Closed test document")

        print("\n" + "=" * 60)
        print("ALL SPRINT 3 TESTS PASSED ✅")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

        # Try to clean up
        try:
            close_document(save=False)
        except:
            pass

        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
