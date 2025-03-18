/**
 * postCards.js - Handles creation and interaction of post cards
 * Provides functions for creating and managing post card UI elements
 */

// PostCards module
const PostCards = (() => {
    /**
     * Create a popular post card element
     * @param {Object} post - Post data
     * @returns {HTMLElement} - Card element
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
        
        // Create HTML structure
        card.innerHTML = `
            <div class="post-thumbnail">
                <img src="${thumbnailUrl}" alt="${title}" loading="lazy">
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
        
        // Add click event to open the video
        card.addEventListener('click', () => {
            if (post.Player && post.Player.EmbedHtml) {
                openVideoPlayer(post);
            }
        });
        
        return card;
    }
    
    /**
     * Create a post card for the all posts list
     * @param {Object} post - Post data
     * @returns {HTMLElement} - Card element
     */
    function createPostListCard(post) {
        if (!post) return null;
        
        const card = document.createElement('div');
        card.className = 'post-card-list';
        
        // Extract post data with fallbacks
        const title = post.Title || 'Untitled Video';
        const description = post.Description || 'No description available';
        const thumbnailUrl = post.ThumbnailUrl || 'img/default-thumbnail.png';
        const publishedDate = formatDate(post.PublishedAt);
        
        // Extract statistics with fallbacks
        const stats = post.PostStatistics || {};
        const viewCount = formatNumber(stats.ViewCount || 0);
        const likeCount = formatNumber(stats.LikeCount || 0);
        const dislikeCount = formatNumber(stats.DislikeCount || 0);
        const commentCount = formatNumber(stats.CommentCount || 0);
        
        // Process embed HTML
        let embedHtml = '';
        if (post.Player && post.Player.EmbedHtml) {
            const srcMatch = post.Player.EmbedHtml.match(/src="([^"]+)"/);
            if (srcMatch && srcMatch[1]) {
                const src = srcMatch[1];
                embedHtml = `<iframe class="post-list-iframe" src="${src}" frameborder="0" allowfullscreen></iframe>`;
            }
        }
        
        // Create HTML structure
        card.innerHTML = `
            <div class="post-list-thumbnail">
                <img src="${thumbnailUrl}" alt="${title}" loading="lazy">
                ${embedHtml}
            </div>
            <div class="post-list-content">
                <h3 class="post-list-title">${title}</h3>
                <p class="post-list-description">${description}</p>
                <div class="post-list-meta">
                    <div class="post-list-date">
                        <i class="fas fa-calendar"></i> ${publishedDate}
                    </div>
                    <div class="post-list-stats">
                        <span><i class="fas fa-eye"></i> ${viewCount}</span>
                        <span><i class="fas fa-thumbs-up"></i> ${likeCount}</span>
                        <span><i class="fas fa-thumbs-down"></i> ${dislikeCount}</span>
                        <span><i class="fas fa-comment"></i> ${commentCount}</span>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }
    
    /**
     * Create a video modal and open it
     * @param {Object} post - Post data
     */
    function openVideoPlayer(post) {
        if (!post.Player || !post.Player.EmbedHtml) return;
        
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
        videoContainer.innerHTML = post.Player.EmbedHtml;
        
        // Create video info
        const videoInfo = document.createElement('div');
        videoInfo.className = 'video-info';
        videoInfo.innerHTML = `
            <h3>${post.Title || 'Untitled Video'}</h3>
            <p>${post.Description || 'No description available'}</p>
        `;
        
        // Assemble modal
        modalContent.appendChild(closeButton);
        modalContent.appendChild(videoContainer);
        modalContent.appendChild(videoInfo);
        modal.appendChild(modalContent);
        
        // Add to body and prevent scrolling
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden';
        
        // Add click outside to close
        modal.addEventListener('click', e => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                document.body.style.overflow = '';
            }
        });
    }
    
    /**
     * Format a number for display (e.g. 1000 -> 1K)
     * @param {number|string} num - The number to format
     * @returns {string} Formatted number string
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
     * Format a date string
     * @param {string} dateString - The ISO date string
     * @returns {string} Formatted date string
     */
    function formatDate(dateString) {
        if (!dateString) return 'Unknown date';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (error) {
            console.error('Error formatting date:', error);
            return 'Invalid date';
        }
    }
    
    /**
     * Populate popular posts section
     * @param {Array} posts - Array of post data
     * @param {HTMLElement} container - Container element
     */
    function populatePopularPosts(posts, container) {
        if (!Array.isArray(posts) || !container) return;
        
        // Clear container
        container.innerHTML = '';
        
        // Sort posts by view count
        const sortedPosts = [...posts].sort((a, b) => {
            const aViews = a.PostStatistics?.ViewCount || 0;
            const bViews = b.PostStatistics?.ViewCount || 0;
            return bViews - aViews;
        });
        
        // Take top 5 posts
        const topPosts = sortedPosts.slice(0, 5);
        
        // Create and append cards
        topPosts.forEach(post => {
            const card = createPopularPostCard(post);
            if (card) {
                container.appendChild(card);
            }
        });
    }
    
    /**
     * Populate all posts section
     * @param {Array} posts - Array of post data
     * @param {HTMLElement} container - Container element
     */
    function populateAllPosts(posts, container) {
        if (!Array.isArray(posts) || !container) return;
        
        // Clear container
        container.innerHTML = '';
        
        // Sort posts by date (newest first)
        const sortedPosts = [...posts].sort((a, b) => {
            const aDate = new Date(a.PublishedAt || 0);
            const bDate = new Date(b.PublishedAt || 0);
            return bDate - aDate;
        });
        
        // Create and append cards
        sortedPosts.forEach(post => {
            const card = createPostListCard(post);
            if (card) {
                container.appendChild(card);
            }
        });
    }
    
    // Add necessary CSS for video modal
    function addModalStyles() {
        const style = document.createElement('style');
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
            }
            
            .video-modal-close {
                position: absolute;
                top: 10px;
                right: 10px;
                font-size: 24px;
                background: none;
                border: none;
                cursor: pointer;
                z-index: 10;
            }
            
            .video-container {
                position: relative;
                padding-bottom: 56.25%;
                height: 0;
                overflow: hidden;
            }
            
            .video-container iframe {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }
            
            .video-info {
                padding: 15px;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Initialize the module
    function init() {
        addModalStyles();
    }
    
    // Call init on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Return public methods
    return {
        createPopularPostCard,
        createPostListCard,
        populatePopularPosts,
        populateAllPosts,
        openVideoPlayer
    };
})();