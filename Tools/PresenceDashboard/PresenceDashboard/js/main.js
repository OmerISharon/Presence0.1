/**
 * main.js - Main JavaScript file for Presence Dashboard
 * Handles initialization and core functionality
 */

// Global state
const state = {
    channels: [],
    currentChannel: null,
    basePath: 'D:/2025/Projects/Presence/Presence0.1/Tools/PresenceDashboard/Resources/output_data_json_files/YoutubeDashboardData/'
};

// DOM elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    channelList: document.getElementById('channel-list'),
    content: document.getElementById('content'),
    welcomeScreen: document.getElementById('welcome-screen'),
    channelContent: document.getElementById('channel-content'),
    loadingOverlay: document.getElementById('loading-overlay'),
    errorMessage: document.getElementById('error-message'),
    errorText: document.getElementById('error-text'),
    errorClose: document.getElementById('error-close')
};

/**
 * Show or hide the loading overlay
 * @param {boolean} show - Whether to show or hide
 */
function showLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.remove('hidden');
    } else {
        elements.loadingOverlay.classList.add('hidden');
    }
}

/**
 * Show error message
 * @param {string} message - The error message to display
 */
function showError(message) {
    console.error('ERROR:', message);
    elements.errorText.textContent = message;
    elements.errorMessage.classList.remove('hidden');
}

/**
 * Load a channel with already fetched data
 * @param {string} channelName - The channel folder name
 * @param {Object} channelData - The channel data
 */
function loadChannelWithData(channelName, channelData) {
    try {
        // Set current channel in state
        state.currentChannel = {
            name: channelName,
            data: channelData
        };
        
        // Store in window for global access
        window.currentChannelData = channelData;
        
        // Mark current channel as active in sidebar
        if (typeof Sidebar !== 'undefined' && Sidebar.setActiveChannel) {
            Sidebar.setActiveChannel(channelName);
        }
        
        // Hide welcome screen and show channel content
        elements.welcomeScreen.classList.add('hidden');
        elements.channelContent.classList.remove('hidden');
        
        console.log('Rendering channel data:', channelName);
        
        // Render channel data using separate components
        if (typeof ChannelInfo !== 'undefined' && ChannelInfo.updateChannelInfo) {
            ChannelInfo.updateChannelInfo(channelData.account.accountprofile);
        }
        
        if (typeof GlobalStats !== 'undefined' && GlobalStats.updateStats) {
            GlobalStats.updateStats(channelData.account.AccountStatistics);
        }
        
        if (typeof PopularPosts !== 'undefined' && PopularPosts.updatePosts) {
            PopularPosts.updatePosts(channelData.posts);
        }
        
        if (typeof AllPosts !== 'undefined' && AllPosts.updatePosts) {
            AllPosts.updatePosts(channelData.posts);
        }
        
        // Scroll to top
        window.scrollTo(0, 0);
    } catch (error) {
        console.error(`Error processing channel data for ${channelName}:`, error);
        showError(`Failed to process channel data for "${channelName}": ${error.message}`);
    }
}

/**
 * Load a specific channel's data
 * @param {string} channelName - The channel folder name
 */
async function loadChannel(channelName) {
    try {
        // Show loading overlay
        showLoading(true);
        
        console.log('Loading channel data for:', channelName);
        
        // Get the latest JSON file for the channel
        const channelData = await FileHandler.getLatestChannelData(channelName);
        
        // Process and display the channel data
        loadChannelWithData(channelName, channelData);
        
        // Hide loading overlay
        showLoading(false);
    } catch (error) {
        console.error(`Error loading channel ${channelName}:`, error);
        showError(`Failed to load channel "${channelName}": ${error.message}`);
        showLoading(false);
    }
}

/**
 * Load the channel list from the file system
 */
async function loadChannelList() {
    try {
        console.log('Loading channel folders...');
        
        // Get channel folders
        const channels = await FileHandler.getChannelFolders();
        state.channels = channels;
        
        console.log('Channel folders loaded:', channels);
        
        // Check if Sidebar module is available before using it
        if (typeof Sidebar !== 'undefined' && Sidebar.updateChannelList) {
            // Update the sidebar menu with folder names first
            // Sidebar module will handle loading channel titles
            await Sidebar.updateChannelList(channels);
        } else {
            console.error('Sidebar module is not available');
            showError('Failed to initialize the dashboard: Sidebar module is not available');
        }
        
        // If no channels found
        if (channels.length === 0) {
            showError('No channel folders found. Please check the base directory path.');
        }
    } catch (error) {
        console.error('Error loading channel list:', error);
        showError('Failed to load channel list: ' + error.message);
        throw error;
    }
}

/**
 * Initialize event listeners
 */
function initEventListeners() {
    // Error close button
    if (elements.errorClose) {
        elements.errorClose.addEventListener('click', () => {
            elements.errorMessage.classList.add('hidden');
        });
    }
    
    // Listen for channel selection
    document.addEventListener('channel:selected', async (event) => {
        const { folderName, channelData } = event.detail;
        
        if (channelData) {
            // We already have the data from the sidebar's preload
            console.log('Channel selected with preloaded data:', folderName);
            loadChannelWithData(folderName, channelData);
        } else {
            // We need to load the data
            console.log('Channel selected, loading data:', folderName);
            await loadChannel(folderName);
        }
    });
}

/**
 * Initialize the application
 */
async function init() {
    try {
        console.log('Initializing dashboard...');
        
        // Show loading overlay
        showLoading(true);
        
        // Initialize event listeners
        initEventListeners();
        
        // Wait a moment to ensure all modules are loaded
        setTimeout(async () => {
            try {
                // Load channel list
                await loadChannelList();
                
                // Hide loading overlay
                showLoading(false);
            } catch (error) {
                console.error('Error during delayed initialization:', error);
                showError('Failed to initialize the dashboard: ' + error.message);
                showLoading(false);
            }
        }, 1000); // 1 second delay to ensure all scripts are loaded
        
    } catch (error) {
        console.error('Initialization error:', error);
        showError('Failed to initialize the dashboard: ' + error.message);
        showLoading(false);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);