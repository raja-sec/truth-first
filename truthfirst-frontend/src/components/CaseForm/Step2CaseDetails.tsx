import React from 'react'
import { useTranslation } from 'react-i18next'
import { FileImage, Mail as MailIcon, Link as LinkIcon, FileText, Video } from 'lucide-react'
import { CaseInfo } from '../../types'

const VIDEO_ENABLED = true

interface Props {
  data: CaseInfo
  onChange: (data: CaseInfo) => void
  onNext: () => void
  onBack: () => void
}

const sourceOptions = [
  'WhatsApp',
  'Facebook',
  'Instagram',
  'Twitter / X',
  'LinkedIn',
  'Email',
  'SMS',
  'Telegram',
  'Signal',
  'Website',
  'YouTube',
  'TikTok',
  'Snapchat',
  'Other',
]

const Step2CaseDetails: React.FC<Props> = ({ data, onChange, onNext, onBack }) => {
  const { t } = useTranslation()
  
  const isVideoSelected = data.type === 'VIDEO'
  const isVideoDisabled = data.type === 'VIDEO' && !VIDEO_ENABLED

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!data.source) {
      alert('Please select a source')
      return
    }
    onNext()
  }

  const handleChange = (field: keyof CaseInfo, value: string) => {
    onChange({ ...data, [field]: value })
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {t('form.caseDetails.title', 'Case Details')}
          </h2>
          <div className="flex items-center gap-2 text-sm text-neutral">
            <span className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
              2
            </span>
            <span>Step 2 of 4</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Content Type */}
          <div>
            <label className="block text-sm font-medium mb-3">
              {t('form.caseDetails.type', 'Content Type')} *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { value: 'IMAGE', icon: FileImage, label: 'Image' },
                { value: 'VIDEO', icon: Video, label: 'Video' },
                { value: 'EMAIL', icon: MailIcon, label: 'Email' },
                { value: 'URL', icon: LinkIcon, label: 'URL' },
              ].map(({ value, icon: Icon, label }) => (
                <button
                  key={value}
                  type="button"
                  disabled={value === 'VIDEO' && !VIDEO_ENABLED}
                  onClick={() => handleChange('type', value as any)}
                  className={`p-4 rounded-lg border-2 transition-all
                    ${
                      value === 'VIDEO' && !VIDEO_ENABLED
                        ? 'opacity-50 cursor-not-allowed border-gray-300'
                        : data.type === value
                          ? 'border-primary bg-primary/10 dark:bg-primary/20'
                          : 'border-gray-300 dark:border-gray-600 hover:border-primary/50'
                    }
                  `}
                >
                  <Icon
                    size={32}
                    className={`mx-auto mb-2 ${data.type === value ? 'text-primary' : 'text-neutral'}`}
                  />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Source Dropdown */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <div className="flex items-center gap-2">
                <FileText size={16} />
                {t('form.caseDetails.source', 'Source Platform')} *
              </div>
            </label>
            <select
              required
              value={data.source}
              onChange={(e) => handleChange('source', e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600
                         bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary
                         focus:border-transparent transition-all"
            >
              <option value="">Select source platform</option>
              {sourceOptions.map((source) => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
            <p className="text-xs text-neutral mt-1">
              Where did you encounter this content?
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-2">
              {t('form.caseDetails.description', 'Description')}  
            </label>
            <textarea
              required={false}
              value={data.description}
              onChange={(e) => handleChange('description', e.target.value)}
              rows={4}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary focus:border-transparent transition-all resize-none"
              placeholder="Describe what you want us to analyze..."
            />
          </div>

          <div className="flex gap-4">
            {isVideoDisabled && (
              <p className="text-sm text-warning text-center w-full">
                Video analysis is currently disabled.
              </p>
            )}

            <button
              type="button"
              onClick={onBack}
              className="flex-1 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
            >
              ← Back
            </button>

            <button
              type="submit"
              disabled={isVideoDisabled}
              className={`flex-1 py-3 rounded-lg font-semibold transition-all
                ${
                  isVideoSelected && !VIDEO_ENABLED
                    ? 'bg-gray-400 cursor-not-allowed text-white'
                    : 'bg-primary text-white hover:bg-primary-dark hover:scale-105'
                }
              `}
            >
              {isVideoDisabled ? 'Currently Unavailable' : 'Next Step →'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Step2CaseDetails