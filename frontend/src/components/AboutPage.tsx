import React from 'react';
import { Brain, Search, Shield, Zap, Users, Award } from 'lucide-react';

const AboutPage: React.FC = () => {
  const techFeatures = [
    {
      icon: Brain,
      title: 'Advanced RAG Technology',
      description: 'Retrieval-Augmented Generation combines the power of large language models with comprehensive legal databases for accurate, contextual responses.',
    },
    {
      icon: Search,
      title: 'Natural Language Processing',
      description: 'Our NLP engine understands complex legal queries and can interpret legal language, precedents, and case law relationships.',
    },
    {
      icon: Shield,
      title: 'Verified Legal Sources',
      description: 'All responses are backed by verified legal sources from courts, statutes, and authoritative legal databases.',
    },
  ];

  const stats = [
    { number: '500K+', label: 'Legal Cases' },
    { number: '50+', label: 'Jurisdictions' },
    { number: '99.9%', label: 'Accuracy Rate' },
    { number: '< 3s', label: 'Response Time' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-gray-800 dark:to-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-6">
              Democratizing Legal Research with AI
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-4xl mx-auto leading-relaxed">
              LegalRAG transforms how legal professionals conduct research by combining artificial intelligence 
              with comprehensive legal databases, making complex case law analysis accessible to everyone.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-amber-500 mb-2">
                  {stat.number}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-gray-100 dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-8">
              Our Mission
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed mb-8">
              We believe that access to legal knowledge should not be limited by resources or expertise. 
              Our AI-powered platform democratizes legal research by making complex case law analysis 
              simple, fast, and accurate for legal professionals, students, and anyone seeking legal insights.
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center space-x-2">
                <Users className="h-4 w-4" />
                <span>Accessible to All</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4" />
                <span>Lightning Fast</span>
              </div>
              <div className="flex items-center space-x-2">
                <Award className="h-4 w-4" />
                <span>Precision Focused</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Powered by Advanced Technology
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Our platform leverages cutting-edge AI technologies to deliver accurate, 
              contextual legal research capabilities.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {techFeatures.map((feature, index) => (
              <div
                key={index}
                className="p-8 rounded-xl bg-gray-50 dark:bg-gray-800 hover:bg-white dark:hover:bg-gray-700 transition-all duration-300 shadow-md hover:shadow-lg"
              >
                <div className="flex items-center justify-center w-12 h-12 bg-amber-500 rounded-lg mb-6">
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-gradient-to-r from-amber-500 to-orange-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-8">
              Our Commitment
            </h2>
            <div className="grid md:grid-cols-3 gap-8 text-white">
              <div>
                <h3 className="text-xl font-semibold mb-4">Accuracy</h3>
                <p className="text-amber-100">
                  We maintain the highest standards of accuracy in legal research, 
                  with verified sources and precise citations.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-4">Privacy</h3>
                <p className="text-amber-100">
                  Your research queries and data remain private and secure, 
                  with no data retention or sharing.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-4">Innovation</h3>
                <p className="text-amber-100">
                  We continuously improve our AI capabilities to provide better, 
                  faster, and more comprehensive legal insights.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;