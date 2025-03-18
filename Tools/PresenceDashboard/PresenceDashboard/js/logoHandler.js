/**
 * logoHandler.js - Handles loading and displaying the system logo
 */

// Logo handler module
const LogoHandler = (() => {
    // Logo path
    const logoPath = 'D:/2025/Projects/Presence/Presence0.1/Resources/Brand_Resources/Brand Logo/v1/Presence Logo v1.jpg';
    
    /**
     * Initialize logo functionality
     */
    function init() {
        loadLogo();
    }
    
    /**
     * Load and display the logo
     */
    function loadLogo() {
        try {
            // For Electron environment with file system access
            if (typeof require !== 'undefined') {
                const fs = require('fs');
                const path = require('path');
                
                // Check if file exists
                if (fs.existsSync(logoPath)) {
                    // Read the logo file
                    const logoData = fs.readFileSync(logoPath);
                    // Convert to base64
                    const base64Logo = Buffer.from(logoData).toString('base64');
                    // Detect mime type based on extension
                    const mimeType = 'image/jpeg';  // For .jpg files
                    // Create data URL
                    const dataUrl = `data:${mimeType};base64,${base64Logo}`;
                    
                    // Set logo in the sidebar
                    updateLogoInSidebar(dataUrl);
                } else {
                    console.error('Logo file not found at path:', logoPath);
                    // Use default logo or text as fallback
                    updateLogoInSidebar(null);
                }
            } else {
                // Fallback for non-Electron environment
                console.warn('Cannot load logo from filesystem in browser environment');
                updateLogoInSidebar(null);
            }
        } catch (error) {
            console.error('Error loading logo:', error);
            updateLogoInSidebar(null);
        }
    }
    
    /**
     * Update the logo in the sidebar
     * @param {string} logoDataUrl - Data URL of the logo
     */
    function updateLogoInSidebar(logoDataUrl) {
        const sidebarHeader = document.querySelector('.sidebar-header');
        if (!sidebarHeader) return;
        
        // Clear existing content
        sidebarHeader.innerHTML = '';
        
        if (logoDataUrl) {
            // Create logo container with link to home
            const logoLink = document.createElement('a');
            logoLink.href = '#';
            logoLink.className = 'logo-link';
            logoLink.title = 'Go to Dashboard Home';
            logoLink.setAttribute('aria-label', 'Go to Dashboard Home');
            
            // Add click event to navigate to home
            logoLink.addEventListener('click', (e) => {
                e.preventDefault();
                goToHome();
            });
            
            // Create logo container
            const logoContainer = document.createElement('div');
            logoContainer.className = 'logo-container';
            
            // Create logo image
            const logoImg = document.createElement('img');
            logoImg.src = logoDataUrl;
            logoImg.alt = 'Presence Dashboard';
            logoImg.className = 'sidebar-logo';
            
            // Add logo to container
            logoContainer.appendChild(logoImg);
            
            // Add container to link
            logoLink.appendChild(logoContainer);
            
            // Add to sidebar header
            sidebarHeader.appendChild(logoLink);
        } else {
            // Fallback to text if no logo
            const titleLink = document.createElement('a');
            titleLink.href = '#';
            titleLink.className = 'logo-link';
            
            // Add click event to navigate to home
            titleLink.addEventListener('click', (e) => {
                e.preventDefault();
                goToHome();
            });
            
            // Just use a div instead of an h1 to avoid any text rendering
            const logoPlaceholder = document.createElement('div');
            logoPlaceholder.className = 'logo-placeholder';
            
            titleLink.appendChild(logoPlaceholder);
            sidebarHeader.appendChild(titleLink);
        }
        
        // Add logo styles if not already added
        addLogoStyles();
    }
    
    /**
     * Navigate to home/welcome screen
     */
    function goToHome() {
        console.log('Navigating to dashboard home');
        
        // Get welcome and content elements
        const welcomeScreen = document.getElementById('welcome-screen');
        const channelContent = document.getElementById('channel-content');
        
        if (welcomeScreen && channelContent) {
            // Show welcome screen, hide channel content
            welcomeScreen.classList.remove('hidden');
            channelContent.classList.add('hidden');
            
            // Update page title
            document.title = 'Presence Dashboard';
            
            // Clear any active channel in sidebar
            if (typeof Sidebar !== 'undefined' && Sidebar.clearActiveChannel) {
                Sidebar.clearActiveChannel();
            }
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
    }
    
    /**
     * Add CSS styles for the logo
     */
    function addLogoStyles() {
        if (document.getElementById('logo-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'logo-styles';
        style.textContent = `
            .sidebar-header {
                padding: var(--spacing-md);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
            }
            
            .logo-link {
                display: block;
                text-decoration: none;
                color: inherit;
                transition: transform 0.2s ease;
                cursor: pointer;
            }
            
            .logo-link:hover {
                transform: scale(1.02);
            }
            
            .logo-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .sidebar-logo {
                width: 100px;
                height: 100px;
                object-fit: cover;
                border-radius: 50%;
                transition: transform 0.3s ease;
            }
            
            .logo-link:hover .sidebar-logo {
                transform: scale(1.05);
            }
        `;
        
        document.head.appendChild(style);
    }
    
    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Return public methods
    return {
        loadLogo,
        updateLogoInSidebar,
        goToHome
    };
})();