import React from 'react'
import { Link } from 'react-router-dom'
// import { useTranslation } from 'react-i18next'
import { Shield, Mail, Github, Twitter, Linkedin, ExternalLink } from 'lucide-react'

const Footer: React.FC = () => {
  // const { t } = useTranslation()
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-gray-900 text-gray-300 pt-12 pb-6">
      <div className="max-w-6xl mx-auto px-6">
        {/* Main Footer Content */}
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand Column */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <Shield size={32} className="text-primary" />
              <span className="text-2xl font-bold text-white">TruthFirst</span>
            </div>
            <p className="text-sm mb-4 max-w-md">
              Comprehensive multi-modal deception detection platform. Defending digital trust across images, video, URLs, and emails with explainable AI.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/truthfirst"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
                aria-label="GitHub"
              >
                <Github size={20} />
              </a>
              <a
                href="https://twitter.com/truthfirst"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
                aria-label="Twitter"
              >
                <Twitter size={20} />
              </a>
              <a
                href="https://linkedin.com/company/truthfirst"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-primary transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin size={20} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="hover:text-primary transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <a href="#features" className="hover:text-primary transition-colors">
                  Features
                </a>
              </li>
              <li>
                <a href="#about" className="hover:text-primary transition-colors">
                  About Us
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-primary transition-colors">
                  How It Works
                </a>
              </li>
              <li>
                <a href="#team" className="hover:text-primary transition-colors">
                  Our Team
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-white font-semibold mb-4">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/submit" className="hover:text-primary transition-colors">
                  Submit Case
                </Link>
              </li>
              <li>
                <a
                  href="https://cybercrime.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-primary transition-colors inline-flex items-center gap-1"
                >
                  Cyber Crime Portal
                  <ExternalLink size={12} />
                </a>
              </li>
              <li>
                <a href="#privacy" className="hover:text-primary transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#terms" className="hover:text-primary transition-colors">
                  Terms of Service
                </a>
              </li>
              <li>
                <a
                  href="mailto:contact@truthfirst.ai"
                  className="hover:text-primary transition-colors inline-flex items-center gap-1"
                >
                  <Mail size={14} />
                  Contact Us
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-800 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm">
            {/* Copyright */}
            <p className="text-center md:text-left">
              © {currentYear} TruthFirst. All rights reserved.
            </p>

            {/* Legal Links */}
            <div className="flex items-center gap-4">
              <a href="#disclaimer" className="hover:text-primary transition-colors">
                Disclaimer
              </a>
              <span className="text-gray-700">|</span>
              <a href="#accessibility" className="hover:text-primary transition-colors">
                Accessibility
              </a>
              <span className="text-gray-700">|</span>
              <a href="#cookies" className="hover:text-primary transition-colors">
                Cookie Policy
              </a>
            </div>
          </div>

          {/* Attribution */}
          <p className="text-xs text-gray-600 text-center mt-4">
            Built with 💙 for digital safety. Powered by AI, backed by research.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer