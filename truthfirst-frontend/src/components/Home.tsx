import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
// import { Shield, Search, FileCheck } from 'lucide-react'
import {
  Shield,
  Search,
  FileCheck,
  Image as ImageIcon,
  Video,
  Mail,
  Link as LinkIcon,
  Target,
  Github,
  Linkedin
} from 'lucide-react'


const Home = () => {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const features = [
  {
    icon: ImageIcon,
    title: t('home.features.image.title', 'Image Deepfake Detection'),
    description: t(
      'home.features.image.desc',
      'Advanced hybrid ensemble (CNN + Frequency + Artifacts) analyzes visual inconsistencies and generates explainable Grad-CAM heatmaps.'
    ),
    accuracy: 'Pixel-Level Forensics',
    color: 'text-blue-500',
  },
  {
    icon: Video,
    title: t('home.features.video.title', 'Video Deepfake Detection'),
    description: t(
      'home.features.video.desc',
      'Spatial-temporal architecture (ResNeXt-50 + LSTM) analyzes frame sequences to detect flickering, blending, and unnatural expression shifts.'
    ),
    accuracy: 'Deep Time-Series',
    color: 'text-blue-500',
  },
  {
    icon: Mail,
    title: t('home.features.email.title', 'Email Phishing Detection'),
    description: t(
      'home.features.email.desc',
      'Fine-tuned BERT NLP model fused with deep header forensics (SPF/DKIM) and embedded URL threat intelligence.'
    ),
    accuracy: t('home.features.email.accuracy', 'Multi-Layer Defense'),
    color: 'text-green-500',
  },
  {
    icon: LinkIcon,
    title: t('home.features.url.title', 'Malicious URL Detection'),
    description: t(
      'home.features.url.desc',
      'Real-time multi-API threat fusion querying VirusTotal, Google Safe Browsing, and URLScan with in-memory caching.'
    ),
    accuracy: t('home.features.url.accuracy', 'Global Threat Intel'),
    color: 'text-red-500',
  },
]
  const teamMembers = [
  {
    name: 'Raja Mishra',
    role: 'Team Leader',
    image: '/team/raja-mishra.png',
    github: 'https://github.com/raja-sec',
    linkedin: 'https://www.linkedin.com/in/raja-mishra/',
  },
  {
    name: 'Rajvi Savla',
    role: 'Co-leader',
    image: '/team/rajvi-savla.png',
    github: 'https://github.com/Rajvi2005',
    linkedin: 'https://www.linkedin.com/in/rajvi-savla-a4641b28b/',
  },
]


  return (
    // <div className="pt-24 px-6 max-w-6xl mx-auto">
    <div className="pt-24 px-6 max-w-6xl mx-auto">
      {/* Hero Section */}
      {/* <div className="text-center py-20"> */}
      <section id="hero" className="text-center py-20 scroll-mt-20">
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
          {t('home.hero.title')}
        </h1>
        <p className="text-xl text-neutral dark:text-gray-400 mb-8">
          {t('home.hero.subtitle')}
        </p>
        <button
          onClick={() => navigate('/submit')}
          className="bg-primary text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-primary-dark transition-all hover:scale-105"
        >
          {t('home.hero.cta')} →
        </button>
      {/* </div> */}
      </section>


<section id="about" className="py-16 scroll-mt-20">
  <div className="bg-gradient-to-br from-primary/10 to-blue-500/10 dark:from-primary/20 dark:to-blue-500/20 rounded-card p-12">
    {/* 1. Change to a 3-column grid */}
    <div className="grid md:grid-cols-3 gap-12 items-center">
      
      {/* 2. Tell the text to take up 2 of those 3 columns */}
      <div className="md:col-span-2">
        <h2 className="text-4xl font-bold mb-6">
          {t('home.about.title', 'About TruthFirst')}
        </h2>
        <p className="text-lg text-neutral dark:text-gray-300 mb-4">
          {t(
            'home.about.p1',
            'TruthFirst is an AI-powered platform dedicated to combating digital deception.'
          )}
        </p>
        <p className="text-lg text-neutral dark:text-gray-300 mb-4">
          {t(
            'home.about.p2',
            'We empower users to verify digital content through transparent, explainable AI, providing actionable forensic reports and legally safe guidance for cybercrime reporting.'
          )}
        </p>
      </div>

      {/* The icon will naturally take up the remaining 1 column */}
      <div className="flex justify-center">
        <Target size={200} className="text-primary opacity-20" />
      </div>
      
    </div>
  </div>
</section>

<section id="features" className="py-16 scroll-mt-20">
  <h2 className="text-4xl font-bold text-center mb-4">
    {t('home.features.title', 'Our Detection Capabilities')}
  </h2>
  <p className="text-center text-neutral dark:text-gray-400 mb-12 max-w-2xl mx-auto">
    {t(
      'home.features.subtitle',
      'Powered by state-of-the-art AI models trained on real-world data'
    )}
  </p>

  <div className="grid md:grid-cols-4 gap-6">
    {features.map((feature, index) => (
      <div
        key={index}
        className="bg-white dark:bg-gray-800 rounded-card p-6 shadow-lg hover:shadow-xl transition-all hover:scale-105"
      >
        <feature.icon size={48} className={`${feature.color} mb-4`} />
        <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
        <p className="text-neutral dark:text-gray-400 mb-4 text-sm">
          {feature.description}
        </p>
        <div className="inline-block bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-semibold">
          {feature.accuracy}
        </div>
      </div>
    ))}
  </div>
</section>


      {/* How It Works */}
      {/* <div className="py-16"> */}
      <section id="how-it-works" className="py-16 scroll-mt-20">
        <h2 className="text-3xl font-bold text-center mb-12">{t('home.howItWorks.title')}</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6 rounded-card bg-gray-50 dark:bg-gray-800">
            <Shield size={48} className="mx-auto mb-4 text-primary" />
            <h3 className="text-xl font-semibold mb-2">{t('home.howItWorks.step1')}</h3>
            <p className="text-neutral dark:text-gray-400">Upload your image, video, email, or URL for analysis</p>
          </div>
          <div className="text-center p-6 rounded-card bg-gray-50 dark:bg-gray-800">
            <Search size={48} className="mx-auto mb-4 text-primary" />
            <h3 className="text-xl font-semibold mb-2">{t('home.howItWorks.step2')}</h3>
            <p className="text-neutral dark:text-gray-400">Our AI analyzes the content</p>
          </div>
          <div className="text-center p-6 rounded-card bg-gray-50 dark:bg-gray-800">
            <FileCheck size={48} className="mx-auto mb-4 text-primary" />
            <h3 className="text-xl font-semibold mb-2">{t('home.howItWorks.step3')}</h3>
            <p className="text-neutral dark:text-gray-400">Get detailed results with PDF reports</p>
          </div>
        </div>
      {/* </div> */}
      </section>




<section id="team" className="py-16 scroll-mt-20">
  <h2 className="text-4xl font-bold text-center mb-4">Meet Our Team</h2>
  <p className="text-center text-neutral dark:text-gray-400 mb-12 max-w-2xl mx-auto">
    The people building TruthFirst
  </p>

  <div className="grid sm:grid-cols-2 gap-6 max-w-3xl mx-auto">
    {teamMembers.map((member, index) => (
      <div
        key={index}
        className="bg-white dark:bg-gray-800 rounded-card p-6 text-center shadow-lg hover:shadow-xl transition-all hover:scale-105"
      >
        {/* Avatar */}
        <div className="mb-6">
          <img 
            src={member.image} 
            alt={`${member.name} - ${member.role}`}
            className="w-32 h-32 mx-auto rounded-full object-cover border-4 border-primary/20 shadow-md transition-transform hover:scale-105"
          />
        </div>

        {/* Name */}
        <h3 className="text-lg font-bold mb-1">{member.name}</h3>

        {/* Role */}
        <p className="text-sm text-primary mb-4">{member.role}</p>

        {/* Social Links */}
        <div className="flex justify-center gap-4">
          <a
            href={member.github}
            target="_blank"
            rel="noopener noreferrer"
            className="text-neutral hover:text-primary transition-colors"
            aria-label="GitHub"
          >
            <Github size={20} />
          </a>

          <a
            href={member.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="text-neutral hover:text-primary transition-colors"
            aria-label="LinkedIn"
          >
            <Linkedin size={20} />
          </a>
        </div>
      </div>
    ))}
  </div>
</section>



    </div>
  )
}

export default Home