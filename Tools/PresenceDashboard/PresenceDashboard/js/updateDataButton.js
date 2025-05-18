/**
 * dataUpdateButton.js - Handles the Data Update Button functionality
 * Updates platform data via a batch file
 */

(function() {
    // Module state
    const state = {
        button: null,
        isLoading: false
    };

    // File path for credentials
    const credentialsFilePath = 'C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json';

    /**
     * Create the data update button
     */
    function createDataUpdateButton() {
        // Check if button already exists
        if (document.querySelector('.data-update-btn')) {
            console.log('Data update button already exists');
            state.button = document.querySelector('.data-update-btn');
            return;
        }
        
        console.log('Creating Data Update Button');
        
        // Create button element
        const button = document.createElement('div');
        button.className = 'data-update-btn';
        button.innerHTML = '<i class="fas fa-sync"></i>';
        button.title = 'Update Platform Data';
        
        // Add click event listener
        button.addEventListener('click', handleUpdateClick);
        
        // Add to document next to sidebar toggle
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.insertAdjacentElement('afterend', button);
        } else {
            document.body.appendChild(button);
        }
        
        console.log('Button added to DOM');
        
        // Store reference to button
        state.button = button;
    }

    /**
     * Handle button click for data update
     */
    function handleUpdateClick() {
        // Prevent multiple simultaneous updates
        if (state.isLoading) {
            console.log('Update already in progress');
            return;
        }

        // Show loading state
        setLoadingState(true);

        try {
            // Try different methods to access Electron IPC
            if (window.electronAPI) {
                console.log('Using window.electronAPI');
                window.electronAPI.send('update-data');
                
                window.electronAPI.on('data-update-result', (result) => {
                    if (result.success) {
                        handleUpdateSuccess(result);
                    } else {
                        handleUpdateError(result.error);
                    }
                });
            } 
            else if (window.ipcRenderer) {
                console.log('Using window.ipcRenderer directly');
                window.ipcRenderer.send('update-data');
                
                window.ipcRenderer.on('data-update-result', (event, result) => {
                    if (result.success) {
                        handleUpdateSuccess(result);
                    } else {
                        handleUpdateError(result.error);
                    }
                });
            }
            else if (typeof require === 'function') {
                console.log('Using require to get ipcRenderer');
                try {
                    const electron = require('electron');
                    const ipcRenderer = electron.ipcRenderer;
                    
                    ipcRenderer.send('update-data');
                    
                    ipcRenderer.on('data-update-result', (event, result) => {
                        if (result.success) {
                            handleUpdateSuccess(result);
                        } else {
                            handleUpdateError(result.error);
                        }
                    });
                } catch (e) {
                    // Try another approach with remote
                    try {
                        const remote = require('@electron/remote');
                        const ipcRenderer = remote.ipcRenderer;
                        
                        ipcRenderer.send('update-data');
                        
                        ipcRenderer.on('data-update-result', (event, result) => {
                            if (result.success) {
                                handleUpdateSuccess(result);
                            } else {
                                handleUpdateError(result.error);
                            }
                        });
                    } catch (e2) {
                        throw new Error("Could not access Electron IPC: " + e2.message);
                    }
                }
            }
            else if (window.preloadContext && window.preloadContext.ipcRenderer) {
                console.log('Using preloadContext.ipcRenderer');
                const ipcRenderer = window.preloadContext.ipcRenderer;
                
                ipcRenderer.send('update-data');
                
                ipcRenderer.on('data-update-result', (event, result) => {
                    if (result.success) {
                        handleUpdateSuccess(result);
                    } else {
                        handleUpdateError(result.error);
                    }
                });
            }
            else {
                throw new Error("Electron API is not available");
            }

            // Set up timeout
            const updateTimeout = setTimeout(() => {
                console.error('Data update timed out');
                handleUpdateError('Update timed out');
            }, 30000); // 30 seconds timeout
            
            // Store timeout ID so it can be cleared on success/error
            window.updateTimeoutId = updateTimeout;

        } catch (error) {
            handleUpdateError(error.message);
        }
    }

    /**
     * Set loading state of the button
     * @param {boolean} isLoading - Whether the button is in loading state
     */
    function setLoadingState(isLoading) {
        if (!state.button) return;

        state.isLoading = isLoading;

        if (isLoading) {
            state.button.classList.add('loading');
            state.button.style.pointerEvents = 'none';
        } else {
            state.button.classList.remove('loading');
            state.button.style.pointerEvents = 'auto';
        }
    }

    /**
     * Force reload channels like on startup
     * This uses the same logic that's used when the application first loads
     */
    function reloadChannels() {
        console.log('Forcing reload of all channels...');
        
        // Access the main.js loadChannelList function if it exists
        if (typeof loadChannelList === 'function') {
            console.log('Using global loadChannelList function');
            loadChannelList();
        }
        // Or try to find the Sidebar module's updateChannelList function
        else if (typeof Sidebar !== 'undefined' && typeof Sidebar.updateChannelList === 'function') {
            console.log('Using Sidebar.updateChannelList function');
            // First try to get the channels from FileHandler
            if (typeof FileHandler !== 'undefined' && typeof FileHandler.getChannelFolders === 'function') {
                FileHandler.getChannelFolders().then(channels => {
                    Sidebar.updateChannelList(channels);
                    console.log('Channels reloaded successfully');
                }).catch(error => {
                    console.error('Error reloading channels:', error);
                });
            }
        }
        // If none of these approaches work, reload the whole page as a fallback
        else {
            console.log('No reload functions found, attempting simpler approach');
            // Try a simple approach - just trigger reloading of the channel again
            const activeChannel = document.querySelector('#channel-list .active a');
            if (activeChannel) {
                console.log('Clicking active channel to reload data');
                // Click it twice - once to deselect, once to select again
                activeChannel.click();
                setTimeout(() => {
                    activeChannel.click();
                }, 100);
            }
        }
    }

    /**
     * Handle successful update
     * @param {Object} result - Update result
     */
    function handleUpdateSuccess(result) {
        // Clear timeout if it exists
        if (window.updateTimeoutId) {
            clearTimeout(window.updateTimeoutId);
            window.updateTimeoutId = null;
        }
        
        console.log('Data update successful', result);
        
        // Create success message
        const successMessage = document.createElement('div');
        successMessage.className = 'success-message';
        successMessage.innerHTML = `
            <div class="success-content">
                <i class="fas fa-check-circle"></i>
                <p>Data updated successfully!</p>
            </div>
        `;
        document.body.appendChild(successMessage);

        // Wait a moment to ensure file system has updated
        setTimeout(() => {
            // Force reload of channels to refresh all data
            reloadChannels();
            
            // Reset loading state after reload attempt
            setLoadingState(false);
            
            // Remove success message after 3 seconds
            setTimeout(() => {
                if (successMessage.parentNode) {
                    successMessage.parentNode.removeChild(successMessage);
                }
            }, 3000);
        }, 1000);
    }

    /**
     * Handle update error
     * @param {string} errorMessage - Error message
     */
    function handleUpdateError(errorMessage) {
        // Clear timeout if it exists
        if (window.updateTimeoutId) {
            clearTimeout(window.updateTimeoutId);
            window.updateTimeoutId = null;
        }
        
        // Reset loading state
        setLoadingState(false);

        // Create error message
        const errorMessageEl = document.createElement('div');
        errorMessageEl.className = 'error-message';
        errorMessageEl.innerHTML = `
            <div class="error-content">
                <h3>Update Error</h3>
                <p>${errorMessage}</p>
                <button id="error-close">Close</button>
            </div>
        `;
        document.body.appendChild(errorMessageEl);

        // Close button functionality
        const closeButton = errorMessageEl.querySelector('#error-close');
        closeButton.addEventListener('click', () => {
            if (errorMessageEl.parentNode) {
                errorMessageEl.parentNode.removeChild(errorMessageEl);
            }
        });

        // Log error details
        console.error('Data update failed:', errorMessage);
    }

    /**
     * Initialize the module
     */
    function init() {
        console.log('Initializing Data Update Button module');
        
        // Create button when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createDataUpdateButton);
        } else {
            createDataUpdateButton();
        }
    }

    // Initialize the module
    init();
})();