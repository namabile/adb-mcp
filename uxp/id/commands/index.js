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

// DEBUG: Log module load start
console.log("[MCP] Loading commands/index.js...");

const {app, DocumentIntentOptions} = require("indesign");
console.log("[MCP] InDesign module loaded successfully");

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

const getUnitForIntent = (intent) => {
    if(intent && intent.toString() === DocumentIntentOptions.WEB_INTENT.toString()) {
        return "px";
    }
    throw new Error(`getUnitForIntent : unknown intent [${intent}]`);
};

// =============================================================================
// ORIGINAL: DOCUMENT CREATION
// =============================================================================

const createDocument = async (command) => {
    console.log("[MCP] createDocument called");
    const options = command.options;
    let documents = app.documents;
    let margins = options.margins;
    let unit = getUnitForIntent(DocumentIntentOptions.WEB_INTENT);

    app.marginPreferences.bottom = `${margins.bottom}${unit}`;
    app.marginPreferences.top = `${margins.top}${unit}`;
    app.marginPreferences.left = `${margins.left}${unit}`;
    app.marginPreferences.right = `${margins.right}${unit}`;
    app.marginPreferences.columnCount = options.columns.count;
    app.marginPreferences.columnGutter = `${options.columns.gutter}${unit}`;

    let documentPreferences = {
        pageWidth: `${options.pageWidth}${unit}`,
        pageHeight: `${options.pageHeight}${unit}`,
        pagesPerDocument: options.pagesPerDocument,
        facingPages: options.facingPages,
        intent: DocumentIntentOptions.WEB_INTENT
    };

    const showingWindow = true;
    const doc = documents.add({showingWindow, documentPreferences});
    return { success: true, documentId: doc.id };
};

// =============================================================================
// NEW: TEXT FRAME (minimal)
// =============================================================================

const createTextFrame = async (command) => {
    console.log("[MCP] createTextFrame called");
    const doc = app.activeDocument;
    const options = command.options;
    const page = doc.pages[options.pageIndex || 0];

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

// =============================================================================
// NEW: DOCUMENT INFO (read-only, safe)
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

// =============================================================================
// NEW: PAGE COUNT (simplest possible)
// =============================================================================

const getPageCount = async (command) => {
    console.log("[MCP] getPageCount called");
    const doc = app.activeDocument;
    return { success: true, pageCount: doc.pages.length };
};

// =============================================================================
// COMMAND ROUTING
// =============================================================================

const commandHandlers = {
    createDocument,
    createTextFrame,
    getDocumentInfo,
    getPageCount
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
