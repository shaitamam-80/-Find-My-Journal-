import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Search, BarChart2, Zap, BookOpen,
  FileText, Globe, Award, Clock, Users, CheckCircle, ArrowRight,
  Menu, X, Target, Layers
} from 'lucide-react'

export function LandingPage() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [sideMenuOpen, setSideMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const menuItems = [
    { icon: <BookOpen className="w-5 h-5" />, name: 'Home', id: 'hero' },
    { icon: <Target className="w-5 h-5" />, name: 'About', id: 'about' },
    { icon: <Layers className="w-5 h-5" />, name: 'How It Works', id: 'how' },
    { icon: <Zap className="w-5 h-5" />, name: 'Features', id: 'features' },
  ]

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) element.scrollIntoView({ behavior: 'smooth' })
    setSideMenuOpen(false)
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Side Menu */}
      <div className={`fixed top-0 start-0 h-full w-72 bg-white border-e border-slate-200 shadow-xl z-50 transform transition-transform duration-300 ${sideMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-slate-900">FindMyJournal</span>
            </div>
            <button onClick={() => setSideMenuOpen(false)} className="p-2 hover:bg-slate-100 rounded-lg">
              <X className="w-5 h-5 text-slate-500" />
            </button>
          </div>

          <nav className="space-y-2">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => scrollToSection(item.id)}
                className="w-full flex items-center gap-3 px-4 py-3 text-slate-600 hover:text-teal-600 hover:bg-slate-50 rounded-xl transition-all"
              >
                {item.icon}
                <span className="font-medium">{item.name}</span>
              </button>
            ))}
          </nav>

          <div className="mt-8 pt-8 border-t border-slate-200 space-y-3">
            <Link
              to="/login"
              className="block w-full py-3 text-center text-slate-600 font-semibold hover:bg-slate-50 rounded-xl transition-colors"
            >
              Log In
            </Link>
            <Link
              to="/signup"
              className="block w-full py-3 text-center bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-all"
            >
              Sign Up Free
            </Link>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {sideMenuOpen && (
        <div className="fixed inset-0 bg-black/20 z-40" onClick={() => setSideMenuOpen(false)} />
      )}

      {/* Top Navigation */}
      <nav className={`fixed top-0 start-0 end-0 z-30 transition-all duration-300 ${
        isScrolled ? 'bg-white/95 backdrop-blur-sm shadow-sm border-b border-slate-200' : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button onClick={() => setSideMenuOpen(true)} className="p-2 hover:bg-slate-100 rounded-xl transition-colors lg:hidden">
                <Menu className="w-6 h-6 text-slate-600" />
              </button>
              <div className="w-11 h-11 bg-slate-900 rounded-2xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900">Find<span className="text-teal-600">My</span>Journal</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center gap-8">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className="text-slate-600 hover:text-teal-600 font-medium transition-colors"
                >
                  {item.name}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-3">
              <Link to="/login" className="px-5 py-2.5 text-slate-600 font-semibold hover:text-slate-900 transition-colors">
                Log In
              </Link>
              <Link to="/signup" className="px-6 py-2.5 bg-slate-900 text-white font-semibold rounded-xl hover:bg-slate-800 transition-all">
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="hero" className="relative pt-32 pb-20 px-6 bg-slate-50">
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-teal-50 border border-teal-200 rounded-full text-teal-600 text-sm font-medium mb-8">
              <Zap className="w-4 h-4" />
              <span>Powered by Advanced AI</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-slate-900 mb-6 leading-tight">
              Find the Perfect Home
              <br />
              <span className="text-teal-600">
                for Your Research
              </span>
            </h1>

            <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              The intelligent platform that analyzes your paper and matches it with the most suitable academic journals -
              in seconds, not weeks.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/signup" className="group px-8 py-4 bg-slate-900 text-white font-bold text-lg rounded-2xl hover:bg-slate-800 transition-all flex items-center justify-center gap-2">
                Get Started Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button className="px-8 py-4 bg-white text-slate-700 font-semibold text-lg rounded-2xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all">
                Watch Demo
              </button>
            </div>

            <div className="mt-16 flex flex-wrap items-center justify-center gap-8 text-slate-500">
              <div className="flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                <span className="font-medium">Powered by OpenAlex</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                <span className="font-medium">40+ Languages Supported</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                <span className="font-medium">Instant Results</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section - White Cards with Border */}
      <section id="about" className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              What is <span className="text-teal-600">FindMyJournal</span>?
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              An AI-powered platform that helps researchers find the most suitable academic journal for their work.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: <Target className="w-8 h-8" />, title: "Precise Matching", desc: "Our algorithm analyzes your abstract, methodology, and field to find the perfect journal fit." },
              { icon: <Clock className="w-8 h-8" />, title: "Save Time", desc: "Instead of spending weeks searching manually, get personalized recommendations in seconds." },
              { icon: <BarChart2 className="w-8 h-8" />, title: "Quality Indicators", desc: "View journal metrics including H-index, citation counts, and Open Access status to make informed decisions." }
            ].map((item, i) => (
              <div key={i} className="bg-white rounded-2xl p-8 border border-slate-200 hover:border-teal-200 hover:shadow-lg transition-all group">
                <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center text-teal-600 mb-6 group-hover:bg-teal-50 transition-colors">
                  {item.icon}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{item.title}</h3>
                <p className="text-slate-600 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Goals Section - Light Background */}
      <section className="py-24 px-6 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Our Goals</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              We believe every researcher deserves to publish their work in the right place.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: <Globe className="w-6 h-6" />, title: "Global Accessibility", desc: "Making the publication process accessible to researchers worldwide." },
              { icon: <Zap className="w-6 h-6" />, title: "Maximum Efficiency", desc: "Saving valuable time in the journal search process." },
              { icon: <Award className="w-6 h-6" />, title: "Quality Without Compromise", desc: "Ensuring matches only with high-quality journals." },
              { icon: <Users className="w-6 h-6" />, title: "Community Support", desc: "Building a supportive and collaborative researcher community." }
            ].map((goal, i) => (
              <div key={i} className="bg-white rounded-2xl p-6 border border-slate-200 hover:border-teal-200 hover:shadow-md transition-all group">
                <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-teal-600 mb-4 group-hover:bg-teal-50 transition-colors">
                  {goal.icon}
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{goal.title}</h3>
                <p className="text-slate-600 text-sm">{goal.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how" className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">How Does It Work?</h2>
            <p className="text-xl text-slate-600">Three simple steps to find your perfect journal.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-16 start-[20%] end-[20%] h-0.5 bg-slate-200 rounded-full" />

            {[
              { step: "01", title: "Upload Your Abstract", desc: "Simply copy and paste your paper's abstract or enter the title and keywords.", icon: <FileText className="w-8 h-8" /> },
              { step: "02", title: "AI Analysis", desc: "Our system analyzes your content and identifies the field, methodology, and unique contribution.", icon: <Layers className="w-8 h-8" /> },
              { step: "03", title: "Get Recommendations", desc: "Receive a ranked list of suitable journals with H-index, citation metrics, and Open Access information.", icon: <CheckCircle className="w-8 h-8" /> }
            ].map((item, i) => (
              <div key={i} className="relative text-center group">
                <div className="w-20 h-20 mx-auto bg-slate-900 rounded-3xl flex items-center justify-center text-white mb-6 group-hover:bg-teal-600 transition-colors relative z-10">
                  {item.icon}
                </div>
                <div className="text-sm font-bold text-teal-600 mb-2">Step {item.step}</div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{item.title}</h3>
                <p className="text-slate-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Advanced Features</h2>
            <p className="text-xl text-slate-600">Everything you need to find the perfect journal.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: <Search className="w-6 h-6" />, title: "Deep Context Analysis", desc: "In-depth understanding of research field, methodology, and unique contribution." },
              { icon: <BarChart2 className="w-6 h-6" />, title: "Journal Metrics", desc: "H-index, citation counts, and publication volume for informed decisions." },
              { icon: <BarChart2 className="w-6 h-6" />, title: "Comprehensive Metrics", desc: "Works count, citation data, and publisher information for each journal." },
              { icon: <Zap className="w-6 h-6" />, title: "AI-Powered Matching", desc: "Smart algorithm matches your research to the most relevant journals." },
              { icon: <Globe className="w-6 h-6" />, title: "Support for 40+ Languages", desc: "Find journals in different languages and regions." },
              { icon: <FileText className="w-6 h-6" />, title: "Open Access Detection", desc: "Easily identify open access journals and their publication fees." }
            ].map((feature, i) => (
              <div key={i} className="bg-white rounded-2xl p-6 border border-slate-200 hover:border-teal-200 hover:shadow-md transition-all group">
                <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center text-teal-600 mb-4 group-hover:bg-teal-50 transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Data Source Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="bg-slate-900 rounded-3xl p-12">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-white mb-4">Powered by OpenAlex</h3>
              <p className="text-slate-300 max-w-2xl mx-auto">
                Access comprehensive academic journal data from OpenAlex, an open catalog of the global research system with data on publications, authors, institutions, and more.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-slate-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Ready to Find Your Perfect Journal?
          </h2>
          <p className="text-slate-600 text-lg mb-8 max-w-xl mx-auto">
            Start finding the perfect journal for your research today.
          </p>
          <Link to="/signup" className="inline-block px-10 py-4 bg-slate-900 text-white font-bold text-lg rounded-2xl hover:bg-slate-800 transition-all">
            Start Free - No Credit Card Required
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-slate-900">FindMyJournal</span>
          </div>
          <p className="text-slate-500 text-sm">&copy; 2024 FindMyJournal. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
