import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PostPreview = () => {
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [editingContent, setEditingContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/posts', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPosts(response.data);
      } catch (err) {
        setError('Failed to fetch posts');
        console.error('Error fetching posts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  const handleEdit = (post) => {
    setSelectedPost(post);
    setEditingContent(post.content);
  };

  const handleSave = async () => {
    if (!selectedPost) return;
    
    try {
      setSaving(true);
      const token = localStorage.getItem('token');
      const response = await axios.put(
        `/api/posts/${selectedPost.id}`,
        { content: editingContent },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      setPosts(posts.map(post => 
        post.id === selectedPost.id ? response.data : post
      ));
      setSelectedPost(response.data);
    } catch (err) {
      console.error('Error saving post:', err);
      alert('Failed to save post');
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async (postId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `/api/posts/${postId}/approve`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      setPosts(posts.map(post => 
        post.id === postId ? response.data : post
      ));
      if (selectedPost?.id === postId) {
        setSelectedPost(response.data);
      }
    } catch (err) {
      console.error('Error approving post:', err);
      alert('Failed to approve post');
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Loading posts...</div>;
  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar with post list */}
      <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-medium">Posts</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {posts.map((post) => (
            <div 
              key={post.id}
              className={`p-4 cursor-pointer hover:bg-gray-50 ${selectedPost?.id === post.id ? 'bg-blue-50' : ''}`}
              onClick={() => setSelectedPost(post)}
            >
              <h3 className="font-medium">{post.title || 'Untitled Post'}</h3>
              <p className="text-sm text-gray-500 truncate">
                {post.summary || 'No summary available'}
              </p>
              <div className="mt-2 flex items-center justify-between">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  post.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                  post.status === 'pending' ? 'bg-blue-100 text-blue-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {post.status}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(post.updatedAt).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {selectedPost ? (
          <>
            <div className="p-6 border-b border-gray-200 bg-white">
              <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold">{selectedPost.title}</h1>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(selectedPost)}
                    className="px-4 py-2 border border-gray-300 text-sm rounded hover:bg-gray-50"
                  >
                    Edit
                  </button>
                  {selectedPost.status !== 'approved' && (
                    <button
                      onClick={() => handleApprove(selectedPost.id)}
                      className="px-4 py-2 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                    >
                      Approve
                    </button>
                  )}
                </div>
              </div>
              <div className="flex items-center text-sm text-gray-500 space-x-4">
                <span>Author: {selectedPost.author || 'Unknown'}</span>
                <span>•</span>
                <span>Created: {new Date(selectedPost.createdAt).toLocaleString()}</span>
                <span>•</span>
                <span>Updated: {new Date(selectedPost.updatedAt).toLocaleString()}</span>
              </div>
            </div>

            <div className="flex-1 overflow-auto p-6">
              {selectedPost.content ? (
                <div 
                  className="prose max-w-none"
                  dangerouslySetInnerHTML={{ __html: selectedPost.content }}
                />
              ) : (
                <div className="text-gray-500 italic">No content available</div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a post to view details
          </div>
        )}
      </div>

      {/* Edit Modal */}
      {selectedPost && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium">Edit Post</h3>
              <button 
                onClick={() => setSelectedPost(null)}
                className="text-gray-400 hover:text-gray-500"
              >
                <span className="sr-only">Close</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4 flex-1 overflow-auto">
              <textarea
                value={editingContent}
                onChange={(e) => setEditingContent(e.target.value)}
                className="w-full h-64 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="p-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => setSelectedPost(null)}
                className="px-4 py-2 border border-gray-300 text-sm rounded hover:bg-gray-50"
                disabled={saving}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PostPreview;
