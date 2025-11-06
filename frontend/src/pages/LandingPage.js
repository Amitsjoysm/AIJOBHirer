import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Sparkles, Zap, Target, Users, BarChart3, Calendar } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-8 h-8 text-indigo-600" />
            <span className="text-2xl font-bold gradient-text">HireFlow AI</span>
          </div>
          <div className="flex items-center space-x-4">
            <Button data-testid="login-btn" variant="ghost" onClick={() => navigate('/login')}>
              Login
            </Button>
            <Button data-testid="register-btn" onClick={() => navigate('/register')}>
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto text-center max-w-5xl">
          <div className="animate-fadeIn">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              Automate Your
              <span className="gradient-text"> Hiring Process</span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-10 max-w-3xl mx-auto">
              AI-powered hiring assistant that automates 80% of your recruitment workflow.
              From job posting to interview scheduling, we've got you covered.
            </p>
            <div className="flex justify-center space-x-4">
              <Button data-testid="get-started-hero-btn" size="lg" className="px-8 py-6 text-lg" onClick={() => navigate('/register')}>
                Start Free Trial
              </Button>
              <Button data-testid="learn-more-btn" size="lg" variant="outline" className="px-8 py-6 text-lg">
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-white">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-4xl font-bold text-center mb-16">Powerful AI Features</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Zap className="w-12 h-12 text-indigo-600" />,
                title: "AI Job Descriptions",
                description: "Generate compelling job descriptions and screening questions in seconds using advanced AI."
              },
              {
                icon: <Target className="w-12 h-12 text-purple-600" />,
                title: "Smart Resume Parsing",
                description: "Automatically parse, analyze, and score candidates against job requirements."
              },
              {
                icon: <Users className="w-12 h-12 text-indigo-600" />,
                title: "Auto Communication",
                description: "AI-powered email responses to candidates at every stage of the hiring process."
              },
              {
                icon: <Calendar className="w-12 h-12 text-purple-600" />,
                title: "Smart Scheduling",
                description: "Intelligent interview scheduling with automatic calendar integration."
              },
              {
                icon: <BarChart3 className="w-12 h-12 text-indigo-600" />,
                title: "Deep Analytics",
                description: "Get insights into your hiring funnel with AI-generated reports."
              },
              {
                icon: <Sparkles className="w-12 h-12 text-purple-600" />,
                title: "Company Persona",
                description: "AI learns your company culture and hiring preferences over time."
              }
            ].map((feature, index) => (
              <div key={index} className="p-8 rounded-2xl border-2 border-gray-100 hover:border-indigo-200 card-hover bg-white">
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="container mx-auto text-center max-w-4xl">
          <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Hiring?</h2>
          <p className="text-xl mb-10 opacity-90">
            Join innovative SMBs that are saving 15+ hours per week on hiring.
          </p>
          <Button data-testid="cta-start-btn" size="lg" variant="secondary" className="px-10 py-6 text-lg bg-white text-indigo-600 hover:bg-gray-50" onClick={() => navigate('/register')}>
            Get Started Now
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 bg-gray-50 border-t">
        <div className="container mx-auto text-center text-gray-600">
          <p>&copy; 2025 HireFlow AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
