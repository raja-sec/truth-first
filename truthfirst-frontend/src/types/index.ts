// Type Definitions for TruthFirst Frontend

export interface PersonalInfo {
  name: string
  email: string
  phone: string
  location: string
}

export interface CaseInfo {
  type: 'IMAGE' | 'EMAIL' | 'URL' | 'VIDEO'
  source: string
  description: string
}

export interface FormData {
  personalInfo: PersonalInfo
  caseInfo: CaseInfo
  file: File | null
  contentText: string
  verificationToken: string
}

export interface OTPResponse {
  success: boolean
  message: string
  email: string
  expires_in_minutes: number
}

export interface OTPVerifyResponse {
  success: boolean
  message: string
  verification_token: string
  token_expires_in_minutes: number
}

export interface CaseSubmitResponse {
  case_id: string
  status: string
  message: string
  created_at: string
}

export interface AnalysisResult {
  message: string
  case_id: string
  status: string
  verdict: string
  confidence: number
  risk_score: number
}

export interface CaseDetails {
  id: string
  case_id: string;
  user_name: string
  user_email: string
  case_type: string
  case_source: string
  case_description: string
  status: string
  analysis_result: {
  overall_verdict: string
  overall_confidence: number
  overall_risk_score: number

  image_result?: {
    verdict: string
    confidence: number
    flags: string[]
    explanation: string
    grad_cam_base64?: string
  }

  video_result?: VideoAnalysisResult

  flags: string[]
  recommendations: string[]
}

  created_at: string
  analyzed_at: string
}

export interface ComplaintGuidance {
  case_id: string
  case_type: string
  verdict_category: string
  finding_summary: string
  guidance: {
    title: string
    warning_header: {
      text: string
      emphasis: string[]
    }
    when_to_report: {
      title: string
      conditional_note: string
      checklist: string[]
    }
    when_not_to_report: {
      title: string
      checklist: string[]
    }
    legal_responsibility: {
      title: string
      points: string[]
    }
    examples: {
      good_complaint: {
        label: string
        text: string
        why_good: string
      }
      bad_complaint: {
        label: string
        text: string
        why_bad: string
      }
    }
    disclaimer: {
      title: string
      points: string[]
    }
  }
  actions: {
    cybercrime_portal_url: string
    pdf_report_url: string
  }
}


export interface VideoAnalysisResult {
  verdict: string
  confidence: number
  frames_analyzed: number
  fake_probability: number
  video_duration?: number
  total_frames?: number
}