import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Moon, Sun, Shield } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'

const Navbar = () => {
  const { t } = useTranslation()
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()

  const scrollToSection = (sectionId: string) => {
    if (location.pathname !== '/') {
      window.location.href = `/#${sectionId}`
    } else {
      const element = document.getElementById(sectionId)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }

  return (
    <nav className="fixed top-3 left-5 right-5 z-50">
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md rounded-card shadow-md px-6 py-3">
        <div className="flex items-center justify-between">
          
          <Link to="/" className="flex items-center gap-2">
            <Shield size={28} className="text-primary" />
            <span className="text-xl font-bold text-primary">TruthFirst</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link to="/" className="hover:text-primary transition-colors">
              {t('nav.home')}
            </Link>

            <button
              onClick={() => scrollToSection('about')}
              className="hover:text-primary transition-colors"
            >
              {t('nav.about')}
            </button>

            <button
              onClick={() => scrollToSection('features')}
              className="hover:text-primary transition-colors"
            >
              Features
            </button>

            <button
              onClick={() => scrollToSection('how-it-works')}
              className="hover:text-primary transition-colors"
            >
              {t('nav.howItWorks')}
            </button>

            <button
              onClick={() => scrollToSection('team')}
              className="hover:text-primary transition-colors"
            >
              Team
            </button>

            <Link to="/submit" className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors">
              {t('nav.startInvestigation')}
            </Link>

            {/* Translation Button Removed Here */}

            <button onClick={toggleTheme} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>

          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar