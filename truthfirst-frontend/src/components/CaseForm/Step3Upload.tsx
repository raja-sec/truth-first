import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
// import { Upload, FileImage, X, Info, FileText } from 'lucide-react'
import { Upload, FileImage, X, Info, FileText, Video } from 'lucide-react'
import { CaseInfo } from '../../types'
import { useEffect } from 'react'



interface Props {
  caseType: CaseInfo['type']
  file: File | null
  contentText: string
  onFileChange: (file: File | null) => void
  onTextChange: (text: string) => void
  onNext: () => void
  onBack: () => void
}

const Step3Upload: React.FC<Props> = ({
  caseType,
  file,
  contentText,
  onFileChange,
  onTextChange,
  onNext,
  onBack,
}) => {
  const { t } = useTranslation()
  const [dragActive, setDragActive] = useState(false)
  const [showEmailGuide, setShowEmailGuide] = useState(false)
const [emailInputMode, setEmailInputMode] = useState<'file' | 'paste'>('file')
const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null)



  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

      useEffect(() => {
  onFileChange(null)
  setVideoPreviewUrl(null)
}, [caseType])


  const processSelectedFile = (selectedFile: File) => {



  // Cleanup old video preview if switching modes
  if (caseType !== 'VIDEO' && videoPreviewUrl) {
    URL.revokeObjectURL(videoPreviewUrl)
    setVideoPreviewUrl(null)
  }

  if (caseType === 'IMAGE') {
    const validTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!validTypes.includes(selectedFile.type)) {
      alert('Please upload a valid image (JPG, PNG, WEBP)')
      return
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('Image must be less than 10MB')
      return
    }
  }

  if (caseType === 'VIDEO') {
    const validTypes = ['video/mp4', 'video/x-msvideo', 'video/quicktime']
    if (!validTypes.includes(selectedFile.type)) {
      alert('Please upload a valid video file (MP4, AVI, MOV)')
      return
    }
    if (selectedFile.size > 50 * 1024 * 1024) {
      alert('Video must be less than 50MB')
      return
    }

    if (videoPreviewUrl) {
      URL.revokeObjectURL(videoPreviewUrl)
    }

    const previewUrl = URL.createObjectURL(selectedFile)
    setVideoPreviewUrl(previewUrl)
  }


if (caseType === 'EMAIL') {
  const isEml =
    selectedFile.type === 'message/rfc822' ||
    selectedFile.name.toLowerCase().endsWith('.eml')

  const isImage =
    selectedFile.type.startsWith('image/') &&
    ['png', 'jpg', 'jpeg', 'webp'].some(ext =>
      selectedFile.name.toLowerCase().endsWith(ext)
    )

  if (!isEml && !isImage) {
    alert('Upload .eml file or email screenshot (PNG/JPG)')
    return
  }

  // Size limits
  if (isEml && selectedFile.size > 5 * 1024 * 1024) {
    alert('.eml file must be under 5MB')
    return
  }

  if (isImage && selectedFile.size > 10 * 1024 * 1024) {
    alert('Screenshot must be under 10MB')
    return
  }
}



  onFileChange(selectedFile)
}

  const handleDrop = (e: React.DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  setDragActive(false)

  if (!e.dataTransfer.files || !e.dataTransfer.files[0]) return
  processSelectedFile(e.dataTransfer.files[0])
}

const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
  if (!e.target.files || !e.target.files[0]) return
  processSelectedFile(e.target.files[0])
}

useEffect(() => {
  if (caseType === 'EMAIL') {
    if (emailInputMode === 'file') {
      onTextChange('')
    } else {
      onFileChange(null)
    }
  }
}, [emailInputMode])


  const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()

  if (caseType === 'IMAGE' && !file) {
    alert('Please upload an image')
    return
  }

  if (caseType === 'VIDEO' && !file) {
  alert('Please upload a video')
  return
}

    if (caseType === 'VIDEO' && contentText.trim()) {
    alert('Video cases do not accept text input')
    return
  }


  if (caseType === 'EMAIL') {
    if (emailInputMode === 'file' && !file) {
      alert('Please upload an .eml file or switch to paste mode')
      return
    }
    if (emailInputMode === 'paste' && !contentText.trim()) {
      alert('Please paste email content')
      return
    }
  }

  if (caseType === 'URL' && !contentText.trim()) {
    alert('Please enter a URL')
    return
  }

  onNext()
}


  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {t('form.upload.title')}
          </h2>
          <div className="flex items-center gap-2 text-sm text-neutral">
            <span className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs">
              3
            </span>
            <span>Step 3 of 4</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {caseType === 'IMAGE' ? (
            <>
              {/* File Upload */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
                  dragActive
                    ? 'border-primary bg-primary/10 dark:bg-primary/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-primary/50'
                }`}
              >
                {file ? (
                  <div className="space-y-4">
                    <FileImage size={48} className="mx-auto text-success" />
                    <div>
                      <p className="font-medium">{file.name}</p>
                      <p className="text-sm text-neutral">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => onFileChange(null)}
                      className="inline-flex items-center gap-2 text-danger hover:underline"
                    >
                      <X size={16} />
                      Remove
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Upload size={48} className="mx-auto text-neutral" />
                    <div>
                      <p className="text-lg font-medium mb-1">{t('form.upload.dragDrop')}</p>
                      <p className="text-sm text-neutral">JPG, PNG, WEBP (Max 10MB)</p>
                    </div>
                    <label className="inline-block bg-primary text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-primary-dark transition-all">
                      Choose File
                      <input type="file" accept="image/*" onChange={handleFileInput} className="hidden" />
                    </label>
                  </div>
                )}
              </div>
            </>
          ) : caseType === 'VIDEO' ? (
<>
  <div
    onDragEnter={handleDrag}
    onDragLeave={handleDrag}
    onDragOver={handleDrag}
    onDrop={handleDrop}
    className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
      dragActive
        ? 'border-primary bg-primary/10 dark:bg-primary/20'
        : 'border-gray-300 dark:border-gray-600 hover:border-primary/50'
    }`}
  >
    {!file ? (
      <div className="space-y-4">
        <Video size={48} className="mx-auto text-neutral" />
        <div>
          <p className="text-lg font-medium">Upload Suspicious Video</p>
          <p className="text-sm text-neutral">
            MP4, AVI, MOV • Max 50MB • Max 60 seconds
          </p>
        </div>
        <label className="inline-block bg-primary text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-primary-dark">
          Choose Video
          <input
            type="file"
            accept="video/mp4,video/x-msvideo,video/quicktime"
            onChange={handleFileInput}
            className="hidden"
          />
        </label>
      </div>
    ) : (
    

      // (preview disabled) 
      <div className="space-y-4">
        <div className="flex flex-col items-center gap-3">
  <Video size={64} className="text-primary" />
  <p className="text-sm text-neutral">
    Video file selected
  </p>
</div>


        <div>
          <p className="font-medium">{file.name}</p>
          <p className="text-sm text-neutral">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            onFileChange(null)
            if (videoPreviewUrl) URL.revokeObjectURL(videoPreviewUrl)
            setVideoPreviewUrl(null)
          }}
          className="inline-flex items-center gap-2 text-danger hover:underline"
        >
          <X size={16} />
          Remove
        </button>
      </div>
    )}
  </div>

  {/* Requirements */}
  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 text-sm">
    <strong>Video Requirements:</strong>
    <ul className="list-disc ml-5 mt-2 space-y-1">
      <li>Clearly visible human face</li>
      <li>Maximum duration: 60 seconds</li>
      <li>Analysis may take 30–60 seconds</li>
    </ul>
  </div>
</>


          ) : caseType === 'EMAIL' ? (
            <>
  {/* Email Mode Toggle */}
  <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
    <div className="flex items-center gap-2">
      {/* <span className="text-sm font-medium">Input Method:</span> */}
      <div className="flex gap-2">
        <button
          type="button"
     
          onClick={() => {
  setEmailInputMode('file')
  onTextChange('')
  onFileChange(null)
}}

          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            emailInputMode === 'file'
              ? 'bg-primary text-white'
              : 'bg-white dark:bg-gray-800 border'
          }`}
        >
          Upload .eml or image file
        </button>

        <button
          type="button"
          onClick={() => {
            setEmailInputMode('paste')
            onFileChange(null)
          }}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            emailInputMode === 'paste'
              ? 'bg-primary text-white'
              : 'bg-white dark:bg-gray-800 border'
          }`}
        >
          Paste Content
        </button>
      </div>
    </div>

    <button
      type="button"
      onClick={() => setShowEmailGuide(true)}
      className="flex items-center gap-2 text-primary"
    >
      <Info size={18} /> Help
    </button>
  </div>

  {emailInputMode === 'file' ? (
    /* .eml upload block */
<div
  onDragEnter={handleDrag}
  onDragLeave={handleDrag}
  onDragOver={handleDrag}
  onDrop={handleDrop}
  className={`border-2 border-dashed rounded-lg p-12 text-center transition-all ${
    dragActive
      ? 'border-primary bg-primary/10 dark:bg-primary/20'
      : 'border-gray-300 dark:border-gray-600 hover:border-primary/50'
  }`}
>
  {file ? (
    <div className="space-y-4">
      <FileText size={48} className="mx-auto text-success" />

      <div>
        <p className="font-medium">{file.name}</p>
        <p className="text-sm text-neutral">
          {(file.size / 1024).toFixed(2)} KB
        </p>
      </div>

      <button
        type="button"
        onClick={() => onFileChange(null)}
        className="inline-flex items-center gap-2 text-danger hover:underline"
      >
        <X size={16} />
        Remove
      </button>
    </div>
  ) : (
    <div className="space-y-4">
      <Upload size={48} className="mx-auto text-neutral" />

      <div>

        <p className="text-lg font-medium mb-1">
  Upload email (.eml) or screenshot
</p>
<p className="text-sm text-neutral">
  Supports .eml files OR screenshots (PNG/JPG)
</p>

        <p className="text-sm text-neutral">
  Upload email (.eml) or screenshot (PNG, JPG, WEBP) • Max 5MB
</p>

      </div>

      <label className="inline-block bg-primary text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-primary-dark transition-all">
        Choose .eml or image File
        <input
  type="file"
  accept=".eml,message/rfc822,image/png,image/jpeg,image/webp"
  onChange={handleFileInput}
  className="hidden"
/>

      </label>
    </div>
  )}
</div>

  ) : (
    /* Paste email content */
    <textarea
      value={contentText}
      onChange={(e) => onTextChange(e.target.value)}
      rows={12}
      className="w-full px-4 py-3 rounded-lg font-mono"
      placeholder="Paste full email headers and body..."
    />
  )}
</>
) : (
  /* URL */
  <textarea
    value={contentText}
    onChange={(e) => onTextChange(e.target.value)}
    rows={4}
    className="w-full px-4 py-3 rounded-lg font-mono"
    placeholder="https://example.com/suspicious-link"
  />
)}
            

          <div className="flex gap-4">
            <button
              type="button"
              onClick={onBack}
              className="flex-1 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
            >
              ← Back
            </button>
            <button
              type="submit"
              className="flex-1 bg-primary text-white py-3 rounded-lg font-semibold hover:bg-primary-dark transition-all hover:scale-105"
            >
              Next Step →
            </button>
          </div>
        </form>
      </div>
      {showEmailGuide && (
  <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
    <div className="bg-white dark:bg-gray-800 p-6 rounded-card max-w-2xl">
      <button onClick={() => setShowEmailGuide(false)} className="float-right">
        <X />
      </button>
      <iframe
        className="w-full aspect-video"
        src="https://youtu.be/fIm_ol9pur0?si=xBXG1olK90OMqi2g"
        allowFullScreen
      />
    </div>
  </div>
)}

    </div>
  )
}

export default Step3Upload