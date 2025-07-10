import React, { useState } from 'react';
import { Send, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import FixedSearchBar from './FixedSearchBar';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  loading?: boolean;
}

interface Citation {
  id: string; // Generated client-side for uniqueness
  title: string; // Map from citation field or use a default
  court: string; // Map from source or use a default
  year: string; // Placeholder; backend doesn't provide this
  url: string; // Placeholder; backend doesn't provide this
  citation: string; // From backend
  source: string; // From backend
}

const SearchPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedCitations, setExpandedCitations] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      loading: true,
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input, model_id: null }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch results');
      }

      const data = await response.json();

      // Map backend response to frontend structure
      const assistantMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: data.data.answer || "I couldn't find relevant information for your query. Please try rephrasing your question.",
        citations: data.data.citations?.map((c: { citation: string; source: string }) => ({
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9), // Unique ID
          title: c.citation.split('.')[0] || c.citation, // Extract title from citation
          court: c.source.split(',')[0] || c.source, // Extract court from source
          year: 'N/A', // Placeholder; add if backend provides
          url: '#', // Placeholder; add if backend provides
          citation: c.citation,
          source: c.source,
        })) || [],
      };

      setMessages(prev => prev.slice(0, -1).concat([assistantMessage]));
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: "I'm sorry, I couldn't process your request. Please check your connection and try again.",
      };
      setMessages(prev => prev.slice(0, -1).concat([errorMessage]));
    } finally {
      setIsLoading(false);
    }
  };

  const toggleCitations = (messageId: string) => {
    setExpandedCitations(prev =>
      prev.includes(messageId)
        ? prev.filter(id => id !== messageId)
        : [...prev, messageId]
    );
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900 relative">
      {/* Chat Messages */}
      <main className={`flex-1 overflow-y-auto ${messages.length > 0 ? 'pb-24 sm:pb-28' : ''}`}>
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full px-4">
            <div className="text-center max-w-md">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Ask LegalRAG Anything
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-8">
                Get instant answers to your legal research questions with AI-powered analysis
              </p>
              <div className="space-y-2 text-sm text-gray-500 dark:text-gray-500">
                <p>• "Explain the reasonable person test in tort law"</p>
                <p>• "What are the elements of breach of contract?"</p>
                <p>• "How do courts determine negligence?"</p>
              </div>
              
              {/* Centered Input Form */}
              <div className="mt-8">
                <form onSubmit={handleSubmit} className="flex space-x-3">
                  <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Describe your legal query... e.g., 'Explain the reasonable person test in tort law'"
                    className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent shadow-sm"
                    disabled={isLoading}
                    autoComplete="off"
                  />
                  <button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className="px-6 py-3 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 flex items-center space-x-2 shadow-sm hover:shadow-md transform hover:scale-105 disabled:transform-none"
                  >
                    {isLoading ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </button>
                </form>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto px-4 py-6 space-y-6 min-h-full">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-amber-500 text-white'
                      : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                  }`}
                >
                  {message.loading ? (
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm">Researching...</span>
                    </div>
                  ) : (
                    <>
                      <div className="whitespace-pre-wrap">{message.content}</div>
                      
                      {message.citations && message.citations.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                          <button
                            onClick={() => toggleCitations(message.id)}
                            className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                          >
                            <span>Citations ({message.citations.length})</span>
                            {expandedCitations.includes(message.id) ? (
                              <ChevronUp className="h-4 w-4" />
                            ) : (
                              <ChevronDown className="h-4 w-4" />
                            )}
                          </button>
                          
                          {expandedCitations.includes(message.id) && (
                            <div className="mt-3 space-y-2">
                              {message.citations.map((citation) => (
                                <div
                                  key={citation.id}
                                  className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                                >
                                  <h4 className="font-medium text-sm mb-1">
                                    {citation.title}
                                  </h4>
                                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                                    {citation.court} • {citation.year}
                                  </p>
                                  <a
                                    href={citation.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-amber-600 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-300"
                                  >
                                    View Case →
                                  </a>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Fixed Search Bar - Only show when there are messages */}
      <FixedSearchBar
        input={input}
        setInput={setInput}
        onSubmit={handleSubmit}
        isLoading={isLoading}
        isVisible={messages.length > 0}
      />
    </div>
  );
};

export default SearchPage;