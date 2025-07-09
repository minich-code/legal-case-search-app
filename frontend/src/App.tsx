import React, { useState } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import Header from './components/Header';
import LandingPage from './components/LandingPage';
import SearchPage from './components/SearchPage';
import AboutPage from './components/AboutPage';
import PricingPage from './components/PricingPage';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <LandingPage onNavigate={setCurrentPage} />;
      case 'search':
        return <SearchPage />;
      case 'about':
        return <AboutPage />;
      case 'pricing':
        return <PricingPage />;
      default:
        return <LandingPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 font-inter">
        <Header currentPage={currentPage} onNavigate={setCurrentPage} />
        {renderPage()}
      </div>
    </ThemeProvider>
  );
}

export default App;