import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Step1Personal from './Step1Personal'
import Step2CaseDetails from './Step2CaseDetails'
import Step3Upload from './Step3Upload'
import Step4OTP from './Step4OTP'
import type { PersonalInfo, CaseInfo, FormData } from '../../types';
// import { PersonalInfo, CaseInfo, FormData } from '../../types'
import { caseAPI } from '../../services/api'

const CaseFormContainer: React.FC = () => {
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [formData, setFormData] = useState<FormData>({
    personalInfo: {
      name: '',
      email: '',
      phone: '',
      location: '',
    },
    caseInfo: {
      type: 'IMAGE',
      source: '',
      description: '',
    },
    file: null,
    contentText: '',
    verificationToken: '',
  })

  const handlePersonalInfoChange = (data: PersonalInfo) => {
    setFormData(prev => ({ ...prev, personalInfo: data }))
  }

  const handleCaseInfoChange = (data: CaseInfo) => {
    setFormData(prev => ({ ...prev, caseInfo: data }))
  }

  const handleFileChange = (file: File | null) => {
    setFormData(prev => ({ ...prev, file }))
  }

  const handleTextChange = (text: string) => {
    setFormData(prev => ({ ...prev, contentText: text }))
  }

  const handleVerified = (token: string) => {
    setFormData(prev => ({ ...prev, verificationToken: token }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)

    try {
      // Create FormData for multipart upload
      const submitData = new FormData()

      // Add personal info
      submitData.append('personal_info', JSON.stringify(formData.personalInfo))

      // Add case info
      submitData.append('case_info', JSON.stringify(formData.caseInfo))

      // Add file or text content (FIXED)
      if (formData.file) {
        // IMAGE, VIDEO, EMAIL (.eml)
        submitData.append('file', formData.file)
      }

      if (formData.contentText?.trim()) {
        // URL or pasted EMAIL
        submitData.append('content_text', formData.contentText)
      }


      // Add verification token
      submitData.append('verification_token', formData.verificationToken)

      // Submit case
      const response = await caseAPI.submitCase(submitData, formData.verificationToken)

      // Trigger analysis
      await caseAPI.analyzeCase(response.case_id)

      // Navigate to results
      navigate(`/results/${response.case_id}`)
    } catch (error: any) {
      console.error('Submission error:', error)
      alert(error.response?.data?.detail || 'Failed to submit case. Please try again.')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="pt-24 pb-12 px-6 min-h-screen">
      {/* Progress Bar */}
      <div className="max-w-2xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-2">
          {[1, 2, 3, 4].map(step => (
            <div
              key={step}
              className={`flex items-center ${step < 4 ? 'flex-1' : ''}`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                  step <= currentStep
                    ? 'bg-primary text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-neutral'
                }`}
              >
                {step}
              </div>
              {step < 4 && (
                <div
                  className={`flex-1 h-1 mx-2 transition-all ${
                    step < currentStep
                      ? 'bg-primary'
                      : 'bg-gray-200 dark:bg-gray-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        <div className="flex justify-between text-xs text-neutral">
          <span>Personal</span>
          <span>Details</span>
          <span>Upload</span>
          <span>Verify</span>
        </div>
      </div>

      {/* Step Content */}
      {currentStep === 1 && (
        <Step1Personal
          data={formData.personalInfo}
          onChange={handlePersonalInfoChange}
          onNext={() => setCurrentStep(2)}
        />
      )}

      {currentStep === 2 && (
        <Step2CaseDetails
          data={formData.caseInfo}
          onChange={handleCaseInfoChange}
          onNext={() => setCurrentStep(3)}
          onBack={() => setCurrentStep(1)}
        />
      )}

      {currentStep === 3 && (
        <Step3Upload
          caseType={formData.caseInfo.type}
          file={formData.file}
          contentText={formData.contentText}
          onFileChange={handleFileChange}
          onTextChange={handleTextChange}
          onNext={() => setCurrentStep(4)}
          onBack={() => setCurrentStep(2)}
        />
      )}

      {currentStep === 4 && (
        <Step4OTP
          email={formData.personalInfo.email}
          onVerified={handleVerified}
          onSubmit={handleSubmit}
          onBack={() => setCurrentStep(3)}
          isSubmitting={isSubmitting}
        />
      )}
    </div>
  )
}

export default CaseFormContainer