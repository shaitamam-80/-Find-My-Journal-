import React, { useState, useEffect } from 'react';
import { 
  Search, BarChart2, Shield, Zap, BookOpen, 
  FileText, Globe, Award, Clock, Users, CheckCircle, ArrowRight,
  Menu, X, Target, Layers, Home, Info, DollarSign, HelpCircle
} from 'lucide-react';

// ==================== LANDING PAGE ====================
const LandingPage = ({ onNavigate }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [sideMenuOpen, setSideMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const menuItems = [
    { icon: <Home className="w-5 h-5" />, name: 'בית', id: 'hero' },
    { icon: <Info className="w-5 h-5" />, name: 'אודות', id: 'about' },
    { icon: <Layers className="w-5 h-5" />, name: 'איך זה עובד', id: 'how' },
    { icon: <Zap className="w-5 h-5" />, name: 'תכונות', id: 'features' },
  ];

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) element.scrollIntoView({ behavior: 'smooth' });
    setSideMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-blue-50" dir="rtl">
      {/* Side Menu */}
      <div className={`fixed top-0 right-0 h-full w-72 bg-white/90 backdrop-blur-xl border-l border-blue-100/50 shadow-2xl z-50 transform transition-transform duration-300 ${sideMenuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-gray-800">FindMyJournal</span>
            </div>
            <button onClick={() => setSideMenuOpen(false)} className="p-2 hover:bg-gray-100 rounded-lg">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
          
          <nav className="space-y-2">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => scrollToSection(item.id)}
                className="w-full flex items-center gap-3 px-4 py-3 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all"
              >
                {item.icon}
                <span className="font-medium">{item.name}</span>
              </button>
            ))}
          </nav>

          <div className="mt-8 pt-8 border-t border-gray-100 space-y-3">
            <button 
              onClick={() => onNavigate('login')}
              className="w-full py-3 text-blue-600 font-semibold hover:bg-blue-50 rounded-xl transition-colors"
            >
              התחברות
            </button>
            <button 
              onClick={() => onNavigate('register')}
              className="w-full py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-xl hover:shadow-lg transition-all"
            >
              הרשמה חינם
            </button>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {sideMenuOpen && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40" onClick={() => setSideMenuOpen(false)} />
      )}

      {/* Top Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-30 transition-all duration-300 ${
        isScrolled ? 'bg-white/80 backdrop-blur-xl shadow-lg shadow-blue-100/30 border-b border-blue-50' : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button onClick={() => setSideMenuOpen(true)} className="p-2 hover:bg-blue-50 rounded-xl transition-colors">
              <Menu className="w-6 h-6 text-gray-600" />
            </button>

            <div className="flex items-center gap-3">
              <div className="w-11 h-11 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-800">Find<span className="text-blue-500">My</span>Journal</span>
            </div>

            <div className="flex items-center gap-3">
              <button onClick={() => onNavigate('login')} className="px-5 py-2.5 text-blue-600 font-semibold hover:text-blue-700 transition-colors">
                התחברות
              </button>
              <button onClick={() => onNavigate('register')} className="px-6 py-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-200 transition-all hover:-translate-y-0.5">
                הרשמה
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="hero" className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="absolute top-20 right-10 w-72 h-72 bg-blue-200/40 rounded-full blur-3xl" />
        <div className="absolute bottom-10 left-10 w-64 h-64 bg-cyan-200/40 rounded-full blur-3xl" />
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 backdrop-blur-sm border border-blue-200/50 rounded-full text-blue-600 text-sm font-medium mb-8">
              <Zap className="w-4 h-4" />
              <span>מופעל בינה מלאכותית מתקדמת</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold text-gray-800 mb-6 leading-tight">
              מצא את הבית המושלם
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-500">
                למחקר שלך
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              הפלטפורמה החכמה שמנתחת את המאמר שלך ומתאימה אותו לכתבי העת המתאימים ביותר - 
              בתוך שניות ולא שבועות
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button onClick={() => onNavigate('register')} className="group px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold text-lg rounded-2xl hover:shadow-xl hover:shadow-blue-200 transition-all hover:-translate-y-1 flex items-center justify-center gap-2">
                התחל בחינם
                <ArrowRight className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
              </button>
              <button className="px-8 py-4 bg-white/70 backdrop-blur-sm text-gray-700 font-semibold text-lg rounded-2xl border border-gray-200/50 hover:border-blue-300 hover:bg-white transition-all">
                צפה בהדגמה
              </button>
            </div>
            
            <div className="mt-16 flex flex-wrap items-center justify-center gap-8 text-gray-500">
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                <span className="font-medium">20,000+ חוקרים</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                <span className="font-medium">150+ מדינות</span>
              </div>
              <div className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                <span className="font-medium">98% דיוק</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section - Blue Glass Cards */}
      <section id="about" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              מה זה <span className="text-blue-500">FindMyJournal</span>?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              פלטפורמה מבוססת בינה מלאכותית שמסייעת לחוקרים למצוא את כתב העת האקדמי המתאים ביותר
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: <Target className="w-8 h-8" />, title: "התאמה מדויקת", desc: "האלגוריתם שלנו מנתח את התקציר, המתודולוגיה והתחום שלך כדי למצוא התאמה מושלמת" },
              { icon: <Clock className="w-8 h-8" />, title: "חיסכון בזמן", desc: "במקום לבזבז שבועות בחיפוש ידני, קבל המלצות מותאמות אישית בתוך שניות" },
              { icon: <Shield className="w-8 h-8" />, title: "הגנה מפני טורפים", desc: "סינון אוטומטי של כתבי עת טורפניים ולא אמינים מרשימת ההמלצות" }
            ].map((item, i) => (
              <div key={i} className="relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-3xl" />
                <div className="absolute inset-0 bg-white/10 backdrop-blur-sm rounded-3xl" />
                <div className="relative p-8 rounded-3xl border border-white/30">
                  <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform border border-white/30">
                    {item.icon}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3">{item.title}</h3>
                  <p className="text-blue-100 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Goals Section */}
      <section className="py-24 px-6 bg-gradient-to-br from-blue-600 via-blue-500 to-cyan-500 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iNCIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">המטרות שלנו</h2>
            <p className="text-xl text-blue-100 max-w-2xl mx-auto">
              אנחנו מאמינים שכל חוקר ראוי לפרסם את עבודתו במקום הנכון
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: <Globe className="w-6 h-6" />, title: "נגישות גלובלית", desc: "להנגיש את תהליך הפרסום לחוקרים מכל העולם" },
              { icon: <Zap className="w-6 h-6" />, title: "יעילות מקסימלית", desc: "לחסוך זמן יקר בתהליך חיפוש כתבי העת" },
              { icon: <Award className="w-6 h-6" />, title: "איכות ללא פשרות", desc: "להבטיח התאמה לכתבי עת איכותיים בלבד" },
              { icon: <Users className="w-6 h-6" />, title: "תמיכה בקהילה", desc: "לבנות קהילת חוקרים תומכת ומשתפת" }
            ].map((goal, i) => (
              <div key={i} className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20 hover:bg-white/20 transition-all group">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform">
                  {goal.icon}
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{goal.title}</h3>
                <p className="text-blue-100 text-sm">{goal.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how" className="py-24 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">איך להשתמש במערכת?</h2>
            <p className="text-xl text-gray-600">שלושה צעדים פשוטים למציאת כתב העת המושלם</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-24 left-[20%] right-[20%] h-1 bg-gradient-to-r from-blue-200 via-cyan-300 to-blue-200 rounded-full" />
            
            {[
              { step: "01", title: "העלה את התקציר", desc: "פשוט העתק והדבק את התקציר של המאמר שלך או הכנס את הכותרת והמילות מפתח", icon: <FileText className="w-8 h-8" /> },
              { step: "02", title: "ניתוח AI", desc: "המערכת מנתחת את התוכן שלך ומזהה את התחום, המתודולוגיה והתרומה הייחודית", icon: <Layers className="w-8 h-8" /> },
              { step: "03", title: "קבל המלצות", desc: "קבל רשימה מדורגת של כתבי עת מתאימים עם מדדי השפעה, אחוזי קבלה וזמני פרסום", icon: <CheckCircle className="w-8 h-8" /> }
            ].map((item, i) => (
              <div key={i} className="relative text-center group">
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-cyan-500 rounded-3xl flex items-center justify-center text-white mb-6 shadow-xl shadow-blue-200 group-hover:scale-110 transition-transform relative z-10">
                  {item.icon}
                </div>
                <div className="text-sm font-bold text-blue-500 mb-2">שלב {item.step}</div>
                <h3 className="text-xl font-bold text-gray-800 mb-3">{item.title}</h3>
                <p className="text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-gradient-to-b from-blue-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">תכונות מתקדמות</h2>
            <p className="text-xl text-gray-600">כל מה שצריך כדי למצוא את כתב העת המושלם</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: <Search className="w-6 h-6" />, title: "ניתוח הקשר עמוק", desc: "הבנה מעמיקה של תחום המחקר, המתודולוגיה והתרומה הייחודית" },
              { icon: <BarChart2 className="w-6 h-6" />, title: "מדדים בזמן אמת", desc: "Impact Factor, h-index, אחוזי קבלה ומגמות פרסום עדכניות" },
              { icon: <Shield className="w-6 h-6" />, title: "סינון כתבי עת טורפניים", desc: "הגנה אוטומטית מפני כתבי עת לא אמינים" },
              { icon: <Clock className="w-6 h-6" />, title: "זמני פרסום משוערים", desc: "הערכת זמן מהגשה ועד פרסום לכל כתב עת" },
              { icon: <Globe className="w-6 h-6" />, title: "תמיכה ב-40+ שפות", desc: "מציאת כתבי עת בשפות ואזורים שונים" },
              { icon: <FileText className="w-6 h-6" />, title: "ייצוא למנהלי רפרנסים", desc: "אינטגרציה עם Zotero, Mendeley ו-EndNote" }
            ].map((feature, i) => (
              <div key={i} className="relative group overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/90 to-cyan-500/90 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-blue-100/50 group-hover:border-white/30 transition-all h-full">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-bold text-gray-800 group-hover:text-white mb-2 transition-colors">{feature.title}</h3>
                  <p className="text-gray-600 text-sm group-hover:text-blue-100 transition-colors">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-3xl p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-white/5 backdrop-blur-sm" />
            <div className="relative grid grid-cols-2 md:grid-cols-4 gap-8">
              {[
                { value: "50,000+", label: "כתבי עת באינדקס" },
                { value: "2M+", label: "מאמרים נותחו" },
                { value: "98%", label: "דיוק התאמה" },
                { value: "150+", label: "מדינות" }
              ].map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-4xl font-bold text-white mb-2">{stat.value}</div>
                  <div className="text-blue-100 font-medium">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-gradient-to-b from-white to-blue-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
            מוכן למצוא את כתב העת המושלם?
          </h2>
          <p className="text-gray-600 text-lg mb-8 max-w-xl mx-auto">
            הצטרף ל-20,000+ חוקרים שכבר מצאו את הבית למחקר שלהם
          </p>
          <button onClick={() => onNavigate('register')} className="px-10 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold text-lg rounded-2xl hover:shadow-xl hover:shadow-blue-200 transition-all hover:-translate-y-1">
            התחל בחינם - ללא כרטיס אשראי
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-800">FindMyJournal</span>
          </div>
          <p className="text-gray-500 text-sm">© 2024 FindMyJournal. כל הזכויות שמורות.</p>
        </div>
      </footer>
    </div>
  );
};

// ==================== REGISTER PAGE ====================
const RegisterPage = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    name: '', email: '', password: '', confirmPassword: '', institution: ''
  });

  return (
    <div className="min-h-screen relative overflow-hidden" dir="rtl">
      {/* Animated Horizontal Gradient Background */}
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-cyan-500 to-blue-600" />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-300/30 to-transparent animate-slide-right" style={{ backgroundSize: '200% 100%' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent animate-slide-left" style={{ backgroundSize: '200% 100%', animationDelay: '1s' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-transparent to-blue-500/20 animate-slide-right-slow" style={{ backgroundSize: '300% 100%' }} />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-60" />
      </div>

      {/* Navigation */}
      <nav className="relative z-20 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <button onClick={() => onNavigate('home')} className="flex items-center gap-3 group">
            <div className="w-11 h-11 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center group-hover:bg-white/30 transition-all border border-white/30">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">FindMyJournal</span>
          </button>
          <button onClick={() => onNavigate('login')} className="px-5 py-2.5 text-white/90 font-semibold hover:text-white bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all">
            כבר יש לך חשבון? התחבר
          </button>
        </div>
      </nav>

      {/* Form */}
      <div className="relative z-10 min-h-[calc(100vh-80px)] flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-3xl p-8 shadow-2xl shadow-blue-900/30">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">צור חשבון חדש</h1>
              <p className="text-gray-500">הצטרף לאלפי חוקרים שמשתמשים בפלטפורמה</p>
            </div>

            <form className="space-y-5">
              {[
                { label: 'שם מלא', key: 'name', type: 'text', placeholder: 'ד״ר ישראל ישראלי' },
                { label: 'כתובת אימייל', key: 'email', type: 'email', placeholder: 'researcher@university.ac.il' },
                { label: 'מוסד אקדמי', key: 'institution', type: 'text', placeholder: 'אוניברסיטה / מכון מחקר' },
                { label: 'סיסמה', key: 'password', type: 'password', placeholder: '••••••••' },
                { label: 'אימות סיסמה', key: 'confirmPassword', type: 'password', placeholder: '••••••••' },
              ].map((field) => (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-cyan-600 mb-2">{field.label}</label>
                  <input
                    type={field.type}
                    value={formData[field.key]}
                    onChange={(e) => setFormData({...formData, [field.key]: e.target.value})}
                    className="w-full px-4 py-3.5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-800 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 transition-all placeholder:text-gray-400"
                    placeholder={field.placeholder}
                  />
                </div>
              ))}

              <button type="submit" className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold text-lg rounded-xl hover:shadow-lg hover:shadow-blue-300 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2">
                צור חשבון
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-500 text-sm">
                בהרשמה אתה מסכים ל<a href="#" className="text-cyan-600 font-medium"> תנאי השימוש </a>
                ול<a href="#" className="text-cyan-600 font-medium"> מדיניות הפרטיות</a>
              </p>
            </div>
          </div>

          <div className="mt-8 grid grid-cols-3 gap-4">
            {[
              { icon: <CheckCircle className="w-5 h-5" />, text: 'חינם לנסיון' },
              { icon: <Shield className="w-5 h-5" />, text: 'אבטחה מלאה' },
              { icon: <Zap className="w-5 h-5" />, text: 'התחל מיד' }
            ].map((item, i) => (
              <div key={i} className="flex flex-col items-center gap-2 text-white bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
                {item.icon}
                <span className="text-sm font-medium text-center">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== LOGIN PAGE ====================
const LoginPage = ({ onNavigate }) => {
  const [loginData, setLoginData] = useState({ email: '', password: '' });

  return (
    <div className="min-h-screen relative overflow-hidden" dir="rtl">
      {/* Animated Horizontal Gradient Background */}
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-blue-500 to-blue-600" />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-300/30 to-transparent animate-slide-right" style={{ backgroundSize: '200% 100%' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-400/25 to-transparent animate-slide-left" style={{ backgroundSize: '200% 100%', animationDelay: '0.5s' }} />
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/15 via-transparent to-cyan-500/15 animate-slide-right-slow" style={{ backgroundSize: '300% 100%' }} />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMyIvPjwvZz48L2c+PC9zdmc+')] opacity-70" />
      </div>

      {/* Navigation */}
      <nav className="relative z-20 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <button onClick={() => onNavigate('home')} className="flex items-center gap-3 group">
            <div className="w-11 h-11 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center group-hover:bg-white/30 transition-all border border-white/30">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">FindMyJournal</span>
          </button>
          <button onClick={() => onNavigate('register')} className="px-5 py-2.5 text-white/90 font-semibold hover:text-white bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 hover:bg-white/20 transition-all">
            אין לך חשבון? הירשם
          </button>
        </div>
      </nav>

      {/* Form */}
      <div className="relative z-10 min-h-[calc(100vh-80px)] flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-3xl p-8 shadow-2xl shadow-blue-900/30">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-200">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">ברוך הבא חזרה</h1>
              <p className="text-gray-500">התחבר לחשבון שלך להמשיך</p>
            </div>

            <form className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-cyan-600 mb-2">כתובת אימייל</label>
                <input
                  type="email"
                  value={loginData.email}
                  onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                  className="w-full px-4 py-3.5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-800 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 transition-all placeholder:text-gray-400"
                  placeholder="researcher@university.ac.il"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-cyan-600">סיסמה</label>
                  <a href="#" className="text-sm text-blue-500 hover:text-blue-600 font-medium">שכחת סיסמה?</a>
                </div>
                <input
                  type="password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  className="w-full px-4 py-3.5 bg-blue-50/50 border border-blue-100 rounded-xl text-gray-800 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-100 transition-all placeholder:text-gray-400"
                  placeholder="••••••••"
                />
              </div>

              <div className="flex items-center gap-3">
                <input type="checkbox" id="remember" className="w-5 h-5 rounded-lg border-blue-200 text-cyan-500 focus:ring-cyan-200 cursor-pointer" />
                <label htmlFor="remember" className="text-gray-600 cursor-pointer">זכור אותי</label>
              </div>

              <button type="submit" className="w-full py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-bold text-lg rounded-xl hover:shadow-lg hover:shadow-blue-300 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2">
                התחבר
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>

            <div className="mt-8 text-center">
              <p className="text-gray-500 text-sm">
                אין לך חשבון עדיין?{' '}
                <button onClick={() => onNavigate('register')} className="text-cyan-600 hover:text-cyan-700 font-semibold">
                  הירשם עכשיו
                </button>
              </p>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-white/80 text-sm bg-white/10 backdrop-blur-md rounded-xl px-6 py-4 border border-white/20">
              הצטרף ל-20,000+ חוקרים שכבר מצאו את כתב העת המושלם למחקר שלהם
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== MAIN APP ====================
const FindMyJournalApp = () => {
  const [currentPage, setCurrentPage] = useState('home');

  const handleNavigate = (page) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  return (
    <div className="font-sans">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');
        body { font-family: 'Heebo', sans-serif; margin: 0; padding: 0; }
        
        @keyframes slide-right {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes slide-left {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        @keyframes slide-right-slow {
          0% { transform: translateX(-50%); }
          100% { transform: translateX(50%); }
        }
        .animate-slide-right {
          animation: slide-right 8s ease-in-out infinite;
        }
        .animate-slide-left {
          animation: slide-left 12s ease-in-out infinite;
        }
        .animate-slide-right-slow {
          animation: slide-right-slow 18s ease-in-out infinite alternate;
        }
      `}</style>

      {currentPage === 'home' && <LandingPage onNavigate={handleNavigate} />}
      {currentPage === 'register' && <RegisterPage onNavigate={handleNavigate} />}
      {currentPage === 'login' && <LoginPage onNavigate={handleNavigate} />}
    </div>
  );
};

export default FindMyJournalApp;