import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmailSummaries = () => {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const limit = 10;

  useEffect(() => {
    const fetchSummaries = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get(`/api/emails/summaries?page=${page}&limit=${limit}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        setSummaries(prev => [...prev, ...response.data.summaries]);
        setHasMore(response.data.hasMore);
      } catch (err) {
        setError('Failed to fetch email summaries');
        console.error('Error fetching summaries:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSummaries();
  }, [page]);

  const loadMore = () => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
    }
  };

  if (loading && summaries.length === 0) {
    return <div className="flex justify-center items-center h-64">Loading email summaries...</div>;
  }

  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Email Summaries</h1>
      <div className="space-y-4">
        {summaries.map((summary) => (
          <div key={summary.id} className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium text-lg">{summary.subject}</h3>
                <p className="text-gray-600 text-sm">From: {summary.sender}</p>
                <p className="text-gray-600 text-sm">Date: {new Date(summary.date).toLocaleString()}</p>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full ${
                summary.status === 'processed' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {summary.status}
              </span>
            </div>
            <p className="mt-2 text-gray-700">{summary.summary}</p>
            <div className="mt-3 flex space-x-2">
              <button className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600">
                View Details
              </button>
              {summary.status === 'pending' && (
                <button className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600">
                  Process
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      {hasMore && (
        <div className="mt-6 text-center">
          <button
            onClick={loadMore}
            disabled={loading}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}
    </div>
  );
};

export default EmailSummaries;
