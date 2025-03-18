/**
 * channelRenderer.js - Handles rendering channel data in the UI
 * Responsible for populating all sections of the channel page
 */

// ChannelRenderer module
const ChannelRenderer = (() => {
    // DOM element references
    const elements = {
        channelTitle: document.getElementById('channel-title'),
        channelDescription: document.getElementById('channel-description'),
        channelThumbnail: document.getElementById('channel-thumbnail'),
        channelUrl: document.getElementById('channel-url'),
        globalStatistics: document.querySelector('.statistics-grid'),
        popularPosts: document.querySelector('.post-cards-row'),
        allPosts: document.querySelector('.post-cards-list')
    };
    
    /**
     * Render all channel data
     * @param {Object} channelData - The channel data to render
     */
    function renderChannel(channelData) {
        if (!channelData || !channelData.account) {
            console.error('Invalid channel data:', channelData);
            return;
        }
        
        try {
            // Render each section
            renderChannelInfo(channelData.account.accountprofile);
            renderGlobalStatistics(channelData.account.AccountStatistics);
            renderPopularPosts(channelData.posts);
            renderAllPosts(channelData.posts);
            
            // Set page title
            document.title = `${channelData.account.accountprofile.title} - Presence Dashboard`;
        } catch (error) {
            console.error('Error rendering channel data:', error);
        }
    }
    
    /**
     * Render the channel info section
     * @param {Object} profile - The channel profile data
     */
    function renderChannelInfo(profile) {
        if (!profile) return;
        
        // Set channel title
        if (elements.channelTitle) {
            elements.channelTitle.textContent = profile.title || 'Unnamed Channel';
        }
        
        // Set channel description
        if (elements.channelDescription) {
            elements.channelDescription.textContent = profile.Description || 'No description available';
        }
        
        // Set channel thumbnail
        if (elements.channelThumbnail) {
            elements.channelThumbnail.src = profile.ThumbnailUrl || 'img/default-channel.png';
            elements.channelThumbnail.alt = `${profile.title} thumbnail`;
        }
        
        // Set channel URL
        if (elements.channelUrl) {
            const customUrl = profile.CustomUrl || '';
            elements.channelUrl.href = customUrl.startsWith('http') 
                ? customUrl 
                : `https://www.youtube.com/${customUrl}`;
            elements.channelUrl.textContent = 'Visit Channel on YouTube';
        }
    }
    
    /**
     * Render the global statistics section
     * @param {Object} statistics - The channel statistics
     */
    function renderGlobalStatistics(statistics) {
        if (!statistics || !elements.globalStatistics) return;
        
        elements.globalStatistics.innerHTML = '';
        
        // Define statistics to display
        const statsToShow = [
            { key: 'ViewCount', label: 'Total Views', icon: 'fa-eye' },
            { key: 'SubscriberCount', label: 'Subscribers', icon: 'fa-users' },
            { key: 'VideoCount', label: 'Videos', icon: 'fa-video' },
            { key: 'CommentCount', label: 'Comments', icon: 'fa-comment' }
        ];
        
        // Create statistic cards
        statsToShow.forEach(stat => {
            if (stat.key === 'HiddenSubscriberCount') return; // Skip as per requirements
            
            const value = statistics[stat.key];
            if (value !== undefined) {
                const formattedValue = formatNumber(value);
                
                const statCard = document.createElement('div');
                statCard.className = 'stat-card';
                
                statCard.innerHTML = `
                    <div class="stat-icon">
                        <i class="fas ${stat.icon}"></i>
                    </div>
                    <div class="stat-value">${formattedValue}</div>
                    <div class="stat-label">${stat.label}</div>
                `;
                
                elements.globalStatistics.appendChild(statCard);
            }
        });
    }
    
    /**
     * Render the most popular posts section
     * @param {Array} posts - The array of posts
     */
    function renderPopularPosts(posts) {
        if (!Array.isArray(posts) || !elements.popularPosts) return;
        
        elements.popularPosts.innerHTML = '';
        
        // Sort posts by view count (descending)
        const sortedPosts = [...posts].sort((a, b) => {
            const aViews = a.PostStatistics?.ViewCount || 0;
            const bViews = b.PostStatistics?.ViewCount || 0;
            return bViews - aViews;
        });
        
        // Take the top 5 posts
        const topPosts = sortedPosts.slice(0, 5);
        
        // Create post cards
        topPosts.forEach(post => {
            const postCard = document.createElement('div');
            postCard.className = 'post-card-popular';
            
            const viewCount = formatNumber(post.PostStatistics?.ViewCount || 0);
            const likeCount = formatNumber(post.PostStatistics?.LikeCount || 0);
            const dislikeCount = formatNumber(post.PostStatistics?.DislikeCount || 0);
            const commentCount = formatNumber(post.PostStatistics?.CommentCount || 0);
            
            postCard.innerHTML = `
                <div class="post-thumbnail">
                    <img src="${post.ThumbnailUrl || 'img/default-thumbnail.png'}" alt="${post.Title || 'Video thumbnail'}">
                    <div class="post-meta">
                        <span><i class="fas fa-eye"></i> ${viewCount}</span>
                        <span><i class="fas fa-calendar"></i> ${formatDate(post.PublishedAt)}</span>
                    </div>
                </div>
                <div class="post-content">
                    <h3 class="post-title">${post.Title || 'Untitled Video'}</h3>
                    <div class="post-stats">
                        <div class="post-stat"><i class="fas fa-thumbs-up"></i> ${likeCount}</div>
                        <div class="post-stat"><i class="fas fa-thumbs-down"></i> ${dislikeCount}</div>
                        <div class="post-stat"><i class="fas fa-comment"></i> ${commentCount}</div>
                    </div>
                </div>
            `;
            
            elements.popularPosts.appendChild(postCard);
        });
    }
    
    /**
     * Render the all posts section
     * @param {Array} posts - The array of posts
     */
    function renderAllPosts(posts) {
        if (!Array.isArray(posts) || !elements.allPosts) return;
        
        elements.allPosts.innerHTML = '';
        
        // Sort posts by published date (newest first)
        const sortedPosts = [...posts].sort((a, b) => {
            const aDate = new Date(a.PublishedAt || 0);
            const bDate = new Date(b.PublishedAt || 0);
            return bDate - aDate;
        });
        
        // Create post cards
        sortedPosts.forEach(post => {
            const postCard = document.createElement('div');
            postCard.className = 'post-card-list';
            
            const viewCount = formatNumber(post.PostStatistics?.ViewCount || 0);
            const likeCount = formatNumber(post.PostStatistics?.LikeCount || 0);
            const dislikeCount = formatNumber(post.PostStatistics?.DislikeCount || 0);
            const commentCount = formatNumber(post.PostStatistics?.CommentCount || 0);
            
            // Process the embed HTML to make it minimized
            let embedHtml = post.Player?.EmbedHtml || '';
            if (embedHtml) {
                // Parse the iframe src
                const srcMatch = embedHtml.match(/src="([^"]+)"/);
                if (srcMatch && srcMatch[1]) {
                    const src = srcMatch[1];
                    embedHtml = `<iframe class="post-list-iframe" src="${src}" frameborder="0" allowfullscreen></iframe>`;
                }
            }
            
            postCard.innerHTML = `
                <div class="post-list-thumbnail">
                    <img src="${post.ThumbnailUrl || 'img/default-thumbnail.png'}" alt="${post.Title || 'Video thumbnail'}">
                    ${embedHtml}
                </div>
                <div class="post-list-content">
                    <h3 class="post-list-title">${post.Title || 'Untitled Video'}</h3>
                    <p class="post-list-description">${post.Description || 'No description available'}</p>
                    <div class="post-list-meta">
                        <div class="post-list-date">
                            <i class="fas fa-calendar"></i> ${formatDate(post.PublishedAt)}
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
            
            elements.allPosts.appendChild(postCard);
        });
    }
    
    /**
     * Format a number for display (e.g. 1000 -> 1K)
     * @param {number} num - The number to format
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
    
    // Return public methods
    return {
        renderChannel
    };
})();