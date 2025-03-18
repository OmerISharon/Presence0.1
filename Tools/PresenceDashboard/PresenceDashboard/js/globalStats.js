/**
 * globalStats.js - Handles global statistics section functionality
 * Creates and manages statistical display for channel data
 */

// GlobalStats module
const GlobalStats = (() => {
    // DOM elements
    const elements = {
        statsSection: document.getElementById('global-statistics'),
        statsGrid: document.querySelector('.statistics-grid')
    };

    // Icons for different stats
    const statIcons = {
        ViewCount: 'fa-eye',
        TotalViews: 'fa-eye',
        SubscriberCount: 'fa-users',
        VideoCount: 'fa-video',
        CommentCount: 'fa-comment',
        LikeCount: 'fa-thumbs-up',
        DislikeCount: 'fa-thumbs-down',
        EngagementRate: 'fa-chart-line',
        AverageViews: 'fa-chart-bar',
        AvgCommentCount: 'fa-comments'
    };

    // Labels for different stats
    const statLabels = {
        ViewCount: 'Total Views',
        TotalViews: 'Total Views',
        SubscriberCount: 'Subscribers',
        VideoCount: 'Videos',
        CommentCount: 'Comments',
        LikeCount: 'Total Likes',
        DislikeCount: 'Total Dislikes',
        EngagementRate: 'Engagement Rate',
        AverageViews: 'Avg. Views Per Video',
        AvgCommentCount: 'Avg. Comments Per Video'
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
     * Update the global statistics section
     * @param {Object} statistics - The channel statistics data
     * @param {Object} [additionalStats] - Additional calculated statistics
     */
    function updateStats(statistics, additionalStats = {}) {
        if (!statistics) {
            console.error('Cannot update stats: Missing statistics data');
            return;
        }

        try {
            console.log('Updating global statistics:', statistics);
            
            if (!elements.statsGrid) {
                console.error('Statistics grid element not found');
                return;
            }
            
            // Clear existing stats
            elements.statsGrid.innerHTML = '';

            // Merge standard and additional stats
            const allStats = { ...statistics, ...additionalStats };

            // Define which stats to display and in what order
            const statsToShow = [
                'TotalViews', 
                'SubscriberCount', 
                'VideoCount',
                'CommentCount'
            ];
            
            // Calculate total views from posts
            if (Array.isArray(window.currentChannelData?.posts)) {
                let totalViews = 0;
                window.currentChannelData.posts.forEach(post => {
                    if (post.PostStatistics && post.PostStatistics.ViewCount) {
                        const views = parseInt(post.PostStatistics.ViewCount, 10);
                        if (!isNaN(views)) {
                            totalViews += views;
                        }
                    }
                });
                allStats.TotalViews = totalViews;
            }

            // Add additional stats if available in the data
            if (statistics.LikeCount !== undefined) {
                statsToShow.push('LikeCount');
            }
            
            if (statistics.DislikeCount !== undefined) {
                statsToShow.push('DislikeCount');
            }

            // Add advanced stats if available
            if (additionalStats.AverageViews) {
                statsToShow.push('AverageViews');
            }
            
            if (additionalStats.EngagementRate) {
                statsToShow.push('EngagementRate');
            }

            // Create stat cards for each statistic
            statsToShow.forEach(statKey => {
                if (statKey === 'HiddenSubscriberCount') return; // Skip as per requirements
                
                // Check if the stat exists
                if (allStats[statKey] !== undefined) {
                    const statCard = createStatCard(statKey, allStats[statKey]);
                    elements.statsGrid.appendChild(statCard);
                }
            });

            // Show the section
            if (elements.statsSection) {
                elements.statsSection.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error updating global statistics:', error);
            showError('Failed to update statistics: ' + error.message);
        }
    }

    /**
     * Create a statistical card element
     * @param {string} statKey - The key for the statistic
     * @param {number|string} value - The value of the statistic
     * @returns {HTMLElement} - The stat card element
     */
    function createStatCard(statKey, value) {
        const card = document.createElement('div');
        card.className = 'stat-card';
        card.dataset.stat = statKey;

        // Get icon and label for the stat
        const icon = statIcons[statKey] || 'fa-chart-bar';
        const label = statLabels[statKey] || statKey;

        // Format the value
        const formattedValue = formatStatValue(statKey, value);

        // Create card content
        card.innerHTML = `
            <div class="stat-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="stat-value">${formattedValue}</div>
            <div class="stat-label">${label}</div>
        `;

        return card;
    }

    /**
     * Format a stat value based on its type
     * @param {string} statKey - The key for the statistic
     * @param {number|string} value - The value to format
     * @returns {string} - Formatted value
     */
    function formatStatValue(statKey, value) {
        // Handle null or undefined
        if (value === null || value === undefined) return '0';
        
        // Convert to number if it's a string
        let numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        // Return original value if it's not a number
        if (isNaN(numValue)) return value;
        
        // Format based on stat type
        switch (statKey) {
            case 'EngagementRate':
                return numValue.toFixed(2) + '%';
                
            case 'ViewCount':
            case 'SubscriberCount':
            case 'LikeCount':
            case 'DislikeCount':
            case 'CommentCount':
                return formatLargeNumber(numValue);
                
            case 'AverageViews':
            case 'AvgCommentCount':
                return formatLargeNumber(numValue);
                
            default:
                return String(value);
        }
    }

    /**
     * Format large numbers (e.g., 1000 -> 1K)
     * @param {number} num - The number to format
     * @returns {string} - Formatted number
     */
    function formatLargeNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    /**
     * Show loading state
     */
    function showLoading() {
        if (elements.statsGrid) {
            elements.statsGrid.innerHTML = `
                <div class="loading-stats">
                    <div class="spinner"></div>
                    <p>Loading statistics...</p>
                </div>
            `;
        }
    }

    /**
     * Show error state
     * @param {string} message - Error message to display
     */
    function showError(message = 'Failed to load statistics') {
        if (elements.statsGrid) {
            elements.statsGrid.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${message}</p>
                </div>
            `;
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
        updateStats,
        showLoading,
        showError
    };
})();