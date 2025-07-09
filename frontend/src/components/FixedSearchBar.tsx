import React from 'react';
import { Send, Loader2 } from 'lucide-react';

interface FixedSearchBarProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  isVisible: boolean;
}

const FixedSearchBar: React.FC<FixedSearchBarProps> = ({
  input,
  setInput,
  onSubmit,
  isLoading,
  isVisible,
}) => {
  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-50 transition-all duration-300 ease-in-out transform ${
        isVisible ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
      }`}
    >
      {/* Background with blur effect */}
      <div className="absolute inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t border-gray-200 dark:border-gray-700" />
      
      {/* Content */}
      <div className="relative p-4 sm:p-6">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={onSubmit} className="flex space-x-3 sm:space-x-4">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask another legal question..."
              className="flex-1 px-4 py-3 sm:py-4 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent shadow-sm text-sm sm:text-base"
              disabled={isLoading}
              autoComplete="off"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 sm:px-6 py-3 sm:py-4 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 shadow-sm hover:shadow-md transform hover:scale-105 disabled:transform-none min-w-[48px] sm:min-w-[auto]"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <Send className="h-5 w-5" />
                  <span className="hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default FixedSearchBar;