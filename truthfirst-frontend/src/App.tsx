import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import Navbar from './components/Navbar'
import Home from './components/Home'
import CaseFormContainer from './components/CaseForm/CaseFormContainer'
import Results from './components/Results'
import './i18n/config'
import Footer from './components/Footer'


function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-white transition-colors flex flex-col">
          <Navbar />
          <main className="flex-1">
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/submit" element={<CaseFormContainer />} />
    <Route path="/results/:caseId" element={<Results />} />
  </Routes>
</main>
          <Footer />
        </div>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App