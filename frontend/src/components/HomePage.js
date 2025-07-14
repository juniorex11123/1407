import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';

const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const scrollToSection = (sectionId) => {
    if (location.pathname !== '/') {
      // If not on homepage, navigate to homepage first then scroll
      return window.location.href = `/#${sectionId}`;
    }
    
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  const handlePanelClick = () => {
    navigate('/panel');
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-blue-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">
              TimeTracker Pro
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <button onClick={() => scrollToSection('features')} className="text-gray-700 hover:text-blue-600 transition-colors">
              Funkcje
            </button>
            <button onClick={() => scrollToSection('benefits')} className="text-gray-700 hover:text-blue-600 transition-colors">
              Korzyści
            </button>
            <button onClick={() => scrollToSection('testimonials')} className="text-gray-700 hover:text-blue-600 transition-colors">
              Opinie
            </button>
            <button onClick={() => scrollToSection('pricing')} className="text-gray-700 hover:text-blue-600 transition-colors">
              Cennik
            </button>
            <button onClick={() => scrollToSection('contact')} className="text-gray-700 hover:text-blue-600 transition-colors">
              Kontakt
            </button>
            <button 
              onClick={handlePanelClick}
              className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-2 rounded-full hover:from-blue-700 hover:to-blue-800 transition-all transform hover:scale-105 shadow-lg"
            >
              Zaloguj do panelu
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-700 hover:text-blue-600 focus:outline-none focus:text-blue-600"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 bg-white border-t border-blue-100">
              <button onClick={() => scrollToSection('features')} className="block px-3 py-2 text-gray-700 hover:text-blue-600 w-full text-left">
                Funkcje
              </button>
              <button onClick={() => scrollToSection('benefits')} className="block px-3 py-2 text-gray-700 hover:text-blue-600 w-full text-left">
                Korzyści
              </button>
              <button onClick={() => scrollToSection('testimonials')} className="block px-3 py-2 text-gray-700 hover:text-blue-600 w-full text-left">
                Opinie
              </button>
              <button onClick={() => scrollToSection('pricing')} className="block px-3 py-2 text-gray-700 hover:text-blue-600 w-full text-left">
                Cennik
              </button>
              <button onClick={() => scrollToSection('contact')} className="block px-3 py-2 text-gray-700 hover:text-blue-600 w-full text-left">
                Kontakt
              </button>
              <button 
                onClick={handlePanelClick}
                className="block px-3 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg text-center mt-2"
              >
                Zaloguj do panelu
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

const HomePage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    phone: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    setTimeout(() => {
      setSubmitStatus('success');
      setIsSubmitting(false);
      setFormData({ name: '', email: '', company: '', phone: '', message: '' });
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-blue-50 to-indigo-100 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                TimeTracker Pro
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Nowoczesny system do zarządzania czasem pracy dla małych i średnich firm. 
              Zwiększ produktywność o 35% dzięki inteligentnym narzędziom.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                onClick={() => scrollToSection('pricing')}
                className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-4 rounded-full text-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all transform hover:scale-105 shadow-lg"
              >
                Rozpocznij 14-dniowy darmowy okres próbny
              </button>
              <button 
                onClick={() => scrollToSection('features')}
                className="border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-blue-50 transition-all"
              >
                Zobacz funkcje
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Funkcje, które zwiększą Twoją produktywność
            </h2>
            <p className="text-xl text-gray-600">
              Wszystko czego potrzebujesz do zarządzania czasem i projektami
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: '⏱️',
                title: 'Śledzenie czasu w czasie rzeczywistym',
                description: 'Automatyczne śledzenie czasu z precyzją do sekundy. Inteligentne wykrywanie przerw i nieaktywności.'
              },
              {
                icon: '📊',
                title: 'Zaawansowane raporty',
                description: 'Szczegółowe raporty produktywności, analiza trendów i eksport do Excel/PDF.'
              },
              {
                icon: '🔄',
                title: 'Automatyczna fakturacja',
                description: 'Generowanie faktur na podstawie przepracowanych godzin z integracją z systemami księgowymi.'
              },
              {
                icon: '👥',
                title: 'Zarządzanie zespołem',
                description: 'Przegląd aktywności zespołu, przydzielanie zadań i monitorowanie postępów.'
              },
              {
                icon: '📱',
                title: 'Aplikacja mobilna',
                description: 'Śledź czas z dowolnego miejsca dzięki aplikacji na iOS i Android.'
              },
              {
                icon: '🔐',
                title: 'Bezpieczeństwo danych',
                description: 'Szyfrowanie SSL, backup w chmurze i zgodność z RODO.'
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div id="benefits" className="py-20 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Korzyści dla Twojego biznesu
            </h2>
            <p className="text-xl text-gray-600">
              Sprawdzone rezultaty wśród tysięcy firm
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                stat: '40%',
                title: 'Oszczędność czasu do 40%',
                description: 'Automatyzacja procesów eliminuje manualne wprowadzanie danych i skraca czas administracyjny.'
              },
              {
                stat: '25%',
                title: 'Zwiększ zyski o 25%',
                description: 'Precyzyjne śledzenie czasu zapewnia pełną rozliczalność projektów i eliminuje straty.'
              },
              {
                stat: '95%',
                title: 'Lepsza organizacja zespołu',
                description: 'Przejrzyste zadania, deadliny i komunikacja w jednym miejscu.'
              }
            ].map((benefit, index) => (
              <div key={index} className="text-center">
                <div className="text-6xl font-bold text-blue-600 mb-4">{benefit.stat}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{benefit.title}</h3>
                <p className="text-gray-600">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Co mówią nasi klienci
            </h2>
            <p className="text-xl text-gray-600">
              Ponad 10,000 firm już nam zaufało
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: 'Anna Kowalska',
                position: 'CEO, TechSolutions',
                image: 'https://images.pexels.com/photos/7616608/pexels-photo-7616608.jpeg',
                content: 'TimeTracker Pro zrewolucjonizował sposób zarządzania naszym zespołem. Wzrost produktywności o 35% w pierwszym miesiącu!'
              },
              {
                name: 'Marek Nowak',
                position: 'Dyrektor, Creative Agency',
                image: 'https://images.unsplash.com/photo-1610631066894-62452ccb927c',
                content: 'Najlepsze narzędzie do śledzenia czasu i rozliczania projektów. Intuicyjne, szybkie i niezawodne.'
              },
              {
                name: 'Kasia Wiśniewska',
                position: 'PM, Development Team',
                image: 'https://images.unsplash.com/photo-1573497701175-00c200fd57f0',
                content: 'Automatyczna fakturacja oszczędza nam tygodnie pracy. ROI zwrócił się już w drugim miesiącu użytkowania.'
              }
            ].map((testimonial, index) => (
              <div key={index} className="bg-gray-50 rounded-xl p-8 shadow-lg">
                <div className="flex items-center mb-6">
                  <img 
                    src={testimonial.image} 
                    alt={testimonial.name}
                    className="w-16 h-16 rounded-full object-cover mr-4"
                  />
                  <div>
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <p className="text-gray-600 text-sm">{testimonial.position}</p>
                  </div>
                </div>
                <p className="text-gray-700 italic">"{testimonial.content}"</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div id="pricing" className="py-20 bg-gradient-to-r from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Wybierz plan dla siebie
            </h2>
            <p className="text-xl text-gray-600">
              Bez ukrytych kosztów, anuluj w dowolnym momencie
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: 'Starter',
                price: '29',
                description: 'Idealny dla małych zespołów',
                features: [
                  'Do 5 użytkowników',
                  'Podstawowe śledzenie czasu',
                  'Proste raporty',
                  'Email support',
                  'Aplikacja mobilna'
                ],
                highlighted: false
              },
              {
                name: 'Professional',
                price: '59',
                description: 'Najpopularniejszy wśród firm',
                features: [
                  'Do 25 użytkowników',
                  'Zaawansowane śledzenie',
                  'Automatyczna fakturacja',
                  'Zarządzanie projektami',
                  'Integracje z systemami',
                  'Priorytetowy support'
                ],
                highlighted: true
              },
              {
                name: 'Enterprise',
                price: '99',
                description: 'Dla większych organizacji',
                features: [
                  'Nieograniczona liczba użytkowników',
                  'Wszystkie funkcje Professional',
                  'Zaawansowane raporty',
                  'API access',
                  'Dedykowany manager',
                  'SLA 99.9%'
                ],
                highlighted: false
              }
            ].map((plan, index) => (
              <div key={index} className={`bg-white rounded-xl p-8 shadow-lg relative ${plan.highlighted ? 'border-2 border-blue-500 transform scale-105' : ''}`}>
                {plan.highlighted && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                    Najpopularniejszy
                  </div>
                )}
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                  <div className="text-4xl font-bold text-blue-600 mb-2">
                    {plan.price}zł
                    <span className="text-lg text-gray-500 font-normal">/miesięcznie</span>
                  </div>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center">
                      <svg className="w-5 h-5 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                <button className={`w-full py-3 rounded-lg font-semibold transition-all ${plan.highlighted ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'}`}>
                  Wybierz plan
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Contact Section */}
      <div id="contact" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Skontaktuj się z nami
            </h2>
            <p className="text-xl text-gray-600">
              Masz pytania? Chętnie pomożemy!
            </p>
          </div>
          <div className="max-w-2xl mx-auto">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Imię i nazwisko *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Firma
                  </label>
                  <input
                    type="text"
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Telefon
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Wiadomość *
                </label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  rows={5}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Opisz jak możemy Ci pomóc..."
                />
              </div>
              <div className="text-center">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all disabled:opacity-50"
                >
                  {isSubmitting ? 'Wysyłanie...' : 'Wyślij wiadomość'}
                </button>
              </div>
            </form>
            {submitStatus === 'success' && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 text-center">
                  Dziękujemy za wiadomość! Odpowiemy najszybciej jak to możliwe.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">TimeTracker Pro</h3>
            <p className="text-gray-400 mb-8">Nowoczesne zarządzanie czasem dla nowoczesnych firm</p>
            <div className="flex justify-center space-x-6">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Polityka prywatności</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Regulamin</a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">Kontakt</a>
            </div>
            <p className="text-gray-400 mt-8">© 2025 TimeTracker Pro. Wszystkie prawa zastrzeżone.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

const MainApp = () => {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      <HomePage />
    </div>
  );
};

export default MainApp;