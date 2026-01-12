/* commands.js
 * Illustrator command handlers
 */


const getDocuments = async (command) => {
    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length > 0) {
                        var activeDoc = app.activeDocument;
                        var docs = [];
                        
                        for (var i = 0; i < app.documents.length; i++) {
                            var doc = app.documents[i];
                            docs.push($.global.createDocumentInfo(doc, activeDoc));
                        }
                        
                        return docs;
                    } else {
                        return [];
                    }
                })();
                
                if (result === undefined) {
                    return 'null';
                }
                
                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;
    
    let result = await executeCommand(script);
    return createPacket(result);
}

const exportPNG = async (command) => {
    const options = command.options || {};
    
    // Extract all options into variables
    const path = options.path;
    const transparency = options.transparency !== undefined ? options.transparency : true;
    const antiAliasing = options.antiAliasing !== undefined ? options.antiAliasing : true;
    const artBoardClipping = options.artBoardClipping !== undefined ? options.artBoardClipping : true;
    const horizontalScale = options.horizontalScale || 100;
    const verticalScale = options.verticalScale || 100;
    const exportType = options.exportType || 'PNG24';
    const matte = options.matte;
    const matteColor = options.matteColor;
    
    // Validate required path parameter
    if (!path) {
        return createPacket(JSON.stringify({
            error: "Path is required for PNG export"
        }));
    }
    
    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }
                    
                    var doc = app.activeDocument;
                    var exportPath = "${path}";
                    
                    // Export options from variables
                    var exportOptions = {
                        transparency: ${transparency},
                        antiAliasing: ${antiAliasing},
                        artBoardClipping: ${artBoardClipping},
                        horizontalScale: ${horizontalScale},
                        verticalScale: ${verticalScale},
                        exportType: "${exportType}"
                    };
                    
                    ${matte !== undefined ? `exportOptions.matte = ${matte};` : ''}
                    ${matteColor ? `exportOptions.matteColor = ${JSON.stringify(matteColor)};` : ''}
                    
                    // Use the global helper function if available, otherwise inline export
                    if (typeof $.global.exportToPNG === 'function') {
                        return $.global.exportToPNG(doc, exportPath, exportOptions);
                    } else {
                        // Inline export logic
                        try {
                            // Create PNG export options
                            var pngOptions = exportOptions.exportType === 'PNG8' ? 
                                new ExportOptionsPNG8() : new ExportOptionsPNG24();
                                
                            pngOptions.transparency = exportOptions.transparency;
                            pngOptions.antiAliasing = exportOptions.antiAliasing;
                            pngOptions.artBoardClipping = exportOptions.artBoardClipping;
                            pngOptions.horizontalScale = exportOptions.horizontalScale;
                            pngOptions.verticalScale = exportOptions.verticalScale;
                            
                            ${matte !== undefined ? `pngOptions.matte = ${matte};` : ''}
                            
                            ${matteColor ? `
                            // Set matte color
                            pngOptions.matteColor.red = ${matteColor.red};
                            pngOptions.matteColor.green = ${matteColor.green};
                            pngOptions.matteColor.blue = ${matteColor.blue};
                            ` : ''}
                            
                            // Create file object
                            var exportFile = new File(exportPath);
                            
                            // Determine export type
                            var exportType = exportOptions.exportType === 'PNG8' ? 
                                ExportType.PNG8 : ExportType.PNG24;
                            
                            // Export the file
                            doc.exportFile(exportFile, exportType, pngOptions);
                            
                            return {
                                success: true,
                                filePath: exportFile.fsName,
                                fileExists: exportFile.exists,
                                options: exportOptions,
                                documentName: doc.name
                            };
                            
                        } catch(exportError) {
                            return {
                                success: false,
                                error: exportError.toString(),
                                filePath: exportPath,
                                options: exportOptions,
                                documentName: doc.name
                            };
                        }
                    }
                })();
                
                if (result === undefined) {
                    return 'null';
                }
                
                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;
    
    let result = await executeCommand(script);
    return createPacket(result);
}

const openFile = async (command) => {
    const options = command.options || {};
    
    // Extract path parameter
    const path = options.path;
    
    // Validate required path parameter
    if (!path) {
        return createPacket(JSON.stringify({
            error: "Path is required to open an Illustrator file"
        }));
    }
    
    const script = `
        (function() {
            try {
                var result = (function() {
                    var filePath = "${path}";
                    
                    try {
                        // Create file object
                        var fileToOpen = new File(filePath);
                        
                        // Check if file exists
                        if (!fileToOpen.exists) {
                            return {
                                success: false,
                                error: "File does not exist at the specified path",
                                filePath: filePath
                            };
                        }
                        
                        // Open the document
                        var doc = app.open(fileToOpen);
                        
                        return {
                            success: true,
                        };
                        
                    } catch(openError) {
                        return {
                            success: false,
                            error: openError.toString(),
                            filePath: filePath
                        };
                    }
                })();
                
                if (result === undefined) {
                    return 'null';
                }
                
                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;
    
    let result = await executeCommand(script);
    return createPacket(result);
};

const getActiveDocumentInfo = async (command) => {
    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length > 0) {
                        var doc = app.activeDocument;
                        return $.global.createDocumentInfo(doc, doc);
                    } else {
                        return { error: "No document is currently open" };
                    }
                })();
                
                if (result === undefined) {
                    return 'null';
                }
                
                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;
    
    let result = await executeCommand(script);
    return createPacket(result);
}

// Execute Illustrator command via ExtendScript
function executeCommand(script) {
    return new Promise((resolve, reject) => {
        const csInterface = new CSInterface();
        csInterface.evalScript(script, (result) => {
            if (result === 'EvalScript error.') {
                reject(new Error('ExtendScript execution failed'));
            } else {
                try {
                    resolve(JSON.parse(result));
                } catch (e) {
                    resolve(result);
                }
            }
        });
    });
}


async function executeExtendScript(command) {
    const options = command.options
    const scriptString = options.scriptString;

    const script = `
        (function() {
            try {
                ${scriptString}
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;
    
    const result = await executeCommand(script);
    
    return createPacket(result);
}

const createPacket = (result) => {
    return {
        content: [{
            type: "text",
            text: JSON.stringify(result, null, 2)
        }]
    };
}

const parseAndRouteCommand = async (command) => {
    let action = command.action;

    let f = commandHandlers[action];

    if (typeof f !== "function") {
        throw new Error(`Unknown Command: ${action}`);
    }

    console.log(f.name)
    return await f(command);
};


// Execute commands
/*
async function executeCommand(command) {
    switch(command.action) {

        case "getLayers":
            return await getLayers();
        
        case "executeExtendScript":
            return await executeExtendScript(command);
        
        default:
            throw new Error(`Unknown command: ${command.action}`);
    }
}*/

// ============================================================
// Document Management
// ============================================================

const createDocument = async (command) => {
    const options = command.options || {};
    const width = options.width || 612;  // Letter width in points
    const height = options.height || 792; // Letter height in points
    const name = options.name || "Untitled";
    const colorMode = options.colorMode || "RGB";
    const numArtboards = options.numArtboards || 1;

    const script = `
        (function() {
            try {
                var result = (function() {
                    var docPreset = new DocumentPreset();
                    docPreset.width = ${width};
                    docPreset.height = ${height};
                    docPreset.title = "${name.replace(/"/g, '\\"')}";
                    docPreset.colorMode = DocumentColorSpace.${colorMode};
                    docPreset.numArtboards = ${numArtboards};
                    docPreset.units = RulerUnits.Points;

                    var doc = app.documents.addDocument("", docPreset);

                    return {
                        success: true,
                        name: doc.name,
                        width: doc.width,
                        height: doc.height,
                        colorSpace: doc.documentColorSpace.toString(),
                        numArtboards: doc.artboards.length
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const saveDocument = async (command) => {
    const options = command.options || {};
    const filePath = options.filePath;

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    ${filePath ? `
                    // Save As to new location
                    var saveFile = new File("${filePath.replace(/\\/g, '/')}");
                    var saveOptions = new IllustratorSaveOptions();
                    saveOptions.compatibility = Compatibility.ILLUSTRATOR24;
                    saveOptions.flattenOutput = OutputFlattening.PRESERVEAPPEARANCE;
                    doc.saveAs(saveFile, saveOptions);
                    ` : `
                    // Save in place
                    if (doc.fullName) {
                        doc.save();
                    } else {
                        return { error: "Document has never been saved. Please provide a file path." };
                    }
                    `}

                    return {
                        success: true,
                        name: doc.name,
                        path: doc.fullName ? doc.fullName.fsName : null,
                        saved: doc.saved
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const closeDocument = async (command) => {
    const options = command.options || {};
    const save = options.save !== undefined ? options.save : false;

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    var docName = doc.name;

                    ${save ? `
                    // Save before closing
                    if (doc.fullName) {
                        doc.save();
                    }
                    ` : ''}

                    doc.close(${save ? 'SaveOptions.SAVECHANGES' : 'SaveOptions.DONOTSAVECHANGES'});

                    return {
                        success: true,
                        documentName: docName,
                        saved: ${save}
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

// ============================================================
// Color and Swatch Management
// ============================================================

const createColorSwatch = async (command) => {
    const options = command.options || {};
    const name = options.name;
    const colorValue = options.colorValue;

    if (!name || !colorValue) {
        return createPacket({ error: "Both 'name' and 'colorValue' are required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    var swatchName = "${name.replace(/"/g, '\\"')}";

                    // Check if swatch already exists
                    try {
                        var existingSwatch = doc.swatches.getByName(swatchName);
                        return {
                            success: true,
                            swatchName: swatchName,
                            message: "Swatch already exists",
                            alreadyExisted: true
                        };
                    } catch(e) {
                        // Swatch doesn't exist, create it
                    }

                    // Create spot color
                    var spot = doc.spots.add();
                    spot.name = swatchName;
                    spot.color = $.global.hexToColor("${colorValue}");
                    spot.colorType = ColorModel.SPOT;

                    return {
                        success: true,
                        swatchName: swatchName,
                        colorValue: "${colorValue}",
                        alreadyExisted: false
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const createBrandSwatches = async (command) => {
    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var created = $.global.createBrandSwatches();

                    return {
                        success: true,
                        createdSwatches: created,
                        brandColors: $.global.BRAND_COLORS
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const listSwatches = async (command) => {
    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    var swatches = [];

                    for (var i = 0; i < doc.swatches.length; i++) {
                        var swatch = doc.swatches[i];
                        var swatchInfo = {
                            name: swatch.name,
                            index: i
                        };

                        // Try to get color info
                        try {
                            if (swatch.color.typename === 'RGBColor') {
                                swatchInfo.colorType = 'RGB';
                                swatchInfo.red = swatch.color.red;
                                swatchInfo.green = swatch.color.green;
                                swatchInfo.blue = swatch.color.blue;
                                swatchInfo.hex = $.global.colorToHex(swatch.color);
                            } else if (swatch.color.typename === 'CMYKColor') {
                                swatchInfo.colorType = 'CMYK';
                                swatchInfo.cyan = swatch.color.cyan;
                                swatchInfo.magenta = swatch.color.magenta;
                                swatchInfo.yellow = swatch.color.yellow;
                                swatchInfo.black = swatch.color.black;
                            } else if (swatch.color.typename === 'SpotColor') {
                                swatchInfo.colorType = 'Spot';
                                swatchInfo.spotName = swatch.color.spot.name;
                            } else {
                                swatchInfo.colorType = swatch.color.typename;
                            }
                        } catch(e) {
                            swatchInfo.colorType = 'unknown';
                        }

                        swatches.push(swatchInfo);
                    }

                    return {
                        success: true,
                        count: swatches.length,
                        swatches: swatches
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

// ============================================================
// Shape Tools
// ============================================================

const createRectangle = async (command) => {
    const options = command.options || {};
    const x = options.x || 0;
    const y = options.y || 0;
    const width = options.width || 100;
    const height = options.height || 100;
    const fillColor = options.fillColor;
    const strokeColor = options.strokeColor;
    const strokeWeight = options.strokeWeight || 1;
    const cornerRadius = options.cornerRadius || 0;
    const layerName = options.layerName;
    const itemName = options.name;

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    // Get or create target layer
                    var layer;
                    ${layerName ? `
                    try {
                        layer = doc.layers.getByName("${layerName.replace(/"/g, '\\"')}");
                    } catch(e) {
                        layer = doc.layers.add();
                        layer.name = "${layerName.replace(/"/g, '\\"')}";
                    }
                    ` : 'layer = doc.activeLayer;'}

                    // Create rectangle (note: Illustrator Y is inverted, 0 is bottom)
                    var rect;
                    ${cornerRadius > 0 ? `
                    rect = layer.pathItems.roundedRectangle(
                        -${y},           // Top (negative because AI Y-axis)
                        ${x},            // Left
                        ${width},        // Width
                        ${height},       // Height
                        ${cornerRadius}, // Horizontal corner radius
                        ${cornerRadius}  // Vertical corner radius
                    );
                    ` : `
                    rect = layer.pathItems.rectangle(
                        -${y},           // Top
                        ${x},            // Left
                        ${width},        // Width
                        ${height}        // Height
                    );
                    `}

                    // Set item name
                    ${itemName ? `rect.name = "${itemName.replace(/"/g, '\\"')}";` : `
                    rect.name = $.global.generateUniqueName("Rectangle", layer.pathItems);
                    `}

                    // Apply fill
                    ${fillColor ? `
                    rect.filled = true;
                    rect.fillColor = $.global.hexToColor("${fillColor}");
                    ` : 'rect.filled = false;'}

                    // Apply stroke
                    ${strokeColor ? `
                    rect.stroked = true;
                    rect.strokeColor = $.global.hexToColor("${strokeColor}");
                    rect.strokeWidth = ${strokeWeight};
                    ` : 'rect.stroked = false;'}

                    return {
                        success: true,
                        itemName: rect.name,
                        layer: layer.name,
                        bounds: {
                            left: rect.left,
                            top: rect.top,
                            width: rect.width,
                            height: rect.height
                        }
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const createEllipse = async (command) => {
    const options = command.options || {};
    const x = options.x || 0;
    const y = options.y || 0;
    const width = options.width || 100;
    const height = options.height || 100;
    const fillColor = options.fillColor;
    const strokeColor = options.strokeColor;
    const strokeWeight = options.strokeWeight || 1;
    const layerName = options.layerName;
    const itemName = options.name;

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    // Get or create target layer
                    var layer;
                    ${layerName ? `
                    try {
                        layer = doc.layers.getByName("${layerName.replace(/"/g, '\\"')}");
                    } catch(e) {
                        layer = doc.layers.add();
                        layer.name = "${layerName.replace(/"/g, '\\"')}";
                    }
                    ` : 'layer = doc.activeLayer;'}

                    // Create ellipse
                    var ellipse = layer.pathItems.ellipse(
                        -${y},           // Top (negative because AI Y-axis)
                        ${x},            // Left
                        ${width},        // Width
                        ${height}        // Height
                    );

                    // Set item name
                    ${itemName ? `ellipse.name = "${itemName.replace(/"/g, '\\"')}";` : `
                    ellipse.name = $.global.generateUniqueName("Ellipse", layer.pathItems);
                    `}

                    // Apply fill
                    ${fillColor ? `
                    ellipse.filled = true;
                    ellipse.fillColor = $.global.hexToColor("${fillColor}");
                    ` : 'ellipse.filled = false;'}

                    // Apply stroke
                    ${strokeColor ? `
                    ellipse.stroked = true;
                    ellipse.strokeColor = $.global.hexToColor("${strokeColor}");
                    ellipse.strokeWidth = ${strokeWeight};
                    ` : 'ellipse.stroked = false;'}

                    return {
                        success: true,
                        itemName: ellipse.name,
                        layer: layer.name,
                        bounds: {
                            left: ellipse.left,
                            top: ellipse.top,
                            width: ellipse.width,
                            height: ellipse.height
                        }
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const createLine = async (command) => {
    const options = command.options || {};
    const startX = options.startX || 0;
    const startY = options.startY || 0;
    const endX = options.endX || 100;
    const endY = options.endY || 100;
    const strokeColor = options.strokeColor || "#000000";
    const strokeWeight = options.strokeWeight || 1;
    const strokeCap = options.strokeCap || "BUTTENDCAP";
    const layerName = options.layerName;
    const itemName = options.name;

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    // Get or create target layer
                    var layer;
                    ${layerName ? `
                    try {
                        layer = doc.layers.getByName("${layerName.replace(/"/g, '\\"')}");
                    } catch(e) {
                        layer = doc.layers.add();
                        layer.name = "${layerName.replace(/"/g, '\\"')}";
                    }
                    ` : 'layer = doc.activeLayer;'}

                    // Create line path
                    var line = layer.pathItems.add();
                    line.setEntirePath([
                        [${startX}, -${startY}],
                        [${endX}, -${endY}]
                    ]);

                    // Set item name
                    ${itemName ? `line.name = "${itemName.replace(/"/g, '\\"')}";` : `
                    line.name = $.global.generateUniqueName("Line", layer.pathItems);
                    `}

                    // Lines don't have fill
                    line.filled = false;

                    // Apply stroke
                    line.stroked = true;
                    line.strokeColor = $.global.hexToColor("${strokeColor}");
                    line.strokeWidth = ${strokeWeight};
                    line.strokeCap = StrokeCap.${strokeCap};

                    return {
                        success: true,
                        itemName: line.name,
                        layer: layer.name,
                        start: { x: ${startX}, y: ${startY} },
                        end: { x: ${endX}, y: ${endY} }
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

// ============================================================
// Text Tools
// ============================================================

const createPointText = async (command) => {
    const options = command.options || {};
    const x = options.x || 0;
    const y = options.y || 0;
    const content = options.content || "";
    const fontFamily = options.fontFamily || "Arial";
    const fontStyle = options.fontStyle || "Regular";
    const fontSize = options.fontSize || 24;
    const textColor = options.textColor || "#000000";
    const alignment = options.alignment || "LEFT";
    const tracking = options.tracking || 0;
    const layerName = options.layerName;
    const itemName = options.name;

    const escapedContent = content.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    // Get or create target layer
                    var layer;
                    ${layerName ? `
                    try {
                        layer = doc.layers.getByName("${layerName.replace(/"/g, '\\"')}");
                    } catch(e) {
                        layer = doc.layers.add();
                        layer.name = "${layerName.replace(/"/g, '\\"')}";
                    }
                    ` : 'layer = doc.activeLayer;'}

                    // Create point text
                    var textFrame = layer.textFrames.add();
                    textFrame.kind = TextType.POINTTEXT;
                    textFrame.left = ${x};
                    textFrame.top = -${y};
                    textFrame.contents = "${escapedContent}";

                    // Set item name
                    ${itemName ? `textFrame.name = "${itemName.replace(/"/g, '\\"')}";` : `
                    textFrame.name = $.global.generateUniqueName("Text", layer.textFrames);
                    `}

                    // Apply character attributes
                    var textRange = textFrame.textRange;
                    var charAttr = textRange.characterAttributes;

                    charAttr.size = ${fontSize};

                    // Set font
                    try {
                        var fontName = "${fontFamily}-${fontStyle}";
                        var font = app.textFonts.getByName(fontName);
                        charAttr.textFont = font;
                    } catch(e) {
                        // Font not found, try just the family name
                        try {
                            var font = app.textFonts.getByName("${fontFamily}");
                            charAttr.textFont = font;
                        } catch(e2) {
                            // Use default font
                        }
                    }

                    // Set color
                    charAttr.fillColor = $.global.hexToColor("${textColor}");

                    // Tracking
                    ${tracking !== 0 ? `charAttr.tracking = ${tracking};` : ''}

                    // Paragraph alignment
                    var paraAttr = textRange.paragraphAttributes;
                    paraAttr.justification = Justification.${alignment};

                    return {
                        success: true,
                        itemName: textFrame.name,
                        layer: layer.name,
                        bounds: {
                            left: textFrame.left,
                            top: textFrame.top,
                            width: textFrame.width,
                            height: textFrame.height
                        },
                        content: textFrame.contents
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const createAreaText = async (command) => {
    const options = command.options || {};
    const x = options.x || 0;
    const y = options.y || 0;
    const width = options.width || 200;
    const height = options.height || 100;
    const content = options.content || "";
    const fontFamily = options.fontFamily || "Arial";
    const fontStyle = options.fontStyle || "Regular";
    const fontSize = options.fontSize || 12;
    const textColor = options.textColor || "#000000";
    const alignment = options.alignment || "LEFT";
    const layerName = options.layerName;
    const itemName = options.name;

    const escapedContent = content.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    // Get or create target layer
                    var layer;
                    ${layerName ? `
                    try {
                        layer = doc.layers.getByName("${layerName.replace(/"/g, '\\"')}");
                    } catch(e) {
                        layer = doc.layers.add();
                        layer.name = "${layerName.replace(/"/g, '\\"')}";
                    }
                    ` : 'layer = doc.activeLayer;'}

                    // Create a rectangle for the text area
                    var rect = layer.pathItems.rectangle(
                        -${y},           // Top
                        ${x},            // Left
                        ${width},        // Width
                        ${height}        // Height
                    );

                    // Convert rectangle to area text
                    var textFrame = layer.textFrames.areaText(rect);
                    textFrame.contents = "${escapedContent}";

                    // Set item name
                    ${itemName ? `textFrame.name = "${itemName.replace(/"/g, '\\"')}";` : `
                    textFrame.name = $.global.generateUniqueName("AreaText", layer.textFrames);
                    `}

                    // Apply character attributes
                    var textRange = textFrame.textRange;
                    var charAttr = textRange.characterAttributes;

                    charAttr.size = ${fontSize};

                    // Set font
                    try {
                        var fontName = "${fontFamily}-${fontStyle}";
                        var font = app.textFonts.getByName(fontName);
                        charAttr.textFont = font;
                    } catch(e) {
                        try {
                            var font = app.textFonts.getByName("${fontFamily}");
                            charAttr.textFont = font;
                        } catch(e2) {
                            // Use default font
                        }
                    }

                    // Set color
                    charAttr.fillColor = $.global.hexToColor("${textColor}");

                    // Paragraph alignment
                    var paraAttr = textRange.paragraphAttributes;
                    paraAttr.justification = Justification.${alignment};

                    return {
                        success: true,
                        itemName: textFrame.name,
                        layer: layer.name,
                        bounds: {
                            left: textFrame.left,
                            top: textFrame.top,
                            width: textFrame.width,
                            height: textFrame.height
                        },
                        content: textFrame.contents
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

// ============================================================
// Layer Management
// ============================================================

const createLayer = async (command) => {
    const options = command.options || {};
    const name = options.name || "New Layer";
    const aboveLayer = options.aboveLayer;
    const visible = options.visible !== undefined ? options.visible : true;
    const locked = options.locked !== undefined ? options.locked : false;

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    var newLayer = doc.layers.add();
                    newLayer.name = "${name.replace(/"/g, '\\"')}";
                    newLayer.visible = ${visible};
                    newLayer.locked = ${locked};

                    ${aboveLayer ? `
                    // Move layer above specified layer
                    try {
                        var targetLayer = doc.layers.getByName("${aboveLayer.replace(/"/g, '\\"')}");
                        newLayer.zOrder(ZOrderMethod.BRINGTOFRONT);
                        // Position relative to target
                        while (newLayer.zOrderPosition > targetLayer.zOrderPosition) {
                            newLayer.zOrder(ZOrderMethod.SENDBACKWARD);
                        }
                        newLayer.zOrder(ZOrderMethod.BRINGFORWARD);
                    } catch(e) {
                        // Target layer not found, keep at top
                    }
                    ` : ''}

                    return {
                        success: true,
                        layerName: newLayer.name,
                        visible: newLayer.visible,
                        locked: newLayer.locked,
                        zOrderPosition: newLayer.zOrderPosition,
                        totalLayers: doc.layers.length
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const deleteLayer = async (command) => {
    const options = command.options || {};
    const name = options.name;

    if (!name) {
        return createPacket({ error: "Layer 'name' is required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    // Can't delete the last layer
                    if (doc.layers.length <= 1) {
                        return { error: "Cannot delete the last remaining layer" };
                    }

                    try {
                        var layer = doc.layers.getByName("${name.replace(/"/g, '\\"')}");
                        var layerName = layer.name;
                        layer.remove();

                        return {
                            success: true,
                            deletedLayer: layerName,
                            remainingLayers: doc.layers.length
                        };
                    } catch(e) {
                        return { error: "Layer not found: ${name.replace(/"/g, '\\"')}" };
                    }
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const renameLayer = async (command) => {
    const options = command.options || {};
    const currentName = options.currentName;
    const newName = options.newName;

    if (!currentName || !newName) {
        return createPacket({ error: "Both 'currentName' and 'newName' are required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    try {
                        var layer = doc.layers.getByName("${currentName.replace(/"/g, '\\"')}");
                        var oldName = layer.name;
                        layer.name = "${newName.replace(/"/g, '\\"')}";

                        return {
                            success: true,
                            oldName: oldName,
                            newName: layer.name
                        };
                    } catch(e) {
                        return { error: "Layer not found: ${currentName.replace(/"/g, '\\"')}" };
                    }
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const setLayerVisibility = async (command) => {
    const options = command.options || {};
    const name = options.name;
    const visible = options.visible;

    if (!name || visible === undefined) {
        return createPacket({ error: "Both 'name' and 'visible' are required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    try {
                        var layer = doc.layers.getByName("${name.replace(/"/g, '\\"')}");
                        layer.visible = ${visible};

                        return {
                            success: true,
                            layerName: layer.name,
                            visible: layer.visible
                        };
                    } catch(e) {
                        return { error: "Layer not found: ${name.replace(/"/g, '\\"')}" };
                    }
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const setLayerLock = async (command) => {
    const options = command.options || {};
    const name = options.name;
    const locked = options.locked;

    if (!name || locked === undefined) {
        return createPacket({ error: "Both 'name' and 'locked' are required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    try {
                        var layer = doc.layers.getByName("${name.replace(/"/g, '\\"')}");
                        layer.locked = ${locked};

                        return {
                            success: true,
                            layerName: layer.name,
                            locked: layer.locked
                        };
                    } catch(e) {
                        return { error: "Layer not found: ${name.replace(/"/g, '\\"')}" };
                    }
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const reorderLayer = async (command) => {
    const options = command.options || {};
    const name = options.name;
    const position = options.position; // "front", "back", "forward", "backward", or index number

    if (!name || position === undefined) {
        return createPacket({ error: "Both 'name' and 'position' are required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;

                    try {
                        var layer = doc.layers.getByName("${name.replace(/"/g, '\\"')}");
                        var position = "${position}";

                        if (position === "front") {
                            layer.zOrder(ZOrderMethod.BRINGTOFRONT);
                        } else if (position === "back") {
                            layer.zOrder(ZOrderMethod.SENDTOBACK);
                        } else if (position === "forward") {
                            layer.zOrder(ZOrderMethod.BRINGFORWARD);
                        } else if (position === "backward") {
                            layer.zOrder(ZOrderMethod.SENDBACKWARD);
                        } else {
                            // Numeric index - move to specific position
                            var targetIndex = parseInt(position);
                            if (!isNaN(targetIndex) && targetIndex >= 0 && targetIndex < doc.layers.length) {
                                // Move to front first, then move back to target position
                                layer.zOrder(ZOrderMethod.BRINGTOFRONT);
                                for (var i = 0; i < targetIndex; i++) {
                                    layer.zOrder(ZOrderMethod.SENDBACKWARD);
                                }
                            }
                        }

                        return {
                            success: true,
                            layerName: layer.name,
                            newZOrderPosition: layer.zOrderPosition,
                            totalLayers: doc.layers.length
                        };
                    } catch(e) {
                        return { error: "Layer not found: ${name.replace(/"/g, '\\"')}" };
                    }
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const getLayers = async (command) => {
    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    return $.global.getAllLayersInfo(doc);
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

// ============================================================
// Export Tools
// ============================================================

const exportSVG = async (command) => {
    const options = command.options || {};
    const outputPath = options.outputPath;
    const artboardIndex = options.artboardIndex !== undefined ? options.artboardIndex : 0;
    const embedFonts = options.embedFonts !== undefined ? options.embedFonts : true;
    const embedRasterImages = options.embedRasterImages !== undefined ? options.embedRasterImages : true;
    const cssProperties = options.cssProperties || "STYLEATTRIBUTES"; // STYLEATTRIBUTES, PRESENTATIONATTRIBUTES, STYLEELEMENTS
    const fontSubsetting = options.fontSubsetting || "GLYPHSUSED"; // NONE, GLYPHSUSED, COMMONENGLISH, GLYPHSUSEDPLUSENGLISH, COMMONROMAN, GLYPHSUSEDPLUSROMAN, ALLGLYPHS

    if (!outputPath) {
        return createPacket({ error: "outputPath is required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    var exportFile = new File("${outputPath.replace(/\\/g, '/')}");

                    // Set up SVG export options
                    var svgOptions = new ExportOptionsSVG();
                    svgOptions.embedRasterImages = ${embedRasterImages};
                    svgOptions.cssProperties = SVGCSSPropertyLocation.${cssProperties};
                    svgOptions.fontSubsetting = SVGFontSubsetting.${fontSubsetting};
                    svgOptions.documentEncoding = SVGDocumentEncoding.UTF8;
                    svgOptions.coordinatePrecision = 3;

                    ${embedFonts ? `
                    svgOptions.fontType = SVGFontType.OUTLINEFONT;
                    ` : `
                    svgOptions.fontType = SVGFontType.SVGFONT;
                    `}

                    // Set artboard to export
                    ${artboardIndex >= 0 ? `
                    if (${artboardIndex} < doc.artboards.length) {
                        doc.artboards.setActiveArtboardIndex(${artboardIndex});
                        svgOptions.artboardRange = "${artboardIndex + 1}";
                    }
                    ` : ''}

                    // Export
                    doc.exportFile(exportFile, ExportType.SVG, svgOptions);

                    return {
                        success: true,
                        filePath: exportFile.fsName,
                        fileExists: exportFile.exists,
                        documentName: doc.name,
                        artboardIndex: ${artboardIndex}
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const exportPDF = async (command) => {
    const options = command.options || {};
    const outputPath = options.outputPath;
    const preset = options.preset || "[High Quality Print]";
    const preserveEditability = options.preserveEditability !== undefined ? options.preserveEditability : true;
    const optimizeForFastWebView = options.optimizeForFastWebView !== undefined ? options.optimizeForFastWebView : false;
    const viewAfterSaving = options.viewAfterSaving !== undefined ? options.viewAfterSaving : false;
    const artboardRange = options.artboardRange; // e.g., "1-3" or "1,3,5"

    if (!outputPath) {
        return createPacket({ error: "outputPath is required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    var saveFile = new File("${outputPath.replace(/\\/g, '/')}");

                    // Set up PDF save options
                    var pdfOptions = new PDFSaveOptions();

                    // Try to use preset
                    try {
                        pdfOptions.pDFPreset = "${preset.replace(/"/g, '\\"')}";
                    } catch(e) {
                        // Preset not found, use defaults
                    }

                    pdfOptions.preserveEditability = ${preserveEditability};
                    pdfOptions.optimization = ${optimizeForFastWebView};
                    pdfOptions.viewAfterSaving = ${viewAfterSaving};

                    ${artboardRange ? `
                    pdfOptions.artboardRange = "${artboardRange}";
                    ` : ''}

                    // Save as PDF
                    doc.saveAs(saveFile, pdfOptions);

                    return {
                        success: true,
                        filePath: saveFile.fsName,
                        fileExists: saveFile.exists,
                        documentName: doc.name,
                        preset: "${preset.replace(/"/g, '\\"')}"
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

const exportJPEG = async (command) => {
    const options = command.options || {};
    const outputPath = options.outputPath;
    const artboardIndex = options.artboardIndex !== undefined ? options.artboardIndex : 0;
    const quality = options.quality !== undefined ? options.quality : 80; // 0-100
    const horizontalScale = options.horizontalScale || 100;
    const verticalScale = options.verticalScale || 100;
    const antiAliasing = options.antiAliasing !== undefined ? options.antiAliasing : true;
    const artBoardClipping = options.artBoardClipping !== undefined ? options.artBoardClipping : true;
    const blurAmount = options.blurAmount || 0; // 0-2

    if (!outputPath) {
        return createPacket({ error: "outputPath is required" });
    }

    const script = `
        (function() {
            try {
                var result = (function() {
                    if (app.documents.length === 0) {
                        return { error: "No document is currently open" };
                    }

                    var doc = app.activeDocument;
                    var exportFile = new File("${outputPath.replace(/\\/g, '/')}");

                    // Set up JPEG export options
                    var jpgOptions = new ExportOptionsJPEG();
                    jpgOptions.qualitySetting = ${quality};
                    jpgOptions.horizontalScale = ${horizontalScale};
                    jpgOptions.verticalScale = ${verticalScale};
                    jpgOptions.antiAliasing = ${antiAliasing};
                    jpgOptions.artBoardClipping = ${artBoardClipping};
                    jpgOptions.blurAmount = ${blurAmount};

                    // Set artboard to export
                    ${artboardIndex >= 0 ? `
                    if (${artboardIndex} < doc.artboards.length) {
                        doc.artboards.setActiveArtboardIndex(${artboardIndex});
                    }
                    ` : ''}

                    // Export
                    doc.exportFile(exportFile, ExportType.JPEG, jpgOptions);

                    return {
                        success: true,
                        filePath: exportFile.fsName,
                        fileExists: exportFile.exists,
                        documentName: doc.name,
                        quality: ${quality},
                        artboardIndex: ${artboardIndex}
                    };
                })();

                return JSON.stringify(result);
            } catch(e) {
                return JSON.stringify({
                    error: e.toString(),
                    line: e.line || 'unknown'
                });
            }
        })();
    `;

    let result = await executeCommand(script);
    return createPacket(result);
};

// ============================================================
// Command Handlers Registry
// ============================================================

const commandHandlers = {
    // Existing handlers
    executeExtendScript,
    getDocuments,
    getActiveDocumentInfo,
    exportPNG,
    openFile,
    // Document management
    createDocument,
    saveDocument,
    closeDocument,
    // Color/Swatch management
    createColorSwatch,
    createBrandSwatches,
    listSwatches,
    // Shape tools
    createRectangle,
    createEllipse,
    createLine,
    // Text tools
    createPointText,
    createAreaText,
    // Layer management
    createLayer,
    deleteLayer,
    renameLayer,
    setLayerVisibility,
    setLayerLock,
    reorderLayer,
    getLayers,
    // Export tools
    exportSVG,
    exportPDF,
    exportJPEG
};