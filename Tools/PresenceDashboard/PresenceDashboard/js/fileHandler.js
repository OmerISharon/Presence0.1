/**
 * fileHandler.js - Handles file system operations for the Presence Dashboard
 * Responsible for reading directory structures and loading JSON files
 */

// FileHandler module - Uses direct Node.js file system access
const FileHandler = (() => {
    // Base path to the JSON files directory
    const basePath = 'D:/2025/Projects/Presence/Presence0.1/Tools/PresenceDashboard/Resources/output_data_json_files/YoutubeDashboardData/';
    
    // Require Node.js modules
    const fs = require('fs');
    const path = require('path');
    
    /**
     * Get all channel folders from the base directory
     * @returns {Promise<Array>} Array of channel folder names
     */
    async function getChannelFolders() {
        try {
            console.log('Reading directory:', basePath);
            
            // Read directory synchronously
            const files = fs.readdirSync(basePath, { withFileTypes: true });
            
            // Filter only directories
            const folders = files
                .filter(file => file.isDirectory())
                .map(dir => dir.name);
                
            console.log('Found folders:', folders);
            return folders;
        } catch (error) {
            console.error('Error fetching channel folders:', error);
            throw error;
        }
    }
    
    /**
     * Get the latest JSON file for a specific channel
     * @param {string} channelName - The channel folder name
     * @returns {Promise<Object>} The parsed JSON data
     */
    async function getLatestChannelData(channelName) {
        try {
            const channelPath = path.join(basePath, channelName);
            console.log('Reading channel directory:', channelPath);
            
            // Get all files in the channel directory
            const files = fs.readdirSync(channelPath);
            
            // Filter only JSON files
            const jsonFiles = files.filter(file => file.endsWith('.json'));
            
            if (jsonFiles.length === 0) {
                throw new Error(`No JSON files found for channel ${channelName}`);
            }
            
            console.log(`Found ${jsonFiles.length} JSON files for ${channelName}`);
            
            // Get file stats for each JSON file
            const fileStats = jsonFiles.map(file => {
                const filePath = path.join(channelPath, file);
                const stats = fs.statSync(filePath);
                return { file, mtime: stats.mtime };
            });
            
            // Sort by modification time (newest first)
            fileStats.sort((a, b) => b.mtime - a.mtime);
            
            // Get the latest file
            const latestFile = fileStats[0].file;
            const latestFilePath = path.join(channelPath, latestFile);
            
            console.log(`Loading latest file: ${latestFilePath}`);
            
            // Read and parse the JSON file
            const fileContent = fs.readFileSync(latestFilePath, 'utf8');
            const jsonData = JSON.parse(fileContent);
            
            // Transform data to match our component expectations
            // This normalizes the property naming (changing Account to account, etc)
            return normalizeData(jsonData);
        } catch (error) {
            console.error(`Error fetching latest data for channel ${channelName}:`, error);
            throw error;
        }
    }
    
    /**
     * Normalize the JSON data to have consistent property names
     * @param {Object} data - The original JSON data
     * @returns {Object} - Normalized data
     */
    function normalizeData(data) {
        // Create a standardized structure
        const normalized = {
            account: {
                accountprofile: {},
                AccountStatistics: {}
            },
            posts: []
        };
        
        // Map Account data with case-insensitive property access
        if (data.Account || data.account) {
            const account = data.Account || data.account;
            
            // Handle AccountProfile
            if (account.AccountProfile || account.accountprofile) {
                const profile = account.AccountProfile || account.accountprofile;
                
                normalized.account.accountprofile = {
                    title: profile.Title || profile.title || '',
                    Description: profile.Description || profile.description || '',
                    ThumbnailUrl: profile.ThumbnailUrl || profile.thumbnailUrl || '',
                    CustomUrl: profile.CustomUrl || profile.customUrl || '',
                    PublishedAt: profile.PublishedAt || profile.publishedAt || '',
                    LocalizedInfo: profile.LocalizedInfo || profile.localizedInfo || {}
                };
            }
            
            // Handle AccountStatistics
            if (account.AccountStatistics || account.accountStatistics) {
                const stats = account.AccountStatistics || account.accountStatistics;
                
                normalized.account.AccountStatistics = {
                    ViewCount: stats.ViewCount || stats.viewCount || 0,
                    SubscriberCount: stats.SubscriberCount || stats.subscriberCount || 0,
                    HiddenSubscriberCount: stats.HiddenSubscriberCount || stats.hiddenSubscriberCount || false,
                    VideoCount: stats.VideoCount || stats.videoCount || 0
                };
            }
        }
        
        // Handle Posts
        if (data.Posts || data.posts) {
            const posts = data.Posts || data.posts;
            
            normalized.posts = posts.map(post => {
                const normalizedPost = {};
                
                // Handle PostProfile
                if (post.PostProfile || post.postProfile) {
                    const profile = post.PostProfile || post.postProfile;
                    normalizedPost.Title = profile.Title || profile.title || '';
                    normalizedPost.Description = profile.Description || profile.description || '';
                    normalizedPost.PublishedAt = profile.PublishedAt || profile.publishedAt || '';
                    normalizedPost.ThumbnailUrl = profile.ThumbnailUrl || profile.thumbnailUrl || '';
                }
                
                // Handle PostStatistics
                if (post.PostStatistics || post.postStatistics) {
                    const stats = post.PostStatistics || post.postStatistics;
                    normalizedPost.PostStatistics = {
                        ViewCount: stats.ViewCount || stats.viewCount || 0,
                        LikeCount: stats.LikeCount || stats.likeCount || 0,
                        DislikeCount: stats.DislikeCount || stats.dislikeCount || 0,
                        CommentCount: stats.CommentCount || stats.commentCount || 0
                    };
                }
                
                // Handle Player
                if (post.Player || post.player) {
                    const player = post.Player || post.player;
                    normalizedPost.Player = {
                        EmbedHtml: player.EmbedHtml || player.embedHtml || ''
                    };
                }
                
                return normalizedPost;
            });
        }
        
        // For debugging
        console.log('Normalized data structure:', 
            JSON.stringify({
                accountprofile: normalized.account.accountprofile,
                stats: normalized.account.AccountStatistics,
                postsCount: normalized.posts.length
            }, null, 2)
        );
        
        return normalized;
    }
    
    // Return public methods
    return {
        getChannelFolders,
        getLatestChannelData
    };
})();