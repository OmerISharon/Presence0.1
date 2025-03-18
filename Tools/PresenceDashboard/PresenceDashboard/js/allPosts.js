/**
 * allPosts.js - Handles all posts section functionality
 * Displays and manages the complete list of posts from a channel
 */

// AllPosts module
const AllPosts = (() => {
    // DOM elements
    const elements = {
        section: document.getElementById('all-posts'),
        container: document.querySelector('.post-cards-list')
    };

    // Module state
    const state = {
        posts: [],
        sortBy: 'date', // 'date', 'views', 'likes', 'comments'
        sortDirection: 'desc', // 'asc', 'desc'
        filter: '', // Text filter
        currentPage: 1,
        postsPerPage: 10
    };

    /**
     * Initialize the module
     */
    function init() {
        // Add event listeners
        addEventListeners();
        
        // Add sorting and filtering controls
        addControls();
        
        // Add CSS for video modal if not already added by PopularPosts
        if (!document.getElementById('video-modal-styles')) {
            addVideoModalStyles();
        }
    }

    /**
     * Add event listeners
     */
    function addEventListeners() {
        // No specific events to listen for initially
    }

    /**
     * Add sorting and filtering controls to the section
     */
    function addControls() {
        if (!elements.section) return;
        
        // Create controls container
        const controls = document.createElement('div');
        controls.className = 'post-controls';
        
        // Create search filter
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search posts...';
        searchInput.className = 'search-input';
        searchInput.addEventListener('input', (e) => {
            state.filter = e.target.value;
            state.currentPage = 1; // Reset to first page when filtering
            renderPosts();
        });
        
        const searchIcon = document.createElement('i');
        searchIcon.className = 'fas fa-search search-icon';
        
        searchContainer.appendChild(searchIcon);
        searchContainer.appendChild(searchInput);
        
        // Create sort controls
        const sortContainer = document.createElement('div');
        sortContainer.className = 'sort-container';
        
        const sortLabel = document.createElement('span');
        sortLabel.className = 'sort-label';
        sortLabel.textContent = 'Sort by: ';
        
        const sortSelect = document.createElement('select');
        sortSelect.className = 'sort-select';
        
        const sortOptions = [
            { value: 'date', text: 'Date (newest)' },
            { value: 'date_asc', text: 'Date (oldest)' },
            { value: 'views', text: 'Views (highest)' },
            { value: 'views_asc', text: 'Views (lowest)' },
            { value: 'likes', text: 'Likes (highest)' },
            { value: 'likes_asc', text: 'Likes (lowest)' },
            { value: 'comments', text: 'Comments (highest)' },
            { value: 'comments_asc', text: 'Comments (lowest)' }
        ];
        
        sortOptions.forEach(option => {
            const optElement = document.createElement('option');
            optElement.value = option.value;
            optElement.textContent = option.text;
            sortSelect.appendChild(optElement);
        });
        
        sortSelect.addEventListener('change', (e) => {
            const value = e.target.value;
            
            // Extract sort field and direction
            if (value.includes('_asc')) {
                state.sortBy = value.replace('_asc', '');
                state.sortDirection = 'asc';
            } else {
                state.sortBy = value;
                state.sortDirection = 'desc';
            }
            
            renderPosts();
        });
        
        sortContainer.appendChild(sortLabel);
        sortContainer.appendChild(sortSelect);
        
        // Create posts per page control
        const paginationContainer = document.createElement('div');
        paginationContainer.className = 'pagination-container';
        
        const paginationLabel = document.createElement('span');
        paginationLabel.className = 'pagination-label';
        paginationLabel.textContent = 'Show: ';
        
        const paginationSelect = document.createElement('select');
        paginationSelect.className = 'pagination-select';
        
        [5, 10, 25, 50, 100].forEach(num => {
            const optElement = document.createElement('option');
            optElement.value = num;
            optElement.textContent = `${num} posts`;
            if (num === state.postsPerPage) {
                optElement.selected = true;
            }
            paginationSelect.appendChild(optElement);
        });
        
        paginationSelect.addEventListener('change', (e) => {
            state.postsPerPage = parseInt(e.target.value, 10);
            state.currentPage = 1; // Reset to first page when changing posts per page
            renderPosts();
        });
        
        paginationContainer.appendChild(paginationLabel);
        paginationContainer.appendChild(paginationSelect);
        
        // Assemble controls
        controls.appendChild(searchContainer);
        controls.appendChild(sortContainer);
        controls.appendChild(paginationContainer);
        
        // Add controls before the container
        elements.section.insertBefore(controls, elements.container);
        
        // Add pagination controls container
        const paginationControls = document.createElement('div');
        paginationControls.className = 'pagination-controls';
        elements.section.appendChild(paginationControls);
        
        // Add CSS for controls
        addControlStyles();
    }

    /**
     * Add CSS for controls
     */
    function addControlStyles() {
        if (document.getElementById('all-posts-controls-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'all-posts-controls-styles';
        style.textContent = `
            .post-controls {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                gap: 10px;
            }
            
            .search-container {
                position: relative;
                flex: 1;
                min-width: 200px;
            }
            
            .search-input {
                width: 100%;
                padding: 8px 8px 8px 35px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            
            .search-icon {
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                color: #777;
            }
            
            .sort-container, .pagination-container {
                display: flex;
                align-items: center;
            }
            
            .sort-label, .pagination-label {
                margin-right: 5px;
                font-size: 14px;
                color: #666;
            }
            
            .sort-select, .pagination-select {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                cursor: pointer;
            }
            
            .pagination-controls {
                display: flex;
                justify-content: center;
                margin-top: 20px;
                flex-wrap: wrap;
                gap: 5px;
            }
            
            .page-button {
                padding: 5px 10px;
                border: 1px solid #ddd;
                background-color: white;
                cursor: pointer;
                border-radius: 4px;
                font-size: 14px;
                transition: all 0.2s;
            }
            
            .page-button:hover {
                background-color: #f5f5f5;
            }
            
            .page-button.active {
                background-color: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }
            
            .page-ellipsis {
                padding: 5px 10px;
                font-size: 14px;
                color: #666;
            }
            
            .post-thumbnail {
                position: relative;
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
            
            .post-list-thumbnail:hover .play-button-overlay {
                opacity: 1;
            }
            
            .play-button-overlay i {
                font-size: 3rem;
                color: white;
                text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }
            
            @media (max-width: 768px) {
                .post-controls {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .search-container {
                    margin-bottom: 10px;
                }
                
                .sort-container, .pagination-container {
                    justify-content: space-between;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Update the all posts display
     * @param {Array} posts - Array of post objects
     */
    function updatePosts(posts) {
        if (!Array.isArray(posts)) {
            console.error('Cannot update all posts: Invalid posts data');
            return;
        }

        try {
            console.log('Updating all posts with', posts.length, 'posts');
            
            // Save to state
            state.posts = [...posts];
            state.currentPage = 1; // Reset to first page when loading new posts
            
            // Render posts
            renderPosts();
            
            // Show the section
            if (elements.section) {
                elements.section.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error updating all posts:', error);
            showError('Failed to update posts list');
        }
    }

    /**
     * Render posts based on current state
     */
    function renderPosts() {
        if (!elements.container) return;
        
        // Clear container
        elements.container.innerHTML = '';
        
        // If no posts
        if (state.posts.length === 0) {
            showEmpty();
            return;
        }
        
        // Filter posts if needed
        let filteredPosts = [...state.posts];
        if (state.filter) {
            const filter = state.filter.toLowerCase();
            filteredPosts = filteredPosts.filter(post => {
                const title = (post.Title || '').toLowerCase();
                const description = (post.Description || '').toLowerCase();
                return title.includes(filter) || description.includes(filter);
            });
            
            if (filteredPosts.length === 0) {
                showNoResults();
                return;
            }
        }
        
        // Sort posts
        sortPosts(filteredPosts);
        
        // Paginate posts
        const startIndex = (state.currentPage - 1) * state.postsPerPage;
        const endIndex = Math.min(startIndex + state.postsPerPage, filteredPosts.length);
        const paginatedPosts = filteredPosts.slice(startIndex, endIndex);
        
        // Create post cards
        paginatedPosts.forEach(post => {
            const card = createPostCard(post);
            elements.container.appendChild(card);
        });
        
        // Update pagination controls
        updatePagination(filteredPosts.length);
    }

    /**
     * Sort posts based on current sort criteria
     * @param {Array} posts - Array of posts to sort
     */
    function sortPosts(posts) {
        posts.sort((a, b) => {
            let compareValue = 0;
            
            switch (state.sortBy) {
                case 'date':
                    const dateA = new Date(a.PublishedAt || 0);
                    const dateB = new Date(b.PublishedAt || 0);
                    compareValue = dateA - dateB;
                    break;
                    
                case 'views':
                    const viewsA = parseInt(a.PostStatistics?.ViewCount || 0, 10);
                    const viewsB = parseInt(b.PostStatistics?.ViewCount || 0, 10);
                    compareValue = viewsA - viewsB;
                    break;
                    
                case 'likes':
                    const likesA = parseInt(a.PostStatistics?.LikeCount || 0, 10);
                    const likesB = parseInt(b.PostStatistics?.LikeCount || 0, 10);
                    compareValue = likesA - likesB;
                    break;
                    
                case 'comments':
                    const commentsA = parseInt(a.PostStatistics?.CommentCount || 0, 10);
                    const commentsB = parseInt(b.PostStatistics?.CommentCount || 0, 10);
                    compareValue = commentsA - commentsB;
                    break;
                    
                default:
                    // Default to date
                    const defaultDateA = new Date(a.PublishedAt || 0);
                    const defaultDateB = new Date(b.PublishedAt || 0);
                    compareValue = defaultDateA - defaultDateB;
            }
            
            // Apply sort direction
            return state.sortDirection === 'asc' ? compareValue : -compareValue;
        });
    }

    /**
     * Update pagination controls
     * @param {number} totalPosts - Total number of filtered posts
     */
    function updatePagination(totalPosts) {
        const paginationControls = elements.section.querySelector('.pagination-controls');
        if (!paginationControls) return;
        
        // Clear previous controls
        paginationControls.innerHTML = '';
        
        const totalPages = Math.ceil(totalPosts / state.postsPerPage);
        
        if (totalPages <= 1) {
            return; // No need for pagination
        }
        
        // Previous button
        const prevButton = document.createElement('button');
        prevButton.className = `page-button ${state.currentPage === 1 ? 'disabled' : ''}`;
        prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevButton.disabled = state.currentPage === 1;
        prevButton.addEventListener('click', () => {
            if (state.currentPage > 1) {
                state.currentPage--;
                renderPosts();
                scrollToTop();
            }
        });
        paginationControls.appendChild(prevButton);
        
        // Page buttons with ellipsis for large page counts
        const maxPageButtons = 5;
        let startPage = Math.max(1, state.currentPage - Math.floor(maxPageButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxPageButtons - 1);
        
        // Adjust start page if we're near the end
        if (endPage - startPage + 1 < maxPageButtons) {
            startPage = Math.max(1, endPage - maxPageButtons + 1);
        }
        
        // First page button
        if (startPage > 1) {
            const firstPageButton = document.createElement('button');
            firstPageButton.className = 'page-button';
            firstPageButton.textContent = '1';
            firstPageButton.addEventListener('click', () => {
                state.currentPage = 1;
                renderPosts();
                scrollToTop();
            });
            paginationControls.appendChild(firstPageButton);
            
            // Ellipsis after first page if needed
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'page-ellipsis';
                ellipsis.textContent = '...';
                paginationControls.appendChild(ellipsis);
            }
        }
        
        // Page buttons
        for (let i = startPage; i <= endPage; i++) {
            const pageButton = document.createElement('button');
            pageButton.className = `page-button ${i === state.currentPage ? 'active' : ''}`;
            pageButton.textContent = i.toString();
            
            if (i !== state.currentPage) {
                pageButton.addEventListener('click', () => {
                    state.currentPage = i;
                    renderPosts();
                    scrollToTop();
                });
            }
            
            paginationControls.appendChild(pageButton);
        }
        
        // Ellipsis before last page if needed
        if (endPage < totalPages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'page-ellipsis';
            ellipsis.textContent = '...';
            paginationControls.appendChild(ellipsis);
        }
        
        // Last page button
        if (endPage < totalPages) {
            const lastPageButton = document.createElement('button');
            lastPageButton.className = 'page-button';
            lastPageButton.textContent = totalPages.toString();
            lastPageButton.addEventListener('click', () => {
                state.currentPage = totalPages;
                renderPosts();
                scrollToTop();
            });
            paginationControls.appendChild(lastPageButton);
        }
        
        // Next button
        const nextButton = document.createElement('button');
        nextButton.className = `page-button ${state.currentPage === totalPages ? 'disabled' : ''}`;
        nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextButton.disabled = state.currentPage === totalPages;
        nextButton.addEventListener('click', () => {
            if (state.currentPage < totalPages) {
                state.currentPage++;
                renderPosts();
                scrollToTop();
            }
        });
        paginationControls.appendChild(nextButton);
    }

    /**
     * Scroll to the top of the posts section
     */
    function scrollToTop() {
        if (elements.section) {
            elements.section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    /**
     * Create a post card for the all posts list
     * @param {Object} post - Post data
     * @returns {HTMLElement} - The post card element
     */
    function createPostCard(post) {
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
        
        // Check if post has embed HTML
        const hasEmbed = post.Player && post.Player.EmbedHtml;
        
        // Create play button overlay for video
        const playButton = '<div class="play-button-overlay"><i class="fas fa-play-circle"></i></div>';
        
        // Create card HTML
        card.innerHTML = `
            <div class="post-list-thumbnail">
                <img src="${thumbnailUrl}" alt="${title}" loading="lazy">
                ${hasEmbed ? playButton : ''}
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
        
        // Add click handler to play the video if it has an embed
        if (hasEmbed) {
            const thumbnail = card.querySelector('.post-list-thumbnail');
            thumbnail.style.cursor = 'pointer';
            thumbnail.addEventListener('click', () => {
                openVideoPlayer(post);
            });
        }
        
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
            
            // Ensure allowfullscreen is properly set
            if (!embedHtml.includes('allowfullscreen')) {
                embedHtml = embedHtml.replace('></iframe>', ' allowfullscreen></iframe>');
            }
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
                    <p>Loading posts...</p>
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
     * Show no results state for filter
     */
    function showNoResults() {
        if (elements.container) {
            elements.container.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>No posts match your search criteria</p>
                    <button class="clear-filter-btn">Clear filter</button>
                </div>
            `;
            
            // Add event listener to clear filter button
            const clearButton = elements.container.querySelector('.clear-filter-btn');
            if (clearButton) {
                clearButton.addEventListener('click', () => {
                    const searchInput = document.querySelector('.search-input');
                    if (searchInput) {
                        searchInput.value = '';
                        state.filter = '';
                        renderPosts();
                    }
                });
            }
        }
    }

    /**
     * Show error state
     * @param {string} message - Error message
     */
    function showError(message = 'Failed to load posts') {
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
        openVideoPlayer
    };
})();