import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Download,
  FileText,
  Loader,
  ArrowLeft,
  XCircle,
} from 'lucide-react'
import { caseAPI, reportAPI } from '../services/api'
import { CaseDetails } from '../types'
import ComplaintModal from './ComplaintModal'

const Results: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>()
  const navigate = useNavigate()
  const { t } = useTranslation()

  const [caseData, setCaseData] = useState<CaseDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showComplaintModal, setShowComplaintModal] = useState(false)
  const [downloadingPDF, setDownloadingPDF] = useState(false)

  useEffect(() => {
    if (!caseId) return

    const fetchCaseDetails = async () => {
      try {
        const data = await caseAPI.getCaseDetails(caseId)
        setCaseData(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load case details')
      } finally {
        setLoading(false)
      }
    }

    fetchCaseDetails()

    const interval = setInterval(async () => {
      if (caseData?.status === 'COMPLETED') {
        clearInterval(interval)
        return
      }
      try {
        const data = await caseAPI.getCaseDetails(caseId)
        setCaseData(data)
        if (data.status === 'COMPLETED') clearInterval(interval)
      } catch {
        /* silent polling error */
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [caseId])

  const handleDownloadPDF = async () => {
    if (!caseId) return

    setDownloadingPDF(true)
    try {
      const blob = await reportAPI.downloadPDF(caseId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `TruthFirst_Report_${caseId}.pdf`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to download PDF')
    } finally {
      setDownloadingPDF(false)
    }
  }

  const getVerdictColor = (verdict: string) => {
    if (verdict === 'GENUINE') return 'success'
    if (verdict === 'DEEPFAKE' || verdict === 'PHISHING') return 'danger'
    return 'warning'
  }

  const getVerdictIcon = (verdict: string) => {
    if (verdict === 'GENUINE') return <CheckCircle size={48} />
    if (verdict === 'DEEPFAKE' || verdict === 'PHISHING') return <XCircle size={48} />
    return <AlertTriangle size={48} />
  }

  /** ✅ Donut chart (pure SVG, no libs) */
  const renderDonutChart = (confidence: number, verdict: string) => {
    const percent = Math.round(confidence * 100)
    const radius = 70
    const circumference = 2 * Math.PI * radius
    const offset = circumference - (percent / 100) * circumference

    const color =
      verdict === 'GENUINE'
        ? '#22c55e'
        : verdict === 'DEEPFAKE' || verdict === 'PHISHING'
        ? '#ef4444'
        : '#f59e0b'

    return (
      <svg width="200" height="200" viewBox="0 0 200 200" className="mx-auto">
        <circle
          cx="100"
          cy="100"
          r={radius}
          stroke="#e5e7eb"
          strokeWidth="18"
          fill="none"
          className="dark:stroke-gray-700"
        />
        <circle
          cx="100"
          cy="100"
          r={radius}
          stroke={color}
          strokeWidth="18"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 100 100)"
          className="transition-all duration-1000"
        />
        <text
  x="100"
  y="95"
  textAnchor="middle"
  fontSize="36"
  fontWeight="bold"
  className="fill-black dark:fill-white"
>
  {percent}%
</text>

<text
  x="100"
  y="118"
  textAnchor="middle"
  fontSize="12"
  opacity="0.6"
  className="fill-black dark:fill-white"
>
  Confidence
</text>

      </svg>
    )
  }

 if (loading) {
  return (
    <div className="pt-24 min-h-screen flex flex-col items-center justify-center">
      <Loader size={64} className="animate-spin text-primary mb-4" />
      
      <p className="text-sm text-neutral mt-2">
        This may take up to a minute for video and URL analysis.
      </p>
    </div>
  )
}


  if (error) {
    return (
      <div className="pt-24 min-h-screen flex items-center justify-center text-center">
        <XCircle size={64} className="text-danger mb-4" />
        <p className="text-xl font-semibold">{error}</p>
      </div>
    )
  }

  if (!caseData) return null

  const verdict = caseData.analysis_result?.overall_verdict || 'PROCESSING'
  const confidence = caseData.analysis_result?.overall_confidence || 0
  // const riskScore = caseData.analysis_result?.overall_risk_score || 0
  const flags = caseData.analysis_result?.flags || []
  const recommendations = caseData.analysis_result?.recommendations || []
  const gradCam = caseData.analysis_result?.image_result?.grad_cam_base64

  return (
    <>
      <div className="pt-24 pb-12 px-6">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 mb-6 text-neutral hover:text-primary"
          >
            <ArrowLeft size={20} /> Back to Home
          </button>

          {/* Case Header */}
<div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-6 mb-6">
  <div className="flex items-center justify-between mb-4">
    <div>
      <h1 className="text-2xl font-bold mb-1">Analysis Results</h1>
      <p className="text-sm text-neutral">
        Case ID: {caseData.case_id || caseData.id || 'N/A'}
      </p>
    </div>
    <div className="text-right">
      <p className="text-sm text-neutral">Analyzed</p>
      <p className="text-sm font-medium">
        {new Date(caseData.analyzed_at + 'Z').toLocaleString()}
      </p>
    </div>
  </div>
</div>


          {/* Verdict + Donut */}
          <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-8 mb-6 grid md:grid-cols-2 gap-8 items-center">
            <div>
              <div className={`text-${getVerdictColor(verdict)} mb-4`}>
                {getVerdictIcon(verdict)}
              </div>
              <h2 className="text-4xl font-bold mb-2">{verdict}</h2>
              <p className="text-neutral mb-4">
                Content Type: {caseData.case_type}
              </p>

            </div>

            {renderDonutChart(confidence, verdict)}
          </div>

          {/* Flags */}
          {flags.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-6 mb-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <AlertTriangle className="text-warning" />
                Detected Issues
              </h3>
              <ul className="space-y-2">
                {flags.map((f, i) => (
                  <li key={i}>• {f}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Grad-CAM */}
          {gradCam && (
            <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-6 mb-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Shield className="text-primary" />
                Visual Analysis
              </h3>
              <img
                src={`data:image/jpeg;base64,${gradCam}`}
                alt="Grad-CAM"
                className="rounded-lg mx-auto"
              />
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-6 mb-6">
              <h3 className="text-xl font-bold mb-4">Recommendations</h3>
              <ul className="space-y-2">
                {recommendations.map((r, i) => (
                  <li key={i} className="flex gap-2">
                    <CheckCircle className="text-success" /> {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="grid md:grid-cols-2 gap-4">
            <button
              onClick={handleDownloadPDF}
              disabled={downloadingPDF}
              className="bg-primary text-white py-4 rounded-lg flex justify-center gap-2"
            >
              {downloadingPDF ? (
                <Loader className="animate-spin" />
              ) : (
                <>
                  <Download /> {t('results.downloadPDF')}
                </>
              )}
            </button>

            <button
              onClick={() => setShowComplaintModal(true)}
              className="bg-success text-white py-4 rounded-lg flex justify-center gap-2"
            >
              <FileText /> {t('results.reportCrime')}
            </button>
          </div>
        </div>
      </div>

      {showComplaintModal && (
        <ComplaintModal
          caseId={caseId!}
          onClose={() => setShowComplaintModal(false)}
        />
      )}
    </>
  )
}

export default Results
