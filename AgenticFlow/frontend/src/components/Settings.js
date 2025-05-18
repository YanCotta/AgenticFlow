import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Settings = () => {
  const [prompts, setPrompts] = useState({
    summaryPrompt: '',
    replyPrompt: '',
    newsletterPrompt: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/settings/prompts', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPrompts(response.data);
      } catch (err) {
        setError('Failed to load prompts');
        console.error('Error fetching prompts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPrompts();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPrompts(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      const token = localStorage.getItem('token');
      await axios.post(
        '/api/settings/prompts',
        prompts,
        {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      setSuccess('Settings saved successfully!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error saving prompts:', err);
      setError('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="flex justify-center items-center h-64">Loading settings...</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      
      {error && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
          <p>{error}</p>
        </div>
      )}
      
      {success && (
        <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 text-green-700">
          <p>{success}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">AI Prompts</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Customize the prompts used for generating content
            </p>
          </div>
          
          <div className="px-4 py-5 sm:p-6 space-y-6">
            <div>
              <label htmlFor="summaryPrompt" className="block text-sm font-medium text-gray-700">
                Email Summary Prompt
              </label>
              <div className="mt-1">
                <textarea
                  id="summaryPrompt"
                  name="summaryPrompt"
                  rows={4}
                  value={prompts.summaryPrompt}
                  onChange={handleChange}
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border border-gray-300 rounded-md"
                  placeholder="Enter prompt for generating email summaries..."
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                This prompt will be used to generate summaries of incoming emails.
              </p>
            </div>
            
            <div>
              <label htmlFor="replyPrompt" className="block text-sm font-medium text-gray-700">
                Reply Generation Prompt
              </label>
              <div className="mt-1">
                <textarea
                  id="replyPrompt"
                  name="replyPrompt"
                  rows={4}
                  value={prompts.replyPrompt}
                  onChange={handleChange}
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border border-gray-300 rounded-md"
                  placeholder="Enter prompt for generating email replies..."
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                This prompt will be used to generate email replies.
              </p>
            </div>
            
            <div>
              <label htmlFor="newsletterPrompt" className="block text-sm font-medium text-gray-700">
                Newsletter Generation Prompt
              </label>
              <div className="mt-1">
                <textarea
                  id="newsletterPrompt"
                  name="newsletterPrompt"
                  rows={4}
                  value={prompts.newsletterPrompt}
                  onChange={handleChange}
                  className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border border-gray-300 rounded-md"
                  placeholder="Enter prompt for generating newsletter content..."
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                This prompt will be used to generate newsletter content from approved posts.
              </p>
            </div>
          </div>
          
          <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
        
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">API Configuration</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Configure API keys and endpoints
            </p>
          </div>
          
          <div className="px-4 py-5 sm:p-6">
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700">
                OpenAI API Key
              </label>
              <div className="mt-1 flex rounded-md shadow-sm">
                <input
                  type="password"
                  name="apiKey"
                  id="apiKey"
                  className="focus:ring-blue-500 focus:border-blue-500 flex-1 block w-full rounded-none rounded-l-md sm:text-sm border-gray-300"
                  placeholder="sk-..."
                />
                <button
                  type="button"
                  className="inline-flex items-center px-3 rounded-r-md border border-l-0 border-gray-300 bg-gray-50 text-gray-500 text-sm"
                >
                  Update
                </button>
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Your API key is stored securely and never shared.
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Danger Zone</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Irreversible and destructive actions
            </p>
          </div>
          
          <div className="px-4 py-5 sm:p-6">
            <div className="flex justify-between items-center">
              <div>
                <h4 className="text-md font-medium text-gray-900">Reset All Data</h4>
                <p className="text-sm text-gray-500">
                  This will delete all your data and cannot be undone.
                </p>
              </div>
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                onClick={() => {
                  if (window.confirm('Are you sure you want to reset all data? This cannot be undone.')) {
                    // Handle reset
                  }
                }}
              >
                Reset Data
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Settings;
