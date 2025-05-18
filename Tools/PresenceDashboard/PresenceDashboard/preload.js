/**
 * preload.js - Preload script for Electron
 * Safely exposes Electron APIs to renderer processes
 */

const { contextBridge, ipcRenderer } = require('electron');
const fs = require('fs');
const path = require('path');

// Whitelist channels for security
const validSendChannels = [
    'open-credentials-window', 
    'execute-command', 
    'credential-refresh-completed',
    'update-data',
    'close-current-window'
];

const validReceiveChannels = [
    'command-result', 
    'credential-refresh-completed',
    'data-update-result'
];

// Create API object for exposure
const electronAPI = {
    // IPC communication methods
    send: (channel, data) => {
        if (validSendChannels.includes(channel)) {
            console.log(`Preload: Sending message to channel: ${channel}`, data);
            ipcRenderer.send(channel, data);
        } else {
            console.error(`Preload: Invalid send channel: ${channel}`);
        }
    },
    
    // Receive messages from main process
    on: (channel, func) => {
        if (validReceiveChannels.includes(channel)) {
            // Remove existing listeners to prevent memory leaks
            ipcRenderer.removeAllListeners(channel);
            
            // Add new listener
            ipcRenderer.on(channel, (event, ...args) => {
                console.log(`Preload: Received message on channel: ${channel}`, args);
                func(...args);
            });
        } else {
            console.error(`Preload: Invalid receive channel: ${channel}`);
        }
    },
    
    // File system operations
    readFile: (filePath, options = {}) => {
        return new Promise((resolve, reject) => {
            fs.readFile(filePath, options, (err, data) => {
                if (err) reject(err);
                else resolve(data);
            });
        });
    },
    
    writeFile: (filePath, data, options = {}) => {
        return new Promise((resolve, reject) => {
            fs.writeFile(filePath, data, options, (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    },
    
    // Check if a file exists
    fileExists: (filePath) => {
        return fs.existsSync(filePath);
    },
    
    // Get file information
    getFileInfo: (filePath) => {
        try {
            return fs.statSync(filePath);
        } catch (error) {
            console.error(`Error getting file info: ${error.message}`);
            return null;
        }
    },
    
    // Path resolution
    resolvePath: (pathSegments) => {
        return path.resolve(...pathSegments);
    },
    
    // Close current window
    closeCurrentWindow: () => {
        ipcRenderer.send('close-current-window');
    },
    
    // Debugging method to expose available channels
    getAvailableChannels: () => ({
        sendChannels: validSendChannels,
        receiveChannels: validReceiveChannels
    })
};

// Try to expose via contextBridge if possible
try {
    if (contextBridge && contextBridge.exposeInMainWorld) {
        console.log('Preload: Using contextBridge to expose electronAPI');
        contextBridge.exposeInMainWorld('electronAPI', electronAPI);
        console.log('Preload: ElectronAPI successfully exposed to renderer process via contextBridge');
    } else {
        console.log('Preload: contextBridge not available, exposing API directly on window');
        // Direct exposure to window
        process.once('loaded', () => {
            window.electronAPI = electronAPI;
        });
    }
} catch (error) {
    console.error('Preload: Error exposing ElectronAPI:', error);
    // Fallback - direct exposure
    process.once('loaded', () => {
        window.electronAPI = electronAPI;
    });
}

// Also expose some modules directly to the window for advanced debugging
// and for compatibility with existing code in the application
window.ipcRenderer = ipcRenderer;
window.fs = fs;
window.path = path;

// Store in preloadContext as well
window.preloadContext = {
    fs,
    path,
    ipcRenderer,
    electronAPI,
    nodeIntegration: true,
    contextIsolation: false
};