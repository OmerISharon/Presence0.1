/**
 * popularPosts.js - Handles popular posts section functionality
 * Displays and manages the most popular posts from a channel
 */

// PopularPosts module
const PopularPosts = (() => {
    // DOM elements
    const elements = {
        section: document.getElementById('popular-posts'),
        container: document.querySelector('.post-cards-row')
    };

    // Module state
    const state = {
        posts: [],
        maxPosts: 5  // Number of popular posts to display
    };

    /**
     * Initialize the module
     */
    function init() {
        // Add event listeners
        addEventListeners();
        
        // Check if we need horizontal scroll buttons
        checkForScrollButtons();
        
        // Add CSS for video modal
        addVideoModalStyles();
    }

    /**
     * Add event listeners
     */
    function addEventListeners() {
        // Listen for window resize to check for scroll buttons
        window.addEventListener('resize', checkForScrollButtons);
    }

    /**
     * Update the popular posts display
     * @param {Array} posts - Array of post objects
     */
    function updatePosts(posts) {
        if (!Array.isArray(posts) || !elements.container) {
            console.error('Cannot update popular posts: Invalid posts data or missing DOM elements');
            return;
        }

        try {
            console.log('Updating popular posts with', posts.length, 'posts');
            
            // Save to state
            state.posts = [...posts];
            
            // Clear container
            elements.container.innerHTML = '';
            
            // If no posts
            if (posts.length === 0) {
                showEmpty();
                return;
            }

            // Sort posts by view count (highest first)
            const sortedPosts = [...posts].sort((a, b) => {
                const aViews = parseInt(a.PostStatistics?.ViewCount || 0, 10);
                const bViews = parseInt(b.PostStatistics?.ViewCount || 0, 10);
                return bViews - aViews;
            });
            
            // Take only the top posts
            const topPosts = sortedPosts.slice(0, state.maxPosts);
            
            console.log('Top posts by views:', topPosts.map(p => ({ 
                title: p.Title, 
                views: p.PostStatistics?.ViewCount 
            })));
            
            // Create post cards for each popular post
            topPosts.forEach(post => {
                const card = createPopularPostCard(post);
                elements.container.appendChild(card);
            });
            
            // Add scroll buttons if needed
            checkForScrollButtons();
            
            // Show the section
            if (elements.section) {
                elements.section.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error updating popular posts:', error);
            showError('Failed to update popular posts');
        }
    }

    /**
     * Create a popular post card
     * @param {Object} post - Post data
     * @returns {HTMLElement} - The post card element
     */
    function createPopularPostCard(post) {
        if (!post) return null;
        
        const card = document.createElement('div');
        card.className = 'post-card-popular';
        
        // Extract post data with fallbacks
        const title = post.Title || 'Untitled Video';
        const thumbnailUrl = post.ThumbnailUrl || 'img/default-thumbnail.png';
        const publishedDate = formatDate(post.PublishedAt);
        
        // Extract statistics with fallbacks
        const stats = post.PostStatistics || {};
        const viewCount = formatNumber(stats.ViewCount || 0);
        const likeCount = formatNumber(stats.LikeCount || 0);
        const dislikeCount = formatNumber(stats.DislikeCount || 0);
        const commentCount = formatNumber(stats.CommentCount || 0);
        
        // Create a play button overlay
        const playButton = '<div class="play-button-overlay"><i class="fas fa-play-circle"></i></div>';
        
        // Create card HTML
        card.innerHTML = `
            <div class="post-thumbnail">
                <img src="${thumbnailUrl}" alt="${title}" loading="lazy">
                ${playButton}
                <div class="post-meta">
                    <span><i class="fas fa-eye"></i> ${viewCount}</span>
                    <span><i class="fas fa-calendar"></i> ${publishedDate}</span>
                </div>
            </div>
            <div class="post-content">
                <h3 class="post-title">${title}</h3>
                <div class="post-stats">
                    <div class="post-stat"><i class="fas fa-thumbs-up"></i> ${likeCount}</div>
                    <div class="post-stat"><i class="fas fa-thumbs-down"></i> ${dislikeCount}</div>
                    <div class="post-stat"><i class="fas fa-comment"></i> ${commentCount}</div>
                </div>
            </div>
        `;
        
        // Add click handler to play the video
        card.addEventListener('click', () => {
            if (post.Player && post.Player.EmbedHtml) {
                openVideoPlayer(post);
            }
        });
        
        return card;
    }

    /**
     * Open a video player modal
     * @param {Object} post - Post data containing embed HTML
     */
    function openVideoPlayer(post) {
        if (!post.Player || !post.Player.EmbedHtml) return;
        
        console.log('Opening video player with embed HTML:', post.Player.EmbedHtml);
        
        // Create modal container
        const modal = document.createElement('div');
        modal.className = 'video-modal';
        
        // Create modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'video-modal-content';
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = 'video-modal-close';
        closeButton.innerHTML = '&times;';
        closeButton.addEventListener('click', () => {
            document.body.removeChild(modal);
            document.body.style.overflow = '';
        });
        
        // Create video container
        const videoContainer = document.createElement('div');
        videoContainer.className = 'video-container';
        
        // Ensure the iframe has proper attributes for security and display
        let embedHtml = post.Player.EmbedHtml;
        
        // Fix common issues with embed code
        if (embedHtml) {
            // Make sure src URLs are properly formed (some might have // instead of https://)
            embedHtml = embedHtml.replace('src="//www.youtube.com', 'src="https://www.youtube.com');
            
            // Make sure width and height are set to 100% for responsive display
            embedHtml = embedHtml.replace(/width="[^"]*"/, 'width="100%"');
            embedHtml = embedHtml.replace(/height="[^"]*"/, 'height="100%"');
        }
        
        videoContainer.innerHTML = embedHtml;
        
        // Create info container
        const infoContainer = document.createElement('div');
        infoContainer.className = 'video-info';
        infoContainer.innerHTML = `
            <h3>${post.Title || 'Untitled Video'}</h3>
            <p>${post.Description || 'No description available'}</p>
        `;
        
        // Assemble modal
        modalContent.appendChild(closeButton);
        modalContent.appendChild(videoContainer);
        modalContent.appendChild(infoContainer);
        modal.appendChild(modalContent);
        
        // Add to document
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
        
        // Close when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                document.body.style.overflow = '';
            }
        });
    }

    /**
     * Check if scroll buttons are needed and add them
     */
    function checkForScrollButtons() {
        if (!elements.container) return;
        
        // Remove existing buttons
        const existingButtons = document.querySelectorAll('.scroll-btn');
        existingButtons.forEach(btn => btn.remove());
        
        // Check if scrolling is needed
        const needsScroll = elements.container.scrollWidth > elements.container.clientWidth;
        
        if (needsScroll && elements.section) {
            // Create left scroll button
            const leftBtn = document.createElement('button');
            leftBtn.className = 'scroll-btn scroll-left';
            leftBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
            leftBtn.addEventListener('click', () => {
                elements.container.scrollBy({ left: -300, behavior: 'smooth' });
            });
            
            // Create right scroll button
            const rightBtn = document.createElement('button');
            rightBtn.className = 'scroll-btn scroll-right';
            rightBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
            rightBtn.addEventListener('click', () => {
                elements.container.scrollBy({ left: 300, behavior: 'smooth' });
            });
            
            // Add buttons to the section
            elements.section.appendChild(leftBtn);
            elements.section.appendChild(rightBtn);
            
            // Add CSS for buttons if it doesn't exist
            addScrollButtonStyles();
        }
    }

    /**
     * Add CSS for scroll buttons
     */
    function addScrollButtonStyles() {
        if (document.getElementById('scroll-btn-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'scroll-btn-styles';
        style.textContent = `
            .scroll-btn {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: rgba(0, 0, 0, 0.5);
                color: white;
                border: none;
                cursor: pointer;
                z-index: 10;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0.7;
                transition: opacity 0.3s;
            }
            
            .scroll-btn:hover {
                opacity: 1;
            }
            
            .scroll-left {
                left: 10px;
            }
            
            .scroll-right {
                right: 10px;
            }
            
            #popular-posts {
                position: relative;
            }
            
            .post-cards-row {
                scroll-behavior: smooth;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: thin;
            }
            
            .post-cards-row::-webkit-scrollbar {
                height: 6px;
            }
            
            .post-cards-row::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 10px;
            }
            
            .post-cards-row::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 10px;
            }
            
            .post-cards-row::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            
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
            }
            
            .post-thumbnail:hover .play-button-overlay {
                opacity: 1;
            }
            
            .play-button-overlay i {
                font-size: 3rem;
                color: white;
                text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Add CSS for video modal
     */
    function addVideoModalStyles() {
        if (document.getElementById('video-modal-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'video-modal-styles';
        style.textContent = `
            .video-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            
            .video-modal-content {
                background: white;
                border-radius: 8px;
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow-y: auto;
                position: relative;
                display: flex;
                flex-direction: column;
            }
            
            .video-modal-close {
                position: absolute;
                top: 10px;
                right: 10px;
                font-size: 24px;
                background: rgba(0, 0, 0, 0.5);
                color: white;
                border: none;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                cursor: pointer;
                z-index: 10;
                display: flex;
                align-items: center;
                justify-content: center;
                line-height: 0;
            }
            
            .video-container {
                position: relative;
                padding-bottom: 56.25%;
                height: 0;
                overflow: hidden;
                background: #000;
            }
            
            .video-container iframe {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border: none;
            }
            
            .video-info {
                padding: 15px;
            }
            
            .video-info h3 {
                margin-top: 0;
                margin-bottom: 10px;
            }
            
            .video-info p {
                margin: 0;
                color: #666;
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Format a number (e.g., 1000 -> 1K)
     * @param {number|string} num - Number to format
     * @returns {string} - Formatted number
     */
    function formatNumber(num) {
        if (num === undefined || num === null) return '0';
        
        // Convert to number if it's a string
        num = typeof num === 'string' ? parseInt(num, 10) : num;
        
        if (isNaN(num)) return '0';
        
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    /**
     * Format a date
     * @param {string} dateStr - Date string
     * @returns {string} - Formatted date
     */
    function formatDate(dateStr) {
        if (!dateStr) return 'Unknown date';
        
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            return 'Invalid date';
        }
    }

    /**
     * Show loading state
     */
    function showLoading() {
        if (elements.container) {
            elements.container.innerHTML = `
                <div class="loading-posts">
                    <div class="spinner"></div>
                    <p>Loading popular posts...</p>
                </div>
            `;
        }
    }

    /**
     * Show empty state
     */
    function showEmpty() {
        if (elements.container) {
            elements.container.innerHTML = `
                <div class="empty-posts">
                    <i class="fas fa-file-video"></i>
                    <p>No posts found for this channel</p>
                </div>
            `;
        }
    }

    /**
     * Show error state
     * @param {string} message - Error message
     */
    function showError(message = 'Failed to load popular posts') {
        if (elements.container) {
            elements.container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${message}</p>
                </div>
            `;
        }
    }

    /**
     * Clear all posts
     */
    function clearPosts() {
        if (elements.container) {
            elements.container.innerHTML = '';
        }
        
        if (elements.section) {
            elements.section.classList.add('hidden');
        }
    }

    /**
     * Set maximum number of posts to display
     * @param {number} max - Maximum number of posts
     */
    function setMaxPosts(max) {
        if (typeof max === 'number' && max > 0) {
            state.maxPosts = max;
            
            // Refresh display if we have posts
            if (state.posts.length > 0) {
                updatePosts(state.posts);
            }
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
        updatePosts,
        showLoading,
        showEmpty,
        showError,
        clearPosts,
        setMaxPosts,
        openVideoPlayer
    };
})();