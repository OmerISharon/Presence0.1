/**
 * channelInfo.js - Handles channel info section functionality
 * Manages the channel profile information display
 */

// ChannelInfo module
const ChannelInfo = (() => {
    // DOM elements
    const elements = {
        channelInfoSection: document.getElementById('channel-info'),
        channelTitle: document.getElementById('channel-title'),
        channelDescription: document.getElementById('channel-description'),
        channelThumbnail: document.getElementById('channel-thumbnail'),
        channelUrl: document.getElementById('channel-url')
    };

    /**
     * Initialize the module
     */
    function init() {
        // Add event listeners
        addEventListeners();
    }

    /**
     * Add event listeners
     */
    function addEventListeners() {
        // This is now handled by main.js
    }

    /**
     * Update the channel info section
     * @param {Object} profileData - The channel profile data
     */
    function updateChannelInfo(profileData) {
        if (!profileData) {
            console.error('No profile data provided');
            return;
        }

        try {
            console.log('Updating channel info with profile data:', profileData);
            
            // Update title
            if (elements.channelTitle) {
                // Check different property names
                const title = profileData.title || profileData.Title || 'Unnamed Channel';
                elements.channelTitle.textContent = title;
                
                // Also update page title
                document.title = `${title} - Presence Dashboard`;
            }
            
            // Update description
            if (elements.channelDescription) {
                // Check different property names
                const description = profileData.Description || profileData.description || 'No description available';
                elements.channelDescription.textContent = description;
            }
            
            // Update thumbnail
            if (elements.channelThumbnail) {
                // Check different property names
                const thumbnailUrl = profileData.ThumbnailUrl || profileData.thumbnailUrl || 'img/default-channel.png';
                elements.channelThumbnail.src = thumbnailUrl;
                elements.channelThumbnail.alt = `${profileData.title || 'Channel'} thumbnail`;
                
                // Handle image load errors
                elements.channelThumbnail.onerror = function() {
                    this.src = 'img/default-channel.png';
                    this.alt = 'Default channel thumbnail';
                };
            }
            
            // Update channel URL
            if (elements.channelUrl) {
                const customUrl = profileData.CustomUrl || '';
                const fullUrl = customUrl.startsWith('http') 
                    ? customUrl 
                    : `https://www.youtube.com/${customUrl}`;
                
                console.log('Setting channel URL to:', fullUrl);
                
                elements.channelUrl.href = fullUrl;
                elements.channelUrl.textContent = 'Visit Channel on YouTube';
                elements.channelUrl.setAttribute('target', '_blank');
                elements.channelUrl.setAttribute('rel', 'noopener noreferrer');
                // Add attribute for Electron to identify external links
                elements.channelUrl.setAttribute('data-external-link', 'true');
            }
            
            // Show the channel info section
            if (elements.channelInfoSection) {
                elements.channelInfoSection.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error updating channel info:', error);
        }
    }

    /**
     * Show channel info loading state
     */
    function showLoading() {
        if (elements.channelInfoSection) {
            elements.channelInfoSection.innerHTML = `
                <h2>Channel Info</h2>
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p>Loading channel information...</p>
                </div>
            `;
        }
    }

    /**
     * Show error state
     * @param {string} message - Error message to display
     */
    function showError(message = 'Failed to load channel information') {
        if (elements.channelInfoSection) {
            elements.channelInfoSection.innerHTML = `
                <h2>Channel Info</h2>
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    /**
     * Clear all channel info
     */
    function clearInfo() {
        if (elements.channelTitle) {
            elements.channelTitle.textContent = '';
        }
        
        if (elements.channelDescription) {
            elements.channelDescription.textContent = '';
        }
        
        if (elements.channelThumbnail) {
            elements.channelThumbnail.src = '';
            elements.channelThumbnail.alt = '';
        }
        
        if (elements.channelUrl) {
            elements.channelUrl.href = '#';
            elements.channelUrl.textContent = 'Visit Channel';
        }
        
        if (elements.channelInfoSection) {
            elements.channelInfoSection.classList.add('hidden');
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
        updateChannelInfo,
        showLoading,
        showError,
        clearInfo
    };
})();