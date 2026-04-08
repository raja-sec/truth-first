import React, { useEffect, useState } from 'react'
import { X, ExternalLink, AlertTriangle, Loader, CheckCircle, XCircle } from 'lucide-react'
import { reportAPI } from '../services/api'
import { ComplaintGuidance } from '../types'

interface Props {
  caseId: string
  onClose: () => void
}

const ComplaintModal: React.FC<Props> = ({ caseId, onClose }) => {
  const [guidance, setGuidance] = useState<ComplaintGuidance | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchGuidance = async () => {
      try {
        const data = await reportAPI.getComplaintGuidance(caseId)
        setGuidance(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load guidance')
      } finally {
        setLoading(false)
      }
    }

    fetchGuidance()
  }, [caseId])

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="bg-white dark:bg-gray-800 rounded-card shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold">Complaint Filing Guidance</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-12">
              <Loader size={48} className="animate-spin mx-auto mb-4 text-primary" />
              <p className="text-neutral">Loading guidance...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <XCircle size={48} className="mx-auto mb-4 text-danger" />
              <p className="font-semibold mb-2">Error</p>
              <p className="text-neutral">{error}</p>
            </div>
          ) : guidance ? (
            <div className="space-y-6">
              {/* Warning Header */}
              <div className="bg-warning/10 border-2 border-warning rounded-lg p-6">
                <div className="flex items-start gap-3">
                  <AlertTriangle size={32} className="text-warning flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-xl font-bold mb-2">
                      {guidance.guidance.warning_header.text}
                    </h3>
                    <ul className="space-y-1 text-sm">
                      {guidance.guidance.warning_header.emphasis.map((point, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-warning mt-0.5">•</span>
                          <span className="font-semibold">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Case Summary */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h3 className="font-bold mb-2">Our Analysis (Reference Only)</h3>
                <p className="text-sm text-neutral mb-2">
                  <strong>Case ID:</strong> {guidance.case_id}
                </p>
                <p className="text-sm text-neutral mb-2">
                  <strong>Content Type:</strong> {guidance.case_type}
                </p>
                <p className="text-sm">{guidance.finding_summary}</p>
              </div>

              {/* When to Report */}
              <div>
                <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <CheckCircle size={20} className="text-success" />
                  {guidance.guidance.when_to_report.title}
                </h3>
                {guidance.guidance.when_to_report.conditional_note && (
                  <p className="text-sm text-neutral mb-3">
                    {guidance.guidance.when_to_report.conditional_note}
                  </p>
                )}
                <ul className="space-y-2">
                  {guidance.guidance.when_to_report.checklist.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                      <CheckCircle size={16} className="text-success mt-0.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* When NOT to Report */}
              <div>
                <h3 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <XCircle size={20} className="text-danger" />
                  {guidance.guidance.when_not_to_report.title}
                </h3>
                <ul className="space-y-2">
                  {guidance.guidance.when_not_to_report.checklist.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                      <XCircle size={16} className="text-danger mt-0.5 flex-shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Legal Responsibility */}
              <div className="bg-danger/10 border border-danger rounded-lg p-4">
                <h3 className="text-lg font-bold mb-3">
                  {guidance.guidance.legal_responsibility.title}
                </h3>
                <ul className="space-y-2">
                  {guidance.guidance.legal_responsibility.points.map((point, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                      <span className="text-danger mt-0.5">⚠</span>
                      <span className="font-semibold">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Examples */}
              <div className="grid md:grid-cols-2 gap-4">
                {/* Good Example */}
                <div className="bg-success/10 border border-success rounded-lg p-4">
                  <h4 className="font-bold text-success mb-2">
                    {guidance.guidance.examples.good_complaint.label}
                  </h4>
                  <p className="text-sm italic mb-2">
                    "{guidance.guidance.examples.good_complaint.text}"
                  </p>
                  <p className="text-xs text-neutral">
                    <strong>Why good:</strong> {guidance.guidance.examples.good_complaint.why_good}
                  </p>
                </div>

                {/* Bad Example */}
                <div className="bg-danger/10 border border-danger rounded-lg p-4">
                  <h4 className="font-bold text-danger mb-2">
                    {guidance.guidance.examples.bad_complaint.label}
                  </h4>
                  <p className="text-sm italic mb-2">
                    "{guidance.guidance.examples.bad_complaint.text}"
                  </p>
                  <p className="text-xs text-neutral">
                    <strong>Why bad:</strong> {guidance.guidance.examples.bad_complaint.why_bad}
                  </p>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h3 className="font-bold mb-3">{guidance.guidance.disclaimer.title}</h3>
                <ul className="space-y-2">
                  {guidance.guidance.disclaimer.points.map((point, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-neutral">
                      <span className="mt-0.5">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        {guidance && (
          <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900/50">
            <div className="flex gap-4">
              <a
                href={guidance.actions.cybercrime_portal_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 bg-primary text-white py-3 rounded-lg font-semibold hover:bg-primary-dark transition-all"
              >
                Visit Cyber Crime Portal
                <ExternalLink size={20} />
              </a>
              <button
                onClick={onClose}
                className="px-6 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg font-semibold hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ComplaintModal