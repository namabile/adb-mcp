// jsx/illustrator-helpers.jsx

// Helper function to extract XMP attribute values
$.global.extractXMPAttribute = function(xmpStr, tagName, attrName) {
    var pattern = new RegExp(tagName + '[^>]*' + attrName + '="([^"]+)"', 'i');
    var match = xmpStr.match(pattern);
    return match ? match[1] : null;
};

// Helper function to extract XMP tag values
$.global.extractXMPValue = function(xmpStr, tagName) {
    var pattern = new RegExp('<' + tagName + '>([^<]+)<\\/' + tagName + '>', 'i');
    var match = xmpStr.match(pattern);
    return match ? match[1] : null;
};

// Helper function to get document ID from XMP
$.global.getDocumentID = function(doc) {
    try {
        var xmpString = doc.XMPString;
        if (!xmpString) return null;
        
        return $.global.extractXMPAttribute(xmpString, 'xmpMM:DocumentID', 'rdf:resource') || 
               $.global.extractXMPValue(xmpString, 'xmpMM:DocumentID');
    } catch(e) {
        return null;
    }
};

// jsx/illustrator-helpers.jsx

// ... existing helper functions ...

// Helper function to create document info object
$.global.createDocumentInfo = function(doc, activeDoc) {
    return {
        id: $.global.getDocumentID(doc),
        name: doc.name,
        width: doc.width,
        height: doc.height,
        colorSpace: doc.documentColorSpace.toString(),
        numLayers: doc.layers.length,
        numArtboards: doc.artboards.length,
        saved: doc.saved,
        isActive: doc === activeDoc
    };
};


// Helper function to get detailed layer information
$.global.getLayerInfo = function(layer, includeSubLayers) {
    if (includeSubLayers === undefined) includeSubLayers = true;
    
    try {
        var layerInfo = {
            id: layer.absoluteZOrderPosition,
            name: layer.name,
            visible: layer.visible,
            locked: layer.locked,
            opacity: layer.opacity,
            printable: layer.printable,
            preview: layer.preview,
            sliced: layer.sliced,
            isIsolated: layer.isIsolated,
            hasSelectedArtwork: layer.hasSelectedArtwork,
            itemCount: layer.pageItems.length,
            zOrderPosition: layer.zOrderPosition,
            absoluteZOrderPosition: layer.absoluteZOrderPosition,
            dimPlacedImages: layer.dimPlacedImages,
            typename: layer.typename
        };
        
        // Get blending mode
        try {
            layerInfo.blendingMode = layer.blendingMode.toString();
        } catch(e) {
            layerInfo.blendingMode = "Normal";
        }
        
        // Get color info if available
        try {
            layerInfo.color = {
                red: layer.color.red,
                green: layer.color.green,
                blue: layer.color.blue
            };
        } catch(e) {
            layerInfo.color = null;
        }
        
        // Get artwork knockout state
        try {
            layerInfo.artworkKnockout = layer.artworkKnockout.toString();
        } catch(e) {
            layerInfo.artworkKnockout = "Inherited";
        }
        
        // Count different types of items on the layer
        try {
            layerInfo.itemCounts = {
                total: layer.pageItems.length,
                pathItems: layer.pathItems.length,
                textFrames: layer.textFrames.length,
                groupItems: layer.groupItems.length,
                compoundPathItems: layer.compoundPathItems.length,
                placedItems: layer.placedItems.length,
                rasterItems: layer.rasterItems.length,
                meshItems: layer.meshItems.length,
                symbolItems: layer.symbolItems.length
            };
        } catch(e) {
            layerInfo.itemCounts = { total: 0 };
        }
        
        // Handle sublayers
        layerInfo.subLayerCount = layer.layers.length;
        layerInfo.hasSubLayers = layer.layers.length > 0;
        
        if (includeSubLayers && layer.layers.length > 0) {
            layerInfo.subLayers = [];
            for (var j = 0; j < layer.layers.length; j++) {
                var subLayer = layer.layers[j];
                // Recursively get sublayer info (but don't go deeper to avoid infinite recursion)
                var subLayerInfo = $.global.getLayerInfo(subLayer, false);
                layerInfo.subLayers.push(subLayerInfo);
            }
        }
        
        return layerInfo;
    } catch(e) {
        return {
            error: "Error processing layer: " + e.toString(),
            layerName: layer.name || "Unknown"
        };
    }
};

// Helper function to get all layers information for a document
$.global.getAllLayersInfo = function(doc) {
    try {
        var layersInfo = [];
        
        for (var i = 0; i < doc.layers.length; i++) {
            var layer = doc.layers[i];
            var layerInfo = $.global.getLayerInfo(layer, true);
            layersInfo.push(layerInfo);
        }
        
        return {
            totalLayers: doc.layers.length,
            layers: layersInfo
        };
    } catch(e) {
        return {
            error: e.toString(),
            totalLayers: 0,
            layers: []
        };
    }
};

$.global.createDocumentInfo = function(doc, activeDoc) {
    var docInfo = {
        id: $.global.getDocumentID(doc),
        name: doc.name,
        width: doc.width,
        height: doc.height,
        colorSpace: doc.documentColorSpace.toString(),
        numLayers: doc.layers.length,
        numArtboards: doc.artboards.length,
        saved: doc.saved,
        isActive: doc === activeDoc
    };
    
    // Add layers information
    var layersResult = $.global.getAllLayersInfo(doc);
    docInfo.layers = layersResult.layers;
    docInfo.totalLayers = layersResult.totalLayers;
    
    return docInfo;
};

// ============================================================
// Color Conversion Helpers
// ============================================================

// Convert hex color string or swatch name to Illustrator color object
$.global.hexToColor = function(hex) {
    // Handle swatch names first
    try {
        var doc = app.activeDocument;
        var swatch = doc.swatches.getByName(hex);
        return swatch.color;
    } catch(e) {
        // Not a swatch name, continue to parse as hex
    }

    // Handle "none" for no fill/stroke
    if (hex === 'none' || hex === null) {
        return null;
    }

    // Parse hex color
    hex = hex.replace('#', '');

    // Handle shorthand hex (#RGB)
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }

    var r = parseInt(hex.substring(0, 2), 16);
    var g = parseInt(hex.substring(2, 4), 16);
    var b = parseInt(hex.substring(4, 6), 16);

    var color = new RGBColor();
    color.red = r;
    color.green = g;
    color.blue = b;
    return color;
};

// Convert Illustrator color object to hex string
$.global.colorToHex = function(color) {
    if (!color) return null;

    if (color.typename === 'RGBColor') {
        var r = Math.round(color.red).toString(16);
        var g = Math.round(color.green).toString(16);
        var b = Math.round(color.blue).toString(16);

        if (r.length === 1) r = '0' + r;
        if (g.length === 1) g = '0' + g;
        if (b.length === 1) b = '0' + b;

        return '#' + r + g + b;
    }

    // For CMYK or other color types, return a description
    return color.typename;
};

// ============================================================
// Brand Color Constants (Ultrathink Solutions)
// ============================================================

$.global.BRAND_COLORS = {
    'Synaptic Blue': '#0D1B2A',
    'Void Black': '#0B090A',
    'Axon White': '#F5F5F5',
    'Neural Gold': '#FFB703',
    'Spark Yellow': '#FFD000',
    'Electric Orange': '#FB8500'
};

// Create all brand swatches in the active document
$.global.createBrandSwatches = function() {
    var doc = app.activeDocument;
    var created = [];

    for (var name in $.global.BRAND_COLORS) {
        if ($.global.BRAND_COLORS.hasOwnProperty(name)) {
            try {
                // Check if swatch already exists
                doc.swatches.getByName(name);
                // Swatch exists, skip
            } catch(e) {
                // Create new spot color
                var spot = doc.spots.add();
                spot.name = name;
                spot.color = $.global.hexToColor($.global.BRAND_COLORS[name]);
                spot.colorType = ColorModel.SPOT;
                created.push(name);
            }
        }
    }

    return created;
};

// ============================================================
// Item Name Management (Illustrator doesn't have UUIDs)
// ============================================================

// Get item by name from a collection
$.global.getItemByName = function(name, collection) {
    for (var i = 0; i < collection.length; i++) {
        if (collection[i].name === name) {
            return collection[i];
        }
    }
    return null;
};

// Generate unique name for items
$.global.generateUniqueName = function(baseName, collection) {
    var name = baseName;
    var counter = 1;

    while ($.global.getItemByName(name, collection)) {
        name = baseName + '_' + counter;
        counter++;
    }

    return name;
};

// ============================================================
// Path Item Helpers
// ============================================================

// Get path item info for JSON serialization
$.global.getPathItemInfo = function(pathItem) {
    return {
        name: pathItem.name,
        typename: pathItem.typename,
        left: pathItem.left,
        top: pathItem.top,
        width: pathItem.width,
        height: pathItem.height,
        filled: pathItem.filled,
        stroked: pathItem.stroked,
        strokeWidth: pathItem.strokeWidth,
        opacity: pathItem.opacity,
        visible: !pathItem.hidden,
        locked: pathItem.locked
    };
};

// ============================================================
// Text Frame Helpers
// ============================================================

// Get text frame info for JSON serialization
$.global.getTextFrameInfo = function(textFrame) {
    return {
        name: textFrame.name,
        typename: textFrame.typename,
        kind: textFrame.kind.toString(),
        contents: textFrame.contents,
        left: textFrame.left,
        top: textFrame.top,
        width: textFrame.width,
        height: textFrame.height,
        opacity: textFrame.opacity,
        visible: !textFrame.hidden,
        locked: textFrame.locked
    };
};