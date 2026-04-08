import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

export const otpAPI = {
  sendOTP: async (email: string) => {
    const response = await api.post('/api/otp/send', { email })
    return response.data
  },

  verifyOTP: async (email: string, otpCode: string) => {
    const response = await api.post('/api/otp/verify', { email, otp_code: otpCode })
    return response.data
  },
}

export const caseAPI = {
  submitCase: async (formData: FormData, verificationToken: string) => {
    // Attach the OTP token to the form data before sending
    formData.append('verification_token', verificationToken)
    
    const response = await api.post('/api/case/submit', formData)
    return response.data
  },

  analyzeCase: async (caseId: string) => {
    const response = await api.post(`/api/case/${caseId}/analyze`)
    return response.data
  },

  getCaseDetails: async (caseId: string) => {
    const response = await api.get(`/api/case/${caseId}`)
    return response.data
  },
}

export const reportAPI = {
  downloadPDF: async (caseId: string) => {
    const response = await api.get(`/api/report/${caseId}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },

  getComplaintGuidance: async (caseId: string) => {
    const response = await api.get(`/api/report/${caseId}/complaint-guidance`)
    return response.data
  },
}

export default api