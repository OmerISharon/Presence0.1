/**
 * statistics.js - Handles advanced statistics processing for the dashboard
 * Calculates metrics and provides data for visualizations
 */

// Statistics module
const Statistics = (() => {
    /**
     * Calculate engagement metrics for a channel
     * @param {Object} channelData - The channel data
     * @returns {Object} Engagement metrics
     */
    function calculateEngagementMetrics(channelData) {
        if (!channelData || !Array.isArray(channelData.posts) || channelData.posts.length === 0) {
            return {
                averageLikes: 0,
                averageComments: 0,
                averageViews: 0,
                engagementRate: 0,
                likeToViewRatio: 0,
                commentToViewRatio: 0
            };
        }
        
        // Get total metrics
        let totalLikes = 0;
        let totalDislikes = 0;
        let totalComments = 0;
        let totalViews = 0;
        let validPostCount = 0;
        
        channelData.posts.forEach(post => {
            if (post.PostStatistics) {
                const stats = post.PostStatistics;
                
                const likes = parseInt(stats.LikeCount || 0, 10);
                const dislikes = parseInt(stats.DislikeCount || 0, 10);
                const comments = parseInt(stats.CommentCount || 0, 10);
                const views = parseInt(stats.ViewCount || 0, 10);
                
                if (!isNaN(likes)) totalLikes += likes;
                if (!isNaN(dislikes)) totalDislikes += dislikes;
                if (!isNaN(comments)) totalComments += comments;
                if (!isNaN(views)) totalViews += views;
                
                validPostCount++;
            }
        });
        
        // Calculate averages
        const averageLikes = validPostCount > 0 ? totalLikes / validPostCount : 0;
        const averageDislikes = validPostCount > 0 ? totalDislikes / validPostCount : 0;
        const averageComments = validPostCount > 0 ? totalComments / validPostCount : 0;
        const averageViews = validPostCount > 0 ? totalViews / validPostCount : 0;
        
        // Calculate ratios
        const likeToViewRatio = averageViews > 0 ? (averageLikes / averageViews) * 100 : 0;
        const commentToViewRatio = averageViews > 0 ? (averageComments / averageViews) * 100 : 0;
        
        // Calculate overall engagement rate (likes + dislikes + comments) / views
        const engagementRate = averageViews > 0 
            ? ((averageLikes + averageDislikes + averageComments) / averageViews) * 100 
            : 0;
        
        return {
            averageLikes: parseFloat(averageLikes.toFixed(2)),
            averageDislikes: parseFloat(averageDislikes.toFixed(2)),
            averageComments: parseFloat(averageComments.toFixed(2)),
            averageViews: parseFloat(averageViews.toFixed(2)),
            engagementRate: parseFloat(engagementRate.toFixed(2)),
            likeToViewRatio: parseFloat(likeToViewRatio.toFixed(2)),
            commentToViewRatio: parseFloat(commentToViewRatio.toFixed(2)),
            totalPosts: validPostCount
        };
    }
    
    /**
     * Get posting frequency metrics
     * @param {Object} channelData - The channel data
     * @returns {Object} Posting frequency metrics
     */
    function getPostingFrequency(channelData) {
        if (!channelData || !Array.isArray(channelData.posts) || channelData.posts.length < 2) {
            return {
                averageDaysBetweenPosts: 0,
                postsPerMonth: 0,
                mostActiveMonth: null,
                leastActiveMonth: null
            };
        }
        
        // Get all valid dates
        const dates = channelData.posts
            .map(post => post.PublishedAt)
            .filter(date => !!date)
            .map(date => new Date(date))
            .filter(date => !isNaN(date.getTime()))
            .sort((a, b) => a.getTime() - b.getTime());
        
        if (dates.length < 2) {
            return {
                averageDaysBetweenPosts: 0,
                postsPerMonth: 0,
                mostActiveMonth: null,
                leastActiveMonth: null
            };
        }
        
        // Calculate average days between posts
        let totalDaysBetween = 0;
        for (let i = 1; i < dates.length; i++) {
            const diffTime = Math.abs(dates[i].getTime() - dates[i-1].getTime());
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            totalDaysBetween += diffDays;
        }
        
        const averageDaysBetweenPosts = totalDaysBetween / (dates.length - 1);
        
        // Group posts by month
        const postsByMonth = {};
        channelData.posts.forEach(post => {
            if (post.PublishedAt) {
                const date = new Date(post.PublishedAt);
                if (!isNaN(date.getTime())) {
                    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                    if (!postsByMonth[monthKey]) {
                        postsByMonth[monthKey] = 0;
                    }
                    postsByMonth[monthKey]++;
                }
            }
        });
        
        // Get most and least active months
        let mostActiveMonth = null;
        let mostActivePosts = 0;
        let leastActiveMonth = null;
        let leastActivePosts = Infinity;
        
        for (const [month, count] of Object.entries(postsByMonth)) {
            if (count > mostActivePosts) {
                mostActiveMonth = month;
                mostActivePosts = count;
            }
            if (count < leastActivePosts) {
                leastActiveMonth = month;
                leastActivePosts = count;
            }
        }
        
        // Format month names
        function formatMonthYear(monthStr) {
            if (!monthStr) return null;
            
            const [year, month] = monthStr.split('-');
            const date = new Date(parseInt(year, 10), parseInt(month, 10) - 1, 1);
            
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long'
            });
        }
        
        // Calculate posts per month
        const totalMonths = Object.keys(postsByMonth).length;
        const postsPerMonth = totalMonths > 0 
            ? channelData.posts.length / totalMonths 
            : 0;
        
        return {
            averageDaysBetweenPosts: parseFloat(averageDaysBetweenPosts.toFixed(1)),
            postsPerMonth: parseFloat(postsPerMonth.toFixed(1)),
            mostActiveMonth: formatMonthYear(mostActiveMonth),
            mostActivePosts,
            leastActiveMonth: formatMonthYear(leastActiveMonth),
            leastActivePosts: leastActivePosts === Infinity ? 0 : leastActivePosts
        };
    }
    
    /**
     * Calculate performance metrics for individual posts
     * @param {Object} channelData - The channel data
     * @returns {Array} Array of post performance metrics
     */
    function getPostPerformanceMetrics(channelData) {
        if (!channelData || !Array.isArray(channelData.posts)) {
            return [];
        }
        
        return channelData.posts.map(post => {
            const stats = post.PostStatistics || {};
            
            const views = parseInt(stats.ViewCount || 0, 10);
            const likes = parseInt(stats.LikeCount || 0, 10);
            const dislikes = parseInt(stats.DislikeCount || 0, 10);
            const comments = parseInt(stats.CommentCount || 0, 10);
            
            // Calculate engagement rate
            const engagementRate = views > 0 
                ? ((likes + dislikes + comments) / views) * 100 
                : 0;
            
            // Calculate like-to-dislike ratio
            const likeToDislikeRatio = dislikes > 0 
                ? likes / dislikes 
                : likes > 0 ? likes : 0;
            
            return {
                title: post.Title || 'Untitled',
                publishedAt: post.PublishedAt,
                views,
                likes,
                dislikes,
                comments,
                engagementRate: parseFloat(engagementRate.toFixed(2)),
                likeToDislikeRatio: parseFloat(likeToDislikeRatio.toFixed(2))
            };
        });
    }
    
    /**
     * Get performance trends over time
     * @param {Object} channelData - The channel data
     * @returns {Object} Performance trends data
     */
    function getPerformanceTrends(channelData) {
        if (!channelData || !Array.isArray(channelData.posts) || channelData.posts.length === 0) {
            return {
                viewsTrend: [],
                likesTrend: [],
                commentsTrend: []
            };
        }
        
        // Sort posts by date
        const sortedPosts = [...channelData.posts]
            .filter(post => post.PublishedAt)
            .sort((a, b) => {
                const dateA = new Date(a.PublishedAt);
                const dateB = new Date(b.PublishedAt);
                return dateA.getTime() - dateB.getTime();
            });
        
        if (sortedPosts.length === 0) {
            return {
                viewsTrend: [],
                likesTrend: [],
                commentsTrend: []
            };
        }
        
        // Create trend data
        const viewsTrend = sortedPosts.map(post => ({
            date: new Date(post.PublishedAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            }),
            title: post.Title || 'Untitled',
            value: parseInt(post.PostStatistics?.ViewCount || 0, 10)
        }));
        
        const likesTrend = sortedPosts.map(post => ({
            date: new Date(post.PublishedAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            }),
            title: post.Title || 'Untitled',
            value: parseInt(post.PostStatistics?.LikeCount || 0, 10)
        }));
        
        const commentsTrend = sortedPosts.map(post => ({
            date: new Date(post.PublishedAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            }),
            title: post.Title || 'Untitled',
            value: parseInt(post.PostStatistics?.CommentCount || 0, 10)
        }));
        
        return {
            viewsTrend,
            likesTrend,
            commentsTrend
        };
    }
    
    // Return public methods
    return {
        calculateEngagementMetrics,
        getPostingFrequency,
        getPostPerformanceMetrics,
        getPerformanceTrends
    };
})();