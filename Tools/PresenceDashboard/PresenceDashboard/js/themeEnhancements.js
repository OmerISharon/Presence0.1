/**
 * themeEnhancements.js - Additional style enhancements for the purple theme
 */

// Add additional styling for the purple theme
(function enhanceTheme() {
    // Create style element
    const style = document.createElement('style');
    style.id = 'theme-enhancements';
    
    // Add custom CSS
    style.textContent = `
        /* Add a subtle gradient background to the main content */
        .content {
            background: linear-gradient(135deg, var(--background-color) 0%, #FFF 100%);
        }
        
        /* Enhance cards with purple accents */
        section {
            border-top: 3px solid var(--primary-color);
        }
        
        /* Add subtle purple glow to hover states */
        .card:hover, .post-card-popular:hover, .post-card-list:hover {
            box-shadow: 0 5px 20px rgba(138, 79, 255, 0.15);
        }
        
        /* Enhance buttons */
        .btn, button:not(.page-button):not(.video-modal-close):not(.scroll-btn) {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
            transition: all 0.3s ease;
        }
        
        .btn:hover, button:not(.page-button):not(.video-modal-close):not(.scroll-btn):hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(138, 79, 255, 0.3);
        }
        
        /* Add purple accent to active navigation */
        .page-button.active {
            background: var(--primary-color);
            box-shadow: 0 2px 5px rgba(138, 79, 255, 0.3);
        }
        
        /* Enhance scroll bars with purple accents */
        ::-webkit-scrollbar {
            width: 10px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c7b8ff;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }
        
        /* Enhanced statistics cards */
        .stat-card {
            border-radius: 12px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            opacity: 0.8;
        }
        
        .stat-icon {
            color: var(--primary-color);
        }
        
        /* Enhance Welcome Screen */
        .welcome-screen .welcome-icon {
            color: var(--primary-color);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.05);
                opacity: 0.8;
            }
            100% {
                transform: scale(1);
                opacity: 1;
            }
        }
    `;
    
    // Add style to document
    document.head.appendChild(style);
    
    console.log('Theme enhancements applied');
})();