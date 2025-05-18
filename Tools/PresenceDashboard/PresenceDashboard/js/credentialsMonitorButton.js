/**
 * credentialsMonitorButton.js - Handles the Credentials Monitor button
 * Creates and manages the button that opens the Credentials Monitor window
 */

// Global variable to track if button exists
let credentialsButton = null;

// Immediately create button when script loads
(function() {
    console.log('Initializing Credentials Monitor Button...');
    
    // Add CSS first
    addButtonStyles();
    
    // Create the button
    createButton();
    
    // Check credentials file on startup
    setTimeout(checkCredentialsFile, 1000);
    
    // Set up automatic checking
    setInterval(checkCredentialsFile, 5 * 60 * 1000); // Check every 5 minutes
    
    // Listen for credential refresh events from the credentials monitor
    setupCredentialRefreshListener();
})();

/**
 * Add button styles to document
 */
function addButtonStyles() {
    if (document.getElementById('credentials-button-styles')) return;
    
    console.log('Adding Credentials Monitor Button styles');
    
    const style = document.createElement('style');
    style.id = 'credentials-button-styles';
    style.textContent = `
        .credentials-monitor-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: #8A4FFF;
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            z-index: 9999;
            transition: all 0.3s ease;
        }
        
        .credentials-monitor-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .credentials-monitor-btn i {
            font-size: 20px;
        }
        
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #dc3545;
            color: white;
            font-size: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Create the credentials monitor button
 */
function createButton() {
    // Check if button already exists
    if (document.querySelector('.credentials-monitor-btn')) {
        console.log('Button already exists');
        credentialsButton = document.querySelector('.credentials-monitor-btn');
        return;
    }
    
    console.log('Creating Credentials Monitor Button');
    
    // Create button
    const button = document.createElement('div');
    button.className = 'credentials-monitor-btn';
    button.title = 'Credentials Monitor';
    button.innerHTML = '<i class="fas fa-key"></i>';
    
    // Add click event
    button.addEventListener('click', () => {
        console.log('Credentials Monitor Button clicked');
        openCredentialsWindow();
    });
    
    // Add to document
    document.body.appendChild(button);
    console.log('Button added to DOM');
    
    // Store reference to button
    credentialsButton = button;
}

/**
 * Setup listener for credential refresh events
 */
function setupCredentialRefreshListener() {
    // Try multiple methods to set up listeners for compatibility
    
    // Method 1: Using exposed electronAPI
    if (window.electronAPI) {
        console.log('Setting up listener using electronAPI');
        window.electronAPI.on('credential-refresh-completed', () => {
            console.log('Received credential refresh completed event via electronAPI');
            checkCredentialsFile();
        });
    } 
    // Method 2: Using direct ipcRenderer
    else if (window.ipcRenderer) {
        console.log('Setting up listener using direct ipcRenderer');
        window.ipcRenderer.on('credential-refresh-completed', () => {
            console.log('Received credential refresh completed event via ipcRenderer');
            checkCredentialsFile();
        });
    }
    // Method 3: Using preloadContext
    else if (window.preloadContext && window.preloadContext.ipcRenderer) {
        console.log('Setting up listener using preloadContext.ipcRenderer');
        window.preloadContext.ipcRenderer.on('credential-refresh-completed', () => {
            console.log('Received credential refresh completed event via preloadContext.ipcRenderer');
            checkCredentialsFile();
        });
    }
    
    // Also listen for a custom event (for non-IPC environments)
    window.addEventListener('credential-refresh-completed', () => {
        console.log('Received custom credential refresh completed event');
        checkCredentialsFile();
    });
}

/**
 * Check if credentials file exists and has items
 */
function checkCredentialsFile() {
    console.log('Checking credentials file...');
    
    try {
        // For browser environments or where fs is not available
        if (typeof require !== 'undefined') {
            try {
                const fs = require('fs');
                const credentialsFilePath = 'C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json';
                
                // Check if file exists
                if (fs.existsSync(credentialsFilePath)) {
                    // Read the file
                    fs.readFile(credentialsFilePath, 'utf8', (err, data) => {
                        if (err) {
                            console.error('Error reading credentials file:', err);
                            updateNotificationBadge(false);
                            return;
                        }
                        
                        try {
                            // Parse the JSON data
                            const credentials = JSON.parse(data);
                            
                            // Check if there are any credentials
                            const hasCredentials = Array.isArray(credentials) && credentials.length > 0;
                            console.log('Credentials found:', hasCredentials ? 'Yes' : 'No');
                            
                            // Update notification badge
                            updateNotificationBadge(hasCredentials);
                        } catch (parseError) {
                            console.error('Error parsing credentials JSON:', parseError);
                            updateNotificationBadge(false);
                        }
                    });
                } else {
                    console.warn('Credentials file does not exist:', credentialsFilePath);
                    updateNotificationBadge(false);
                }
            } catch (requireError) {
                console.error('Error requiring fs module:', requireError);
                
                // Try alternate method using window.fs
                if (window.fs) {
                    const fs = window.fs;
                    const credentialsFilePath = 'C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json';
                    
                    if (fs.existsSync(credentialsFilePath)) {
                        fs.readFile(credentialsFilePath, { encoding: 'utf8' }, (err, data) => {
                            if (err) {
                                console.error('Error reading credentials file with window.fs:', err);
                                updateNotificationBadge(false);
                                return;
                            }
                            
                            try {
                                const credentials = JSON.parse(data);
                                const hasCredentials = Array.isArray(credentials) && credentials.length > 0;
                                updateNotificationBadge(hasCredentials);
                            } catch (parseError) {
                                console.error('Error parsing credentials JSON:', parseError);
                                updateNotificationBadge(false);
                            }
                        });
                    } else {
                        updateNotificationBadge(false);
                    }
                } else if (window.preloadContext && window.preloadContext.fs) {
                    const fs = window.preloadContext.fs;
                    const credentialsFilePath = 'C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json';
                    
                    if (fs.existsSync(credentialsFilePath)) {
                        fs.readFile(credentialsFilePath, { encoding: 'utf8' }, (err, data) => {
                            if (err) {
                                console.error('Error reading credentials file with preloadContext.fs:', err);
                                updateNotificationBadge(false);
                                return;
                            }
                            
                            try {
                                const credentials = JSON.parse(data);
                                const hasCredentials = Array.isArray(credentials) && credentials.length > 0;
                                updateNotificationBadge(hasCredentials);
                            } catch (parseError) {
                                console.error('Error parsing credentials JSON:', parseError);
                                updateNotificationBadge(false);
                            }
                        });
                    } else {
                        updateNotificationBadge(false);
                    }
                } else {
                    console.warn('Cannot check credentials file: fs module not available');
                    updateNotificationBadge(false);
                }
            }
        } else if (window.fs) {
            const fs = window.fs;
            const credentialsFilePath = 'C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json';
            
            if (fs.existsSync(credentialsFilePath)) {
                fs.readFile(credentialsFilePath, { encoding: 'utf8' }, (err, data) => {
                    if (err) {
                        console.error('Error reading credentials file with window.fs:', err);
                        updateNotificationBadge(false);
                        return;
                    }
                    
                    try {
                        const credentials = JSON.parse(data);
                        const hasCredentials = Array.isArray(credentials) && credentials.length > 0;
                        updateNotificationBadge(hasCredentials);
                    } catch (parseError) {
                        console.error('Error parsing credentials JSON:', parseError);
                        updateNotificationBadge(false);
                    }
                });
            } else {
                updateNotificationBadge(false);
            }
        } else if (window.preloadContext && window.preloadContext.fs) {
            const fs = window.preloadContext.fs;
            const credentialsFilePath = 'C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json';
            
            if (fs.existsSync(credentialsFilePath)) {
                fs.readFile(credentialsFilePath, { encoding: 'utf8' }, (err, data) => {
                    if (err) {
                        console.error('Error reading credentials file with preloadContext.fs:', err);
                        updateNotificationBadge(false);
                        return;
                    }
                    
                    try {
                        const credentials = JSON.parse(data);
                        const hasCredentials = Array.isArray(credentials) && credentials.length > 0;
                        updateNotificationBadge(hasCredentials);
                    } catch (parseError) {
                        console.error('Error parsing credentials JSON:', parseError);
                        updateNotificationBadge(false);
                    }
                });
            } else {
                updateNotificationBadge(false);
            }
        } else {
            console.warn('Cannot check credentials file: fs module not available');
            updateNotificationBadge(false);
        }
    } catch (error) {
        console.error('Error checking credentials file:', error);
        updateNotificationBadge(false);
    }
}

/**
 * Update the notification badge on the button
 * @param {boolean} show - Whether to show the badge
 */
function updateNotificationBadge(show) {
    if (!credentialsButton) {
        credentialsButton = document.querySelector('.credentials-monitor-btn');
        if (!credentialsButton) {
            console.warn('Cannot update badge: Button not found');
            return;
        }
    }
    
    console.log('Updating notification badge:', show ? 'Showing' : 'Hiding');
    
    // Remove existing badge
    const existingBadge = credentialsButton.querySelector('.notification-badge');
    if (existingBadge) {
        credentialsButton.removeChild(existingBadge);
    }
    
    // Add badge if needed
    if (show) {
        const badge = document.createElement('div');
        badge.className = 'notification-badge';
        badge.innerHTML = '!';
        credentialsButton.appendChild(badge);
    }
}

/**
 * Open the credentials monitor window
 */
function openCredentialsWindow() {
    console.log('Opening Credentials Monitor window...');
    
    try {
        // Method 1: Using exposed electronAPI
        if (window.electronAPI) {
            console.log('Using electronAPI to send message');
            window.electronAPI.send('open-credentials-window');
            return;
        } 
        
        // Method 2: Using direct ipcRenderer
        if (window.ipcRenderer) {
            console.log('Using direct ipcRenderer to send message');
            window.ipcRenderer.send('open-credentials-window');
            return;
        }
        
        // Method 3: Using require with electron
        if (typeof require !== 'undefined') {
            try {
                console.log('Trying require("electron")');
                const electron = require('electron');
                electron.ipcRenderer.send('open-credentials-window');
                return;
            } catch (e) {
                console.log('Error with require("electron"):', e.message);
                // Continue to next method
            }
        }
        
        // Method 4: Using require with @electron/remote
        if (typeof require !== 'undefined') {
            try {
                console.log('Trying require("@electron/remote")');
                const remote = require('@electron/remote');
                remote.ipcRenderer.send('open-credentials-window');
                return;
            } catch (e) {
                console.log('Error with require("@electron/remote"):', e.message);
                // Continue to next method
            }
        }
        
        // Method 5: Using preloadContext
        if (window.preloadContext && window.preloadContext.ipcRenderer) {
            console.log('Using preloadContext.ipcRenderer');
            window.preloadContext.ipcRenderer.send('open-credentials-window');
            return;
        }
        
        // If we get here, all methods failed
        throw new Error("Electron IPC API is not available");
        
    } catch (error) {
        console.error('Error opening Credentials Monitor window:', error);
        alert(`Error opening Credentials Monitor: ${error.message}`);
    }
}

// Export functions for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        checkCredentialsFile,
        updateNotificationBadge
    };
}