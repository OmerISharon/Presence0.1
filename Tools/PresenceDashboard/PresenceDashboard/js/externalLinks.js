/**
 * externalLinks.js - Ensures external links open in the default browser
 * Works in both Electron and web environments
 */

// Handle external links to open in default browser
(function initExternalLinks() {
    // Check if we're in an Electron environment
    const isElectron = window && window.process && window.process.type;
    
    // Setup handler function
    function handleExternalLink(event) {
        const target = event.target.closest('a');
        if (!target) return;
        
        const url = target.getAttribute('href');
        if (!url) return;
        
        // Skip if it's not an external link
        if (url.startsWith('#') || url === 'javascript:void(0)') {
            return;
        }
        
        // External urls start with http:// or https:// or have target="_blank"
        const isExternal = url.startsWith('http') || 
                           url.startsWith('https') || 
                           target.getAttribute('target') === '_blank' ||
                           target.getAttribute('data-external-link') === 'true';
        
        if (isExternal) {
            console.log('Opening external link:', url);
            
            if (isElectron) {
                // In Electron, we'll let main.js handle this with shell.openExternal
                // This is just additional protection
                if (window.electron && window.electron.shell) {
                    event.preventDefault();
                    window.electron.shell.openExternal(url);
                }
            } else {
                // In a regular browser, open in a new tab/window
                target.setAttribute('target', '_blank');
                target.setAttribute('rel', 'noopener noreferrer');
            }
        }
    }

    // Add event listener for all link clicks
    document.addEventListener('click', handleExternalLink);
    
    console.log('External links handler initialized');
})();