const { app, BrowserWindow, shell, ipcMain } = require('electron');
const path = require('path');
// Add this line to import the remote module
const remoteMain = require('@electron/remote/main');
// Initialize remote
remoteMain.initialize();

// Path to preload script
const preloadPath = path.join(__dirname, 'preload.js');

function createWindow() {
    // Create the browser window
    const mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        title: 'Presence Dashboard',
        webPreferences: {
            preload: preloadPath,           // Use preload script
            nodeIntegration: true,          // Enable Node.js integration
            contextIsolation: false,        // Disable context isolation for backward compatibility
            enableRemoteModule: true        // Enable remote module
        }
    });

    // Enable remote module for this window
    remoteMain.enable(mainWindow.webContents);

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

    return mainWindow;
}

/**
 * Create the credentials monitor window
 */
function createCredentialsWindow() {
    // Create a new window for credentials
    const credentialsWindow = new BrowserWindow({
        width: 800,
        height: 600,
        title: 'Credentials Monitor',
        webPreferences: {
            preload: preloadPath,          // Use the same preload script
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        },
        parent: mainWindow, // Make it a child of the main window
        modal: false        // Not modal, so user can interact with main window
    });

    // Enable remote module for this window
    remoteMain.enable(credentialsWindow.webContents);

    // Load the credentials monitor HTML file
    credentialsWindow.loadFile('credentials-monitor.html');
    
    // Uncomment to open DevTools for debugging
    // credentialsWindow.webContents.openDevTools();
    
    return credentialsWindow;
}

// Create window when app is ready
let mainWindow;
app.whenReady().then(() => {
    mainWindow = createWindow();
    
    // Set up IPC handlers for window communication
    setupIpcHandlers();
});

/**
 * Set up IPC handlers for communication between windows
 */
function setupIpcHandlers() {
    // Handle credential refresh executions
    ipcMain.on('execute-command', (event, command) => {
        const { exec } = require('child_process');
        
        console.log('Executing command:', command);
        
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Execution error: ${error.message}`);
                event.reply('command-result', { success: false, error: error.message });
                return;
            }
            
            if (stderr) {
                console.error(`Command stderr: ${stderr}`);
            }
            
            console.log(`Command stdout: ${stdout}`);
            event.reply('command-result', { success: true, stdout, stderr });
        });
    });
    
    // Handle data update command
    ipcMain.on('update-data', (event) => {
        console.log('Received update-data request');
        const { exec } = require('child_process');
        const dataUpdatePath = 'D:\\2025\\Projects\\Presence\\Presence0.1\\Tools\\PresenceDashboard\\POC-Platform-Engagement-Poller.bat';
        
        console.log('Executing data update script at:', dataUpdatePath);
        
        exec(dataUpdatePath, (error, stdout, stderr) => {
            console.log('Data update script execution complete');
            
            if (error) {
                console.error('Data update script error:', error.message);
                event.reply('data-update-result', { 
                    success: false, 
                    error: error.message 
                });
                return;
            }
            
            console.log('Data update script stdout:', stdout);
            
            if (stderr) {
                console.warn('Data update script stderr:', stderr);
            }
            
            event.reply('data-update-result', { 
                success: true, 
                stdout, 
                stderr 
            });
        });
    });
    
    // Handle opening the credentials monitor window
    ipcMain.on('open-credentials-window', (event) => {
        console.log('Received request to open credentials window');
        
        // Check if credentials window already exists
        const existingWindows = BrowserWindow.getAllWindows();
        const credentialsWindowExists = existingWindows.some(window => 
            window.title === 'Credentials Monitor' && !window.isDestroyed()
        );
        
        if (credentialsWindowExists) {
            console.log('Credentials window already open, focusing it');
            // Find and focus the existing window
            const existingWindow = existingWindows.find(window => 
                window.title === 'Credentials Monitor' && !window.isDestroyed()
            );
            if (existingWindow) {
                if (existingWindow.isMinimized()) existingWindow.restore();
                existingWindow.focus();
            }
        } else {
            console.log('Creating new credentials window');
            // Create a new credentials window
            const credentialsWindow = createCredentialsWindow();
            
            // Log when the window is ready
            credentialsWindow.webContents.on('did-finish-load', () => {
                console.log('Credentials window loaded successfully');
            });
        }
    });
    
    // Handle credential refresh completed notification
    ipcMain.on('credential-refresh-completed', (event) => {
        console.log('Credential refresh completed, notifying all windows');
        
        // Notify all windows about the credential refresh
        BrowserWindow.getAllWindows().forEach(window => {
            if (!window.isDestroyed()) {
                window.webContents.send('credential-refresh-completed');
            }
        });
    });
    
    // Handle close current window request
    ipcMain.on('close-current-window', (event) => {
        const win = BrowserWindow.fromWebContents(event.sender);
        if (win) {
            console.log('Closing window by request:', win.getTitle());
            win.close();
        }
    });
}

// Quit the app when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
    app.quit();
});

// On macOS, create a new window when the app icon is clicked and no windows are open
app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        mainWindow = createWindow();
    }
});