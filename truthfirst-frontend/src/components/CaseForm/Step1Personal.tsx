// import React from 'react'
import { useTranslation } from 'react-i18next'
import { User, Mail, Phone, MapPin } from 'lucide-react'
import { PersonalInfo } from '../../types'
import React, { useState, useEffect } from 'react'
import { getStates, getCitiesByState } from '../../utils/locationData'


interface Props {
  data: PersonalInfo
  onChange: (data: PersonalInfo) => void
  onNext: () => void
}

const Step1Personal: React.FC<Props> = ({ data, onChange, onNext }) => {
  const { t } = useTranslation()
  const [selectedState, setSelectedState] = useState('')
  const [selectedCity, setSelectedCity] = useState('')
  const [availableCities, setAvailableCities] = useState<string[]>([])

  const states = getStates()

  useEffect(() => {
  if (data.location) {
    const parts = data.location.split(', ')
    if (parts.length === 2) {
      const [city, state] = parts
      setSelectedState(state)
      setSelectedCity(city)
      setAvailableCities(getCitiesByState(state))
    }
  }
}, [])


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // onNext()
    if (!selectedState || !selectedCity) {
      alert('Please select both state and city')
      return
    }
    onNext()
  }

  const handleChange = (field: keyof PersonalInfo, value: string) => {
    onChange({ ...data, [field]: value })
  }

  const handleStateChange = (state: string) => {
    setSelectedState(state)
    setSelectedCity('')
    setAvailableCities(getCitiesByState(state))
    onChange({ ...data, location: '' })
  }

  const handleCityChange = (city: string) => {
    setSelectedCity(city)
    onChange({ ...data, location: `${city}, ${selectedState}` })
  }


  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {t('form.personal.title')}
          </h2>
          <div className="flex items-center gap-2 text-sm text-neutral">
            <span className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
              1
            </span>
            <span>Step 1 of 4</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <div className="flex items-center gap-2">
                <User size={16} />
                {t('form.personal.name')} *
              </div>
            </label>
            <input
              type="text"
              required
              value={data.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              placeholder="Enter your full name"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <div className="flex items-center gap-2">
                <Mail size={16} />
                {t('form.personal.email')} *
              </div>
            </label>
            <input
              type="email"
              required
              value={data.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              placeholder="your-email@example.com"
            />
            <p className="text-xs text-neutral mt-1">
              You'll receive a verification code at this email
            </p>
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium mb-2">
              <div className="flex items-center gap-2">
                <Phone size={16} />
                {t('form.personal.phone')}
              </div>
            </label>
            <input
              type="tel"
              value={data.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
              placeholder="+91 1234567890"
            />
          </div>

          {/* Location */}
          <div>
<div>
  <label className="block text-sm font-medium mb-2">
    <div className="flex items-center gap-2">
      <MapPin size={16} />
      {t('form.personal.location')} *
    </div>
  </label>

  {/* State + City Row */}
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    {/* State */}
    <select
      required
      value={selectedState}
      onChange={(e) => handleStateChange(e.target.value)}
      className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600
                 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary
                 focus:border-transparent transition-all"
    >
      <option value="">Select your state</option>
      {states.map((state) => (
        <option key={state} value={state}>
          {state}
        </option>
      ))}
    </select>

    {/* City */}
    <select
      required
      value={selectedCity}
      onChange={(e) => handleCityChange(e.target.value)}
      disabled={!selectedState}
      className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600
                 bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary
                 focus:border-transparent transition-all
                 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <option value="">
        {selectedState ? 'Select your city' : 'Select state first'}
      </option>
      {availableCities.map((city) => (
        <option key={city} value={city}>
          {city}
        </option>
      ))}
    </select>
  </div>
</div>

          </div>

          <button
            type="submit"
            className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-primary-dark transition-all hover:scale-105"
          >
            Next Step →
          </button>
        </form>
      </div>
    </div>
  )
}

export default Step1Personal