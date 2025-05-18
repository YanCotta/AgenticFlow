import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalEmails: 0,
    pendingReplies: 0,
    approvedPosts: 0,
    newsletterSubscribers: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/dashboard/metrics', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setMetrics(response.data);
      } catch (err) {
        setError('Failed to fetch dashboard metrics');
        console.error('Error fetching metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) return <div className="flex justify-center items-center h-64">Loading...</div>;
  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Emails"
          value={metrics.totalEmails}
          icon="📧"
          color="blue"
        />
        <MetricCard
          title="Pending Replies"
          value={metrics.pendingReplies}
          icon="⏳"
          color="yellow"
        />
        <MetricCard
          title="Approved Posts"
          value={metrics.approvedPosts}
          icon="✅"
          color="green"
        />
        <MetricCard
          title="Subscribers"
          value={metrics.newsletterSubscribers}
          icon="👥"
          color="purple"
        />
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    green: 'bg-green-100 text-green-800',
    purple: 'bg-purple-100 text-purple-800',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
        </div>
        <span className={`text-3xl p-3 rounded-full ${colorClasses[color]}`}>
          {icon}
        </span>
      </div>
    </div>
  );
};

export default Dashboard;
