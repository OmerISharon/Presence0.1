/**
 * credentialsMonitor.js - Handles the Credentials Monitor window functionality
 * Displays and manages credential refreshes for different platforms
 */

// CredentialsMonitor module
const CredentialsMonitor = (() => {
    // Path to the credentials JSON file
    const credentialsFilePath = 'C:\\Users\\omers\\AppData\\Roaming\\POC-Platform-Engagement-Poller\\AuthorizationRefreshNotifications.json';
    
    // Initialize Electron modules
    let fs, exec, currentWindow, ipcRenderer;
    
    try {
        // Try multiple approaches to get the required modules
        
        // Approach 1: Direct window properties (from preload)
        if (window.fs && window.ipcRenderer) {
            console.log('Using window.fs and window.ipcRenderer');
            fs = window.fs;
            ipcRenderer = window.ipcRenderer;
        } 
        // Approach 2: Try to get modules from electron directly
        else if (typeof require === 'function') {
            try {
                console.log('Trying require("electron")');
                const electron = require('electron');
                fs = require('fs');
                const { exec: childExec } = require('child_process');
                exec = childExec;
                ipcRenderer = electron.ipcRenderer;
                
                // Try to get the current window
                if (electron.remote) {
                    currentWindow = electron.remote.getCurrentWindow();
                }
            } catch (e) {
                console.log('Error with require("electron"):', e.message);
                // Try another approach with remote
                try {
                    console.log('Trying require("@electron/remote")');
                    const remote = require('@electron/remote');
                    if (!fs) fs = require('fs');
                    if (!exec) {
                        const { exec: childExec } = require('child_process');
                        exec = childExec;
                    }
                    currentWindow = remote.getCurrentWindow();
                    if (!ipcRenderer) {
                        ipcRenderer = remote.ipcRenderer;
                    }
                } catch (e2) {
                    console.log('Error with require("@electron/remote"):', e2.message);
                }
            }
        }
        // Approach 3: Try preloadContext
        if ((!fs || !ipcRenderer) && window.preloadContext) {
            console.log('Using window.preloadContext');
            if (!fs) fs = window.preloadContext.fs;
            if (!ipcRenderer) ipcRenderer = window.preloadContext.ipcRenderer;
        }
        
        // Approach 4: Try electronAPI for ipcRenderer functions
        if (window.electronAPI) {
            console.log('Found window.electronAPI');
        }
        
        // Final check
        if (!fs) {
            console.warn('Could not initialize fs module');
        }
        if (!ipcRenderer && !window.electronAPI) {
            console.warn('Could not initialize ipcRenderer');
        }
    } catch (error) {
        console.error('Error initializing Electron modules:', error);
        // Show an error message if needed
    }
    
    // DOM elements
    const elements = {
        lastUpdatedTime: document.getElementById('last-updated-time'),
        credentialsList: document.getElementById('credentials-list'),
        searchInput: document.getElementById('search-credentials'),
        platformFilter: document.getElementById('platform-filter'),
        refreshButton: document.getElementById('refresh-credentials'),
        closeButton: document.getElementById('close-window'),
        loadingOverlay: document.getElementById('credentials-loading-overlay'),
        errorMessage: document.getElementById('credentials-error-message'),
        errorText: document.getElementById('credentials-error-text'),
        errorClose: document.getElementById('credentials-error-close')
    };
    
    // State
    const state = {
        credentials: [],
        filteredCredentials: [],
        platforms: new Set(),
        searchTerm: '',
        selectedPlatform: '',
        isLoading: false
    };
    
    /**
     * Initialize the module
     */
    function init() {
        console.log('Initializing Credentials Monitor...');
        
        // Add event listeners
        addEventListeners();
        
        // Load credentials data
        loadCredentials();
    }
    
    /**
     * Add event listeners
     */
    function addEventListeners() {
        // Search input
        if (elements.searchInput) {
            elements.searchInput.addEventListener('input', (e) => {
                state.searchTerm = e.target.value.toLowerCase();
                filterCredentials();
            });
        }
        
        // Platform filter
        if (elements.platformFilter) {
            elements.platformFilter.addEventListener('change', (e) => {
                state.selectedPlatform = e.target.value;
                filterCredentials();
            });
        }
        
        // Refresh button
        if (elements.refreshButton) {
            elements.refreshButton.addEventListener('click', loadCredentials);
        }
        
        // Close button
        if (elements.closeButton) {
            elements.closeButton.addEventListener('click', () => {
                // First ensure loading state is cleared
                setLoading(false);
                
                // Then try to close the window
                if (currentWindow) {
                    try {
                        currentWindow.close();
                    } catch (error) {
                        console.error('Error closing window:', error);
                        
                        // Try alternative methods if the first one fails
                        closeWindowAlternative();
                    }
                } else {
                    console.error('Cannot close window: currentWindow is not available');
                    
                    // Try alternative approach
                    closeWindowAlternative();
                }
            });
        }
        
        // Error close button
        if (elements.errorClose) {
            elements.errorClose.addEventListener('click', () => {
                elements.errorMessage.classList.add('hidden');
            });
        }
    }
    
    /**
     * Alternative methods to close window
     */
    function closeWindowAlternative() {
        if (window.electronAPI) {
            console.log('Trying to close window with electronAPI');
            window.electronAPI.send('close-current-window');
        } else if (ipcRenderer) {
            console.log('Trying to close window with ipcRenderer');
            ipcRenderer.send('close-current-window');
        } else if (window.preloadContext && window.preloadContext.ipcRenderer) {
            console.log('Trying to close window with preloadContext.ipcRenderer');
            window.preloadContext.ipcRenderer.send('close-current-window');
        } else {
            showError('Could not close window: Electron API not available');
        }
    }
    
    /**
     * Notify main process and other windows that credentials have changed
     */
    function notifyCredentialChange() {
        console.log('Notifying of credential change');
        
        // Try multiple methods to send notification
        
        // Method 1: Using electronAPI
        if (window.electronAPI) {
            console.log('Sending notification with electronAPI');
            window.electronAPI.send('credential-refresh-completed');
        }
        // Method 2: Using direct ipcRenderer
        else if (ipcRenderer) {
            console.log('Sending notification with direct ipcRenderer');
            ipcRenderer.send('credential-refresh-completed');
        }
        // Method 3: Using preloadContext
        else if (window.preloadContext && window.preloadContext.ipcRenderer) {
            console.log('Sending notification with preloadContext.ipcRenderer');
            window.preloadContext.ipcRenderer.send('credential-refresh-completed');
        } else {
            console.warn('Could not send IPC notification: No IPC method available');
        }
        
        // Also dispatch a custom event for non-IPC environments or same-window components
        try {
            const event = new CustomEvent('credential-refresh-completed');
            window.dispatchEvent(event);
            console.log('Dispatched custom event');
        } catch (error) {
            console.error('Error dispatching custom event:', error);
        }
    }
    
    /**
     * Load credentials from the JSON file
     */
    function loadCredentials() {
        setLoading(true);
        
        // Set a timeout to ensure loading state doesn't get stuck
        const loadingTimeout = setTimeout(() => {
            console.log('Loading timeout reached - forcing loading state to clear');
            setLoading(false);
        }, 10000); // 10 second timeout
        
        if (!fs) {
            console.error('Cannot load credentials: fs module is not available');
            showError('Cannot load credentials: Electron API not available');
            setLoading(false);
            clearTimeout(loadingTimeout);
            return;
        }
        
        try {
            // Read the JSON file
            fs.readFile(credentialsFilePath, 'utf8', (err, data) => {
                // Clear timeout since we got a response
                clearTimeout(loadingTimeout);
                
                if (err) {
                    console.error('Error reading credentials file:', err);
                    showError(`Error reading credentials file: ${err.message}`);
                    setLoading(false);
                    // Notify that credentials have been checked (even if error)
                    notifyCredentialChange();
                    return;
                }
                
                try {
                    // Parse the JSON data
                    const credentials = JSON.parse(data);
                    
                    // Update state
                    state.credentials = Array.isArray(credentials) ? credentials : [];
                    
                    // Extract platforms
                    state.platforms = new Set(state.credentials.map(cred => cred.Platform).filter(Boolean));
                    
                    // Update platform filter options
                    updatePlatformFilterOptions();
                    
                    // Apply filters
                    filterCredentials();
                    
                    // Update last updated time
                    updateLastUpdatedTime();
                    
                    setLoading(false);
                    
                    // Notify that credentials have been updated
                    notifyCredentialChange();
                } catch (parseError) {
                    console.error('Error parsing credentials JSON:', parseError);
                    showError(`Error parsing credentials file: ${parseError.message}`);
                    setLoading(false);
                    // Notify that credentials have been checked (even if error)
                    notifyCredentialChange();
                }
            });
        } catch (error) {
            // Make sure to clear timeout and loading state if exception occurs
            clearTimeout(loadingTimeout);
            console.error('Error accessing credentials file:', error);
            showError(`Error accessing credentials file: ${error.message}`);
            setLoading(false);
            // Notify that credentials have been checked (even if error)
            notifyCredentialChange();
        }
    }
    
    /**
     * Filter credentials based on search term and platform filter
     */
    function filterCredentials() {
        state.filteredCredentials = state.credentials.filter(credential => {
            // Apply search term filter
            const matchesSearch = !state.searchTerm || 
                credential.Account?.toLowerCase().includes(state.searchTerm) || 
                credential.Platform?.toLowerCase().includes(state.searchTerm);
            
            // Apply platform filter
            const matchesPlatform = !state.selectedPlatform || 
                credential.Platform === state.selectedPlatform;
            
            return matchesSearch && matchesPlatform;
        });
        
        // Render filtered credentials
        renderCredentialsList();
    }
    
    /**
     * Update platform filter options
     */
    function updatePlatformFilterOptions() {
        if (!elements.platformFilter) return;
        
        // Clear existing options except the first one (All Platforms)
        while (elements.platformFilter.options.length > 1) {
            elements.platformFilter.remove(1);
        }
        
        // Add platform options
        Array.from(state.platforms).sort().forEach(platform => {
            const option = document.createElement('option');
            option.value = platform;
            option.textContent = platform;
            elements.platformFilter.appendChild(option);
        });
    }
    
    /**
     * Render the credentials list
     */
    function renderCredentialsList() {
        if (!elements.credentialsList) return;
        
        // Clear the list
        elements.credentialsList.innerHTML = '';
        
        // If no credentials
        if (state.filteredCredentials.length === 0) {
            showEmptyList();
            return;
        }
        
        // Create credential items
        state.filteredCredentials.forEach(credential => {
            const credentialItem = createCredentialItem(credential);
            elements.credentialsList.appendChild(credentialItem);
        });
    }
    
    /**
     * Create a credential item element
     * @param {Object} credential - The credential data
     * @returns {HTMLElement} - The credential item element
     */
    function createCredentialItem(credential) {
        const item = document.createElement('div');
        item.className = 'credential-item';
        
        // Get platform icon and class
        const { icon, className } = getPlatformIcon(credential.Platform || 'unknown');
        
        // Format date
        const formattedDate = formatDate(credential.UpdatedOn);
        
        // Create item HTML
        item.innerHTML = `
            <div class="credential-info">
                <div class="credential-platform">
                    <span class="platform-icon ${className}">
                        <i class="${icon}"></i>
                    </span>
                    <span class="platform-name">${credential.Platform || 'Unknown'}</span>
                </div>
                <div class="credential-account">${credential.Account || 'Unknown Account'}</div>
                <div class="credential-date">Last refreshed: ${formattedDate}</div>
            </div>
            <div class="credential-actions">
                <button class="refresh-credential-btn" title="Refresh Credentials">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
        `;
        
        // Add event listener to refresh button
        const refreshButton = item.querySelector('.refresh-credential-btn');
        if (refreshButton && credential.ExecutableCommand) {
            refreshButton.addEventListener('click', () => {
                refreshCredential(credential);
            });
        }
        
        return item;
    }
    
    /**
     * Refresh a credential by executing its command
     * @param {Object} credential - The credential data
     */
    function refreshCredential(credential) {
        if (!credential.ExecutableCommand) {
            showError('No executable command found for this credential');
            return;
        }
        
        // Show loading indicator
        setLoading(true);
        // Timeout to ensure loading state doesn't get stuck
        const loadingTimeout = setTimeout(() => {
            console.log('Loading timeout reached - forcing loading state to clear');
            setLoading(false);
            notifyCredentialChange();
        }, 30000);

        // Handler for command result
        function handleCommandResult(response) {
            clearTimeout(loadingTimeout);
            setLoading(false);
            const { success, error: errMsg, stdout, stderr } = response;
            if (!success) {
                showError(`Error refreshing credential: ${errMsg}`);
            } else {
                if (stderr && stderr.trim()) {
                    console.warn(`Command stderr: ${stderr}`);
                    if (stderr.toLowerCase().includes('error') || stderr.toLowerCase().includes('exception')) {
                        showError(`Warning while refreshing credential: ${stderr}`);
                    }
                }
                // Show success message
                const successMessage = document.createElement('div');
                successMessage.className = 'success-message';
                successMessage.innerHTML = `
                    <div class="success-content">
                        <i class="fas fa-check-circle"></i>
                        <p>Credential refreshed successfully!</p>
                    </div>
                `;
                document.body.appendChild(successMessage);
                setTimeout(() => {
                    if (successMessage.parentNode) successMessage.parentNode.removeChild(successMessage);
                }, 3000);
                // Reload credentials after a short delay
                setTimeout(() => { loadCredentials(); }, 1000);
            }
            notifyCredentialChange();
        }

        // Execute via IPC to main process
        if (window.electronAPI && typeof window.electronAPI.send === 'function') {
            window.electronAPI.on('command-result', handleCommandResult);
            window.electronAPI.send('execute-command', credential.ExecutableCommand);
        } else if (ipcRenderer && typeof ipcRenderer.send === 'function') {
            ipcRenderer.once('command-result', (event, response) => handleCommandResult(response));
            ipcRenderer.send('execute-command', credential.ExecutableCommand);
        } else {
            clearTimeout(loadingTimeout);
            setLoading(false);
            console.error('Cannot execute command: Electron API not available');
            showError('Cannot execute command: Electron API not available');
        }
    }
    
    /**
     * Get platform icon and class
     * @param {string} platform - The platform name
     * @returns {Object} - Object with icon and className
     */
    function getPlatformIcon(platform) {
        switch (platform.toLowerCase()) {
            case 'youtube':
                return { icon: 'fab fa-youtube', className: 'platform-youtube' };
            case 'twitter':
                return { icon: 'fab fa-twitter', className: 'platform-twitter' };
            case 'instagram':
                return { icon: 'fab fa-instagram', className: 'platform-instagram' };
            case 'facebook':
                return { icon: 'fab fa-facebook-f', className: 'platform-facebook' };
            case 'tiktok':
                return { icon: 'fab fa-tiktok', className: 'platform-tiktok' };
            default:
                return { icon: 'fas fa-globe', className: '' };
        }
    }
    
    /**
     * Show empty list message
     */
    function showEmptyList() {
        if (!elements.credentialsList) return;
        
        if (state.searchTerm || state.selectedPlatform) {
            // No results message
            elements.credentialsList.innerHTML = `
                <div class="empty-list">
                    <i class="fas fa-search"></i>
                    <p>No credentials match your search criteria</p>
                </div>
            `;
        } else {
            // Empty list message
            elements.credentialsList.innerHTML = `
                <div class="empty-list">
                    <i class="fas fa-user-lock"></i>
                    <p>No credentials found</p>
                </div>
            `;
        }
    }
    
    /**
     * Update the last updated time display
     */
    function updateLastUpdatedTime() {
        if (!elements.lastUpdatedTime) return;
        
        const now = new Date();
        elements.lastUpdatedTime.textContent = now.toLocaleString();
    }
    
    /**
     * Format a date string
     * @param {string} dateString - The date string to format
     * @returns {string} - Formatted date string
     */
    function formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (error) {
            console.error('Error formatting date:', error);
            return dateString;
        }
    }
    
    /**
     * Set loading state
     * @param {boolean} isLoading - Whether loading is active
     */
    function setLoading(isLoading) {
        state.isLoading = isLoading;
        
        if (elements.loadingOverlay) {
            if (isLoading) {
                elements.loadingOverlay.classList.remove('hidden');
            } else {
                elements.loadingOverlay.classList.add('hidden');
            }
        }
    }
    
    /**
     * Show error message
     * @param {string} message - The error message to display
     */
    function showError(message) {
        console.error(message);
        
        if (elements.errorText && elements.errorMessage) {
            elements.errorText.textContent = message;
            elements.errorMessage.classList.remove('hidden');
        }
    }
    
    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Return public methods
    return {
        loadCredentials,
        refreshCredential,
        notifyCredentialChange
    };
})();