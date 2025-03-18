const { app, BrowserWindow, shell } = require('electron');
const path = require('path');

function createWindow() {
    // Create the browser window
    const mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: true,           // Enable Node.js integration
            contextIsolation: false,         // Disable context isolation
            enableRemoteModule: true         // Enable remote module
        }
    });

    // Load the index.html file
    mainWindow.loadFile('index.html');
    
    // Handle external links to open in default browser (Chrome)
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        // Open all external URLs in default browser
        shell.openExternal(url);
        return { action: 'deny' }; // Prevent opening in Electron
    });
    
    // Also handle regular link clicks
    mainWindow.webContents.on('will-navigate', (event, url) => {
        // If it's not a local file URL, open in default browser
        if (!url.startsWith('file://')) {
            event.preventDefault();
            shell.openExternal(url);
        }
    });

    // Uncomment to open DevTools automatically on startup
    // mainWindow.webContents.openDevTools();
}

// Create window when app is ready
app.whenReady().then(createWindow);

// Quit the app when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
    app.quit();
});

// On macOS, create a new window when the app icon is clicked and no windows are open
app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});