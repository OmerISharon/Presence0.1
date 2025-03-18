/**
 * sidebar.js - Handles sidebar functionality for Presence Dashboard
 * Controls channel navigation and mobile responsiveness
 */

// Sidebar module
const Sidebar = (() => {
    // DOM elements
    const elements = {
        sidebar: document.getElementById('sidebar'),
        channelList: document.getElementById('channel-list')
    };

    // State
    let state = {
        isOpen: false,
        activeChannel: null,
        channels: []
    };

    /**
     * Initialize the sidebar
     */
    function init() {
        // Check if elements are available
        if (!elements.sidebar) {
            console.error('Sidebar element not found');
            return;
        }
        
        // Add toggle button for both mobile and desktop
        createToggleButton();
        
        // Default to open on desktop, closed on mobile
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            // Start closed on mobile
            state.isOpen = false;
        } else {
            // Start open on desktop
            state.isOpen = true;
            elements.sidebar.classList.remove('closed');
        }
        
        // Add event listeners
        addEventListeners();
    }

    /**
     * Create the toggle button for mobile view
     */
    function createToggleButton() {
        // Remove any existing button first
        const existingButton = document.querySelector('.sidebar-toggle');
        if (existingButton) {
            existingButton.remove();
        }
        
        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'sidebar-toggle';
        toggleButton.innerHTML = '<i class="fas fa-bars"></i>';
        toggleButton.title = 'Toggle Menu';
        toggleButton.setAttribute('aria-label', 'Toggle Menu');
        
        // Add click event
        toggleButton.addEventListener('click', toggleSidebar);
        
        // Add to document
        document.body.appendChild(toggleButton);
    }

    /**
     * Add event listeners
     */
    function addEventListeners() {
        // Toggle button click event
        const toggleButton = document.querySelector('.sidebar-toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', toggleSidebar);
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            const isMobile = window.innerWidth <= 768;
            const isClickInside = elements.sidebar.contains(e.target);
            const isToggleButton = toggleButton && toggleButton.contains(e.target);
            
            if (isMobile && state.isOpen && !isClickInside && !isToggleButton) {
                closeSidebar();
            }
        });

        // Update on window resize
        window.addEventListener('resize', handleResize);
    }

    /**
     * Toggle sidebar open/closed state
     */
    function toggleSidebar() {
        if (state.isOpen) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    /**
     * Open the sidebar
     */
    function openSidebar() {
        elements.sidebar.classList.add('open');
        elements.sidebar.classList.remove('closed');
        
        // Remove full-width class from content
        const content = document.getElementById('content');
        if (content) {
            content.classList.remove('full-width');
        }
        
        // Add overlay for mobile
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            const overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            document.body.appendChild(overlay);
            
            // Add visible class after a small delay for smooth animation
            setTimeout(() => {
                overlay.classList.add('visible');
            }, 50);
        }
        
        // Update state
        state.isOpen = true;
        
        // No icon change - keep menu icon consistent
        const toggleButton = document.querySelector('.sidebar-toggle');
        if (toggleButton) {
            toggleButton.title = 'Toggle Menu';
        }
    }

    /**
     * Close the sidebar
     */
    function closeSidebar() {
        // For mobile, just remove the open class
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            elements.sidebar.classList.remove('open');
        } else {
            // For desktop, add the closed class
            elements.sidebar.classList.add('closed');
        }
        
        // Add full-width class to content on desktop
        const content = document.getElementById('content');
        if (content && !isMobile) {
            content.classList.add('full-width');
        }
        
        // Remove overlay
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) {
            // First remove the visible class for animation
            overlay.classList.remove('visible');
            
            // Then remove the element after animation completes
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, 300);
        }
        
        // Update state
        state.isOpen = false;
        
        // No icon change - keep menu icon consistent
        const toggleButton = document.querySelector('.sidebar-toggle');
        if (toggleButton) {
            toggleButton.title = 'Toggle Menu';
        }
    }

    /**
     * Handle window resize events
     */
    function handleResize() {
        const isMobile = window.innerWidth <= 768;
        
        // If transitioning from mobile to desktop, ensure sidebar is visible
        if (!isMobile && !state.isOpen) {
            elements.sidebar.classList.remove('open');
            
            // Remove overlay if it exists
            const overlay = document.querySelector('.sidebar-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    }

    /**
     * Load and update the channel list
     * @param {Array} channelFolders - Array of channel folder names
     */
    async function updateChannelList(channelFolders) {
        if (!Array.isArray(channelFolders) || !elements.channelList) return;
        
        try {
            console.log('Updating sidebar with channel folders:', channelFolders);
            // First, show loading state
            elements.channelList.innerHTML = '<li class="loading-item">Loading channels...</li>';
            
            // Load all channel data to get titles
            const channelDetails = [];
            for (const folderName of channelFolders) {
                try {
                    console.log(`Loading data for channel: ${folderName}`);
                    const channelData = await FileHandler.getLatestChannelData(folderName);
                    
                    // Extract channel title - handle different property name cases
                    console.log('Channel data loaded:', JSON.stringify(channelData.account, null, 2));
                    
                    let channelTitle = folderName; // Default fallback
                    
                    // Get title from account profile
                    if (channelData.account && channelData.account.accountprofile) {
                        const profile = channelData.account.accountprofile;
                        if (profile.title) {
                            channelTitle = profile.title;
                        }
                    }
                    
                    console.log(`Channel ${folderName} title: ${channelTitle}`);
                    
                    channelDetails.push({
                        folderName: folderName,
                        title: channelTitle,
                        data: channelData
                    });
                } catch (error) {
                    console.error(`Error loading data for ${folderName}:`, error);
                    // Still add the folder name as fallback
                    channelDetails.push({
                        folderName: folderName,
                        title: folderName,
                        data: null
                    });
                }
            }
            
            // Save to state
            state.channels = channelDetails;
            
            // Clear current list
            elements.channelList.innerHTML = '';
            
            if (channelDetails.length === 0) {
                elements.channelList.innerHTML = '<li class="empty-list">No channels found</li>';
                return;
            }
            
            console.log('Creating sidebar items with titles:', channelDetails.map(c => c.title));
            
            // Create channel items
            channelDetails.forEach(channel => {
                const listItem = document.createElement('li');
                const link = document.createElement('a');
                
                link.href = '#';
                link.textContent = channel.title; // Show title instead of folder name
                link.dataset.channel = channel.folderName; // Store folder name as data attribute
                
                // Add click event
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    
                    // Set active channel
                    setActiveChannel(channel.folderName);
                    
                    // Fire channel selected event with both folder name and data
                    const event = new CustomEvent('channel:selected', { 
                        detail: { 
                            folderName: channel.folderName,
                            channelData: channel.data
                        } 
                    });
                    document.dispatchEvent(event);
                    
                    // Close sidebar on mobile
                    if (window.innerWidth <= 768) {
                        closeSidebar();
                    }
                });
                
                listItem.appendChild(link);
                elements.channelList.appendChild(listItem);
            });
        } catch (error) {
            console.error('Error loading channel titles:', error);
            elements.channelList.innerHTML = '<li class="error-item">Error loading channels</li>';
        }
    }

    /**
     * Set an active channel
     * @param {string} channelName - The channel name to set as active
     */
    function setActiveChannel(channelName) {
        // Update state
        state.activeChannel = channelName;
        
        // Update active class
        const channelItems = elements.channelList.querySelectorAll('li');
        channelItems.forEach(item => {
            const link = item.querySelector('a');
            if (link && link.dataset.channel === channelName) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    /**
     * Clear the active channel (for home navigation)
     */
    function clearActiveChannel() {
        // Update state
        state.activeChannel = null;
        
        // Update active class
        const channelItems = elements.channelList.querySelectorAll('li');
        channelItems.forEach(item => {
            item.classList.remove('active');
        });
    }

    /**
     * Show loading state in the sidebar
     * @param {boolean} isLoading - Whether the sidebar is in loading state
     */
    function setLoading(isLoading) {
        if (isLoading) {
            elements.channelList.innerHTML = '<li class="loading-item">Loading channels...</li>';
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
        updateChannelList,
        setActiveChannel,
        clearActiveChannel,
        setLoading,
        openSidebar,
        closeSidebar,
        toggleSidebar
    };
})();