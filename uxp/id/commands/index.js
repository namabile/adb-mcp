/* MIT License
 *
 * Copyright (c) 2025 Mike Chambers
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

console.log("[MCP] Loading commands/index.js...");

const indesign = require("indesign");
const app = indesign.app;
const DocumentIntentOptions = indesign.DocumentIntentOptions;
const ColorModel = indesign.ColorModel;
const ColorSpace = indesign.ColorSpace;
const Justification = indesign.Justification;
const FitOptions = indesign.FitOptions;
const LocationOptions = indesign.LocationOptions;

console.log("[MCP] InDesign module loaded successfully");

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

const getUnitForIntent = (intent) => {
    if (intent && intent.toString() === DocumentIntentOptions.WEB_INTENT.toString()) {
        return "px";
    }
    throw new Error(`getUnitForIntent : unknown intent [${intent}]`);
};

const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!result) return null;
    return [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
    ];
};

const findOrCreateColor = (doc, colorValue) => {
    // If it's a swatch name, try to find it
    if (!colorValue.startsWith("#")) {
        try {
            const swatch = doc.swatches.itemByName(colorValue);
            const name = swatch.name; // This will throw if not found
            return swatch;
        } catch (e) {
            throw new Error(`Swatch not found: ${colorValue}`);
        }
    }

    // It's a hex color - create or find color
    const rgb = hexToRgb(colorValue);
    if (!rgb) throw new Error(`Invalid hex color: ${colorValue}`);

    const colorName = `RGB_${colorValue.replace("#", "")}`;

    // Try to find existing color
    try {
        const existingColor = doc.colors.itemByName(colorName);
        const name = existingColor.name; // This will throw if not found
        return existingColor;
    } catch (e) {
        // Create new color
        const newColor = doc.colors.add({
            name: colorName,
            space: ColorSpace.RGB,
            colorValue: rgb
        });
        return newColor;
    }
};

// =============================================================================
// DOCUMENT CREATION
// =============================================================================

const createDocument = async (command) => {
    console.log("[MCP] createDocument called");
    const options = command.options || {};
    let documents = app.documents;
    let margins = options.margins || { top: 36, bottom: 36, left: 36, right: 36 };
    let columns = options.columns || { count: 1, gutter: 12 };
    let unit = getUnitForIntent(DocumentIntentOptions.WEB_INTENT);

    app.marginPreferences.bottom = `${margins.bottom}${unit}`;
    app.marginPreferences.top = `${margins.top}${unit}`;
    app.marginPreferences.left = `${margins.left}${unit}`;
    app.marginPreferences.right = `${margins.right}${unit}`;
    app.marginPreferences.columnCount = columns.count;
    app.marginPreferences.columnGutter = `${columns.gutter}${unit}`;

    let documentPreferences = {
        pageWidth: `${options.pageWidth}${unit}`,
        pageHeight: `${options.pageHeight}${unit}`,
        pagesPerDocument: options.pagesPerDocument || 1,
        facingPages: options.facingPages || false,
        intent: DocumentIntentOptions.WEB_INTENT
    };

    const showingWindow = true;
    const doc = documents.add({ showingWindow, documentPreferences });
    return { success: true, documentId: doc.id };
};

// =============================================================================
// TEXT FRAME TOOLS
// =============================================================================

const createTextFrame = async (command) => {
    console.log("[MCP] createTextFrame called");
    const doc = app.activeDocument;
    const options = command.options || {};
    const pageIndex = options.pageIndex !== undefined ? options.pageIndex : 0;
    const page = doc.pages.item(pageIndex);

    const frame = page.textFrames.add();
    frame.geometricBounds = [
        options.y,
        options.x,
        options.y + options.height,
        options.x + options.width
    ];

    if (options.content) {
        frame.contents = options.content;
    }

    return { success: true, frameId: frame.id };
};

const setTextFrameContent = async (command) => {
    console.log("[MCP] setTextFrameContent called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const frame = doc.textFrames.itemByID(options.frameId);
    frame.contents = options.content;

    return { success: true };
};

const applyParagraphStyle = async (command) => {
    console.log("[MCP] applyParagraphStyle called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const frame = doc.textFrames.itemByID(options.frameId);
    const style = doc.paragraphStyles.itemByName(options.styleName);

    frame.paragraphs.everyItem().appliedParagraphStyle = style;

    return { success: true };
};

const applyCharacterStyle = async (command) => {
    console.log("[MCP] applyCharacterStyle called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const frame = doc.textFrames.itemByID(options.frameId);
    const style = doc.characterStyles.itemByName(options.styleName);

    const text = frame.texts.item(0);
    const startIdx = options.startIndex || 0;
    const endIdx = options.endIndex === -1 ? text.characters.length - 1 : options.endIndex;

    for (let i = startIdx; i <= endIdx && i < text.characters.length; i++) {
        text.characters.item(i).appliedCharacterStyle = style;
    }

    return { success: true };
};

// =============================================================================
// COLOR SWATCH TOOLS
// =============================================================================

const createColorSwatch = async (command) => {
    console.log("[MCP] createColorSwatch called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const rgb = hexToRgb(options.colorValue);
    if (!rgb) throw new Error(`Invalid hex color: ${options.colorValue}`);

    const swatch = doc.colors.add({
        name: options.name,
        space: ColorSpace.RGB,
        colorValue: rgb
    });

    return { success: true, swatchName: swatch.name };
};

const listSwatches = async (command) => {
    console.log("[MCP] listSwatches called");
    const doc = app.activeDocument;

    const swatches = [];
    const count = doc.swatches.length;
    for (let i = 0; i < count; i++) {
        try {
            const s = doc.swatches.item(i);
            const name = s.name; // Access property to verify it exists
            swatches.push({
                name: name,
                id: s.id
            });
        } catch (e) {
            // Skip items that can't be accessed
        }
    }

    return { success: true, swatches };
};

// =============================================================================
// STYLE MANAGEMENT TOOLS
// =============================================================================

const createParagraphStyle = async (command) => {
    console.log("[MCP] createParagraphStyle called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const styleProps = {
        name: options.name,
        appliedFont: options.fontFamily,
        pointSize: options.fontSize
    };

    if (options.leading) {
        styleProps.leading = options.leading;
    }

    if (options.alignment) {
        const alignMap = {
            "LEFT_ALIGN": Justification.LEFT_ALIGN,
            "CENTER_ALIGN": Justification.CENTER_ALIGN,
            "RIGHT_ALIGN": Justification.RIGHT_ALIGN,
            "JUSTIFY_ALIGN": Justification.FULLY_JUSTIFIED
        };
        styleProps.justification = alignMap[options.alignment] || Justification.LEFT_ALIGN;
    }

    if (options.spaceBefore) {
        styleProps.spaceBefore = options.spaceBefore;
    }

    if (options.spaceAfter) {
        styleProps.spaceAfter = options.spaceAfter;
    }

    const style = doc.paragraphStyles.add(styleProps);

    // Apply color after creation if specified
    if (options.color) {
        style.fillColor = findOrCreateColor(doc, options.color);
    }

    return { success: true, styleName: style.name };
};

const createCharacterStyle = async (command) => {
    console.log("[MCP] createCharacterStyle called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const styleProps = { name: options.name };

    if (options.fontFamily) {
        styleProps.appliedFont = options.fontFamily;
    }

    if (options.fontSize) {
        styleProps.pointSize = options.fontSize;
    }

    if (options.fontStyle) {
        styleProps.fontStyle = options.fontStyle;
    }

    const style = doc.characterStyles.add(styleProps);

    if (options.color) {
        style.fillColor = findOrCreateColor(doc, options.color);
    }

    return { success: true, styleName: style.name };
};

const listStyles = async (command) => {
    console.log("[MCP] listStyles called");
    const doc = app.activeDocument;

    const paragraphStyles = [];
    const pCount = doc.paragraphStyles.length;
    for (let i = 0; i < pCount; i++) {
        try {
            const s = doc.paragraphStyles.item(i);
            paragraphStyles.push(s.name);
        } catch (e) {
            // Skip
        }
    }

    const characterStyles = [];
    const cCount = doc.characterStyles.length;
    for (let i = 0; i < cCount; i++) {
        try {
            const s = doc.characterStyles.item(i);
            characterStyles.push(s.name);
        } catch (e) {
            // Skip
        }
    }

    return { success: true, paragraphStyles, characterStyles };
};

// =============================================================================
// IMAGE AND SHAPE TOOLS
// =============================================================================

const placeImage = async (command) => {
    console.log("[MCP] placeImage called");
    const doc = app.activeDocument;
    const options = command.options || {};
    const pageIndex = options.pageIndex !== undefined ? options.pageIndex : 0;
    const page = doc.pages.item(pageIndex);

    // Place returns an array
    const placedItems = page.place(options.filePath);
    const graphic = placedItems[0];

    // Get the frame containing the graphic
    const frame = graphic.parent;

    // Set bounds
    const width = options.width || 200;
    const height = options.height || 200;
    frame.geometricBounds = [
        options.y,
        options.x,
        options.y + height,
        options.x + width
    ];

    // Apply fit option
    if (options.fitOption) {
        const fitMap = {
            "PROPORTIONALLY": FitOptions.PROPORTIONALLY,
            "FILL_PROPORTIONALLY": FitOptions.FILL_PROPORTIONALLY,
            "CONTENT_TO_FRAME": FitOptions.CONTENT_TO_FRAME
        };
        const fitOption = fitMap[options.fitOption] || FitOptions.PROPORTIONALLY;
        frame.fit(fitOption);
    }

    return { success: true, frameId: frame.id };
};

const createRectangle = async (command) => {
    console.log("[MCP] createRectangle called");
    const doc = app.activeDocument;
    const options = command.options || {};
    const pageIndex = options.pageIndex !== undefined ? options.pageIndex : 0;
    const page = doc.pages.item(pageIndex);

    const rect = page.rectangles.add();
    rect.geometricBounds = [
        options.y,
        options.x,
        options.y + options.height,
        options.x + options.width
    ];

    if (options.fillColor) {
        rect.fillColor = findOrCreateColor(doc, options.fillColor);
    }

    if (options.strokeColor) {
        rect.strokeColor = findOrCreateColor(doc, options.strokeColor);
    }

    if (options.strokeWeight) {
        rect.strokeWeight = options.strokeWeight;
    }

    return { success: true, frameId: rect.id };
};

// =============================================================================
// PAGE MANAGEMENT TOOLS
// =============================================================================

const addPage = async (command) => {
    console.log("[MCP] addPage called");
    const doc = app.activeDocument;
    const options = command.options || {};

    let newPage;
    if (options.atIndex === -1 || options.atIndex === undefined) {
        newPage = doc.pages.add();
    } else {
        newPage = doc.pages.add(LocationOptions.AT, doc.pages.item(options.atIndex));
    }

    if (options.basedOnMaster) {
        try {
            const master = doc.masterSpreads.itemByName(options.basedOnMaster);
            newPage.appliedMaster = master;
        } catch (e) {
            console.log("[MCP] Master not found:", options.basedOnMaster);
        }
    }

    // Find index of new page
    let pageIndex = 0;
    const pageCount = doc.pages.length;
    for (let i = 0; i < pageCount; i++) {
        const p = doc.pages.item(i);
        if (p.id === newPage.id) {
            pageIndex = i;
            break;
        }
    }

    return { success: true, pageIndex };
};

const getPageCount = async (command) => {
    console.log("[MCP] getPageCount called");
    const doc = app.activeDocument;
    return { success: true, pageCount: doc.pages.length };
};

const deletePage = async (command) => {
    console.log("[MCP] deletePage called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const page = doc.pages.item(options.pageIndex);
    page.remove();

    return { success: true };
};

// =============================================================================
// TABLE TOOLS
// =============================================================================

const createTable = async (command) => {
    console.log("[MCP] createTable called");
    const doc = app.activeDocument;
    const options = command.options || {};
    const pageIndex = options.pageIndex !== undefined ? options.pageIndex : 0;
    const page = doc.pages.item(pageIndex);

    // Create a text frame to hold the table
    const frame = page.textFrames.add();
    frame.geometricBounds = [
        options.y,
        options.x,
        options.y + options.height,
        options.x + options.width
    ];

    // Insert a table into the text frame
    const insertionPoint = frame.insertionPoints.item(0);
    const table = insertionPoint.tables.add({
        bodyRowCount: options.rows,
        columnCount: options.columns
    });

    return { success: true, tableId: table.id, frameId: frame.id };
};

const setTableCell = async (command) => {
    console.log("[MCP] setTableCell called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const frame = doc.textFrames.itemByID(options.frameId);
    const table = frame.tables.item(0);
    const row = table.rows.item(options.row);
    const cell = row.cells.item(options.column);
    cell.contents = options.content;

    return { success: true };
};

const styleTableRow = async (command) => {
    console.log("[MCP] styleTableRow called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const frame = doc.textFrames.itemByID(options.frameId);
    const table = frame.tables.item(0);
    const row = table.rows.item(options.row);

    if (options.fillColor) {
        const color = findOrCreateColor(doc, options.fillColor);
        const cellCount = row.cells.length;
        for (let i = 0; i < cellCount; i++) {
            row.cells.item(i).fillColor = color;
        }
    }

    if (options.textColor) {
        const textColor = findOrCreateColor(doc, options.textColor);
        const cellCount = row.cells.length;
        for (let i = 0; i < cellCount; i++) {
            const cell = row.cells.item(i);
            cell.texts.item(0).fillColor = textColor;
        }
    }

    return { success: true };
};

// =============================================================================
// EXPORT TOOLS
// =============================================================================

const exportPDF = async (command) => {
    console.log("[MCP] exportPDF called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const ExportFormat = indesign.ExportFormat;
    const PageRange = indesign.PageRange;

    // Set page range if specified
    if (options.pageRange && options.pageRange !== "ALL") {
        app.pdfExportPreferences.pageRange = options.pageRange;
    } else {
        app.pdfExportPreferences.pageRange = PageRange.ALL_PAGES;
    }

    // Export
    const outputFile = new File(options.outputPath);
    doc.exportFile(ExportFormat.PDF_TYPE, outputFile);

    return { success: true, outputPath: options.outputPath };
};

const exportJPEG = async (command) => {
    console.log("[MCP] exportJPEG called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const ExportFormat = indesign.ExportFormat;

    // Set JPEG export preferences
    app.jpegExportPreferences.jpegQuality = options.quality || 80;
    app.jpegExportPreferences.exportResolution = options.resolution || 300;
    app.jpegExportPreferences.pageString = String((options.pageIndex || 0) + 1);

    const outputFile = new File(options.outputPath);
    doc.exportFile(ExportFormat.JPG, outputFile);

    return { success: true, outputPath: options.outputPath };
};

// =============================================================================
// DOCUMENT INSPECTION TOOLS
// =============================================================================

const getDocumentInfo = async (command) => {
    console.log("[MCP] getDocumentInfo called");
    const doc = app.activeDocument;
    const dp = doc.documentPreferences;

    return {
        success: true,
        name: doc.name,
        pageCount: doc.pages.length,
        pageWidth: dp.pageWidth,
        pageHeight: dp.pageHeight,
        facingPages: dp.facingPages,
        margins: {
            top: doc.marginPreferences.top,
            bottom: doc.marginPreferences.bottom,
            left: doc.marginPreferences.left,
            right: doc.marginPreferences.right
        }
    };
};

const listTextFrames = async (command) => {
    console.log("[MCP] listTextFrames called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const frames = [];

    if (options.pageIndex !== null && options.pageIndex !== undefined) {
        const page = doc.pages.item(options.pageIndex);
        const count = page.textFrames.length;
        for (let i = 0; i < count; i++) {
            try {
                const f = page.textFrames.item(i);
                frames.push({
                    id: f.id,
                    bounds: f.geometricBounds,
                    contentLength: f.contents.length
                });
            } catch (e) {
                // Skip
            }
        }
    } else {
        const count = doc.textFrames.length;
        for (let i = 0; i < count; i++) {
            try {
                const f = doc.textFrames.item(i);
                frames.push({
                    id: f.id,
                    bounds: f.geometricBounds,
                    contentLength: f.contents.length
                });
            } catch (e) {
                // Skip
            }
        }
    }

    return { success: true, textFrames: frames };
};

const listImages = async (command) => {
    console.log("[MCP] listImages called");
    const doc = app.activeDocument;
    const options = command.options || {};

    const images = [];

    const processRectangles = (page) => {
        const count = page.rectangles.length;
        for (let i = 0; i < count; i++) {
            try {
                const rect = page.rectangles.item(i);
                if (rect.graphics && rect.graphics.length > 0) {
                    const graphic = rect.graphics.item(0);
                    images.push({
                        frameId: rect.id,
                        bounds: rect.geometricBounds,
                        filePath: graphic.itemLink ? graphic.itemLink.filePath : null
                    });
                }
            } catch (e) {
                // Skip
            }
        }
    };

    if (options.pageIndex !== null && options.pageIndex !== undefined) {
        processRectangles(doc.pages.item(options.pageIndex));
    } else {
        const pageCount = doc.pages.length;
        for (let p = 0; p < pageCount; p++) {
            processRectangles(doc.pages.item(p));
        }
    }

    return { success: true, images };
};

const getSelection = async (command) => {
    console.log("[MCP] getSelection called");

    const selection = [];
    if (app.selection && app.selection.length > 0) {
        for (let i = 0; i < app.selection.length; i++) {
            const item = app.selection[i];
            selection.push({
                id: item.id,
                type: item.constructor.name
            });
        }
    }

    return { success: true, selection };
};

// =============================================================================
// COMMAND ROUTING
// =============================================================================

const commandHandlers = {
    // Document
    createDocument,
    getDocumentInfo,
    getPageCount,

    // Text frames
    createTextFrame,
    setTextFrameContent,
    applyParagraphStyle,
    applyCharacterStyle,

    // Colors
    createColorSwatch,
    listSwatches,

    // Styles
    createParagraphStyle,
    createCharacterStyle,
    listStyles,

    // Images and shapes
    placeImage,
    createRectangle,

    // Pages
    addPage,
    deletePage,

    // Tables
    createTable,
    setTableCell,
    styleTableRow,

    // Export
    exportPDF,
    exportJPEG,

    // Inspection
    listTextFrames,
    listImages,
    getSelection
};

console.log("[MCP] Registered handlers:", Object.keys(commandHandlers).join(", "));

const parseAndRouteCommand = async (command) => {
    let action = command.action;
    console.log("[MCP] Routing command:", action);

    let f = commandHandlers[action];

    if (typeof f !== "function") {
        throw new Error(`Unknown Command: ${action}`);
    }

    console.log("[MCP] Executing:", f.name);
    return f(command);
};

// =============================================================================
// EXISTING HELPERS
// =============================================================================

const getActiveDocumentSettings = (command) => {
    const document = app.activeDocument;
    const d = document.documentPreferences;
    const documentPreferences = {
        pageWidth: d.pageWidth,
        pageHeight: d.pageHeight,
        pagesPerDocument: d.pagesPerDocument,
        facingPages: d.facingPages,
        measurementUnit: getUnitForIntent(d.intent)
    };

    const marginPreferences = {
        top: document.marginPreferences.top,
        bottom: document.marginPreferences.bottom,
        left: document.marginPreferences.left,
        right: document.marginPreferences.right,
        columnCount: document.marginPreferences.columnCount,
        columnGutter: document.marginPreferences.columnGutter
    };
    return { documentPreferences, marginPreferences };
};

const checkRequiresActiveDocument = async (command) => {
    if (!requiresActiveDocument(command)) {
        return;
    }

    let document = app.activeDocument;
    if (!document) {
        throw new Error(
            `${command.action} : Requires an open InDesign document`
        );
    }
};

const requiresActiveDocument = (command) => {
    return !["createDocument"].includes(command.action);
};

console.log("[MCP] commands/index.js loaded successfully");

module.exports = {
    getActiveDocumentSettings,
    checkRequiresActiveDocument,
    parseAndRouteCommand
};
