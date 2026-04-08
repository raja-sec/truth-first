import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Mail, Shield, Loader, CheckCircle, XCircle } from 'lucide-react'
import { otpAPI } from '../../services/api'

interface Props {
  email: string
  onVerified: (token: string) => void
  onSubmit: () => void
  onBack: () => void
  isSubmitting: boolean
}

const Step4OTP: React.FC<Props> = ({ email, onVerified, onSubmit, onBack, isSubmitting }) => {
  const { t } = useTranslation()
  const [otpSent, setOtpSent] = useState(false)
  const [otpCode, setOtpCode] = useState('')
  const [isVerified, setIsVerified] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [isVerifying, setIsVerifying] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [error, setError] = useState('')
  const [otpAttempts, setOtpAttempts] = useState(0)

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [countdown])

  const handleSendOTP = async () => {
    setError('')
    setIsSending(true)

    try {
      await otpAPI.sendOTP(email)
      setOtpSent(true)
      setCountdown(300) // 5 minutes
      setOtpAttempts(0) // Reset attempts on new OTP
      setOtpCode('') // Clear previous OTP input
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to send OTP'
      setError(errorMsg)
      console.error('OTP Send Error:', err)
    } finally {
      setIsSending(false)
    }
  }

  const handleVerifyOTP = async () => {
  if (otpCode.length !== 6) {
    setError('Please enter a 6-digit code')
    return
  }

  setError('')
  setIsVerifying(true)

  try {
    const response = await otpAPI.verifyOTP(email, otpCode)
    setIsVerified(true)
    setError('')
    onVerified(response.verification_token)
  } catch (err: any) {
    // ⬇️ MOVE attempt increment HERE
    setOtpAttempts(prev => prev + 1)

    const errorMsg = err.response?.data?.detail?.message || 'Invalid OTP'
    const errorCode = err.response?.data?.detail?.code || ''

    if (errorCode === 'OTP_EXPIRED') {
      setError('⏰ OTP has expired. Please request a new code.')
    } else if (errorCode === 'OTP_INVALID') {
      setError(`❌ Invalid OTP. Please try again. (${3 - (otpAttempts + 1)} attempts remaining)`)
    } else if (errorCode === 'OTP_MAX_ATTEMPTS') {
      setError('🚫 Maximum attempts reached. Please request a new OTP.')
      setOtpCode('')
    } else {
      setError(errorMsg)
    }
  } finally {
    // ⬅️ THIS IS WHAT UNFREEZES THE BUTTON
    setIsVerifying(false)
  }
}


  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {t('form.otp.title')}
          </h2>
          <div className="flex items-center gap-2 text-sm text-neutral">
            <span className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
              4
            </span>
            <span>Step 4 of 4</span>
          </div>
        </div>

        <div className="space-y-6">
          {/* Email Display */}
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-sm">
              <Mail size={16} className="text-primary" />
              <span className="font-medium">{email}</span>
            </div>
          </div>

          {!otpSent ? (
            <>
              {/* Send OTP */}
              <div className="text-center py-8">
                <Shield size={64} className="mx-auto mb-4 text-primary" />
                <p className="text-neutral mb-6">
                  Click the button below to receive a verification code at your email
                </p>
                <button
                  onClick={handleSendOTP}
                  disabled={isSending}
                  className="bg-primary text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-dark transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
                >
                  {isSending ? (
                    <>
                      <Loader size={20} className="animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail size={20} />
                      {t('form.otp.sendOTP')}
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            <>
              {/* OTP Input */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium">{t('form.otp.enterOTP')} *</label>
                  {countdown > 0 && (
                    <span className="text-sm text-neutral">
                      Expires in {formatTime(countdown)}
                    </span>
                  )}
                  {countdown === 0 && (
                    <span className="text-sm text-danger font-semibold">
                      ⏰ OTP Expired
                    </span>
                  )}
                </div>

                <div className="flex gap-4 items-center">
                  <input
                    type="text"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    maxLength={6}
                    // disabled={isVerified}
                    disabled={
  isVerified ||
  countdown === 0 ||
  error.includes('Maximum')
}

                    className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary focus:border-transparent transition-all text-2xl tracking-widest text-center font-mono disabled:opacity-50"
                    placeholder="000000"
                  />

                  {!isVerified && (
                    <button
                      onClick={handleVerifyOTP}
                      // disabled={isVerifying || otpCode.length !== 6 || countdown === 0}
                      disabled={
  isVerifying ||
  otpCode.length !== 6 ||
  countdown === 0 ||
  error.includes('Maximum')
}

                      className="px-6 py-3 bg-success text-white rounded-lg font-semibold hover:bg-success/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {isVerifying ? (
                        <>
                          <Loader size={20} className="animate-spin" />
                          Verifying...
                        </>
                      ) : (
                        <>
                          <Shield size={20} />
                          {t('form.otp.verify')}
                        </>
                      )}
                    </button>
                  )}
                </div>

                {isVerified && (
                  <div className="mt-4 p-4 bg-success/10 border border-success rounded-lg flex items-center gap-2 text-success">
                    <CheckCircle size={20} />
                    <span className="font-medium">Email verified successfully!</span>
                  </div>
                )}
              </div>

              {/* Resend OTP */}
              {!isVerified && (
                <div className="text-center">
                  <button
                    onClick={handleSendOTP}
                    disabled={isSending || countdown > 240}
                    className="text-primary hover:underline text-sm disabled:opacity-50 disabled:no-underline"
                  >
                    {countdown > 240 
                      ? `Resend available in ${formatTime(countdown - 240)}`
                      : "Didn't receive code? Resend"}
                  </button>
                </div>
              )}
            </>
          )}

          {/* Error Display - ALWAYS VISIBLE WHEN ERROR EXISTS */}
          {error && (
            <div className="p-4 bg-danger/10 border-2 border-danger rounded-lg flex items-start gap-3">
              <XCircle size={20} className="text-danger flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-danger font-semibold text-sm">{error}</p>
                {error.includes('expired') && (
                  <button
                    onClick={handleSendOTP}
                    disabled={isSending}
                    className="mt-2 text-xs text-primary hover:underline"
                  >
                    → Request new OTP
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Submit */}
          <div className="flex gap-4">
            <button
              type="button"
              onClick={onBack}
              disabled={isSubmitting}
              className="flex-1 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-100 dark:hover:bg-gray-700 transition-all disabled:opacity-50"
            >
              ← Back
            </button>
            <button
              onClick={onSubmit}
              disabled={!isVerified || isSubmitting}
              className="flex-1 bg-primary text-white py-3 rounded-lg font-semibold hover:bg-primary-dark transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader size={20} className="animate-spin" />
                  Submitting...
                </>
              ) : (
                t('form.otp.submit')
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Step4OTP