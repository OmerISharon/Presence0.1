/**
 * videoModalStyles.js - Adds required styles for video modals
 * This ensures the video modal displays correctly across browsers
 */

// Add video modal styles to document
function addVideoModalStyles() {
    if (document.getElementById('enhanced-video-modal-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'enhanced-video-modal-styles';
    style.textContent = `
        /* Modal container */
        .video-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.85);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        /* Modal content */
        .video-modal-content {
            background: white;
            border-radius: 8px;
            width: 90%;
            max-width: 900px;
            height: 90%;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }
        
        /* Close button */
        .video-modal-close {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 30px;
            height: 30px;
            font-size: 24px;
            background: rgba(0, 0, 0, 0.5);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
        }
        
        .video-modal-close:hover {
            background: rgba(0, 0, 0, 0.8);
        }
        
        /* Video container */
        .video-container {
            flex: 1;
            position: relative;
            background: black;
            min-height: 0;
        }
        
        .video-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100% !important;
            height: 100% !important;
            border: none;
        }
        
        /* Video info */
        .video-info {
            padding: 15px;
            background: white;
            overflow-y: auto;
            max-height: 30%;
        }
        
        .video-info h3 {
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .video-info p {
            margin: 0;
            color: #666;
            font-size: 14px;
        }
        
        /* Play button overlay */
        .play-button-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(0, 0, 0, 0.3);
            opacity: 0;
            transition: opacity 0.3s;
            cursor: pointer;
        }
        
        .post-thumbnail:hover .play-button-overlay,
        .post-list-thumbnail:hover .play-button-overlay {
            opacity: 1;
        }
        
        .play-button-overlay i {
            font-size: 4rem;
            color: white;
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        
        /* Media queries for responsive design */
        @media (max-width: 768px) {
            .video-modal-content {
                width: 95%;
                height: 80%;
            }
            
            .play-button-overlay i {
                font-size: 3rem;
            }
        }
    `;
    
    document.head.appendChild(style);
    
    console.log('Enhanced video modal styles applied');
}

// Execute immediately
addVideoModalStyles();

// Export the function for reuse
if (typeof module !== 'undefined') {
    module.exports = {
        addVideoModalStyles
    };
}