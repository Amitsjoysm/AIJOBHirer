import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { Send, Sparkles, MessageSquare, Trash2, Plus } from 'lucide-react';
import { toast } from 'sonner';

const ChatPage = () => {
  const { API_URL, getAuthHeaders, user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchSessions();
    // Start with a welcome message
    setMessages([
      {
        role: 'assistant',
        content: "👋 Hello! I'm your AI hiring assistant. I can help you with creating jobs, reviewing applications, scheduling interviews, and analyzing your hiring metrics. What would you like to do today?",
        timestamp: new Date().toISOString()
      }
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSessions = async () => {
    try {
      const response = await axios.get(`${API_URL}/chat/sessions`, {
        headers: getAuthHeaders()
      });
      setSessions(response.data);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    }
  };

  const loadSession = async (sid) => {
    try {
      const response = await axios.get(`${API_URL}/chat/history/${sid}`, {
        headers: getAuthHeaders()
      });
      setMessages(response.data);
      setSessionId(sid);
    } catch (error) {
      console.error('Failed to load session:', error);
      toast.error('Failed to load conversation');
    }
  };

  const startNewSession = () => {
    setSessionId(null);
    setMessages([
      {
        role: 'assistant',
        content: "👋 Hello! I'm your AI hiring assistant. How can I help you today?",
        timestamp: new Date().toISOString()
      }
    ]);
  };

  const deleteSession = async (sid) => {
    try {
      await axios.delete(`${API_URL}/chat/sessions/${sid}`, {
        headers: getAuthHeaders()
      });
      toast.success('Conversation deleted');
      fetchSessions();
      if (sessionId === sid) {
        startNewSession();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      toast.error('Failed to delete conversation');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_URL}/chat/`,
        {
          message: userMessage.content,
          session_id: sessionId
        },
        { headers: getAuthHeaders() }
      );

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        action_taken: response.data.action_taken,
        data: response.data.data,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSessionId(response.data.session_id);
      
      // Refresh sessions list
      fetchSessions();
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const quickActions = [
    { label: 'Create a job posting', icon: '📝' },
    { label: 'Review recent applications', icon: '👥' },
    { label: 'Schedule interviews', icon: '📅' },
    { label: 'Show hiring analytics', icon: '📊' }
  ];

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-8rem)]" data-testid="chat-page">
        {/* Sidebar with sessions */}
        <div className="w-64 border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <Button 
              onClick={startNewSession}
              className="w-full mb-4 bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>

            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Recent Conversations</h3>
              {sessions.length > 0 ? (
                sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`p-3 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors group ${
                      sessionId === session.session_id ? 'bg-indigo-50 border border-indigo-200' : 'border border-transparent'
                    }`}
                    onClick={() => loadSession(session.session_id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900 truncate">{session.last_message}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(session.last_updated).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.session_id);
                        }}
                        className="opacity-0 group-hover:opacity-100 ml-2 text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">No conversations yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Main chat area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="border-b border-gray-200 p-4 bg-white">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Sparkles className="w-6 h-6 text-indigo-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">AI Assistant</h2>
                <p className="text-sm text-gray-600">Your intelligent hiring companion</p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex space-x-3 max-w-3xl ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className={message.role === 'user' ? 'bg-indigo-100 text-indigo-600' : 'bg-purple-100 text-purple-600'}>
                      {message.role === 'user' 
                        ? user?.email?.charAt(0).toUpperCase() 
                        : <Sparkles className="w-4 h-4" />
                      }
                    </AvatarFallback>
                  </Avatar>

                  <div className={`flex-1 ${message.role === 'user' ? 'text-right' : ''}`}>
                    <div className={`inline-block p-4 rounded-lg ${
                      message.role === 'user' 
                        ? 'bg-indigo-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      
                      {message.action_taken && (
                        <Badge className="mt-2" variant="secondary">
                          Action: {message.action_taken.replace('_', ' ')}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatTime(message.timestamp || message.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex space-x-3 max-w-3xl">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-purple-100 text-purple-600">
                      <Sparkles className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          {messages.length <= 1 && (
            <div className="px-6 pb-4">
              <p className="text-sm text-gray-600 mb-3">Quick actions:</p>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="justify-start text-left h-auto py-3"
                    onClick={() => setInput(action.label)}
                  >
                    <span className="mr-2">{action.icon}</span>
                    {action.label}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="border-t border-gray-200 p-4 bg-white">
            <form onSubmit={sendMessage} className="flex space-x-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me anything about your hiring process..."
                disabled={loading}
                className="flex-1"
                data-testid="chat-input"
              />
              <Button 
                type="submit" 
                disabled={loading || !input.trim()}
                className="bg-indigo-600 hover:bg-indigo-700"
                data-testid="send-button"
              >
                <Send className="w-4 h-4" />
              </Button>
            </form>
            <p className="text-xs text-gray-500 mt-2">
              AI assistant can help with job creation, candidate review, scheduling, and analytics
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ChatPage;
