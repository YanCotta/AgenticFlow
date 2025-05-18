import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ReplyReview = () => {
  const [replies, setReplies] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editedContent, setEditedContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchPendingReplies = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/replies/pending', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setReplies(response.data);
      } catch (err) {
        setError('Failed to fetch pending replies');
        console.error('Error fetching replies:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPendingReplies();
  }, []);

  const handleEdit = (reply) => {
    setEditingId(reply.id);
    setEditedContent(reply.content);
  };

  const handleSave = async (replyId) => {
    try {
      setSaving(true);
      const token = localStorage.getItem('token');
      await axios.put(
        `/api/replies/${replyId}`,
        { content: editedContent },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      setReplies(replies.map(reply => 
        reply.id === replyId ? { ...reply, content: editedContent } : reply
      ));
      setEditingId(null);
    } catch (err) {
      console.error('Error saving reply:', err);
      alert('Failed to save reply');
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async (replyId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `/api/replies/${replyId}/approve`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      setReplies(replies.filter(reply => reply.id !== replyId));
    } catch (err) {
      console.error('Error approving reply:', err);
      alert('Failed to approve reply');
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Loading pending replies...</div>;
  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Review Replies</h1>
      
      {replies.length === 0 ? (
        <div className="text-center py-10 text-gray-500">
          No pending replies to review
        </div>
      ) : (
        <div className="space-y-6">
          {replies.map((reply) => (
            <div key={reply.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-medium text-lg">Reply to: {reply.recipient}</h3>
                  <p className="text-sm text-gray-500">Regarding: {reply.subject}</p>
                </div>
                <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">
                  Pending Review
                </span>
              </div>
              
              {editingId === reply.id ? (
                <div className="mb-4">
                  <textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="w-full h-40 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              ) : (
                <div className="prose max-w-none mb-4 p-3 bg-gray-50 rounded-lg">
                  {reply.content}
                </div>
              )}
              
              <div className="flex justify-end space-x-3">
                {editingId === reply.id ? (
                  <>
                    <button
                      onClick={() => setEditingId(null)}
                      className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                      disabled={saving}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleSave(reply.id)}
                      className="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
                      disabled={saving}
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => handleEdit(reply)}
                      className="px-4 py-2 border border-gray-300 text-sm rounded hover:bg-gray-50"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleApprove(reply.id)}
                      className="px-4 py-2 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                    >
                      Approve & Send
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReplyReview;
